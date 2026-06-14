import json
from unittest.mock import patch, Mock

from django.test import TestCase
from rest_framework.test import APIClient


def make_session_response(data):
    mock_response = Mock()
    mock_response.json.return_value = data
    return mock_response


class CatalogSearchTestCase(TestCase):

    '''@patch('src.services.categories.get.session.get')
    def test_search_returns_matching_products(self, mock_session_get):
        client = APIClient()

        mock_response_data = {
            "items": [
                {
                    "id": "prod-1",
                    "name": "iPhone 15 Pro Max",
                    "min_price": 12999000,
                    "has_stock": True
                }
            ],
            "total_count": 1,
            "limit": 20,
            "offset": 0
        }
        mock_session_get.return_value = make_session_response(mock_response_data)

        response = client.get('/api/v1/catalog/products?q=iphone')

        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEqual(resp_json, mock_response_data)
        self.assertTrue(mock_session_get.called)'''

    @patch('src.services.categories.get.session.get')
    def test_search_returns_matching_products(self, mock_session_get):
        client = APIClient()

        mock_response_data = {
            "items": [
                {
                    "id": "prod-1",
                    "name": "iPhone 15 Pro Max",
                    "min_price": 12999000,
                    "has_stock": True
                }
            ],
            "total_count": 1,
            "limit": 20,
            "offset": 0
        }
        mock_session_get.return_value = make_session_response(mock_response_data)

        response = client.get('/api/v1/catalog/products?q=iphone')

        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEqual(resp_json, mock_response_data)
        self.assertTrue(mock_session_get.called)

    @patch('src.services.categories.get.session.get')
    def test_short_query_returns_400(self, mock_session_get):
        client = APIClient()

        response = client.get('/api/v1/catalog/products?q=ip')

        self.assertEqual(response.status_code, 400)
        resp_json = json.loads(response.content)
        self.assertEqual(resp_json['code'], 'INVALID_REQUEST')
        self.assertIn('at least 3 characters', resp_json['message'])
        mock_session_get.assert_not_called()

    @patch('src.services.categories.get.session.get')
    def test_special_chars_do_not_break_query(self, mock_session_get):
        client = APIClient()

        mock_session_get.return_value = make_session_response({"items": [], "total_count": 0})

        response = client.get('/api/v1/catalog/products?q=кофе%27%25_')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_session_get.called)

    @patch('src.services.categories.get.session.get')
    def test_empty_results_returns_200(self, mock_session_get):
        client = APIClient()

        mock_session_get.return_value = make_session_response({"items": [], "total_count": 0})

        response = client.get('/api/v1/catalog/products?q=nonexistentproductxyz')

        self.assertEqual(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertEqual(len(resp_json['items']), 0)
        self.assertEqual(resp_json['total_count'], 0)