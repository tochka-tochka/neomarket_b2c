# Create your tests here.
from django.test import TestCase

from src.services.categories.get import make_tree


class MakeTreeTestCate(TestCase):
    def test_make_tree(self):
        c = [
            {"id": 1, "parent_id": None, "children": []},
            {"id": 2, "parent_id": None, "children": []},
            {"id": 3, "parent_id": None, "children": []},
            {"id": 4, "parent_id": 1, "children": []},
            {"id": 5, "parent_id": 3, "children": []},
            {"id": 6, "parent_id": 5, "children": []},
        ]
        should = [
            {"id": 1, "parent_id": None, "children": [
                {"id": 4, "parent_id": 1, "children": []}
            ]},
            {"id": 2, "parent_id": None, "children": []},
            {"id": 3, "parent_id": None,
             "children": [
                 {"id": 5, "parent_id": 3, "children": [
                     {"id": 6, "parent_id": 5, "children": []}
                 ]}
             ]},
        ]
        got = make_tree(c)
        self.assertEqual(got, should)
