from typing import List, Dict
from requests import Session
from neomarket_b2c.settings import B2B_SERVICE_KEY

session = Session()
B2B_HOST = "localhost:8010"


def get_products_batch(product_ids: List[str]) -> Dict[str, dict]:

    if not product_ids:
        return {}

    unique_ids = list(set(product_ids))
    ids_param = ",".join(unique_ids)

    url = f"http://{B2B_HOST}/api/v1/products"
    headers = {"X-Service-Key": B2B_SERVICE_KEY}
    params = {"ids": ids_param}

    response = session.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    items = data.get("items", [])

    return {str(item["id"]): item for item in items}
