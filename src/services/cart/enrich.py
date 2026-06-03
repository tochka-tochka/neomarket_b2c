from typing import List, Dict, Optional
from requests import Session
from neomarket_b2c.settings import B2B_SERVICE_KEY

session = Session()
B2B_HOST = "localhost:8010"

def get_sku_by_id(sku_id: str) -> Optional[dict]:

    url = f"http://{B2B_HOST}/api/v1/public/skus/{sku_id}"
    headers = {"X-Service-Key": B2B_SERVICE_KEY}

    response = session.get(url, headers=headers)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


def get_skus_batch(sku_ids: List[str]) -> Dict[str, dict]:

    if not sku_ids:
        return {}

    unique_sku_ids = list(set(sku_ids))
    result = {}

    for sku_id in unique_sku_ids:
        try:
            sku_data = get_sku_by_id(sku_id)
            if sku_data:
                result[sku_id] = sku_data
            else:
                result[sku_id] = None
        except Exception as e:
            print(f"Failed to fetch SKU {sku_id}: {e}")
            result[sku_id] = None

    return result
