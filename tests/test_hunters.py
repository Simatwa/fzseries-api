import unittest
import fzseries_api.hunter as hunters


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.index = hunters.Index()
        self.query = "love"

    def test_hunt_by_series(self):
        self.assertIsInstance(self.index.search(self.query), str)

    def test_hunt_by_episode(self):
        self.assertIsInstance(self.index.search(self.query, "episodes"), str)


if __name__ == "__main__":
    unittest.main()
