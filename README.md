# Work in Progress (not recomened for deployment)

# Manga Library Server

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
  manga-reader:
    container_name: manga-reader-v2
    build:
      context: https://github.com/koalasam/manga-reader-v2.git
    restart: unless-stopped

    ports:
      - "5000:5000"

    volumes:
      - /path/to/data:/app/data
      - /path/to/manga:/app/manga
```


### Python (not recommended)

#### Installation

1. clone the repo
```bash
git clone https://github.com/koalasam/manga-reader-v2.git
```

2. install dependencies
```bash
pip install -r requirements.txt
```

#### Running the Server

1. Start the server:
```bash
python app.py
```

2. Open your browser to:
```
http://localhost:5000
```