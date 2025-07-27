import unittest
import pytest
from src.search.search_engine import SearchEngine

class TestSearchEngine(unittest.TestCase):
    """
    A class for testing the SearchEngine class.
    """

    @pytest.mark.timeout(5)
    def test_search(self):
        """
        Tests the search method.
        """
        from unittest.mock import patch

        with patch("src.search.search_engine.SearchEngine._search_huggingface") as mock_search_huggingface, \
             patch("src.search.search_engine.SearchEngine._search_github") as mock_search_github:
            mock_search_huggingface.return_value = ["bert-base-uncased"]
            mock_search_github.return_value = ["google-research/bert"]

            search_engine = SearchEngine()
            results = search_engine.search("bert")

            self.assertEqual(len(results), 2)
            self.assertEqual(results[0], "bert-base-uncased")
            self.assertEqual(results[1], "google-research/bert")

if __name__ == "__main__":
    unittest.main()
