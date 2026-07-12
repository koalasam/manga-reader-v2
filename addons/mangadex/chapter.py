"""MangaDex api chapter

fetches chapter listings and chapter details, and resolves the
mangadex@home server needed to actually load a chapter's page images
"""

import requests

BASE_URL = "https://api.mangadex.org"


class Chapter:
    @staticmethod
    def list(
        limit=100,
        offset=0,
        ids=None,
        title=None,
        groups=None,
        uploader=None,
        manga=None,
        volume=None,
        chapter=None,
        translated_language=None,
        original_language=None,
        excluded_original_language=None,
        content_rating=None,
        excluded_groups=None,
        excluded_uploaders=None,
        include_future_updates=None,
        include_empty_pages=None,
        include_future_publish_at=None,
        include_external_url=None,
        created_at_since=None,
        updated_at_since=None,
        publish_at_since=None,
        order=None,
        includes=None,
    ):
        params = {"limit": limit, "offset": offset}

        if ids:
            params["ids[]"] = ids
        if title:
            params["title"] = title
        if groups:
            params["groups[]"] = groups
        if uploader:
            params["uploader"] = uploader
        if manga:
            params["manga"] = manga
        if volume:
            params["volume[]"] = volume
        if chapter:
            params["chapter[]"] = chapter
        if translated_language:
            params["translatedLanguage[]"] = translated_language
        if original_language:
            params["originalLanguage[]"] = original_language
        if excluded_original_language:
            params["excludedOriginalLanguage[]"] = excluded_original_language
        if content_rating:
            params["contentRating[]"] = content_rating
        if excluded_groups:
            params["excludedGroups[]"] = excluded_groups
        if excluded_uploaders:
            params["excludedUploaders[]"] = excluded_uploaders
        if include_future_updates is not None:
            params["includeFutureUpdates"] = str(include_future_updates).lower()
        if include_empty_pages is not None:
            params["includeEmptyPages"] = str(include_empty_pages).lower()
        if include_future_publish_at is not None:
            params["includeFuturePublishAt"] = str(include_future_publish_at).lower()
        if include_external_url is not None:
            params["includeExternalUrl"] = str(include_external_url).lower()
        if created_at_since:
            params["createdAtSince"] = created_at_since
        if updated_at_since:
            params["updatedAtSince"] = updated_at_since
        if publish_at_since:
            params["publishAtSince"] = publish_at_since
        if order:
            for key, value in order.items():
                params[f"order[{key}]"] = value
        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/chapter", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get(chapter_id, includes=None):
        params = {}

        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/chapter/{chapter_id}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def at_home_server(chapter_id, force_port_443=False):
        params = {}

        if force_port_443:
            params["forcePort443"] = str(force_port_443).lower()

        r = requests.get(f"{BASE_URL}/at-home/server/{chapter_id}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def page_urls(at_home_response, data_saver=False):
        base_url = at_home_response["baseUrl"]
        chapter = at_home_response["chapter"]
        quality = "data-saver" if data_saver else "data"
        filenames = chapter["dataSaver"] if data_saver else chapter["data"]

        return [f"{base_url}/{quality}/{chapter['hash']}/{filename}" for filename in filenames]
    