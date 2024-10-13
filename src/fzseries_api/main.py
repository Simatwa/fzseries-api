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

import typing as t
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
