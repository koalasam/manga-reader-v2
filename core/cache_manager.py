"""Filesystem cache manager for API responses and images."""

import os
import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
import requests


class CacheManager:
    """Handles caching of data and images to disk."""

    def __init__(self, cache_root: str = "cache"):
        self.cache_root = cache_root
        self._ensure_dirs([
            "metadata",
            "coverart",
            "manga",
            "search"
        ])

    def _ensure_dirs(self, subdirs):
        for sub in subdirs:
            path = os.path.join(self.cache_root, sub)
            os.makedirs(path, exist_ok=True)

    def _cache_path(self, category: str, key: str, ext: str = "json") -> str:
        """Generate a filesystem path for a given cache entry."""
        # Use a safe filename based on the key
        safe_key = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_root, category, f"{safe_key}.{ext}")

    def get_metadata(self, category: str, key: str, max_age_seconds: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve cached JSON data. If max_age is specified and the cache is older,
        returns None.
        """
        path = self._cache_path(category, key)
        if not os.path.exists(path):
            return None

        if max_age_seconds is not None:
            mtime = os.path.getmtime(path)
            age = (datetime.now().timestamp() - mtime)
            if age > max_age_seconds:
                return None

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def set_metadata(self, category: str, key: str, data: Any):
        """Store JSON data in the cache."""
        path = self._cache_path(category, key)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_image(self, url: str, cache_subpath: str) -> Optional[bytes]:
        """
        Retrieve an image from cache. `cache_subpath` is a relative path under
        the cache root (e.g. "coverart/series_id.jpg").
        """
        path = os.path.join(self.cache_root, cache_subpath)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        return None

    def set_image(self, url: str, cache_subpath: str, data: bytes):
        """Store an image in the cache."""
        path = os.path.join(self.cache_root, cache_subpath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)

    def get_or_fetch_image(self, url: str, cache_subpath: str) -> bytes:
        """
        Return cached image if present; otherwise download, cache, and return.
        """
        cached = self.get_image(url, cache_subpath)
        if cached is not None:
            return cached
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        self.set_image(url, cache_subpath, resp.content)
        return resp.content