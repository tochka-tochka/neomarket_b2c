import uuid

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


def make_tree(flat_categories):
    result = []
    for cat in flat_categories:
        cat["children"] = []
    for cat_a in flat_categories:
        pid_a = cat_a.get("parent_id")
        for cat_b in flat_categories:
            if pid_a == cat_b.get("id"):
                cat_b['children'].append(cat_a)
                break
    for cat in flat_categories:
        if cat["parent_id"] is None:
            result.append(cat)
    return result


__categories_tree = None
__known_flat_categories = None


def get_flat_categories():
    r = session.get(f"http://{B2B_HOST}/api/v1/categories")
    return r.json()["categories"]


def get_tree_categories():
    global __categories_tree, __known_flat_categories
    flat_categories = get_flat_categories()

    if __categories_tree is None or __known_flat_categories != flat_categories:
        __categories_tree = make_tree(flat_categories)
        __known_flat_categories = flat_categories

    return __categories_tree


# TODO: lang support
def get_category(category_id: uuid.UUID, include_product_count: bool, lang: str = "ru"):
    r = session.get(f"http://{B2B_HOST}/api/v1/categories/{category_id}",
                    params={
                        "include_product_count": "true" if include_product_count else "false",
                        "lang": lang
                    })
    return r.json()
