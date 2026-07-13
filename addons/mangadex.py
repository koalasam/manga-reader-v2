"""MangaDex adapter implementing the standard BaseAddon interface."""

import re
from typing import List, Dict, Any, Optional

from core.addon_manager import BaseAddon
from core.rate_limiter import RateLimiter
from core.cache_manager import CacheManager
from .mangadexapi.mangadex_api import MangaDexAPI


class MangaDexAddon(BaseAddon):
    """Adapter for MangaDex."""

    name = "MangaDex"
    version = "1.0"

    def __init__(self):
        self.api = MangaDexAPI
        self.rate_limiter = RateLimiter(max_requests=4, period=1.0)
        self.cache = CacheManager()

    def _call_api(self, func, *args, **kwargs):
        """Rate‑limited API call."""
        self.rate_limiter.acquire()
        return func(*args, **kwargs)

    def _get_cached_or_call(self, cache_category: str, cache_key: str, func, *args, max_age: int = 3600, **kwargs):
        """Helper to use metadata cache."""
        cached = self.cache.get_metadata(cache_category, cache_key, max_age_seconds=max_age)
        if cached is not None:
            return cached
        result = self._call_api(func, *args, **kwargs)
        self.cache.set_metadata(cache_category, cache_key, result)
        return result

    def _get_title(self, attrs: Dict) -> str:
        """
        Extract the title with priority:
        1. Japanese romanised ('ja-ro')
        2. Japanese ('ja')
        3. English ('en')
        4. Any other available language
        """
        title_obj = attrs.get("title", {})
        for lang in ["ja-ro", "ja", "en"]:
            if lang in title_obj and title_obj[lang]:
                return title_obj[lang]
        # fallback to first non-empty value
        for val in title_obj.values():
            if val:
                return val
        return "Unknown Title"

    # ----- Interface methods -----

    def search_series(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        cache_key = f"search:{query}:{limit}:{offset}"
        data = self._get_cached_or_call("search", cache_key, self.api.search, title=query, limit=limit, offset=offset, max_age=300)

        results = []
        for item in data.get("data", []):
            attrs = item.get("attributes", {})
            title = self._get_title(attrs)
            cover_id = None
            for rel in item.get("relationships", []):
                if rel.get("type") == "cover_art":
                    cover_id = rel.get("id")
                    break
            results.append({
                "id": item["id"],
                "title": title,
                "cover_url": f"/cover/{item['id']}" if cover_id else None,
                "description": attrs.get("description", {}).get("en", ""),
                "authors": self._extract_authors(item.get("relationships", [])),
                "tags": [tag.get("attributes", {}).get("name", {}).get("en", "") for tag in attrs.get("tags", [])],
                "status": attrs.get("status", "unknown"),
            })
        return results

    def get_series(self, series_id: str) -> Dict[str, Any]:
        cache_key = f"series:{series_id}"
        data = self._get_cached_or_call("metadata", cache_key, self.api.get_manga, series_id, includes=["author", "artist", "cover_art"], max_age=3600)

        attrs = data.get("data", {}).get("attributes", {})
        rels = data.get("data", {}).get("relationships", [])

        title = self._get_title(attrs)
        description = attrs.get("description", {}).get("en", "")
        status = attrs.get("status", "unknown")
        tags = [tag.get("attributes", {}).get("name", {}).get("en", "") for tag in attrs.get("tags", [])]

        authors = self._extract_authors(rels)

        cover_id = None
        for rel in rels:
            if rel.get("type") == "cover_art":
                cover_id = rel.get("id")
                break

        return {
            "id": series_id,
            "title": title,
            "cover_url": f"/cover/{series_id}",
            "authors": authors,
            "description": description,
            "tags": tags,
            "status": status,
        }

    def _extract_authors(self, relationships: List[Dict]) -> List[str]:
        names = []
        for rel in relationships:
            if rel.get("type") in ("author", "artist"):
                names.append(rel.get("attributes", {}).get("name", "Unknown"))
        return names

    def get_chapters(self, series_id: str) -> List[Dict[str, Any]]:
        # Include language filter in cache key and API call
        cache_key = f"chapters:{series_id}:en"
        data = self._get_cached_or_call(
            "metadata",
            cache_key,
            self.api.manga_feed,
            series_id,
            limit=500,
            includes=["manga"],
            translated_language=["en"],  # Only English chapters
            max_age=600
        )

        chapters = []
        for item in data.get("data", []):
            attrs = item.get("attributes", {})
            chapters.append({
                "id": item["id"],
                "number": attrs.get("chapter", "0"),
                "title": attrs.get("title", ""),
                "volume": attrs.get("volume", ""),
            })

        # Sort by volume then chapter number in correct numerical order
        def sort_key(ch):
            # Convert to float if possible, else treat as 0
            vol_str = ch["volume"]
            try:
                vol = float(vol_str) if vol_str else 0.0
            except ValueError:
                vol = 0.0

            ch_str = ch["number"]
            try:
                ch_num = float(ch_str) if ch_str else 0.0
            except ValueError:
                ch_num = 0.0

            return (vol, ch_num)

        chapters.sort(key=sort_key)
        return chapters

    def get_chapter_pages(self, chapter_id: str) -> List[str]:
        data = self._call_api(self.api.at_home_server, chapter_id, force_port_443=False)
        base_url = data.get("baseUrl")
        chapter_data = data.get("chapter", {})
        hash = chapter_data.get("hash")
        files = chapter_data.get("data", [])
        return [f"{base_url}/data/{hash}/{f}" for f in files]

    def get_cover_url(self, series_id: str) -> str:
        cache_key = f"cover_info:{series_id}"
        data = self._get_cached_or_call("metadata", cache_key, self.api.get_manga, series_id, includes=["cover_art"], max_age=86400)
        rels = data.get("data", {}).get("relationships", [])
        for rel in rels:
            if rel.get("type") == "cover_art":
                cover_attrs = rel.get("attributes", {})
                filename = cover_attrs.get("fileName")
                if filename:
                    return f"https://uploads.mangadex.org/covers/{series_id}/{filename}"
        return None

    def get_tags(self) -> List[Dict[str, str]]:
        cache_key = "tags"
        data = self._get_cached_or_call("metadata", cache_key, self.api.tag_list, max_age=86400)
        return [
            {"id": tag["id"], "name": tag.get("attributes", {}).get("name", {}).get("en", "")}
            for tag in data.get("data", [])
        ]