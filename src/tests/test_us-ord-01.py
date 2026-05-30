import re
import uuid

import pytest
import responses
from django.urls import reverse
from rest_framework import status

from src.tests.fixtures import test_address, test_payment_method


@pytest.fixture
def mock_b2b_reserve_happy_response(responses):
    b2b_url = "http://localhost:8010/api/v1/inventory/reserve"
    responses.add(
        method=responses.POST,
        url=b2b_url,
        json={
            "order_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "status": "RESERVED",
            "reserved_at": "2026-05-30T12:28:47.442Z",
        },
        status=200,
    )
    return responses


@pytest.fixture
def mock_b2b_get_skus_unhappy_response(responses):
    b2b_url_pattern = re.compile(r"http://localhost:8010/api/v1/products\?ids=.*")
    responses.add(
        method=responses.GET,
        url=b2b_url_pattern,
        json=[
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "seller_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "Товар 1",
                "slug": "т1",
                "description": "Товар 1",
                "status": "MODERATED",
                "deleted": False,
                "blocking_reason_id": None,
                "moderator_comment": "Товар1",
                "images": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "url": "some_bucket/1.png",
                        "ordering": 0,
                    }
                ],
                "characteristics": [
                    {
                        "name": "Бренд",
                        "value": "Apple",
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    }
                ],
                "skus": [
                    {
                        "id": "c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
                        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "sku 1",
                        "price": 10,
                        "discount": 0,
                        "cost_price": 10,
                        "stock_quantity": 10,
                        "active_quantity": 10,
                        "reserved_quantity": 10,
                        "article": "string",
                        "images": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "url": "some_bucket/1.png",
                                "ordering": 0,
                            }
                        ],
                        "characteristics": [
                            {
                                "name": "Бренд",
                                "value": "Apple",
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            }
                        ],
                        "created_at": "2026-05-26T09:25:38.860Z",
                        "updated_at": "2026-05-26T09:25:38.860Z",
                    }
                ],
                "created_at": "2026-05-26T09:25:38.860Z",
                "updated_at": "2026-05-26T09:25:38.860Z",
            },
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                "seller_id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                "title": "Товар 2",
                "slug": "т2",
                "description": "Товар 2",
                "status": "MODERATED",
                "deleted": False,
                "blocking_reason_id": None,
                "moderator_comment": "Товар1",
                "images": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "url": "some_bucket/1.png",
                        "ordering": 0,
                    }
                ],
                "characteristics": [
                    {
                        "name": "Бренд",
                        "value": "Apple",
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    }
                ],
                "skus": [
                    {
                        "id": "c6603522-9922-46f7-86ca-1f134095ff9f",
                        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "sku 1",
                        "price": 10,
                        "discount": 0,
                        "cost_price": 10,
                        "stock_quantity": 10,
                        "active_quantity": 0,
                        "reserved_quantity": 0,
                        "article": "string",
                        "images": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "url": "some_bucket/1.png",
                                "ordering": 0,
                            }
                        ],
                        "characteristics": [
                            {
                                "name": "Бренд",
                                "value": "Apple",
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            }
                        ],
                        "created_at": "2026-05-26T09:25:38.860Z",
                        "updated_at": "2026-05-26T09:25:38.860Z",
                    }
                ],
                "created_at": "2026-05-26T09:25:38.860Z",
                "updated_at": "2026-05-26T09:25:38.860Z",
            },
        ],
        status=200,
    )
    return responses


@pytest.fixture
def mock_b2b_get_skus_happy_response(responses):
    b2b_url_pattern = re.compile(r"http://localhost:8010/api/v1/products\?ids=.*")
    responses.add(
        method=responses.GET,
        url=b2b_url_pattern,
        json=[
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "seller_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "title": "Товар 1",
                "slug": "т1",
                "description": "Товар 1",
                "status": "MODERATED",
                "deleted": False,
                "blocking_reason_id": None,
                "moderator_comment": "Товар1",
                "images": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "url": "some_bucket/1.png",
                        "ordering": 0,
                    }
                ],
                "characteristics": [
                    {
                        "name": "Бренд",
                        "value": "Apple",
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    }
                ],
                "skus": [
                    {
                        "id": "c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
                        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "sku 1",
                        "price": 10,
                        "discount": 0,
                        "cost_price": 10,
                        "stock_quantity": 10,
                        "active_quantity": 10,
                        "reserved_quantity": 10,
                        "article": "string",
                        "images": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "url": "some_bucket/1.png",
                                "ordering": 0,
                            }
                        ],
                        "characteristics": [
                            {
                                "name": "Бренд",
                                "value": "Apple",
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            }
                        ],
                        "created_at": "2026-05-26T09:25:38.860Z",
                        "updated_at": "2026-05-26T09:25:38.860Z",
                    }
                ],
                "created_at": "2026-05-26T09:25:38.860Z",
                "updated_at": "2026-05-26T09:25:38.860Z",
            },
            {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                "seller_id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
                "title": "Товар 2",
                "slug": "т2",
                "description": "Товар 2",
                "status": "MODERATED",
                "deleted": False,
                "blocking_reason_id": None,
                "moderator_comment": "Товар1",
                "images": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "url": "some_bucket/1.png",
                        "ordering": 0,
                    }
                ],
                "characteristics": [
                    {
                        "name": "Бренд",
                        "value": "Apple",
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    }
                ],
                "skus": [
                    {
                        "id": "c6603522-9922-46f7-86ca-1f134095ff9f",
                        "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "sku 1",
                        "price": 10,
                        "discount": 0,
                        "cost_price": 10,
                        "stock_quantity": 10,
                        "active_quantity": 10,
                        "reserved_quantity": 10,
                        "article": "string",
                        "images": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "url": "some_bucket/1.png",
                                "ordering": 0,
                            }
                        ],
                        "characteristics": [
                            {
                                "name": "Бренд",
                                "value": "Apple",
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            }
                        ],
                        "created_at": "2026-05-26T09:25:38.860Z",
                        "updated_at": "2026-05-26T09:25:38.860Z",
                    }
                ],
                "created_at": "2026-05-26T09:25:38.860Z",
                "updated_at": "2026-05-26T09:25:38.860Z",
            },
        ],
        status=200,
    )
    return responses


@pytest.mark.django_db
class TestCreateOrder:
    def test_checkout_creates_paid_order_with_fixed_prices(
        self,
        jwt_client,
        test_address,
        test_payment_method,
        mock_b2b_get_skus_happy_response,
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
        mock_b2b_get_skus_unhappy_response,
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
        mock_b2b_get_skus_happy_response,
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
