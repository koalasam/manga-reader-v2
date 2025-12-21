"""
Manga Library Server - Main Application
Main entry point for the manga server
"""

from flask import Flask, render_template, jsonify, send_file, request
from pathlib import Path
import os

from scripts.library_scanner import LibraryScanner
from scripts.metadata_manager import MetadataManager
from scripts.chapter_reader import ChapterReader
from scripts.cover_selector import CoverSelector
from scripts.settings_manager import SettingsManager

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

# Configuration
MANGA_ROOT = os.environ.get('MANGA_ROOT', './manga')
app.config['MANGA_ROOT'] = MANGA_ROOT

# Initialize components
scanner = LibraryScanner(MANGA_ROOT)
metadata_manager = MetadataManager()
reader = ChapterReader(MANGA_ROOT)
cover_selector = CoverSelector(MANGA_ROOT)
settings_manager = SettingsManager()

@app.route('/')
def index():
    """Main library view"""
    return render_template('index.html')

@app.route('/api/library')
def get_library():
    """Get all series in library"""
    series_list = scanner.scan_library()
    # Enhance with metadata and smart covers
    for series in series_list:
        meta = metadata_manager.get_metadata(series['name'])
        if meta:
            series.update(meta)
        # Get smart cover if no custom cover set
        if not series.get('cover') or not series.get('custom_cover'):
            smart_cover = cover_selector.get_best_cover(series['name'])
            if smart_cover:
                series['cover'] = smart_cover
    return jsonify(series_list)

@app.route('/api/series/<path:series_name>')
def get_series(series_name):
    """Get details for a specific series"""
    series_info = scanner.get_series_info(series_name)
    if series_info:
        meta = metadata_manager.get_metadata(series_name)
        if meta:
            series_info.update(meta)
        # Get smart cover
        if not series_info.get('cover') or not series_info.get('custom_cover'):
            smart_cover = cover_selector.get_best_cover(series_name)
            if smart_cover:
                series_info['cover'] = smart_cover
        # Format series name nicely
        series_info['display_name'] = format_series_name(series_name)
        return jsonify(series_info)
    return jsonify({'error': 'Series not found'}), 404

@app.route('/api/chapter/<path:series_name>/<chapter_num>')
def get_chapter(series_name, chapter_num):
    """Get chapter images"""
    chapter_data = reader.get_chapter_pages(series_name, chapter_num)
    if chapter_data:
        return jsonify(chapter_data)
    return jsonify({'error': 'Chapter not found'}), 404

@app.route('/api/image/<path:image_path>')
def serve_image(image_path):
    """Serve manga page images"""
    full_path = Path(MANGA_ROOT) / image_path
    if full_path.exists() and full_path.is_file():
        return send_file(full_path)
    return jsonify({'error': 'Image not found'}), 404

@app.route('/series/<path:series_name>')
def series_view(series_name):
    """Series detail page with chapter list"""
    return render_template('series.html', series_name=series_name)

@app.route('/reader/<path:series_name>/<chapter_num>')
def reader_view(series_name, chapter_num):
    """Manga reader view"""
    return render_template('reader.html', 
                         series_name=series_name,
                         chapter_num=chapter_num)

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Get or update settings"""
    if request.method == 'GET':
        return jsonify(settings_manager.get_all_settings())
    elif request.method == 'POST':
        settings_dict = request.get_json()
        settings_manager.update_settings(settings_dict)
        return jsonify({'success': True, 'settings': settings_manager.get_all_settings()})

def format_series_name(name):
    """Format series name from filepath"""
    return name.replace('-', ' ').replace('_', ' ').title()

if __name__ == '__main__':
    print(f"Starting Manga Server...")
    print(f"Manga root directory: {MANGA_ROOT}")
    app.run(debug=True, host='0.0.0.0', port=5000)