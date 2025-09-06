
from unittest.mock import patch, Mock

from django.test import TestCase
from rest_framework.exceptions import ValidationError

from .. import services


class FetchAndValidateDataTest(TestCase):
    @patch('app.services.clients.get_swapi_data')
    def test_fetch_and_validate_success(self, mock_get_swapi):
        """Test successful data fetching and validation"""
        mock_get_swapi.return_value = [{'name': 'Test', 'height': '172'}]
        
        mock_serializer = Mock()
        mock_serializer.return_value.is_valid.return_value = True
        mock_serializer.return_value.validated_data = [{'name': 'Test', 'height': 172.0}]
        
        result = services.fetch_and_validate_data('test_url', mock_serializer)
        self.assertEqual(result, [{'name': 'Test', 'height': 172.0}])

    @patch('app.services.clients.get_swapi_data')
    def test_fetch_and_validate_validation_error(self, mock_get_swapi):
        """Test validation error handling"""
        mock_get_swapi.return_value = [{'invalid': 'data'}]
        
        mock_serializer = Mock()
        mock_serializer.return_value.is_valid.side_effect = ValidationError('Invalid data')
        
        with self.assertRaises(ValidationError):
            services.fetch_and_validate_data('test_url', mock_serializer)