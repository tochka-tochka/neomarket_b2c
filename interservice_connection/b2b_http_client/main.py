import requests
import os

from requests import Session
import json


class B2B_client:
    def __init__(self):
        self.session = Session()
        self.b2b_url = os.environ.get("B2B_URL")

    def get_products_by_sku_ids(self, sku_ids):
        try:
            products = self.session.get(
                f"{self.b2b_url}/api/v1/products?ids={','.join(sku_ids)}"
            )
            return products
        except requests.ConnectionError as e:
            raise e


b2b_client = B2B_client()
