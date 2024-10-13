import unittest

from fzseries_api.main import Search
import fzseries_api.models as models


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.search = Search("love")

    def test_series_search(self):
        self.assertIsInstance(self.search.results, models.SearchResults)

    def test_episode_search(self):
        self.search.by = "episodes"
        self.assertIsInstance(self.search.results, models.EpisodeSearchResults)


if __name__ == "__main__":
    unittest.main()
