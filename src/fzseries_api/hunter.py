"""
This module does the ground-work of interacting
with fzseries.live in fetching the required resources 
that revolves around:
- Load index page
- Perform search
- Select the target series
- Proceed to download page
- Select link
"""

import requests
import re
import typing as t
import fzseries_api.utils as utils
import fzseries_api.exceptions as exceptions
from fzseries_api import logger

session = requests.Session()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "referer": utils.default_site_url,
}

session.headers.update(headers)

request_timeout = 20


class Index:
    """Accesses site's homepage"""

    session_is_initialized = False
    search_by_options = ("series", "episodes")

    def __init__(self):
        """Initializes `Index`"""
        if not self.session_is_initialized:
            load_index_resp = session.get(
                utils.default_site_url, timeout=request_timeout
            )
            if not load_index_resp.ok:
                logger.debug(
                    f"Headers - {load_index_resp.headers} \nResponse - {load_index_resp.text}"
                )
                raise exceptions.LoadIndexError(
                    f"Failed to load index page - ({load_index_resp.status_code} : {load_index_resp.reason})"
                )
            self.index_resp = load_index_resp

    def __str__(self):
        return f"<fzseries_api.hunter.Index_{self.index_resp.reason}>"

    def search(self, query: str, by: t.Literal["series", "episodes"] = "series") -> str:
        """Perform initial series|episode search

        Args:
            query (str): Series|Episode title.
            by (t.Literal['series', "episodes"], optional): Query category. Defaults to 'series'.

        Returns:
            str: Html contents of the results page
        """
        utils.assert_membership(by, self.search_by_options)
        return Metadata.get_resource(
            utils.get_absolute_url("/search.php"),
            params=dict(
                search=query,
                beginsearch="",
                insearch="Search",
                vsearch="",
                by=by,
            ),
        ).text


class Metadata:
    """Fetch html contents for :
    - Movie page
    - To-download page
    - To-download-links page
    - Movies m
    """

    session_expired_pattern = r".*Your download keys have expired.*"

    @classmethod
    def get_resource(cls, url: str, timeout: int = request_timeout, *args, **kwargs):
        """Fetch online resource

        Args:
            timeout (int): Http request timeout
            url (str): Url to resource
        """
        if not session.cookies.get("PHPSESSID"):
            logger.debug("Initializing session")
            Index()
        resp = session.get(url, timeout=timeout, *args, **kwargs)
        resp.raise_for_status()
        if "text/html" in resp.headers.get("Content-Type", ""):
            has_expired = re.search(cls.session_expired_pattern, resp.text)
            if has_expired:
                raise exceptions.SessionExpired(
                    utils.get_absolute_url(
                        utils.souper(has_expired.group()).find("a").get("href")
                    ),
                )

        return resp

    @classmethod
    def tvseries_page(cls, url: str) -> str:
        """Get page containing series season

        Args:
            url (str): Url to the page

        Returns:
            str: Page contents
        """
        return cls.get_resource(
            utils.validate_url(r".*/subfolder-.*", url, "to-seasons")
        ).text

    @classmethod
    def season_episodes(cls, url: str) -> str:
        """Get page containing praticular season's episode

        Args:
            url (str): Url to the page

        Returns:
            str: Page contents
        """
        return cls.get_resource(
            utils.validate_url(r".*/files-.*", url, "to-episodes")
        ).text

    @classmethod
    def episode_download_links(cls, url: str) -> str:
        """Get page containing download links

        Args:
            url (str): Url to the page

        Returns:
            str: Page contents
        """
        to_download_page = cls.get_resource(
            utils.validate_url(r".*/episode.php\?fileid=.*", url, "to-download-page")
        ).text
        to_download_page_links = (
            utils.souper(to_download_page).find("a", {"id": "dlink2"}).get("href")
        )
        return cls.get_resource(
            utils.validate_url(
                r".*/downloadmp4.php\?fileid=.*",
                utils.get_absolute_url(to_download_page_links),
                "to-download-links",
            )
        ).text

    @classmethod
    def episode_final_download_link(cls, url: str) -> str:
        """Get page containing final download link

        Args:
            url (str): Url to the page.

        Returns:
            str : Html contents of the page.
        """
        resp = cls.get_resource(
            utils.validate_url(r".*/filelink.php\?sn=.*", url, "to-final-download-link")
        ).text
        return resp
