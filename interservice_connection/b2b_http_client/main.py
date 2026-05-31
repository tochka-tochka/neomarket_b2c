import rest_framework.status
import json
import os

import requests
from requests import Session

from src.models.orders import FailedFulfillAttempts


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

    def reserve_skus(self, idempotency_key, order_id, order_items):
        try:
            reserve_items = []
            for item in order_items:
                reserve_items.append(
                    {"sku_id": item["sku_id"], "quantity": item["quantity"]}
                )
            response = self.session.post(
                f"{self.b2b_url}/api/v1/inventory/reserve",
                json={
                    "idempotency_key": idempotency_key,
                    "order_id": str(order_id),
                    "items": reserve_items,
                },
            )
            return response
        except requests.ConnectionError as e:
            raise e

    def unreserve_skus(self, order):
        try:
            items = []
            for item in order["items"]:
                items.append({"sku_id": item["sku_id"], "quantity": item["quantity"]})
            response = self.session.post(
                f"{self.b2b_url}/api/v1/inventory/unreserve",
                json={"order_id": order["id"], "items": items},
            )
            return response
        except requests.ConnectionError as e:
            raise e

    def fulfill_order(self, order):
        try:
            items = []
            for item in order["items"]:
                items.append({"sku_id": item["sku_id"], "quantity": item["quantity"]})
            response = self.session.post(
                f"{self.b2b_url}/api/v1/inventory/fulfill",
                json={"order_id": order["id"], "items": items},
            )
            if response.status_code != rest_framework.status.HTTP_200_OK:
                FailedFulfillAttempts.objects.create(
                    payload={"order_id": order["id"], "items": items}
                )
        except requests.ConnectionError as e:
            FailedFulfillAttempts.objects.create(
                payload={"order_id": order["id"], "items": items}
            )
            raise e


b2b_client = B2B_client()
