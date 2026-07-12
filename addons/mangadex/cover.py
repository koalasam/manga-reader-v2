"""MangaDex api cover

fetches manga cover art metadata and builds the cdn urls used to
actually display cover images
"""

import requests

BASE_URL = "https://api.mangadex.org"
CDN_URL = "https://uploads.mangadex.org"


class Cover:
    @staticmethod
    def list(
        limit=10,
        offset=0,
        manga=None,
        ids=None,
        uploaders=None,
        locales=None,
        order=None,
        includes=None,
    ):
        params = {"limit": limit, "offset": offset}

        if manga:
            params["manga[]"] = manga
        if ids:
            params["ids[]"] = ids
        if uploaders:
            params["uploaders[]"] = uploaders
        if locales:
            params["locales[]"] = locales
        if order:
            for key, value in order.items():
                params[f"order[{key}]"] = value
        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/cover", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get(cover_id, includes=None):
        params = {}

        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/cover/{cover_id}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def image_url(manga_id, filename, size=None):
        if size == 256:
            return f"{CDN_URL}/covers/{manga_id}/{filename}.256.jpg"
        if size == 512:
            return f"{CDN_URL}/covers/{manga_id}/{filename}.512.jpg"
        return f"{CDN_URL}/covers/{manga_id}/{filename}"