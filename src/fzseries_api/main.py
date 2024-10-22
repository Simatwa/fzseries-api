"""
This module does the simple work
of linking the `handler` module (html)
with `hunter` (models) while providing
a higher level API.

It achieves this through 4 classes
- `Search` : Series look-up
- `TVSeriesMatdata` :Extracts metadata for a particular Tvseriese
- `EpisodeMetadata` : Extracts episodes' metadata for a specific season
- `Download` : Downloads an episode
- `Auto` :: Utilises the preceeding 4 classes to download episodes.
"""

from tqdm import tqdm
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

try:
    import click

    cli_deps_installed = True
except ImportError:
    cli_deps_installed = False


class Search(hunter.Index):
    """Series look-up"""

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
        kwargs.setdefault("filename", self.results_cache.filename)
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
        timeout: int = 30 * 60,
        leave: bool = True,
        colour: str = "cyan",
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
            timeout (int, optional): Download timeout. Defaults to 30*60
            leave (bool, optional): Keep all traces of the progressbar. Defaults to True.
            colour (str, optional): Progress bar display color. Defaults to "cyan".

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
            if not path.exists(save_to):
                raise FileNotFoundError(f"File not found in path - '{save_to}'")
            current_downloaded_size = path.getsize(save_to)
            # Set the headers to resume download from the last byte
            hunter.session.headers.update(
                {"Range": f"bytes={current_downloaded_size}-"}
            )
            current_downloaded_size_in_mb = current_downloaded_size / 1000000
            # convert to mb

        default_content_length = 0

        resp = hunter.session.get(episode_file_url, stream=True, timeout=timeout)

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

        size_in_mb = (size_in_bytes / 1_000_000) + current_downloaded_size_in_mb
        chunk_size_in_bytes = chunk_size * 1_000

        saving_mode = "ab" if resume else "wb"
        if progress_bar:
            if not quiet:
                print(f"{filename}")
            with tqdm(
                desc="Downloading",
                total=round(size_in_mb, 1),
                bar_format="{l_bar}{bar}{r_bar}",
                initial=current_downloaded_size_in_mb,
                unit="Mb",
                colour=colour,
                leave=leave,
            ) as p_bar:
                # p_bar.update(current_downloaded_size)
                with open(save_to, saving_mode) as fh:
                    for chunks in resp.iter_content(chunk_size=chunk_size_in_bytes):
                        fh.write(chunks)
                        p_bar.update(round(chunk_size_in_bytes / 1_000_000, 1))
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
        download_trials: int = 10,
        confirm: bool = False,
        **kwargs,
    ) -> Path:
        """Download and save episode using recommended best practices

        Args:
            episode (models.EpisodeInSearch): Episode
            progress_bar(bool, optional): Show download progressbar. Defaults to True.
            format (t.Literal["High MP4", "WEBM"], optional): Defaults to "High MP4".
            directory (str|Path, optional): Parent directory for saving the episode. Defaults to `getcwd()`.
            include_metadata(bool, optional): Add series title and episode-id in filename. Defaults to False.
            download_trials (int, optional): Number of trials before giving up on download. Defaults to 10.
            confirm (bool, optional): Ask user whether to proceed with the download or not. Defaults to False.

            - The rest are arguments for `Download.save`
        Returns:
            Path: Path where the episode has been saved to.
        """
        if confirm:
            if not cli_deps_installed:
                raise Exception(
                    "CLI dependency is missing. Reinstall "
                    "fzseries-api with 'cli' extras ie. "
                    "'pip install fzseries-api[cli]'"
                )
            if not click.confirm(f'Download "{episode.title}"'):
                return
        download = Download(episode=episode, format=format)
        link = download.last_url
        series_name, episode_id, episode_filename = re.findall(
            r"(.+)\s-\s(S\d+)(.+)", episode.title
        )[0]
        episode_dir = Path(directory) / series_name / episode_id
        makedirs(episode_dir, exist_ok=True)
        filename = episode.title if include_metadata else episode_filename
        quiet = kwargs.get("quiet")
        kwargs["quiet"] = True

        def stdout(info):
            if quiet:
                pass
            else:
                print(info)

        for trials in range(download_trials):
            try:
                kwargs["resume"] = Path(episode_dir / filename).exists()
                stdout(f"[T {trials+1}/{download_trials}] {episode.title}")
                resp = download.save(
                    link=link,
                    filename=filename,
                    dir=episode_dir,
                    progress_bar=progress_bar,
                    **kwargs,
                )

            except (KeyboardInterrupt, EOFError, FileExistsError, FileNotFoundError):
                break

            except Exception as e:
                if trials >= download_trials:
                    raise e
            else:
                return resp

    def run(
        self,
        season_offset: int = 1,
        episode_offset: int = 1,
        one_season_only: bool = False,
        ignore_errors: bool = False,
        limit: int = 1000000,
        **kwargs,
    ) -> list[Path]:
        """Initiate the download process

        Args:
            season_offset (int, optiona;): Season number to start downloading from. Defaults to 1.
            episode_offset (int, optional): Episode number to start downloading from. Defaults to 1.
            one_season_only (bool, optional): Download only one season and stop. Defaults to False.
            limit (int, optional): Number of proceeding episodes to download before stopping. Defaults to 1000000.
            ignore_errors(bool, optional): Ignore exceptions raised while downloading episodes. Defaults to False.
            progress_bar(bool, optional): Show download progressbar. Defaults to True.
            format (t.Literal["High MP4", "WEBM"], optional): Defaults to "High MP4".
            directory (str|Path, optional): Parent directory for saving the series. Defaults to `getcwd()`.
            include_metadata(bool, optional): Add series title and episode-id in filename. Defaults to False.
            download_trials (int, optional): Number of trials before giving up on download. Defaults to 10.
            confirm (bool, optional): Ask user whether to proceed with the download or not. Defaults to False.

            - The rest are arguments for `Download.save`
        Returns:
            list[Path]: List of path to downloaded-episodes
        """
        results = self.results
        season_index = season_offset - 1
        episode_index = episode_offset - 1
        episodes_downloaded_count = 0
        downloaded_episodes_path: list[Path] = []

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
                    try:
                        saved_to = self.download_episode(episode, **kwargs)
                        if saved_to:
                            downloaded_episodes_path.append(saved_to)
                    except Exception as e:
                        if not ignore_errors:
                            raise e
                    if episodes_downloaded_count >= limit:
                        break

                if one_season_only or episodes_downloaded_count >= limit:
                    break

        else:
            for result in self.get_all_results(stream=True, limit=limit):
                for episode in result.episodes:
                    episodes_downloaded_count += 1
                    try:
                        saved_to = self.download_episode(episode, **kwargs)
                        if saved_to:
                            downloaded_episodes_path.append(saved_to)
                    except Exception as e:
                        if not ignore_errors:
                            raise e

        return downloaded_episodes_path
