from typing import Literal

from neomarket_b2c.settings import B2B_SERVICE_KEY
from src.services.catalog.facets import make_filters_query_params
from src.services.categories.get import session, B2B_HOST

SortType = Literal["rating", "price_asc", "price_desc", "popularity", "new", "discount_desc"]


def get_catalog_products(limit: int, offset: int, q: str, sort: SortType, filters: dict):
    if sort not in {"rating", "price_asc", "price_desc", "popularity", "new", "discount_desc"}:
        raise ValueError(f"Invalid sort parameter: {sort}")
    category_id = filters.get('category_id', [None])[0] or ""
    filters_string = "&".join(make_filters_query_params(filters))
    # TODO: maybe use `params`?
    r = session.get(f"http://{B2B_HOST}/api/v1/public/products?category_id={category_id}&"
                    f"limit={limit}&offset={offset}&q={q}&sort={sort}&" + filters_string,
                    headers={"X-Service-Key": B2B_SERVICE_KEY})
    print(r.text)
    return r.json()


def get_product_card(product_id):
    response = session.get(f"http://{B2B_HOST}/api/v1/public/products/{product_id}",
                           headers={"X-Service-Key": B2B_SERVICE_KEY})

    return response


def get_products_batch(product_ids):
    response = session.post(f"http://{B2B_HOST}/api/v1/public/products/batch",
                            params={"product_ids": product_ids},
                           headers={"X-Service-Key": B2B_SERVICE_KEY})

    return response


def get_similar_products(product_id, limit: int = 10):
    response = get_product_card(product_id)

    if response.status_code == 200:
        response = session.get(
            f"http://{B2B_HOST}/api/v1/public/products/{product_id}/similar",
            params={"limit": limit + 1},
            headers={"X-Service-Key": B2B_SERVICE_KEY}
        ).json()

        product_ids = [item["id"] for item in response["items"] if item["id"] != product_id][:limit]

        response = get_products_batch(product_ids)

    return response
