import unittest
from unittest.mock import patch

import requests
import streamlit as st
from crawl import show_crawl_page


class TestCrawlPage(unittest.TestCase):

    @patch("requests.post")
    def test_crawl_package_success(self, mock_post):
        # Mock the API response for the crawling request
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "Crawling success"

        # Test the crawl page
        show_crawl_page()

        # Check if the POST request was made successfully
        mock_post.assert_called_once_with(
            "http://lasso_python_crawl:8000/crawl/{package_name}".format(
                package_name="test_package"
            ),
            params={"type_inferencing_engine": None},
        )

    @patch("requests.post")
    @patch("streamlit.error")
    def test_display_error_on_exception(self, mock_error, mock_post):
        """Test that an error message is displayed when an exception occurs during execution."""

        # Mock the POST request to raise an exception
        mock_post.side_effect = Exception("Connection error")

        # Test the crawl page
        show_crawl_page()

        # Check if the error was displayed in Streamlit
        mock_error.assert_called_once_with("An error occurred: Connection error")


if __name__ == "__main__":
    unittest.main()
