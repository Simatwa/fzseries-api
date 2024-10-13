"""
This module provides template
for generating essential series' metadata
for smoother fztvseres.live interaction.

The models are not limited to:
- In search series results
- Specific series metadata
- Specific episode file metadata
- Recommended series
- Download links
"""

import typing as t
from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime


class SeriesInSearch(BaseModel):
    """Series displayed at search results page
    `title` : TVSeries title.
    `url` : Link to the series page
    `cover_photo` : Link to the series release photo
    `about` : Plot of the series.
    """

    title: str
    url: HttpUrl
    cover_photo: str
    about: str

    def __str__(self):
        return f'<SeriesInSearch title="{self.title}">'


class SearchResults(BaseModel):
    """Listed series in Search results
    `series` : List of TVSeries found
    `first_page` : ...
    `previous_lage` : ...
    `next_page` : ...
    `last_page` : ...
    """

    series: list[SeriesInSearch]
    first_page: t.Union[HttpUrl, None] = None
    previous_page: t.Union[HttpUrl, None] = None
    next_page: t.Union[HttpUrl, None] = None
    last_page: t.Union[HttpUrl, None] = None

    def __str__(self):
        return (
            f"<SearchResults series={' | '.join([str(series) for series in self.series])}"
            f" total={len(self.series)}>"
        )


class EpisodeFile(BaseModel):
    """Url to download episode
    `url` : Link to episode's download page
    `identity` : Episode's title
    """

    url: HttpUrl
    identity: str

    def __str__(self):
        return f'<EpisodeFile identity="{self.identity}", url="{self.url}">'


class EpisodeInSearch(BaseModel):
    """Episode in search results
    `title` : Episode title
    `files` : Download files
    `cover_photo` : Episode's release photo
    `aired_on` : Date firstly premiered
    """

    title: str
    files: list[EpisodeFile]
    cover_photo: HttpUrl
    aired_on: datetime
    about: t.Union[str, None] = None
    stars: t.Union[str, None] = None
    director: t.Union[str, None] = None
    writer: t.Union[str, None] = None

    def __str__(self):
        return (
            f'<EpisodeInSearch title="{self.title}", director="{self.director}",'
            f' stars="{self.stars}", files={len(self.files)},'
            f" aired_on={self.aired_on}>"
        )


class EpisodeSearchResults(BaseModel):
    """Listed episodes in Search results
    `episodes` : Episodes found
    `first_page`: ...
    `previous_page` : ...
    `next_page` : ...
    `last_page` : ...
    """

    episodes: list[EpisodeInSearch]
    first_page: t.Union[HttpUrl, None] = None
    previous_page: t.Union[HttpUrl, None] = None
    next_page: t.Union[HttpUrl, None] = None
    last_page: t.Union[HttpUrl, None] = None

    def __str__(self):
        return f"<EpisodeSearchResults episodes={" | ".join([
            str(episode) for episode in self.episodes
        ])}"


class TVSeriesSeason(BaseModel):
    """Particular TV season info
    `url`: Link to the page containing season's episode
    `identity` : Season name
    `number` : Season's index+1
    """

    url: HttpUrl
    identity: str
    number: int

    def __str__(self):
        return f'<SeriesSeason identity="{self.identity}", number={self.number}>'


class TVSeries(BaseModel):
    """Particular TV series info
    `title` : Series title
    `genres` : Genres under which series lies
    `about` : Series plot
    `imdb_rating` : ...
    `last_updated` : Last date movie was updated
    `seasons` : Seasons available.
    """

    title: str
    genres: str
    year: str
    about: str
    imdb_rating: float
    last_updated: datetime
    seasons: list[TVSeriesSeason]

    def __str__(self):
        return f'<TVSeries title="{self.title}", year={self.year}, imdb_rating={self.imdb_rating}>'


class DonwloadEpisode(BaseModel):
    """Episodes download links
    `links` : Link to download episode
    `filename` : Episodes filename
    `size` : Episode file size
    `downloads` : Total downloads
    """

    links: list[HttpUrl]
    filename: str
    size: str
    downloads: int

    def __str__(self):
        return f'<DownloadEpisode filename="{self.filename}", size="{self.size}">'
