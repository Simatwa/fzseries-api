"""
This module contains search filters
along with page navigation filters
"""

import typing as t
from abc import ABC, abstractmethod
from fzseries_api.hunter import Metadata
from fzseries_api.handlers import search_results_handler, episode_search_results_handler
from fzseries_api.utils import get_absolute_url, assert_membership
import fzseries_api.models as models
import fzseries_api.exceptions as exceptions


class Filter(ABC):
    """Abstract Base class for filters"""

    url: str = None
    """Absolute url to the fztvseries-page containing the movie listings"""

    @abstractmethod
    def get_contents(self) -> str:
        """Get Html contents of the url

        Returns:
            str: html contents
        """
        raise NotImplementedError("Method needs to be implemented in child")

    @abstractmethod
    def get_results(self) -> models.SearchResults:
        """Get modelled version of the results

        Returns:
            models.SearchResults: Results
        """
        raise NotImplementedError("Method needs to be implemented in child")


class FilterBase(Filter):
    """Parent base class for Filter classes"""

    def get_contents(self) -> str:
        """Fetch Html contents of the url

        Returns:
            str: html contents
        """
        return Metadata.get_resource(self.url).text

    def get_results(self) -> models.SearchResults:
        """Get modelled version of the series list

        Returns:
            models.SearchResults: Results
        """
        return search_results_handler(self.get_contents())


class IMDBTop250Filter(FilterBase):
    """IMDB TOp 250 series filter"""

    url = get_absolute_url("/imdbtop250.php")


class PopularityFilter(FilterBase):
    """Ordered by popularity filter"""

    url = get_absolute_url("/popular.php")


class AiredTodayFilter(FilterBase):
    """Shows aired today filter"""

    url = get_absolute_url("/airedtoday.php")


class TrendingFilter(FilterBase):
    """Shows trending now filter"""

    url = get_absolute_url("/trending.php")


class FreshSeriesFilter(FilterBase):
    """Fresh in the market shows filter"""

    url = get_absolute_url("/freshseries.php")


class TopRatedMiniseriesFilter(FilterBase):
    """Most rated miniseries filter"""

    url = get_absolute_url("/miniseries.php")


class NetflixOriginalFilter(FilterBase):
    """Netflix orginal series filter"""

    url = get_absolute_url("/netorig.php")


class HBOOriginalFilter(FilterBase):
    """HBO orginal series filter"""

    url = get_absolute_url("/hb.php")


class CartoonFilter(FilterBase):
    """Cartoon series filter"""

    url = get_absolute_url("cartoon.php")


class GenreFilter(FilterBase):
    """Series genre filter"""

    genre_options = (
        "Action",
        "Adventure",
        "Romance",
        "Animation",
        "Cartoon",
        "Crime",
        "Drama",
        "Comedy",
        "Mystery",
        "Thriller",
        "Fantasy",
        "Reality-TV",
        "Sci-Fi",
        "Family",
        "Documentary",
        "Horror",
        "History",
        "Music",
    )

    def __init__(
        self,
        genre: t.Literal[
            "Action",
            "Adventure",
            "Romance",
            "Animation",
            "Cartoon",
            "Crime",
            "Drama",
            "Comedy",
            "Mystery",
            "Thriller",
            "Fantasy",
            "Reality-TV",
            "Sci-Fi",
            "Family",
            "Documentary",
            "Horror",
            "History",
            "Music",
        ] = "Action",
    ):
        """

        Args:
            genre (['Action', 'Adventure', 'Romance', 'Animation',
             'Cartoon', 'Crime', 'Drama', 'Comedy', 'Mystery', 'Thriller',
             'Fantasy', 'Reality-TV', 'Sci-Fi', 'Family', 'Documentary',
             'Horror', 'History', 'Music'], optional): Genre name. Defaults to "Action".
        """
        assert_membership(genre, self.genre_options, "Genre")
        self.url = get_absolute_url(f"/genre.php?genre={genre}")


class AlphabeticalOrderFilter(FilterBase):
    """Series name Alphabetical order filter"""

    available_ranges = (
        "AtoC",
        "DtoC",
        "GtoI",
        "JtoL",
        "MtO",
        "PtoR",
        "StoU",
        "VtoZ",
        "1to9",
    )

    def __init__(
        self,
        range: t.Literal[
            "AtoC", "DtoC", "GtoI", "JtoL", "MtO", "PtoR", "StoU", "VtoZ", "1to9"
        ] = "AtoC",
    ):
        """Initializes `AlphabeticalOrderFilter`

        Args:
            range (t.Literal["AtoC","DtoC","GtoI","JtoL","MtO","PtoR","StoU","VtoZ","1to9"], optional): Alphabetical ranges. Defaults to "AtoC".

        """
        assert_membership(range, self.available_ranges, "Range")
        self.url = get_absolute_url(f"/tv.php?alpha={range}")


class SearchNavigatorFilter(FilterBase):
    """Navigates movie-listing-page"""

    targets = ["first", "previous", "next", "last"]

    def __init__(
        self,
        search_results: t.Union[models.SearchResults, models.EpisodeSearchResults],
        target: t.Literal["first", "previous", "next", "last"] = "next",
    ):
        """Initializes `SearchNavigatorFilter`

        Args:
            search_results (t.Union[models.SearchResults, models.EpisodeSearchResults]): Search results.
            target (t.Literal["first", "previous", "next", "last"]): Page to navigate to. Defaults to "next".
        """
        assert isinstance(
            search_results, (models.SearchResults, models.EpisodeSearchResults)
        ), (
            f"search_results should be an instance of  {models.SearchResults}"
            f" or {models.EpisodeSearchResults} not {type(search_results)}"
        )
        assert target in self.targets, f"Target must be one of {self.targets}"
        target_url_mapper = {
            "first": search_results.first_page,
            "previous": search_results.previous_page,
            "next": search_results.next_page,
            "last": search_results.last_page,
        }
        self.url = target_url_mapper[target]
        if self.url is None:
            raise exceptions.TargetPageURLNotFound(
                f"The targeted page, {target}, has no url"
            )
        self.search_results = search_results

    def get_results(self) -> t.Union[models.SearchResults, models.EpisodeSearchResults]:
        """Get modelled version of the series list

        Returns:
            models.SearchResults: Results
        """
        return (
            search_results_handler(self.get_contents())
            if isinstance(self.search_results, models.SearchResults)
            else episode_search_results_handler(self.get_contents())
        )


fzseriesFilterType = t.Union[
    IMDBTop250Filter,
    PopularityFilter,
    AiredTodayFilter,
    TrendingFilter,
    FreshSeriesFilter,
    TopRatedMiniseriesFilter,
    NetflixOriginalFilter,
    NetflixOriginalFilter,
    HBOOriginalFilter,
    CartoonFilter,
    GenreFilter,
    AlphabeticalOrderFilter,
    SearchNavigatorFilter,
]
