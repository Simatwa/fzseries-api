import unittest
from shutil import rmtree
from os import remove
from pathlib import Path
from fzseries_api.main import Search, TVSeriesMetadata, EpisodeMetadata, Download, Auto
import fzseries_api.models as models
from fzseries_api.filters import AlphabeticalOrderFilter
from typing import Generator

query = "love"


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.search = Search(query)

    def test_html_contents(self):
        self.assertIsInstance(self.search.html_contents, str)

    def test_results(self):
        self.assertIsInstance(self.search.results, models.SearchResults)

    def test_get_all_results(self):
        results = self.search.get_all_results(limit=20)
        self.assertIsInstance(results, models.SearchResults)
        self.assertEqual(len(results.series), 20)

    def test_get_all_results_stream(self):
        stream_get_results = self.search.get_all_results(stream=True, limit=40)
        self.assertIsInstance(stream_get_results, Generator)
        for results in stream_get_results:
            self.assertIsInstance(results, models.SearchResults)


class TestSearchByFilter(unittest.TestCase):

    def setUp(self):
        self.search = Search(query=AlphabeticalOrderFilter())

    def test_html_contents(self):
        self.assertIsInstance(self.search.html_contents, str)

    def test_results(self):
        self.assertIsInstance(self.search.results, models.SearchResults)

    def test_next_navigation(self):
        current_results = self.search.results
        next_search = self.search.next()
        self.assertIsInstance(next_search.results, models.SearchResults)

    def test_previous_navigation(self):
        current_results = self.search.results
        next_search = self.search.next()
        next_search_results = next_search.results
        previous_search = next_search.previous()
        self.assertTrue(self.search.results == previous_search.results)

    def test_last_navigation(self):
        current_results = self.search.results
        last_search = self.search.last()
        last_search_results = last_search.results
        self.assertIsNone(last_search_results.last_page)

    def test_first_navigation(self):
        current_results = self.search.results
        last_search = self.search.last()
        last_search_results = last_search.results
        first_search = last_search.first()
        self.assertIsNone(first_search.results.first_page)


class TestSearchByEpisode(unittest.TestCase):

    def setUp(self):
        self.search = Search(query, by="episodes")

    def test_html_contents(self):
        self.assertIsInstance(self.search.html_contents, str)

    def test_results(self):
        self.assertIsInstance(self.search.results, models.EpisodeSearchResults)

    def test_get_all_results(self):
        results = self.search.get_all_results(limit=20)
        self.assertIsInstance(results, models.EpisodeSearchResults)
        self.assertEqual(len(results.episodes), 20)

    def test_get_all_results_stream(self):
        stream_get_results = self.search.get_all_results(stream=True, limit=40)
        self.assertIsInstance(stream_get_results, Generator)
        for results in stream_get_results:
            self.assertIsInstance(results, models.EpisodeSearchResults)

    def test_next_navigation(self):
        current_results = self.search.results
        next_search = self.search.next()
        self.assertIsInstance(next_search.results, models.EpisodeSearchResults)

    def test_previous_navigation(self):
        current_results = self.search.results
        next_search = self.search.next()
        next_search_results = next_search.results
        previous_search = next_search.previous()
        self.assertTrue(self.search.results == previous_search.results)

    def test_last_navigation(self):
        current_results = self.search.results
        last_search = self.search.last()
        last_search_results = last_search.results
        self.assertIsNone(last_search_results.last_page)

    def test_first_navigation(self):
        current_results = self.search.results
        last_search = self.search.last()
        last_search_results = last_search.results
        first_search = last_search.first()
        self.assertIsNone(first_search.results.first_page)


class TestTVSeriesMetadata(unittest.TestCase):

    def setUp(self):
        self.search = Search(query)
        self.target_series = self.search.results.series[0]
        self.series_metadata = TVSeriesMetadata(self.target_series)

    def test_html_contents(self):
        self.assertIsInstance(self.series_metadata.html_contents, str)

    def test_results(self):
        self.assertIsInstance(self.series_metadata.results, models.TVSeries)


class TestEpisodeMetadata(unittest.TestCase):

    def setUp(self):
        self.search = Search(query)
        self.target_series = self.search.results.series[0]
        self.series_metadata = TVSeriesMetadata(self.target_series)
        self.target_season = self.series_metadata.results.seasons[0]
        self.episode_metadata = EpisodeMetadata(self.target_season)

    def test_html_contents(self):
        self.assertIsInstance(self.episode_metadata.html_contents, str)

    def test_results(self):
        results = self.episode_metadata.results
        self.assertIsInstance(results, models.EpisodeSearchResults)


class TestDownload(unittest.TestCase):

    def setUp(self):
        self.search = Search(query)
        self.target_series = self.search.results.series[0]
        self.series_metadata = TVSeriesMetadata(self.target_series)
        self.target_season = self.series_metadata.results.seasons[0]
        self.episode_metadata = EpisodeMetadata(self.target_season)
        self.target_episode = self.episode_metadata.results.episodes[0]
        self.download = Download(self.target_episode)

    def test_html_contents(self):
        self.assertIsInstance(self.download.html_contents, str)

    def test_results(self):
        self.assertIsInstance(self.download.results, models.DownloadEpisode)

    @unittest.skip("Downloading an episode is resources intensive")
    def test_save(self):
        saved_to = self.download.run()
        self.assertIsInstance(saved_to, Path)
        self.assertTrue(saved_to.is_file())
        remove(saved_to)


class TestDownloadFromSearchByEpisode(unittest.TestCase):

    def setUp(self):
        self.search = Search(query, by="episodes")
        self.target_episode: models.EpisodeSearchResults = self.search.results.episodes[
            0
        ]
        self.download = Download(self.target_episode)

    def test_html_contents(self):
        self.assertIsInstance(self.download.html_contents, str)

    def test_results(self):
        self.assertIsInstance(self.download.results, models.DownloadEpisode)

    @unittest.skip("Downloading an episode is resources intensive")
    def test_save(self):
        saved_to = self.download.run()
        self.assertIsInstance(saved_to, Path)
        self.assertTrue(saved_to.is_file())
        remove(saved_to)


class TestAuto(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.skip("Downloading series is resources intensive")
    def test_with_series_query(self):
        auto = Auto(query=AlphabeticalOrderFilter())
        for path in auto.run(limit=1, quiet=True, progress_bar=True):
            self.assertTrue(path.exists())
            remove(path)

    @unittest.skip("Downloading episode is resources intensive")
    def test_with_episode_query(self):
        auto = Auto(query="love", by="episodes")
        for path in auto.run(limit=1, quiet=True, progress_bar=True):
            self.assertTrue(path.exists())
            remove(path)


if __name__ == "__main__":
    unittest.main()
