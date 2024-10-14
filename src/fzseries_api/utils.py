"""
This module provide functions for
performing common and frequently required tasks
as well as storing common variables across the package
"""

from bs4 import BeautifulSoup as bts
from os import path
import typing as t
import re

available_site_urls: tuple[str] = (
    "https://tvseries.in/",
    "https://mobiletvshows.site/",
    "https://fztvseries.live/",
)
"""Different domains providing same service"""

default_site_url = available_site_urls[2]
"""Default domain"""


def souper(contents: str) -> bts:
    """Converts str object to `soup`"""
    return bts(contents, "html.parser")


def get_absolute_url(relative_url: str) -> str:
    """Makes absolute url from relative url"""
    if relative_url.startswith("/"):
        relative_url = relative_url[1:]
    return path.join(default_site_url, relative_url)


def assert_membership(value: t.Any, elements: t.Iterable, identity="Value"):
    """Asserts value is a member of elements

    Args:
        value (t.Any): member to be checked against.
        elements (t.Iterable): Iterables of members.
        identity (str, optional):. Defaults to "Value".
    """
    assert value in elements, f"{identity} '{value}' is not one of {elements}"


def validate_url(pattern: str, url: str, identity: str = "resource") -> str:
    """Checks pattern presence in a url

    Args:
        pattern (str): Regex pattern
        url (str):
        identity (str): Defaults to "resource"

    Raises:
        ValueError: On mistmatch

    Returns:
        str: url
    """
    match = re.match(pattern, str(url))

    if match:
        return match.group()
    else:
        raise ValueError(f"Invalid {identity} url passed - '{url}'")
