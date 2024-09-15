import unittest
from unittest.mock import patch

import requests
import streamlit as st
from crawl import show_crawl_page


class TestCrawlPage(unittest.TestCase):

    @patch("requests.post")
    @patch("requests.get")
    def test_crawl_package_success(self, mock_get, mock_post):
        # Mock the SOLR ping response
        mock_get.return_value.status_code = 200

        # Mock the API response for the crawling request
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "Crawling success"

        # Create a Streamlit session for testing
        st.session_state.solr_online = True

        # Test the crawl page
        show_crawl_page()

        # Check if the POST request was made successfully
        mock_post.assert_called_once_with(
            "http://lasso_python_crawl:8000/crawl/{package_name}".format(
                package_name="test_package"
            ),
            params={"type_inferencing_engine": None},
        )

    @patch("requests.get")
    def test_solr_offline(self, mock_get):
        # Mock the SOLR ping response as failed
        mock_get.return_value.status_code = 500

        # Test the crawl page
        show_crawl_page()

        # Check if SOLR was correctly marked as offline
        self.assertFalse(st.session_state.get("solr_online", True))


if __name__ == "__main__":
    unittest.main()
if __name__ == "__main__":
    unittest.main()
