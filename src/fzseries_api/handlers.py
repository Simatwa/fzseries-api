"""
Extracts key data from raw html contents 
and use them to generate models
"""

import re
import fzseries_api.utils as utils
import fzseries_api.models as models
import fzseries_api.exceptions as exceptions
from datetime import datetime


def search_results_handler(contents: str) -> models.SearchResults:
    """Extract series from search results page

    Args:
        contents (str): Search results page contents

    Returns:
        models.SearchResults: Modelled search results
    """
    series_found = utils.souper(contents).find_all("div", {"class": "mainbox3"})[2:]

    if series_found:
        series_items: list[dict[str, str]] = []
        for series in series_found:
            span = series.find("span")
            link = span.find("a")
            title = link.find("small").find("b").text.strip()
            url = link.get("href")
            cover_photo = series.find("img").get("src")
            about = span.find_all("small")[-1].text.strip()
            series_items.append(
                {
                    "title": title,
                    "url": utils.get_absolute_url(url),
                    "cover_photo": utils.get_absolute_url(cover_photo),
                    "about": about,
                }
            )
        navigators = series.find_all("div", {"class": "mainbox2"})
        first_page = previous_page = next_page = last_page = None
        if len(navigators) > 3:
            navigator = navigators[-1]
            for hyperlink in navigator.find_all("a"):
                link_text = hyperlink.text
                link = hyperlink.get("href")
                if link_text == "First":
                    first_page = link
                elif link_text == "Prev":
                    previous_page = link
                elif link_text == "Next":
                    next_page = link
                elif link_text == "Last":
                    last_page = link
        return models.SearchResults(
            series=series_items,
            first_page=first_page,
            previous_page=previous_page,
            next_page=next_page,
            last_page=last_page,
        )

    else:
        raise exceptions.ZeroSearchResults("Search query returned zero results")


def episode_search_results_handler(contents: str) -> models.EpisodeSearchResults:
    """Extract series from episode search results page

    Args:
        contents (str): Html contents containing search results.

    Returns:
        models.EpisodeSearchResults: Modelled search results.
    """
    soup = utils.souper(contents)
    episodes = soup.find_all("div", {"class": "mainbox"})
    if episodes:
        episode_items: list[dict[str, str]] = []
        for episode in episodes:
            cover_photo = episode.find("img").get("src")
            span = episode.find("span")
            title = span.find("small").find("b").text.strip()
            files: list[dict[str, str]] = []
            for file in span.find_all("a"):
                url = file.get("href")
                identity = file.text.strip()[1:][-1:]
                files.append(
                    {
                        "url": utils.get_absolute_url(url),
                        "identity": identity,
                    }
                )
            for small in span.find_all("small"):
                i = small.find("i")
                if i:
                    aired_on = i.text.split(" ")[1].replace(")", "")

            about = stars = director = writer = None
            metadata = (
                re.sub(
                    "\n\n",
                    "\n",
                    re.sub(r"<\W?\w*/?>", "\n", str(span.find_all("small")[-1])),
                )
                .strip()
                .split("\n")
            )
            if not len(metadata) == 4:
                for index, entry in enumerate(metadata):
                    text: str = entry.strip()
                    if index == 0:
                        about = text
                    else:
                        splitted_text = text.split(":")
                        if not len(splitted_text) >= 2:
                            continue
                        if index == 1:
                            stars = splitted_text[1].strip()
                        elif index == 2:
                            director = splitted_text[1].strip()
                        elif index == 3:
                            writer = splitted_text[1].strip()

            episode_items.append(
                dict(
                    title=title,
                    cover_photo=utils.get_absolute_url(cover_photo),
                    files=files,
                    aired_on=aired_on,
                    about=about,
                    stars=stars,
                    director=director,
                    writer=writer,
                )
            )

        navigators = soup.find_all("div", {"class": "mainbox2"})
        first_page = previous_page = next_page = last_page = None
        if len(navigators) > 3:
            navigator = navigators[-1]
            for hyperlink in navigator.find_all("a"):
                link_text = hyperlink.text
                link = hyperlink.get("href")
                if link_text == "First":
                    first_page = link
                elif link_text == "Prev":
                    previous_page = link
                elif link_text == "Next":
                    next_page = link
                elif link_text == "Last":
                    last_page = link

        return models.EpisodeSearchResults(
            episodes=episode_items,
            first_page=first_page,
            previous_page=previous_page,
            next_page=next_page,
            last_page=last_page,
        )

    else:
        raise exceptions.ZeroSearchResults("Search query returned zero results")


def tvseries_page_handler(contents: str) -> models.TVSeries:
    """Extract tvseries metadata from page

    Args:
        contents (str): Html contents of page containing series metadata

    Returns:
        models.TVSeries
    """
    soup = utils.souper(contents)
    series_info = soup.find_all("div", {"class": "mainbox3"})[-1]
    span = series_info.find("span")
    url = span.find("a").get("href")
    title = span.find("a").text.strip()
    metadata = span.find_all("small")[-1]
    stripped_tags = re.sub(r"<\W?\w+\W?>", "\n", str(metadata))
    about = stripped_tags.strip().split("\n")[0]
    year, genres, imdb_rating, last_updated = re.findall(
        r".*:\s\(?(.*)\)?", stripped_tags
    )
    season_items: list[dict[str, str | int]] = []
    for number, season in enumerate(
        soup.find("div", {"itemprop": "containsSeason"}).find_all(
            "div", {"class": "mainbox2"}
        ),
        start=1,
    ):
        link = season.find("a")
        season_items.append(
            dict(
                url=utils.get_absolute_url(link.get("href")),
                identity=link.text.strip(),
                number=number,
            )
        )
    return models.TVSeries(
        title=title,
        genres=genres,
        year=year.replace(")", ""),
        about=about,
        imdb_rating=imdb_rating,
        last_updated=datetime.strptime(last_updated, "%d %b, %Y"),
        seasons=season_items,
    )


def season_episodes_handler(contents: str) -> models.EpisodeSearchResults:
    """Extract episodes for a particular season and make models

    Args:
        contents (str): Html contents of the episode's page

    Returns:
        models.EpisodeSearchResults
    """
    return episode_search_results_handler(contents)


def download_links_page_handler(contents: str) -> models.DownloadEpisode:
    """Extract episode download-links and other metadata from html contents
      and make model

    Args:
        contents (str): Html contents of page containing the links

    Returns:
        models.DownloadEpisode
    """
    soup = utils.souper(contents).find("div", {"class": "filedownload"})
    filename = soup.find_all("textcolor1")[0].text.strip()
    downloads = soup.find_all("textcolor1")[-1].text.strip()
    size = soup.find("textcolor2").text.strip()
    links: list[str] = []
    for link in soup.find_all("div", {"class": "downloadlinks2"}):
        links.append(utils.get_absolute_url(link.find("a").get("href")))
    return models.DownloadEpisode(
        links=links, filename=filename, size=size, downloads=downloads
    )


def final_download_link_handler(contents: str) -> str:
    """Extract link pointing to downloadable episode file

    Args:
        contents (str): Html content of page containing the link.

    Returns:
        str: link
    """
    link = re.findall(r".*?location.href='(.*)'.*?", contents)
    return link[0]
