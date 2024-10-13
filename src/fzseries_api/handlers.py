"""
Extracts key data from raw html contents 
and use them to generate models
"""

import re
import fzseries_api.utils as utils
import fzseries_api.models as models
import fzseries_api.exceptions as exceptions


def search_results_handler(contents: str) -> models.SearchResults:
    """Extract series from search results page

    Args:
        contents (str): Search results page contents

    Returns:
        models.SearchResults: Modelled search results
    """
    series_found = utils.souper(contents).find_all("div", {"class": "mainbox3"})[2:]

    with open("test.html", "w") as fh:
        fh.write(utils.souper(contents).prettify())

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
