"""Addon manager – loads and provides access to manga source plugins."""

import importlib
import pkgutil
import os
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class BaseAddon(ABC):
    """Abstract base class that every manga source addon must implement."""

    name: str = "Unknown"
    version: str = "1.0"

    @abstractmethod
    def search_series(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Search for series by title.

        Returns a list of series summaries (id, title, cover_url, description, etc.).
        """
        pass

    @abstractmethod
    def get_series(self, series_id: str) -> Dict[str, Any]:
        """
        Fetch full details of a single series.

        Return structure must contain:
            id, title, cover_url, authors, description, tags, status,
            and optionally chapters (if you want to preload them).
        """
        pass

    @abstractmethod
    def get_chapters(self, series_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all chapters for a series.

        Each chapter dict: id, number (string), title, volume (optional).
        """
        pass

    @abstractmethod
    def get_chapter_pages(self, chapter_id: str) -> List[str]:
        """
        Return a list of direct image URLs for the pages of the given chapter.
        """
        pass

    @abstractmethod
    def get_cover_url(self, series_id: str) -> str:
        """Return the URL of the cover image for the series."""
        pass

    @abstractmethod
    def get_tags(self) -> List[Dict[str, str]]:
        """Return a list of all available tags (id, name)."""
        pass


class AddonManager:
    """Manages loading and providing access to addons."""

    def __init__(self, addons_path: str = "addons"):
        self.addons_path = addons_path
        self._addons: Dict[str, BaseAddon] = {}
        self._load_addons()

    def _load_addons(self):
        """Discover and instantiate all addon classes that inherit from BaseAddon."""
        # Ensure addons package is importable
        if not os.path.exists(self.addons_path):
            os.makedirs(self.addons_path)

        # Import all modules in the addons directory
        for _, module_name, is_pkg in pkgutil.iter_modules([self.addons_path]):
            if not is_pkg and module_name != "__init__":
                try:
                    module = importlib.import_module(f"addons.{module_name}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseAddon)
                            and attr is not BaseAddon
                        ):
                            addon = attr()
                            self._addons[addon.name] = addon
                except Exception as e:
                    print(f"Failed to load addon {module_name}: {e}")

    def get_addon(self, name: str) -> Optional[BaseAddon]:
        """Retrieve an addon by its name."""
        return self._addons.get(name)

    def list_addons(self) -> List[str]:
        """Return a list of available addon names."""
        return list(self._addons.keys())