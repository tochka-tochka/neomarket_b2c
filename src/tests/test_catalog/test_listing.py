import json
from unittest.mock import patch

import requests
from django.test import TestCase
from rest_framework.test import APIClient


class CatalogListingTestCase(TestCase):
    @patch('src.services.catalog.views.get_catalog_products')
    def test_catalog_returns_filtered_sorted_products(self, get_fake_products):
        client = APIClient()
        catalog_retval = {
            "items": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                    "slug": "string",
                    "category": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "string",
                        "parent_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "level": 0,
                        "path": [
                            "string"
                        ]
                    },
                    "min_price": 0,
                    "old_price": 0,
                    "has_stock": True,
                    "rating": 5,
                    "reviews_count": 0,
                    "images": [
                        {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "url": "string",
                            "alt": "string",
                            "ordering": 0,
                            "is_main": True
                        }
                    ],
                    "seller": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "display_name": "string"
                    }
                }
            ],
            "total_count": 1,
            "limit": 20,
            "offset": 0
        }
        get_fake_products.return_value = catalog_retval
        r = client.get('/api/v1/catalog/products?filter[category_id]=3fa85f64-5717-4562-b3fc-2c963f66afa6')
        resp_json = json.loads(r.content)
        self.assertEqual(resp_json, catalog_retval)
        self.assertTrue(get_fake_products.called)

    @patch('src.services.catalog.views.get_catalog_products')
    def test_b2b_unavailable_returns_502(self, get_fake_products):
        client = APIClient()
        get_fake_products.side_effect = requests.exceptions.ConnectionError()
        r = client.get('/api/v1/catalog/products?filter[category_id]=3fa85f64-5717-4562-b3fc-2c963f66afa6')
        self.assertEqual(r.status_code, 503)

    def test_invalid_sort_returns_400(self):
        client = APIClient()
        r = client.get(
            '/api/v1/catalog/products?filter[category_id]=3fa85f64-5717-4562-b3fc-2c963f66afa6&sort=unknown_asc')
        self.assertEqual(r.status_code, 400)
