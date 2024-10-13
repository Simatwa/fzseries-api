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


class TestSeriesHandlers(unittest.TestCase):

    def setUp(self):
        self.search_html_contents = hunters.Index().search("love")
        self.search_series_found = handlers.search_results_handler(
            self.search_html_contents
        )

    def test_tvseries_handler(self):
        target_series = self.search_series_found.series[0]
        tvseries_page_html_contents = hunters.Metadata.tvseries_page(target_series.url)
        self.assertIsInstance(
            handlers.tvseries_page_handler(tvseries_page_html_contents), models.TVSeries
        )

    def test_episodes_handler(self):
        target_series = self.search_series_found.series[0]
        tvseries_page_html_contents = hunters.Metadata.tvseries_page(target_series.url)
        seasons = handlers.tvseries_page_handler(tvseries_page_html_contents).seasons[0]
        season_page_html_contents = hunters.Metadata.season_episodes(seasons.url)
        self.assertIsInstance(
            handlers.season_episodes_handler(season_page_html_contents),
            models.EpisodeSearchResults,
        )


if __name__ == "__main__":
    unittest.main()
