import os

import requests
import rest_framework.status
from requests import Session

from neomarket_b2c.settings import B2B_SERVICE_KEY
from src.models.orders import FailedFulfillAttempts


class B2B_client:
    def __init__(self):
        self.session = Session()
        self.b2b_url = os.environ.get("B2B_URL")

    def get_sku(self, sku_id):
        try:
            sku = self.session.get(
                f"{self.b2b_url}/api/v1/public/skus/{sku_id}",
                headers={"X-Service-Key": B2B_SERVICE_KEY or "SERVICE-KEY-NOT-FOUND"},
            )
            return sku
        except requests.ConnectionError as e:
            raise e

    def get_products(self, product_ids):
        try:
            products = self.session.post(
                f"{self.b2b_url}/api/v1/public/products/batch",
                headers={"X-Service-Key": B2B_SERVICE_KEY or "SERVICE-KEY-NOT-FOUND"},
                json={"product_ids": product_ids},
            )
            return products
        except requests.ConnectionError as e:
            raise e

    def reserve_skus(self, idempotency_key, order_id, order_items):
        try:
            reserve_items = []
            for item in order_items:
                reserve_items.append(
                    {"sku_id": str(item.sku_id), "quantity": item.quantity}
                )
            response = self.session.post(
                f"{self.b2b_url}/api/v1/inventory/reserve",
                headers={"X-Service-Key": B2B_SERVICE_KEY or "SERVICE-KEY-NOT-FOUND"},
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
                headers={"X-Service-Key": B2B_SERVICE_KEY or "SERVICE-KEY-NOT-FOUND"},
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
                headers={"X-Service-Key": B2B_SERVICE_KEY or "SERVICE-KEY-NOT-FOUND"},
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
