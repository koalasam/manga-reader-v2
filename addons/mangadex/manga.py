"""MangaDex api manga

fetches manga details, random manga, the tag list, chapter aggregates,
a manga's chapter feed, and manga relations from the mangadex api
"""

import requests

BASE_URL = "https://api.mangadex.org"


class Manga:
    @staticmethod
    def get(manga_id, includes=None):
        params = {}

        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/manga/{manga_id}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def random(
        includes=None,
        content_rating=None,
        included_tags=None,
        excluded_tags=None,
        included_tags_mode=None,
        excluded_tags_mode=None,
    ):
        params = {}

        if includes:
            params["includes[]"] = includes
        if content_rating:
            params["contentRating[]"] = content_rating
        if included_tags:
            params["includedTags[]"] = included_tags
        if excluded_tags:
            params["excludedTags[]"] = excluded_tags
        if included_tags_mode:
            params["includedTagsMode"] = included_tags_mode
        if excluded_tags_mode:
            params["excludedTagsMode"] = excluded_tags_mode

        r = requests.get(f"{BASE_URL}/manga/random", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def tag_list():
        r = requests.get(f"{BASE_URL}/manga/tag", timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def aggregate(manga_id, translated_language=None, groups=None):
        params = {}

        if translated_language:
            params["translatedLanguage[]"] = translated_language
        if groups:
            params["groups[]"] = groups

        r = requests.get(f"{BASE_URL}/manga/{manga_id}/aggregate", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def feed(
        manga_id,
        limit=100,
        offset=0,
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

        r = requests.get(f"{BASE_URL}/manga/{manga_id}/feed", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def relation(manga_id, includes=None):
        params = {}

        if includes:
            params["includes[]"] = includes

        r = requests.get(f"{BASE_URL}/manga/{manga_id}/relation", params=params, timeout=30)
        r.raise_for_status()
        return r.json()