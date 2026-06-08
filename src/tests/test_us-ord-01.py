import re
import uuid

import pytest
import responses
from django.urls import reverse
from rest_framework import status

from src.tests.fixtures import (
    mock_b2b_reserve_happy_response,
    mock_products_happy_response,
    mock_products_unhappy_response,
    mock_sku1_happy_response,
    mock_sku2_happy_response,
    mock_sku2_unhappy_response,
    test_address,
    test_payment_method,
)


@pytest.mark.django_db(transaction=True)
class TestCreateOrder:
    def test_checkout_creates_paid_order_with_fixed_prices(
        self,
        jwt_client,
        test_address,
        test_payment_method,
        mock_products_happy_response,
        mock_sku1_happy_response,
        mock_sku2_happy_response,
        mock_b2b_reserve_happy_response,
    ):
        url = reverse("orders")

        payload = {
            "address_id": test_address.id,
            "payment_method_id": test_payment_method.id,
            "comment": "fsdhgdfgj",
            "items_snapshot": [
                {
                    "sku_id": "c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
                    "quantity": 1,
                    "unit_price": 10,
                },
                {
                    "sku_id": "c6603522-9922-46f7-86ca-1f134095ff9f",
                    "quantity": 1,
                    "unit_price": 10,
                },
            ],
        }

        response = jwt_client.post(
            url,
            data=payload,
            headers={"Idempotency-Key": str(uuid.uuid4())},
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_201_CREATED, response.json()
        for order_item in response.json()["items"]:
            assert order_item["unit_price"] is not None

    def test_partial_reserve_failure_returns_409(
        self,
        jwt_client,
        test_address,
        test_payment_method,
        mock_products_unhappy_response,
        mock_sku1_happy_response,
        mock_sku2_unhappy_response,
    ):
        url = reverse("orders")

        payload = {
            "address_id": test_address.id,
            "payment_method_id": test_payment_method.id,
            "comment": "fsdhgdfgj",
            "items_snapshot": [
                {
                    "sku_id": "c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
                    "quantity": 1,
                    "unit_price": 10,
                },
                {
                    "sku_id": "c6603522-9922-46f7-86ca-1f134095ff9f",
                    "quantity": 1,
                    "unit_price": 10,
                },
            ],
        }

        response = jwt_client.post(
            url,
            data=payload,
            headers={"Idempotency-Key": str(uuid.uuid4())},
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_409_CONFLICT, response.json()
        for order_item in response.json()["failed_items"]:
            assert order_item["reason"] == "RESERVE_FAILED"

    def test_idempotency_returns_existing_order(
        self,
        jwt_client,
        test_address,
        test_payment_method,
        mock_products_happy_response,
        mock_sku1_happy_response,
        mock_sku2_happy_response,
        mock_b2b_reserve_happy_response,
    ):
        url = reverse("orders")

        payload = {
            "address_id": test_address.id,
            "payment_method_id": test_payment_method.id,
            "comment": "fsdhgdfgj",
            "items_snapshot": [
                {
                    "sku_id": "c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
                    "quantity": 1,
                    "unit_price": 10,
                },
                {
                    "sku_id": "c6603522-9922-46f7-86ca-1f134095ff9f",
                    "quantity": 1,
                    "unit_price": 10,
                },
            ],
        }

        idmpotency_key = str(uuid.uuid4())

        response1 = jwt_client.post(
            url,
            data=payload,
            headers={"Idempotency-Key": idmpotency_key},
            content_type="application/json",
        )

        assert response1.status_code == status.HTTP_201_CREATED, response1.json()
        for order_item in response1.json()["items"]:
            assert order_item["unit_price"] is not None

        response2 = jwt_client.post(
            url,
            data=payload,
            headers={"Idempotency-Key": idmpotency_key},
            content_type="application/json",
        )

        assert response1.status_code == status.HTTP_201_CREATED, response1.json()
        assert response2.json()["id"] == response1.json()["id"]

    def test_b2b_unavailable_returns_503(
        self, jwt_client, test_address, test_payment_method
    ):
        url = reverse("orders")

        payload = {
            "address_id": test_address.id,
            "payment_method_id": test_payment_method.id,
            "comment": "fsdhgdfgj",
            "items_snapshot": [
                {
                    "sku_id": "c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
                    "quantity": 1,
                    "unit_price": 10,
                },
                {
                    "sku_id": "c6603522-9922-46f7-86ca-1f134095ff9f",
                    "quantity": 1,
                    "unit_price": 10,
                },
            ],
        }

        response = jwt_client.post(
            url,
            data=payload,
            headers={"Idempotency-Key": str(uuid.uuid4())},
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE, (
            response.json()
        )
