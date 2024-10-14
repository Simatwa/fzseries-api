"""
This module does the simple work
of linking the `handler` module (html)
with `hunter` (models) while providing
a higher level API.

It achieves this through 4 classes
- `Search` : Movie look-up
- `Navigate` : Progress to the targeted movie
- `DownloadLinks` : Links to the downloadable movie file
- `Download` : Download the movie file
- `Auto` : Ultimately download items of index 0.
"""

from tqdm import tqdm
from colorama import Fore
from os import path, getcwd, makedirs
from pathlib import Path
import typing as t
import re
from fzseries_api import logger
from fzseries_api.filters import fzseriesFilterType, Filter, SearchNavigatorFilter
import fzseries_api.hunter as hunter
import fzseries_api.models as models
import fzseries_api.handlers as handlers
import fzseries_api.utils as utils
import fzseries_api.exceptions as exceptions


class Search(hunter.Index):
    """Perform search query and generate models"""

    def __init__(
        self,
        query: t.Union[str, fzseriesFilterType],
        by: t.Literal["series", "episodes"] = "series",
    ):
        """Initializes `Search`

        Args:
            query (t.Union[str, fzseriesFilterType]): Series name/episode or filter.
            by (t.Literal['series', 'episodes'], optional): Query category. Defaults to 'series'.
        """
        self.query = query
        if isinstance(self.query, Filter):
            self._query_is_filter = True
        else:
            self._query_is_filter = False
            utils.assert_membership(by, self.search_by_options)
            self.by = by

        super().__init__()

    def __str__(self):
        return f'<fzseries_api.main.Search query="{str(self.query)}">'

    @property
    def html_contents(self) -> str:
        """Html contents of the search results page"""
        return (
            self.query.get_contents()
            if self._query_is_filter
            else self.search(query=self.query, by=self.by)
        )

    @property
    def results(self) -> t.Union[models.SearchResults, models.EpisodeSearchResults]:
        """Modelled search results

        Returns:
            t.Union[models.SearchResults, models.EpisodeSearchResults]
        """
        if self._query_is_filter:
            resp = self.query.get_results()
        else:
            if self.by == "series":
                resp = handlers.search_results_handler(self.html_contents)
            else:
                resp = handlers.episode_search_results_handler(self.html_contents)
        self._latest_results = resp
        return resp

    @property
    def all_results(self) -> t.Union[models.SearchResults, models.EpisodeSearchResults]:
        """All search results"""
        return self.get_all_results()

    def get_all_results(
        self, stream: bool = False, limit: int = 1000000
    ) -> (
        t.Union[models.SearchResults, models.EpisodeSearchResults]
        | t.Generator[
            t.Union[models.SearchResults, models.EpisodeSearchResults], None, None
        ]
    ):
        """Fetch all search results

        Args:
            stream (bool, optional): Yield results. Defaults to False.
            limit (int, optional): Total series not to exceed - `multiple of 20`. Defaults to 1000000.

        Returns:
            t.Union[models.SearchResults, models.EpisodeSearchResults] | t.Generator[
            t.Union[models.SearchResults, models.EpisodeSearchResults], None, None]
        """

        def for_stream(self, limit):
            total_series_search = 0
            while True:
                r: models.SearchResults | models.EpisodeSearchResults = self.results
                total_series_search += (
                    len(r.series) if hasattr(r, "series") else len(r.episodes)
                )
                yield r
                if r.next_page:
                    self = self.next()
                else:
                    break

                if total_series_search >= limit:
                    break

        def for_non_stream(self, limit):
            cache = None
            for results in for_stream(self, limit):
                if cache is None:
                    cache = results
                else:
                    cache = cache + results
            return cache

        return for_stream(self, limit) if stream else for_non_stream(self, limit)

    def first(self) -> "Search":
        """Navigate to the first page of search-results

        Returns:
            Search
        """
        assert self._latest_results != None, "Query results first before navigating."
        return Search(
            query=SearchNavigatorFilter(
                self._latest_results,
                "first",
            )
        )

    def previous(self) -> "Search":
        """Navigate to the previous page of search-results

        Returns:
            Search
        """
        assert self._latest_results != None, "Query results first before navigating."
        return Search(
            query=SearchNavigatorFilter(
                self._latest_results,
                "previous",
            )
        )

    def next(self) -> "Search":
        """Navigate to the next page of search-results

        Returns:
            Search
        """
        assert self._latest_results != None, "Query results first before navigating."
        return Search(
            query=SearchNavigatorFilter(
                self._latest_results,
                "next",
            )
        )

    def last(self) -> "Search":
        """Navigate to the last page of search-results

        Returns:
            Search
        """
        assert self._latest_results, "Query results first before navigating."
        return Search(
            query=SearchNavigatorFilter(
                self._latest_results,
                "last",
            )
        )


class TVSeriesMetadata:
    """Extracts metadata for a particular Tvseries"""

    def __init__(self, series: models.SeriesInSearch):
        """Initializes `Navigate`

        Args:
            series (models.SeriesInSearch): Series found in search results
        """
        assert isinstance(series, models.SeriesInSearch), (
            f"Series should be an instance of {models.SeriesInSearch} "
            f"not type({type(series)})"
        )

        self.series = series

    def __str__(self):
        f"<fzseries_api.main.Navigate series={str(self.series)}>"

    @property
    def html_contents(self) -> str:
        """Contents of the page containing series episode listings"""
        return hunter.Metadata.tvseries_page(self.series.url)

    @property
    def results(self) -> models.TVSeries:
        """Get TVSeries metadata

        Returns:
            models.TVSeries
        """
        return handlers.tvseries_page_handler(self.html_contents)


class EpisodeMetadata:
    """Extracts episodes' metadata for a specific season"""

    def __init__(self, season: models.TVSeriesSeason):
        """Initializes `Download`

        Args:
            season (models.TVSeriesSeason): Particular season for a TVSeries
        """
        assert isinstance(season, models.TVSeriesSeason), (
            f"Series should be an instance of {models.TVSeriesSeason} "
            f"not type({type(season)})"
        )
        self.season = season

    @property
    def html_contents(self) -> str:
        """Html contents of the page containing episodes for
         particular season

        Returns:
            str
        """
        return hunter.Metadata.season_episodes(self.season.url)

    @property
    def results(self) -> models.EpisodeSearchResults:
        """All episodes of the season

        Returns:
            models.EpisodeSearchResult
        """
        return handlers.season_episodes_handler(self.html_contents)


class Download:
    """Downloads an episode"""

    download_format_options = ("High MP4", "WEBM")

    def __init__(
        self,
        episode: models.EpisodeInSearch,
        format: t.Literal["High MP4", "WEBM"] = "High MP4",
    ):
        """Initializes `Download`

        Args:
            episode (models.EpisodeInSearch): Season episode.
            format (t.Literal["High MP4", "WEBM"], optional): _description_. Defaults to "High MP4".
        """
        assert isinstance(episode, models.EpisodeInSearch), (
            f"Series should be an instance of {models.EpisodeInSearch} "
            f"not type({type(episode)})"
        )
        self.episode = episode
        utils.assert_membership(format, self.download_format_options)
        self.format = format
        self.final_download_link_index = 0
        """Downloadlink file index - the first ones tend to be better"""
        self.results_cache: models.DownloadEpisode = None

    def __str__(self):
        return f"<fzseries_api.main.Download episode={str(self.episodes)}>"

    @property
    def html_contents(self):
        if len(self.episode.files) > 1:
            link = self.episode.files[self.download_format_options.index(self.format)]
        else:
            link = self.episode.files[0]

        return hunter.Metadata.episode_download_links(link.url)

    @property
    def results(self) -> models.DownloadEpisode:
        return handlers.download_links_page_handler(self.html_contents)

    @property
    def last_url(self):
        self.results_cache = self.results
        final_download_link_page = hunter.Metadata.episode_final_download_link(
            self.results_cache.links[self.final_download_link_index]
        )
        return handlers.final_download_link_handler(final_download_link_page)

    def run(self, **kwargs) -> Path:
        """Download and save the episode in disk
        - kwargs : arguments for `Download.save`

        Returns:
            Path: Absolute path to the downloaded episode
        """
        kwargs["link"] = self.last_url
        if not kwargs.get("filename"):
            kwargs["filename"] = self.results_cache.filename
        return self.save(**kwargs)

    @classmethod
    def save(
        cls,
        link: str,
        filename: str,
        dir: str = getcwd(),
        progress_bar: bool = True,
        quiet: bool = False,
        chunk_size: int = 512,
        resume: bool = False,
    ):
        """Save the episode in disk
        Args:
            link (str) : URL pointing to downloadable episode file - `Final download link`
            filename (str): Episode filename
            dir (str, optional): Directory for saving the contents Defaults to current directory.
            progress_bar (bool, optional): Display download progress bar. Defaults to True.
            quiet (bool, optional): Not to stdout anything. Defaults to False.
            chunk_size (int, optional): Chunk_size for downloading files in KB. Defaults to 512.
            resume (bool, optional):  Resume the incomplete download. Defaults to False.

        Raises:
            FileExistsError:  Incase of `resume=True` but the download was complete
            Exception

        Returns:
            str: Path where the episode contents have been saved to.
        """
        current_downloaded_size = 0
        current_downloaded_size_in_mb = 0
        save_to = Path(dir) / filename
        episode_file_url = link

        def pop_range_in_session_headers():
            if hunter.session.headers.get("Range"):
                hunter.session.headers.pop("Range")

        if resume:
            assert path.exists(save_to), f"File not found in path - '{save_to}'"
            current_downloaded_size = path.getsize(save_to)
            # Set the headers to resume download from the last byte
            hunter.session.headers.update(
                {"Range": f"bytes={current_downloaded_size}-"}
            )
            current_downloaded_size_in_mb = round(
                current_downloaded_size / 1000000, 2
            )  # convert to mb

        default_content_length = 0

        resp = hunter.session.get(episode_file_url, stream=True)

        size_in_bytes = int(resp.headers.get("content-length", default_content_length))
        if not size_in_bytes:
            if resume:
                raise FileExistsError(
                    f"Download completed for the file in path - '{save_to}'"
                )
            else:
                raise Exception(
                    f"Cannot download file of content-length {size_in_bytes} bytes"
                )

        if resume:
            assert (
                size_in_bytes != current_downloaded_size
            ), f"Download completed for the file in path - '{save_to}'"

        size_in_mb = round(size_in_bytes / 1000000, 2) + current_downloaded_size_in_mb
        chunk_size_in_bytes = chunk_size * 1024

        saving_mode = "ab" if resume else "wb"
        if progress_bar:
            if not quiet:
                print(f"{filename}")
            with tqdm(
                total=size_in_bytes + current_downloaded_size,
                bar_format="%s%d MB %s{bar} %s{l_bar}%s"
                % (Fore.GREEN, size_in_mb, Fore.CYAN, Fore.YELLOW, Fore.RESET),
                initial=current_downloaded_size,
            ) as p_bar:
                # p_bar.update(current_downloaded_size)
                with open(save_to, saving_mode) as fh:
                    for chunks in resp.iter_content(chunk_size=chunk_size_in_bytes):
                        fh.write(chunks)
                        p_bar.update(chunk_size_in_bytes)
                pop_range_in_session_headers()
                return save_to
        else:
            with open(save_to, saving_mode) as fh:
                for chunks in resp.iter_content(chunk_size=chunk_size_in_bytes):
                    fh.write(chunks)

            logger.info(f"{filename} - {size_in_mb}MB ✅")
            pop_range_in_session_headers()
            return save_to


class Auto(Search):
    """Download a whole series|seasons|episodes automatically"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def download_episode(
        cls,
        episode: models.EpisodeInSearch,
        progress_bar: bool = True,
        format: t.Literal["High MP4", "WEBM"] = "High MP4",
        directory: str | Path = getcwd(),
        include_metadata: bool = False,
        **kwargs,
    ) -> Path:
        """Download and save episode using recommended best practices

        Args:
            episode (models.EpisodeInSearch): Episode in
            progress_bar(bool, optional): Show download progressbar. Defaults to True.
            format (t.Literal["High MP4", "WEBM"], optional): Defaults to "High MP4".
            directory (str|Path, optional): Parent directory for saving the episode.
                Defaults to `getcwd()`.
            include_metadata(bool, optional): Add series title and episode-id in filename.
                Defaults to False.

        Returns:
            Path: Path where the episode has been saved to.
        """
        download = Download(episode=episode, format=format)
        link = download.last_url
        # results_cache = download.results_cache
        series_name, episode_id, episode_filename = re.findall(
            r"(.+)\s-\s(.+)\s-\s(.+)", episode.title
        )[0]
        episode_dir = Path(directory) / series_name / episode_id
        makedirs(episode_dir, exist_ok=True)
        return download.save(
            link=link,
            filename=episode.title if include_metadata else episode_filename,
            dir=episode_dir,
            progress_bar=progress_bar,
            **kwargs,
        )

    def run(
        self,
        season_offset: int = 1,
        episode_offset: int = 1,
        limit: int = 1000000,
        **kwargs,
    ) -> list[Path]:
        """Start the download process

        Args:
            season_offset (int): Season offset
            episode_offset (int): Episode offset
            limit (int, optional): Number of proceeding episodes to download before stopping.
              Defaults to 1000000.
            progress_bar(bool, optional): Show download progressbar. Defaults to True.
            format (t.Literal["High MP4", "WEBM"], optional): Defaults to "High MP4".
            directory (str|Path, optional): Parent directory for saving the series.
                Defaults to `getcwd()`.
            include_metadata(bool, optional): Add series title and episode-id in filename.
                Defaults to False.
        Returns:
            list[Path]: List of paths to downloaded-episodes
        """
        results = self.results
        season_index = season_offset - 1
        episode_index = episode_offset - 1
        episodes_downloaded_count = 0
        downloaded_episodes_path: list[Path] = []

        def stdout(info):
            if kwargs.get("quiet"):
                pass
            else:
                print(info)

        if isinstance(results, models.SearchResults):
            tvseries_metadata = TVSeriesMetadata(results.series[0]).results
            seasons = tvseries_metadata.seasons
            for index, target_season in enumerate(seasons[season_index:]):
                episode_metadata = EpisodeMetadata(target_season).results
                for episode in (
                    episode_metadata.episodes[episode_index:]
                    if index == 0
                    else episode_metadata.episodes
                ):
                    episodes_downloaded_count += 1
                    downloaded_episodes_path.append(
                        self.download_episode(episode, **kwargs)
                    )
                    if episodes_downloaded_count >= limit:
                        break

                if episodes_downloaded_count >= limit:
                    break

        else:
            for result in self.get_all_results(stream=True, limit=limit):
                for episode in result.episodes:
                    episodes_downloaded_count += 1
                    downloaded_episodes_path.append(
                        self.download_episode(episode, **kwargs)
                    )
        return downloaded_episodes_path
