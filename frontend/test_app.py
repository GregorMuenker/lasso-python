import time  # Importing time to mock time.sleep
import unittest
from unittest.mock import MagicMock, patch

# Import the relevant functions from app.py
from app import check_containers, retry_check


class TestStreamlitApp(unittest.TestCase):

    @patch("docker.from_env")
    def test_check_containers_all_running(self, mock_docker):
        """Test that `check_containers` returns True when all containers are running."""

        # Mock Docker container list response
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container_1 = MagicMock()
        mock_container_2 = MagicMock()
        mock_container_1.name = "lasso_ignite"
        mock_container_2.name = "lasso_python_crawl"
        mock_client.containers.list.return_value = [mock_container_1, mock_container_2]

        # Simulate all required containers are running
        is_running, missing = check_containers()
        self.assertTrue(is_running)
        self.assertEqual(missing, [])

    @patch("docker.from_env")
    def test_check_containers_some_missing(self, mock_docker):
        """Test that `check_containers` returns False when some containers are missing."""

        # Mock Docker container list response
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container_1 = MagicMock()
        mock_container_1.name = "lasso_ignite"
        mock_client.containers.list.return_value = [mock_container_1]

        # Simulate that one container is missing
        is_running, missing = check_containers()
        self.assertFalse(is_running)
        self.assertIn("lasso_python_crawl", missing)

    @patch(
        "time.sleep", return_value=None
    )  # Mock time.sleep to avoid real waiting during tests
    @patch("app.check_containers")
    def test_retry_check_success(self, mock_check_containers, mock_sleep):
        """Test that `retry_check` succeeds if containers start running before max retries."""

        # First 2 attempts fail, then containers are running
        mock_check_containers.side_effect = [
            (False, ["lasso_python_crawl"]),
            (False, ["lasso_python_crawl"]),
            (True, []),  # On the third try, all containers are running
        ]

        result = retry_check()
        self.assertTrue(result)

    @patch(
        "time.sleep", return_value=None
    )  # Mock time.sleep to avoid real waiting during tests
    @patch("app.check_containers")
    def test_retry_check_failure(self, mock_check_containers, mock_sleep):
        """Test that `retry_check` fails after max retries if containers are not running."""

        # Simulate that the containers never start running
        mock_check_containers.return_value = (False, ["lasso_python_crawl"])

        result = retry_check()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
