"""Main Flask application for the manga reader platform."""

import os
import re
from flask import Flask, render_template, request, jsonify, send_file, abort, url_for
from werkzeug.utils import secure_filename

from core.addon_manager import AddonManager
from core.cache_manager import CacheManager

# Initialize Flask
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-me")

# Load addons
addon_manager = AddonManager()
cache_manager = CacheManager()

# Default addon
DEFAULT_ADDON = "MangaDex"

def get_addon(name=None):
    """Return the requested addon or the default one."""
    if name is None:
        name = DEFAULT_ADDON
    addon = addon_manager.get_addon(name)
    if not addon:
        abort(404, f"Addon '{name}' not found")
    return addon

# ----- Routes -----

@app.route("/")
def home():
    """Home page."""
    return render_template("home.html", addons=addon_manager.list_addons())

@app.route("/search")
def search_page():
    """Search page."""
    addons = addon_manager.list_addons()
    return render_template("search.html", addons=addons, selected=DEFAULT_ADDON)

@app.route("/api/search")
def api_search():
    """API endpoint for search."""
    query = request.args.get("q", "").strip()
    source = request.args.get("source", DEFAULT_ADDON)
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    if not query:
        return jsonify({"error": "Missing query"}), 400

    addon = get_addon(source)
    try:
        results = addon.search_series(query, limit=limit, offset=offset)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/series/<series_id>")
def series_page(series_id):
    """Series detail page."""
    source = request.args.get("source", DEFAULT_ADDON)
    addon = get_addon(source)

    try:
        series = addon.get_series(series_id)
        chapters = addon.get_chapters(series_id)
        # Add cover URL if not present
        if not series.get("cover_url"):
            series["cover_url"] = url_for("cover_image", series_id=series_id, _external=True)
        return render_template("series.html", series=series, chapters=chapters, source=source)
    except Exception as e:
        abort(500, f"Error fetching series: {e}")

@app.route("/cover/<series_id>")
def cover_image(series_id):
    """Serve cached cover image."""
    source = request.args.get("source", DEFAULT_ADDON)
    addon = get_addon(source)

    # Try to get the cover URL from the addon
    try:
        cover_url = addon.get_cover_url(series_id)
        if not cover_url:
            abort(404, "Cover not found")

        # Determine file extension from URL
        ext = cover_url.split('.')[-1] if '.' in cover_url else "jpg"
        if ext not in ("jpg", "jpeg", "png", "webp"):
            ext = "jpg"
        cache_subpath = f"coverart/{series_id}.{ext}"

        image_data = cache_manager.get_or_fetch_image(cover_url, cache_subpath)
        return send_file(
            os.path.join(cache_manager.cache_root, cache_subpath),
            mimetype=f"image/{ext}",
            as_attachment=False
        )
    except Exception as e:
        abort(404, f"Could not retrieve cover: {e}")

@app.route("/reader/<chapter_id>")
def reader_page(chapter_id):
    """Reader page for a chapter."""
    source = request.args.get("source", DEFAULT_ADDON)
    addon = get_addon(source)

    try:
        # Get chapter pages
        page_urls = addon.get_chapter_pages(chapter_id)
        # We need series title and chapter info for navigation and display
        # Since we only have chapter_id, we need to get chapter details.
        # We'll derive series from the chapter's manga relationship - but we don't have that info here.
        # For simplicity, we'll assume the chapter_id is enough and we'll fetch
        # series title from a cache? Alternatively, we can store series_id in session or query.
        # We'll pass series_id via query param.
        series_id = request.args.get("series_id")
        series_title = "Unknown Series"
        chapter_title = f"Chapter {chapter_id}"
        next_chapter_id = None

        # Fetch series info to get title and next chapter
        if series_id:
            series = addon.get_series(series_id)
            series_title = series.get("title", "Unknown Series")
            chapters = addon.get_chapters(series_id)
            # Find current chapter index and next
            for idx, ch in enumerate(chapters):
                if ch["id"] == chapter_id:
                    chapter_title = ch.get("title", f"Chapter {ch.get('number', '?')}")
                    if idx + 1 < len(chapters):
                        next_chapter_id = chapters[idx + 1]["id"]
                    break

        # Generate URLs for each page using our proxy
        page_proxy_urls = []
        for idx, url in enumerate(page_urls):
            page_proxy_urls.append(url_for("chapter_image", chapter_id=chapter_id, page_num=idx, _external=True))

        return render_template(
            "reader.html",
            series_title=series_title,
            chapter_title=chapter_title,
            pages=page_proxy_urls,
            next_chapter_id=next_chapter_id,
            series_id=series_id,
            source=source
        )
    except Exception as e:
        abort(500, f"Error loading chapter: {e}")

@app.route("/chapter_image/<chapter_id>/<int:page_num>")
def chapter_image(chapter_id, page_num):
    """Serve a cached chapter page image."""
    source = request.args.get("source", DEFAULT_ADDON)
    addon = get_addon(source)

    # We need to get the actual URL for this page.
    # We could cache the list of page URLs for the chapter to avoid repeated calls.
    # For simplicity, we'll fetch the list again (but with caching).
    # We'll implement a simple in-memory or filesystem cache for page URLs.
    # Here we use a separate cache key for page list.
    cache_key = f"chapter_pages:{chapter_id}"
    page_urls = cache_manager.get_metadata("metadata", cache_key)
    if page_urls is None:
        page_urls = addon.get_chapter_pages(chapter_id)
        cache_manager.set_metadata("metadata", cache_key, page_urls)

    if page_num < 0 or page_num >= len(page_urls):
        abort(404, "Page not found")

    image_url = page_urls[page_num]
    # Determine file extension
    ext = image_url.split('.')[-1] if '.' in image_url else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"

    # We need series title to build cache path. We can get series_id from the chapter metadata.
    # For simplicity, we'll use chapter_id in the path.
    cache_subpath = f"manga/{chapter_id}/page_{page_num:03d}.{ext}"
    try:
        image_data = cache_manager.get_or_fetch_image(image_url, cache_subpath)
        return send_file(
            os.path.join(cache_manager.cache_root, cache_subpath),
            mimetype=f"image/{ext}",
            as_attachment=False
        )
    except Exception as e:
        abort(500, f"Error loading image: {e}")

# ----- Run -----
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)