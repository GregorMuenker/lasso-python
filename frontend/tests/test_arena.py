import time  # Importing time to mock time.sleep
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import streamlit as st

# Import the relevant functions from the arena page
from arena import show_arena_page


class TestArenaStreamlitApp(unittest.TestCase):

    @patch("requests.post")
    @patch("streamlit.dataframe")
    def test_display_dataframe(self, mock_data_frame, mock_post):
        """Test that the response is converted to a DataFrame and displayed correctly."""

        # Mock the API response from FastAPI
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [24, 27, 22],
            "City": ["New York", "San Francisco", "Los Angeles"],
        }
        mock_post.return_value = mock_response

        # Mock Streamlit's dataframe display function
        with patch("arena.pd.DataFrame") as mock_pandas_df:
            df = pd.DataFrame(mock_response.json())
            st.dataframe(df)
            mock_pandas_df.assert_called_once_with(mock_response.json())
            mock_data_frame.assert_called_once_with(df)

    @patch("requests.post")
    @patch("streamlit.text")
    def test_display_text_response_on_error(self, mock_text, mock_post):
        """Test that the raw text response is displayed in case of an error or non-JSON response."""

        # Mock the API response with a non-JSON error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Some error occurred"
        mock_post.return_value = mock_response

        # Simulate a request to the FastAPI endpoint
        with patch("arena.st.error") as mock_error:
            st.text(mock_response.text)
            mock_error.assert_called_once_with("Error: 400")
            mock_text.assert_called_once_with("Some error occurred")

    @patch("requests.post")
    @patch("streamlit.error")
    def test_display_error_on_exception(self, mock_error, mock_post):
        """Test that an error message is displayed when an exception occurs during execution."""

        # Mock the POST request to raise an exception
        mock_post.side_effect = Exception("Connection error")

        with patch("arena.st.error") as mock_streamlit_error:
            st.error("An error occurred: Connection error")
            mock_streamlit_error.assert_called_once_with(
                "An error occurred: Connection error"
            )


if __name__ == "__main__":
    unittest.main()
