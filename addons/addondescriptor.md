# Manga Source Addon Interface Specification

This document defines the standard interface that every manga source addon must implement. The core platform interacts exclusively with this interface, ensuring that adding new sources does not require changes to the core or frontend.

## Required Methods

All addon classes must inherit from `core.addon_manager.BaseAddon` and implement the following methods.

---

### `search_series(query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]`

Search for manga series by title.

**Parameters:**
- `query` – search string
- `limit` – maximum number of results
- `offset` – pagination offset

**Returns:** A list of series summaries. Each item must contain:
- `id` (str): unique identifier for the series
- `title` (str): series title
- `cover_url` (str, optional): URL to the cover image (or a relative path that the platform can resolve)
- `description` (str, optional): short description
- `authors` (List[str]): list of author/artist names
- `tags` (List[str]): list of genre/tag names
- `status` (str): e.g., "ongoing", "completed", "unknown"

---

### `get_series(series_id: str) -> Dict[str, Any]`

Fetch full details of a single series.

**Parameters:**
- `series_id` – the unique identifier of the series

**Returns:** A dictionary containing:
- `id` (str)
- `title` (str)
- `cover_url` (str, optional)
- `authors` (List[str])
- `description` (str)
- `tags` (List[str])
- `status` (str)

---

### `get_chapters(series_id: str) -> List[Dict[str, Any]]`

Fetch all chapters for a given series.

**Parameters:**
- `series_id` – the series identifier

**Returns:** A list of chapter objects, each containing:
- `id` (str): unique chapter identifier
- `number` (str): chapter number (may be non‑numeric)
- `title` (str): chapter title (if any)
- `volume` (str, optional): volume number

Chapters should be sorted in reading order (e.g., by volume and chapter number).

---

### `get_chapter_pages(chapter_id: str) -> List[str]`

Return direct image URLs for all pages of a chapter.

**Parameters:**
- `chapter_id` – the chapter identifier

**Returns:** A list of strings, each a fully qualified URL to a page image.

---

### `get_cover_url(series_id: str) -> str`

Return the URL of the cover image for a series.

**Parameters:**
- `series_id` – the series identifier

**Returns:** A string containing the URL of the cover image.

---

### `get_tags() -> List[Dict[str, str]]`

Return all available tags from the source.

**Returns:** A list of tag objects, each containing:
- `id` (str)
- `name` (str)

---

## Error Handling

- All methods should raise appropriate exceptions (e.g., `requests.exceptions.RequestException`, `ValueError`) on failure. The core platform will catch and log them.
- Network errors should be propagated as exceptions.

## Caching Expectations

- The core platform provides a `CacheManager` that can be used to cache API responses and images.
- Addons are encouraged to cache frequently accessed data (e.g., series info, chapter lists) to reduce API calls.
- Images (cover art and pages) are cached by the platform; the addon only needs to supply URLs.

## Rate Limiting

- The platform provides a `RateLimiter` that the addon should use for all outgoing API requests to respect the source’s rate limits.
- The addon should acquire a token via `rate_limiter.acquire()` before each request.

## Authentication

- Future plugins that require authentication (e.g., OAuth, API keys) can extend this interface. The `BaseAddon` class may be extended to include login methods, but they are not required for MangaDex.

---

This specification ensures that any new source can be integrated by simply implementing these methods and registering the addon class.