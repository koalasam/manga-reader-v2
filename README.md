# Manga Library Server

A self-hostable manga library and reading server with a scrolling reader layout.

## Manga File Structure

```
path_to_manga/
└── manga/
    ├── series-name-1/
    │   ├── chapter-1/
    │   │   ├──01.jpg
    │   │   ├──02.jpg
    │   │   └── ...
    │   └──chapter-#/
    │       └── ...
    └──.../  
```

## Installation

### Docker Compose (recommended)
```
services:
  manga-app:
    container_name: manga-library
    image: python:3.11-slim
    restart: unless-stopped

    working_dir: /app/manga-reader-v2

    command: >
      sh -c "
      apt-get update &&
      apt-get install -y git &&
      rm -rf /app/* &&
      git clone https://github.com/koalasam/manga-reader-v2.git /app/manga-reader-v2 &&
      pip install --no-cache-dir -r requirements.txt &&
      python app.py
      "

    volumes:
      # Read-only manga library
      - path_to_manga_directory/manga:/manga:ro

      # Read-write app data
      - /app/manga-reader-v2/data:/data:rw

    environment:
      - PYTHONUNBUFFERED=1

    ports:
      - "9008:5000"
```


### Python (not recommended)
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create the required directories:
```bash
mkdir -p scripts templates static/css static/js data manga
```

3. Organize your manga files in this format:
```
manga/
├── One Piece/
│   ├── chapter-1/
│   │   ├── 001.jpg
│   │   ├── 002.jpg
│   │   └── ...
│   ├── chapter-2/
│   └── ...
└── Naruto/
    ├── chapter-1/
    └── ...
```

## Running the Server

1. Set your manga directory (optional, defaults to ./manga):
```bash
export MANGA_ROOT=/path/to/your/manga
```

2. Start the server:
```bash
python app.py
```

3. Open your browser to:
```
http://localhost:5000
```

## Features

### Current Features
- **Library View**: Browse all manga series with cover images
- **Series Pages**: Dedicated page for each series with banner, cover art, and chapter list
- **Smart Cover Detection**: Automatically finds first color image from first chapter
- **Dual Reader Modes**:
  - **Scrolling Mode**: Vertical continuous scroll through all pages
  - **Single Page Mode**: One page at a time with click navigation
- **Customizable Reading**: Settings panel with options for:
  - Reader mode selection
  - Reading direction (LTR/RTL for single page mode)
  - Image fit mode (width/height/original)
- **Click Navigation**: In single page mode, click left/right sides to navigate
- **Search**: Find series by name or alternate titles
- **Chapter Navigation**: Navigate between chapters with buttons or arrow keys
- **Page Tracking**: See current page in both reader modes
- **Metadata Support**: Store series descriptions, alternate titles, author, genres, and more
- **Name Formatting**: Automatically formats series names from filepath (replaces - and _ with spaces)
- **Persistent Settings**: Reader preferences saved across sessions

### Reader Controls

**Scrolling Mode:**
- **Scroll**: Read pages naturally by scrolling
- **Arrow Left/Right**: Navigate to previous/next chapter
- **← Back button**: Return to series page

**Single Page Mode:**
- **Click Left/Right**: Navigate pages (direction based on settings)
  - LTR: Click right to go forward, left to go back
  - RTL: Click left to go forward, right to go back
- **Arrow Keys**: Navigate pages (respects reading direction)
- **Bottom Controls**: Previous/Next page buttons with page counter
- **⚙️ Settings**: Open settings panel to customize reader

**Settings Panel:**
- **Reader Mode**: Switch between Scrolling and Single Page
- **Reading Direction**: LTR or RTL (for single page mode)
- **Image Fit**: Fit to width, height, or original size
- **Reset to Defaults**: Restore default settings

## Metadata Management

Metadata is stored in `data/metadata.json`. You can manually edit this file or use the MetadataManager class:

```python
from scripts.metadata_manager import MetadataManager

meta = MetadataManager()
meta.set_metadata('One Piece', {
    'description': 'A story about pirates...',
    'alternate_titles': ['ワンピース'],
    'author': 'Eiichiro Oda',
    'status': 'ongoing',
    'genres': ['Action', 'Adventure']
})
```

## Supported Image Formats
- JPG/JPEG
- PNG
- GIF
- WebP

## Future Enhancement Ideas
- Multiple reader layouts (single page, double page)
- Reading progress tracking
- Bookmarks
- Download chapters
- User accounts
- Dark/light theme toggle
- Manga scraping/import tools
- API for mobile apps

## API Endpoints

- `GET /` - Library view
- `GET /api/library` - Get all series
- `GET /api/series/<series_name>` - Get series details
- `GET /series/<series_name>` - Series detail page
- `GET /api/chapter/<series_name>/<chapter_num>` - Get chapter pages
- `GET /api/image/<image_path>` - Serve manga images
- `GET /reader/<series_name>/<chapter_num>` - Reader view

## Smart Cover Selection

The system automatically selects the best cover image:
1. Checks metadata for custom cover path
2. If no custom cover, scans first chapter for first **color** image (skips B&W pages)
3. Falls back to first image if all pages are B&W
4. Series names are formatted from filepath: `my-manga-series` → `My Manga Series`
