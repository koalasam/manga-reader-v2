"""MangaDex api author

fetches authors and artists, both of which are served by the same
endpoints on the mangadex api
"""

import requests

BASE_URL = "https://api.mangadex.org"


class Author:
    @staticmethod
    def list(limit=10, offset=0, ids=None, name=None, order=None, includes=None):
        params = {"limit": limit, "offset": offset}

        if ids:
            params["ids[]"] = ids
        if name:
            params["name"] = name
        if order:
            for key, value in order.items():
                params[f"order[{key}]"] = value
        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/author", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get(author_id, includes=None):
        params = {}

        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/author/{author_id}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()