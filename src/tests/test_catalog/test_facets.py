import json
from unittest.mock import patch

import requests.exceptions
from django.test import TestCase
from rest_framework.test import APIClient


class GetFacetsTestCase(TestCase):
    @patch('src.services.catalog.views.get_catalog_facets')
    def test_facets_return_counts_per_filter_value(self, get_fake_facets):
        client = APIClient()
        facet_retval = {
            "category_id": '28bc2f27-3e37-47d1-a1f0-6fce7603ffe1',
            "facets": [
                {
                    "name": "Color",
                    "values": [
                        {
                            "value": "blue",
                            "count": 2
                        }
                    ]
                }
            ]
        }
        get_fake_facets.return_value = facet_retval
        r = client.get('/api/v1/catalog/facets?category_id=28bc2f27-3e37-47d1-a1f0-6fce7603ffe1&filter[Color]=blue')
        resp_json = json.loads(r.content)
        self.assertEqual(resp_json, facet_retval)
        self.assertTrue(get_fake_facets.called)

