# Create your tests here.
from django.test import TestCase

from src.services.categories.get import make_tree


class MakeTreeTestCate(TestCase):
    def test_make_tree(self):
        c = [
            {"id": 1, "name": "a", "parent_id": None, "children": []},
            {"id": 2, "name": "b", "parent_id": None, "children": []},
            {"id": 3, "name": "c", "parent_id": None, "children": []},
            {"id": 4, "name": "d", "parent_id": 1, "children": []},
            {"id": 5, "name": "e", "parent_id": 3, "children": []},
            {"id": 6, "name": "f", "parent_id": 5, "children": []},
        ]
        should = [
            {"id": 1, "name": "a", "parent_id": None, "level": 0, "path": ["a"], "children": [
                {"id": 4, "name": "d", "level": 1, "path": ["a", "d"], "parent_id": 1, "children": []}
            ]},
            {"id": 2, "name": "b", "level": 0, "path": ["b"], "parent_id": None, "children": []},
            {"id": 3, "parent_id": None, "level": 0,
             "name": "c", "path": ["c"],
             "children": [
                 {"id": 5, "name": "e", "level": 1, "path": ["c", "e"], "parent_id": 3, "children": [
                     {"id": 6, "name": "f", "level": 2, "path": ["c", "e", "f"], "parent_id": 5, "children": []}
                 ]}
             ]},
        ]
        got = make_tree(c)
        self.assertEqual(should, got)
