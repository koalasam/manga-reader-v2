"""MangaDex api ping

simple health check against the mangadex api
"""

import requests

BASE_URL = "https://api.mangadex.org"


class Ping:
    @staticmethod
    def ping():
        r = requests.get(f"{BASE_URL}/ping", timeout=30)
        r.raise_for_status()
        return r.text