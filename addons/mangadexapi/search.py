"""MangaDex api search

searches the mangadex database through the api
"""

import requests

BASE_URL = "https://api.mangadex.org"


class Search:
    @staticmethod
    def search(
        title=None,
        limit=10,
        offset=0,
        author_or_artist=None,
        authors=None,
        artists=None,
        year=None,
        included_tags=None,
        excluded_tags=None,
        included_tags_mode=None,
        excluded_tags_mode=None,
        status=None,
        original_language=None,
        excluded_original_language=None,
        available_translated_language=None,
        publication_demographic=None,
        ids=None,
        content_rating=None,
        has_available_chapters=None,
        has_unavailable_chapters=None,
        order=None,
    ):
        params = {"limit": limit, "offset": offset}

        if title:
            params["title"] = title
        if author_or_artist:
            params["authorOrArtist"] = author_or_artist
        if authors:
            params["authors[]"] = authors
        if artists:
            params["artists[]"] = artists
        if year is not None:
            params["year"] = year
        if included_tags:
            params["includedTags[]"] = included_tags
        if excluded_tags:
            params["excludedTags[]"] = excluded_tags
        if included_tags_mode:
            params["includedTagsMode"] = included_tags_mode
        if excluded_tags_mode:
            params["excludedTagsMode"] = excluded_tags_mode
        if status:
            params["status[]"] = status
        if original_language:
            params["originalLanguage[]"] = original_language
        if excluded_original_language:
            params["excludedOriginalLanguage[]"] = excluded_original_language
        if available_translated_language:
            params["availableTranslatedLanguage[]"] = available_translated_language
        if publication_demographic:
            params["publicationDemographic[]"] = publication_demographic
        if ids:
            params["ids[]"] = ids
        if content_rating:
            params["contentRating[]"] = content_rating
        if has_available_chapters is not None:
            params["hasAvailableChapters"] = str(has_available_chapters).lower()
        if has_unavailable_chapters is not None:
            params["hasUnavailableChapters"] = str(has_unavailable_chapters).lower()
        if order:
            for key, value in order.items():
                params[f"order[{key}]"] = value

        r = requests.get(f"{BASE_URL}/manga", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def query(title):
        data = Search.search(title=title)
        return [manga["id"] for manga in data.get("data", [])]
    