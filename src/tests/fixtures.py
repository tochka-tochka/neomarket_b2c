import re
import uuid

import pytest

from src.models.orders import Address, Order, OrderItem, OrderStatus, PaymentMethod
from src.models.cart import CartItem

@pytest.fixture
def test_address(test_user):
    address = Address.objects.create(
        country="Россия",
        city="Екатеринбург",
        street="Ленина",
        building="1",
        apartment="1",
        postal_code="111111",
        recipient_name="recipient",
        recipient_phone="+79999999999",
        comment="rwqjflgtj",
        buyer=test_user,
    )
    return address


@pytest.fixture
def test_payment_method(test_user):
    payment_method = PaymentMethod.objects.create(
        type="CARD", card_last4="1111", card_brand="VISA", buyer=test_user
    )
    return payment_method

@pytest.fixture
def test_cart(test_user):
    CartItem.objects.create(
        user_id=test_user.id,
        sku_id="c35ca151-1b23-43b4-b78c-ec297d9a7fd0",
        quantity=1,
    )
    CartItem.objects.create(
        user_id=test_user.id,
        sku_id="c6603522-9922-46f7-86ca-1f134095ff9f",
        quantity=1,
    )


@pytest.fixture
def test_order(test_user, test_address, test_payment_method):
    order = Order.objects.create(
        buyer=test_user,
        number="ORD-SKU-123",
        status=OrderStatus.PAID,
        address=test_address,
        payment_method=test_payment_method,
    )
    OrderItem.objects.create(
        order=order,
        sku_id=str(uuid.uuid4()),
        product_id=str(uuid.uuid4()),
        name="Product 1",
        quantity=2,
        unit_price=100.00,
        line_total=200.00,
        image_url="http://example.com/image1.jpg",
    )
    OrderItem.objects.create(
        order=order,
        sku_id=str(uuid.uuid4()),
        product_id=str(uuid.uuid4()),
        name="Product 2",
        quantity=1,
        unit_price=50.00,
        line_total=50.00,
        image_url="http://example.com/image2.jpg",
    )
    return order


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
def mock_sku1_happy_response(responses):
    b2b_url = (
        "http://localhost:8010/api/v1/public/skus/c35ca151-1b23-43b4-b78c-ec297d9a7fd0"
    )
    responses.add(
        method=responses.GET,
        url=b2b_url,
        json={
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
        },
        status=200,
    )
    return responses

@pytest.fixture
def mock_sku2_happy_response(responses):
    b2b_url = (
        "http://localhost:8010/api/v1/public/skus/c6603522-9922-46f7-86ca-1f134095ff9f"
    )
    responses.add(
        method=responses.GET,
        url=b2b_url,
        json={
            "id": "c6603522-9922-46f7-86ca-1f134095ff9f",
            "product_id": "84ec26d7-5868-4c1f-ae10-14ae7cb2d25e",
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
        },
        status=200,
    )
    return responses


@pytest.fixture
def mock_sku2_unhappy_response(responses):
    b2b_url = (
        "http://localhost:8010/api/v1/public/skus/c6603522-9922-46f7-86ca-1f134095ff9f"
    )
    responses.add(
        method=responses.GET,
        url=b2b_url,
        json={
            "id": "c6603522-9922-46f7-86ca-1f134095ff9f",
            "product_id": "84ec26d7-5868-4c1f-ae10-14ae7cb2d25e",
            "name": "sku 1",
            "price": 10,
            "discount": 0,
            "cost_price": 10,
            "stock_quantity": 10,
            "active_quantity": 0,
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
        },
        status=200,
    )
    return responses

@pytest.fixture
def mock_products_happy_response(responses):
    b2b_url = "http://localhost:8010/api/v1/public/products/batch"
    responses.add(
        method=responses.POST,
        url=b2b_url,
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
                "id": "84ec26d7-5868-4c1f-ae10-14ae7cb2d25e",
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

@pytest.fixture
def mock_products_unhappy_response(responses):
    b2b_url = "http://localhost:8010/api/v1/public/products/batch"
    responses.add(
        method=responses.POST,
        url=b2b_url,
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
                "id": "84ec26d7-5868-4c1f-ae10-14ae7cb2d25e",
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
