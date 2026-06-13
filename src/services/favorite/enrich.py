from typing import List, Dict
from requests import Session
from neomarket_b2c.settings import B2B_SERVICE_KEY

session = Session()
B2B_HOST = "localhost:8010"


def get_products_batch(product_ids: List[str]) -> Dict[str, dict]:

    if not product_ids:
        return {}

    unique_ids = list(set(product_ids))

    url = f"http://{B2B_HOST}/api/v1/public/products/batch"
    headers = {"X-Service-Key": B2B_SERVICE_KEY}

    response = session.post(url, headers=headers, json={"product_ids": unique_ids})
    response.raise_for_status()

    items = response.json()

    return {str(item["id"]): item for item in items}
