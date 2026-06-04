import uuid
from typing import Iterable

from requests import Session

session = Session()
B2B_HOST = "localhost:8010"


def __put_into_tree(cat, tree_categories: list):
    for guess_parent_cat in tree_categories:
        if guess_parent_cat['id'] == cat['parent_id']:
            guess_parent_cat["children"].append(cat)
            return True
        found = __put_into_tree(cat, guess_parent_cat["children"])
        if found:
            return True
    return False


def fill_level_path(tree: list[dict], path_prefix: list[str] | None = None):
    for sub in tree:
        sub["path"] = (path_prefix or []) + [sub["name"]]
        sub["level"] = len(sub["path"]) - 1
        fill_level_path(sub["children"], sub["path"])


def make_tree(flat_categories):
    result = []
    for cat in flat_categories:
        cat["children"] = []

    for cat_a in flat_categories:
        pid_a = cat_a.get("parent_id")
        found = False
        for cat_b in flat_categories:
            if pid_a == cat_b.get("id"):
                cat_b['children'].append(cat_a)
                found = True
                break
        if pid_a and not found:
            raise KeyError

    for cat in flat_categories:
        if cat["parent_id"] is None:
            result.append(cat)
    fill_level_path(result)
    return result


__categories_tree = None
__known_flat_categories = None


def get_raw_categories():
    r = session.get(f"http://{B2B_HOST}/api/v1/categories")
    return r.json()["categories"]


def get_tree_categories():
    global __categories_tree, __known_flat_categories
    flat_categories = get_raw_categories()

    if __categories_tree is None or __known_flat_categories != flat_categories:
        __categories_tree = make_tree(flat_categories)
        __known_flat_categories = flat_categories

    return __categories_tree


def __tree_to_flat_categories(tree, level=0, path=None) -> Iterable:
    current_path = (path or []) + [tree["name"]]
    yield {
        "id": tree["id"],
        "name": tree["name"],
        "parent_id": tree["parent_id"],
        "level": level,
        "path": current_path
    }
    for cat in __tree_to_flat_categories(tree["children"], level + 1, current_path):
        yield cat


def get_flat_categories():
    tree = get_tree_categories()
    return __tree_to_flat_categories(tree)


def get_category(category_id: uuid.UUID, include_product_count: bool, lang: str = "ru") -> dict | None:
    r = session.get(f"http://{B2B_HOST}/api/v1/categories/{category_id}",
                    params={
                        "include_product_count": "true" if include_product_count else "false",
                        "lang": lang
                    })
    if r.status_code == 404:
        return None
    return r.json()


def get_category_filter(category_id: uuid.UUID):
    r = session.get(f"http://{B2B_HOST}/api/v1/categories/{category_id}/filters")
    return r.json()


def get_breadcrumbs(_id: uuid.UUID, is_product: bool) -> list | None:
    if is_product:
        url = f"http://{B2B_HOST}/api/v1/products/{_id}/breadcrumbs"
    else:
        url = f"http://{B2B_HOST}/api/v1/categories/{_id}/breadcrumbs"
    r = session.get(url)
    if r.status_code == 404:
        return None
    return r.json()
