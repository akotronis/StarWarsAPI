from unittest.mock import Mock, patch

from django.test import TestCase
from requests.exceptions import ConnectionError, HTTPError, Timeout

from ..clients import get_swapi_data


class GetSWAPIDataTest(TestCase):
    @patch("app.clients.requests.get")
    def test_get_swapi_data_success(self, mock_get):
        """Test successful API call"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"name": "Luke Skywalker", "height": "172"},
            {"name": "Darth Vader", "height": "202"},
        ]
        mock_get.return_value = mock_response

        url = "https://swapi.dev/api/people/"
        result = get_swapi_data(url)

        mock_get.assert_called_once_with(url)
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
        self.assertEqual(result, mock_response.json.return_value)

    @patch("app.clients.requests.get")
    def test_get_swapi_data_http_error(self, mock_get):
        """Test HTTP error handling"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        url = "https://swapi.dev/api/people/999/"

        with self.assertRaises(HTTPError) as context:
            get_swapi_data(url)

        self.assertEqual(str(context.exception), "404 Not Found")
        mock_get.assert_called_once_with(url)
        mock_response.raise_for_status.assert_called_once()

    @patch("app.clients.requests.get")
    def test_get_swapi_data_connection_error(self, mock_get):
        """Test connection error handling"""
        mock_get.side_effect = ConnectionError("Connection failed")

        url = "https://swapi.dev/api/people/"

        with self.assertRaises(ConnectionError) as context:
            get_swapi_data(url)

        self.assertEqual(str(context.exception), "Connection failed")
        mock_get.assert_called_once_with(url)

    @patch("app.clients.requests.get")
    def test_get_swapi_data_timeout_error(self, mock_get):
        """Test timeout error handling"""
        mock_get.side_effect = Timeout("Request timed out")

        url = "https://swapi.dev/api/people/"

        with self.assertRaises(Timeout) as context:
            get_swapi_data(url)

        self.assertEqual(str(context.exception), "Request timed out")
        mock_get.assert_called_once_with(url)

    @patch("app.clients.requests.get")
    def test_get_swapi_data_empty_response(self, mock_get):
        """Test handling of empty response"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        url = "https://swapi.dev/api/people/"
        result = get_swapi_data(url)

        self.assertEqual(result, {})

    @patch("app.clients.requests.get")
    def test_get_swapi_data_invalid_url(self, mock_get):
        """Test behavior with invalid URL format"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"error": "not found"}
        mock_get.return_value = mock_response

        url = "invalid-url"
        result = get_swapi_data(url)

        mock_get.assert_called_once_with(url)
        self.assertEqual(result, {"error": "not found"})
