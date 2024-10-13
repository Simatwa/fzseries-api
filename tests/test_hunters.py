import unittest
import fzseries_api.hunter as hunters
import fzseries_api.handlers as handlers


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.index = hunters.Index()
        self.query = "love"

    def test_hunt_by_series(self):
        self.assertIsInstance(self.index.search(self.query), str)

    def test_hunt_by_episode(self):
        self.assertIsInstance(self.index.search(self.query, "episodes"), str)


class TestSeriesNavigation(unittest.TestCase):
    def setUp(self):
        self.search_html_contents = hunters.Index().search("love")
        self.search_series_found = handlers.search_results_handler(
            self.search_html_contents
        )

    def test_tvseries_page(self):
        target_series = self.search_series_found.series[0]
        tvseries_page_html_contents = hunters.Metadata.tvseries_page(target_series.url)
        self.assertIsInstance(tvseries_page_html_contents, str)

    def test_episodes_page(self):
        target_series = self.search_series_found.series[0]
        tvseries_page_html_contents = hunters.Metadata.tvseries_page(target_series.url)
        seasons = handlers.tvseries_page_handler(tvseries_page_html_contents).seasons[0]
        season_page_html_contents = hunters.Metadata.season_episodes(seasons.url)
        self.assertIsInstance(season_page_html_contents, str)

    def test_download_links_page(self):
        target_series = self.search_series_found.series[0]
        tvseries_page_html_contents = hunters.Metadata.tvseries_page(target_series.url)
        seasons = handlers.tvseries_page_handler(tvseries_page_html_contents).seasons[0]
        season_page_html_contents = hunters.Metadata.season_episodes(seasons.url)
        episodes = handlers.season_episodes_handler(season_page_html_contents)
        episode_file = episodes.episodes[0].files[0]
        download_links_page = hunters.Metadata.episode_download_links(episode_file.url)
        self.assertIsInstance(download_links_page, str)

    def test_final_download_link_page(self):
        target_series = self.search_series_found.series[0]
        tvseries_page_html_contents = hunters.Metadata.tvseries_page(target_series.url)
        seasons = handlers.tvseries_page_handler(tvseries_page_html_contents).seasons[0]
        season_page_html_contents = hunters.Metadata.season_episodes(seasons.url)
        episodes = handlers.season_episodes_handler(season_page_html_contents)
        episode_file = episodes.episodes[0].files[0]
        download_links_page = hunters.Metadata.episode_download_links(episode_file.url)
        download_links = handlers.download_links_page_handler(download_links_page)
        final_download_link_page = hunters.Metadata.episode_final_download_link(
            download_links.links[0]
        )
        self.assertIsInstance(final_download_link_page, str)


if __name__ == "__main__":
    unittest.main()
