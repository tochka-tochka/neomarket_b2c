from typing import Literal

from src.services.catalog.facets import make_filters_query_params
from src.services.categories.get import session, B2B_HOST

SortType = Literal["rating", "price_asc", "price_desc", "popularity", "new", "discount_desc"]


def get_catalog_products(limit: int, offset: int, q: str, sort: SortType, filters: dict):
    if sort not in {"rating", "price_asc", "price_desc", "popularity", "new", "discount_desc"}:
        raise ValueError(f"Invalid sort parameter: {sort}")
    category_id = filters.pop('category_id')[0]
    filters_string = "&".join(make_filters_query_params(filters))
    # TODO: maybe use `params`?
    r = session.get(f"http://{B2B_HOST}/api/v1/public/products?category_id={category_id}&"
                    f"limit={limit}&offset={offset}&q={q}&sort={sort}&" + filters_string,
                    headers={"X-Service-Key": "key"})
    print(r.text)
    return r.json()
