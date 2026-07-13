"""MangaDex api router

Single entry point for the mangadex addon. Every static method here
just routes the call to the script responsible for that feature, so
the rest of the app only has to import MangaDexAPI instead of every
individual script in this folder.
"""

from .search import Search
from .manga import Manga
from .chapter import Chapter
from .cover import Cover
from .author import Author
from .ping import Ping


class MangaDexAPI:
    # ---- routes to search.py ----
    @staticmethod
    def search(**kwargs):
        return Search.search(**kwargs)

    @staticmethod
    def query(title):
        return Search.query(title)

    # ---- routes to manga.py ----
    @staticmethod
    def get_manga(manga_id, includes=None):
        return Manga.get(manga_id, includes=includes)

    @staticmethod
    def random_manga(**kwargs):
        return Manga.random(**kwargs)

    @staticmethod
    def tag_list():
        return Manga.tag_list()

    @staticmethod
    def manga_aggregate(manga_id, **kwargs):
        return Manga.aggregate(manga_id, **kwargs)

    @staticmethod
    def manga_feed(manga_id, **kwargs):
        return Manga.feed(manga_id, **kwargs)

    @staticmethod
    def manga_relation(manga_id, includes=None):
        return Manga.relation(manga_id, includes=includes)

    # ---- routes to chapter.py ----
    @staticmethod
    def chapter_list(**kwargs):
        return Chapter.list(**kwargs)

    @staticmethod
    def get_chapter(chapter_id, includes=None):
        return Chapter.get(chapter_id, includes=includes)

    @staticmethod
    def at_home_server(chapter_id, force_port_443=False):
        return Chapter.at_home_server(chapter_id, force_port_443=force_port_443)

    @staticmethod
    def chapter_page_urls(at_home_response, data_saver=False):
        return Chapter.page_urls(at_home_response, data_saver=data_saver)

    # ---- routes to cover.py ----
    @staticmethod
    def cover_list(**kwargs):
        return Cover.list(**kwargs)

    @staticmethod
    def get_cover(cover_id, includes=None):
        return Cover.get(cover_id, includes=includes)

    @staticmethod
    def cover_image_url(manga_id, filename, size=None):
        return Cover.image_url(manga_id, filename, size=size)

    # ---- routes to author.py ----
    @staticmethod
    def author_list(**kwargs):
        return Author.list(**kwargs)

    @staticmethod
    def get_author(author_id, includes=None):
        return Author.get(author_id, includes=includes)

    # ---- routes to ping.py ----
    @staticmethod
    def ping():
        return Ping.ping()