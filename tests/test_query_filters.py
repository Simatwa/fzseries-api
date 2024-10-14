import unittest
from fzseries_api.models import SearchResults
import fzseries_api.filters as f
from fzseries_api.main import Search
from unittest import TestCase


class FiltersTestBase:

    def setUp(self):
        self.filter_class = None

    def test_html_contents(self):
        """Test fetching series from online"""
        self.assertIsInstance(self.filter_class.get_contents(), str)

    def test_results(self):
        """Test query results modelling"""
        self.assertIsInstance(self.filter_class.get_results(), SearchResults)


class TestIMDBTop250Filter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.IMDBTop250Filter()


class TestPopularityFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.PopularityFilter()


class TestAiredTodayFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.AiredTodayFilter()


class TestTrendingFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.TrendingFilter()


class TestFreshSeriesFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.FreshSeriesFilter()


class TestTopRatedMiniseriesFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.TopRatedMiniseriesFilter()


class TestNetflixOriginalFilterFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.NetflixOriginalFilter()


class TestHBOOriginalFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.HBOOriginalFilter()


class TestCartoonFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.CartoonFilter()


class GenreFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.GenreFilter()


class SearchNavigatorFilter(FiltersTestBase, TestCase):

    def setUp(self):
        self.filter_class = f.SearchNavigatorFilter(Search("love").results)


if __name__ == "__main__":
    unittest.main()
