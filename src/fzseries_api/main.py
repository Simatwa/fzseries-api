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
from os import path, getcwd
from pathlib import Path
import typing as t
from fzseries_api import logger
import fzseries_api.hunter as hunter
import fzseries_api.models as models
import fzseries_api.handlers as handlers
import fzseries_api.utils as utils


class Search(hunter.Index):
    """Perform search query and generate models"""

    def __init__(self, query: str, by: t.Literal["series", "episodes"] = "series"):
        """Initializes `Search`

        Args:
            query (str): Series name or episode
            by (t.Literal['series', 'episodes'], optional): Query category. Defaults to 'series'.
        """
        self.query = query
        utils.assert_membership(by, self.search_by_options)
        self.by = by
        super().__init__()

    def __str__(self):
        return f'<fzseries_api.main.Search query="{self.query}">'

    @property
    def html_contents(self) -> str:
        """Html contents of the search results page"""
        return self.search(query=self.query, by=self.by)

    @property
    def results(self) -> t.Union[models.SearchResults, models.EpisodeSearchResults]:
        """Modelled search results

        Returns:
            t.Union[models.SearchResults, models.EpisodeSearchResults]
        """
        if self.by == "series":
            return handlers.search_results_handler(self.html_contents)
        else:
            return handlers.episode_search_results_handler(self.html_contents)


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
        """Get Episodes for a particular season

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
        self._results = self.results
        final_download_link_page = hunter.Metadata.episode_final_download_link(
            self._results.links[self.final_download_link_index]
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
            kwargs["filename"] = self._results.filename
        return self.save(**kwargs)

    @classmethod
    def save(
        cls,
        link: str,
        filename: str,
        dir: str = getcwd(),
        progress_bar=True,
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
