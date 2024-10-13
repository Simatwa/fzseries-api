import unittest

import fzseries_api.hunter as hunters
import fzseries_api.handlers as handlers
import fzseries_api.models as models


class TestSearchHandlers(unittest.TestCase):

    def setUp(self):
        self.index = hunters.Index()
        self.query = "love"

    def test_series_search_handler(self):
        html_contents = self.index.search(self.query)
        self.assertIsInstance(
            handlers.search_results_handler(html_contents), models.SearchResults
        )

    def test_episode_search_handler(self):
        html_contents = self.index.search(self.query, "episodes")
        self.assertIsInstance(
            handlers.episode_search_results_handler(html_contents),
            models.EpisodeSearchResults,
        )


if __name__ == "__main__":
    unittest.main()
