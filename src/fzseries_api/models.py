"""
This module provides template
for generating essential series' metadata
for smoother fztvseres.live interaction.

The models are not limited to:
- In search movie results
- Specific movie metadata
- Specific movie file metadata
- Recommended movies
- Download links
"""

import typing as t
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class SeriesInSearch(BaseModel):
    """Series displayed at search results page"""

    title: str
    url: HttpUrl
    cover_photo: str
    about: str

    def __str__(self):
        return f'<SeriesInSearch title="{self.title}">'


class SearchResults(BaseModel):
    """Listed series in Search results"""

    series: list[SeriesInSearch]
    first_page: t.Union[HttpUrl, None] = None
    previous_page: t.Union[HttpUrl, None] = None
    next_page: t.Union[HttpUrl, None] = None
    last_page: t.Union[HttpUrl, None] = None

    def __str__(self):
        return f"<SearchResults series={' | '.join([str(series) for series in self.series])} total={len(self.series)}>"


class EpisodeFile(BaseModel):
    """Url to download episode"""

    url: HttpUrl
    identity: str

    def __str__(self):
        return f'<EpisodeFile identity="{self.identity}", url="{self.url}">'


class EpisodeInSearch(BaseModel):
    """Episode in search results"""

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
            f" date_aired={self.date_aired}>"
        )


class EpisodeSearchResults(BaseModel):
    """Listed episodes in Search results"""

    episodes: list[EpisodeInSearch]
    first_page: t.Union[HttpUrl, None] = None
    previous_page: t.Union[HttpUrl, None] = None
    next_page: t.Union[HttpUrl, None] = None
    last_page: t.Union[HttpUrl, None] = None

    def __str__(self):
        return f"<EpisodeSearchResults episodes={" | ".join([
            str(episode) for episode in self.episodes
        ])}"
