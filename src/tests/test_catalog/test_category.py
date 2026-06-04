import json
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class GetCategoryTestCase(TestCase):
    @patch('src.services.categories.get.get_raw_categories')
    def test_category_tree_returns_nested_structure(self, get_fake_categories):
        client = APIClient()
        parent_category_id = "7db94395-f8da-4582-b177-4c24fe586eb6"
        child_id_1 = "5f9785f9-ebab-4024-8a1c-4c3261f3f16b"
        child_id_2 = "23cc8d28-77a8-4759-ab53-ed418662cd0e"
        get_fake_categories.return_value = [
            {
                "id": child_id_1,
                "parent_id": parent_category_id,
                "name": "Утюги"
            },
            {
                "id": child_id_2,
                "parent_id": parent_category_id,
                "name": "Зубные щётки"
            },
            {
                "id": parent_category_id,
                "parent_id": None,
                "name": "Бытовая техника и уход"
            }
        ]

        r = client.get('/api/v1/catalog/categories/tree')
        resp_json = json.loads(r.content)
        print(resp_json)
        self.assertEqual(resp_json, [
            {
                "id": parent_category_id,
                "name": "Бытовая техника и уход",
                "parent_id": None,
                "level": 0,
                "path": ["Бытовая техника и уход"],
                "children": [
                    {
                        "id": child_id_1,
                        "name": "Утюги",
                        "parent_id": parent_category_id,
                        "level": 1,
                        "path": ["Бытовая техника и уход", "Утюги"],
                        "children": []
                    },
                    {
                        "id": child_id_2,
                        "name": "Зубные щётки",
                        "parent_id": parent_category_id,
                        "level": 1,
                        "path": ["Бытовая техника и уход", "Зубные щётки"],
                        "children": []
                    }
                ]
            }
        ])
        self.assertTrue(get_fake_categories.called)

    @patch('src.services.categories.get.get_raw_categories')
    def test_orphan_node_returns_422(self, get_fake_categories):
        client = APIClient()
        parent_category_id = "7db94395-f8da-4582-b177-4c24fe586eb6"
        child_id_1 = "5f9785f9-ebab-4024-8a1c-4c3261f3f16b"
        child_id_2 = "23cc8d28-77a8-4759-ab53-ed418662cd0e"
        get_fake_categories.return_value = [
            {
                "id": child_id_1,
                "parent_id": parent_category_id,
                "name": "Утюги"
            },
            {
                "id": child_id_2,
                "parent_id": parent_category_id,
                "name": "Зубные щётки"
            }
        ]

        r = client.get('/api/v1/catalog/categories/tree')
        self.assertEqual(r.status_code, 422)
        self.assertTrue(get_fake_categories.called)

    @patch('src.views.catalog.get_breadcrumbs')
    def test_breadcrumbs_return_path_from_root(self, get_fake_breadcrumbs):
        breadcrumbs_retval = [
            {
                "id": "7db94395-f8da-4582-b177-4c24fe586eb6",
                "name": "Бытовая техника и уход",
                "parent_id": None,
                "level": 0,
                "path": "/home-appliances-and-care",
                "is_active": True,
                "created_at": "2026-05-19T10:47:28.760Z"
            },
            {
                "id": "fc6ba7d8-9799-46e3-a0df-377cd72eb855",
                "name": "Весы",
                "parent_id": "7db94395-f8da-4582-b177-4c24fe586eb6",
                "level": 1,
                "path": "/home-appliances-and-care/scales",
                "is_active": True,
                "created_at": "2026-05-19T10:47:28.760Z"
            }
        ]
        get_fake_breadcrumbs.return_value = breadcrumbs_retval
        client = APIClient()

        r = client.get('/api/v1/catalog/breadcrumbs?category_id=fc6ba7d8-9799-46e3-a0df-377cd72eb855')
        resp_json = json.loads(r.content)

        self.assertEqual(resp_json, breadcrumbs_retval)
        self.assertTrue(get_fake_breadcrumbs.called)

    def test_ambiguous_params_returns_400(self):
        client = APIClient()
        r = client.get(
            '/api/v1/catalog/breadcrumbs',
            query_params={
                "category_id": "fc6ba7d8-9799-46e3-a0df-377cd72eb855",
                "product_id": "fc6ba7d8-9799-46e3-a0df-377cd72eb855"
            }
        )
        self.assertEqual(r.status_code, 400)

    @patch('src.views.category.get_category')
    def test_unknown_category_returns_404(self, get_fake_category):
        client = APIClient()
        get_fake_category.return_value = None
        r = client.get('/api/v1/catalog/categories/fc6ba7d8-9799-46e3-a0df-377cd72eb855')
        self.assertEqual(r.status_code, 404)
