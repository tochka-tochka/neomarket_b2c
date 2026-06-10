import pytest
from src.models.user import User
from django.urls import reverse
from rest_framework import status

from src.models.orders import Order, OrderItem, OrderStatus
from src.tests.fixtures import test_address, test_order, test_payment_method


@pytest.mark.django_db
class TestGetOrders:
    ORDERS_LIST_URL = reverse("orders")

    @pytest.fixture(autouse=True)
    def setup(self, db, api_client, test_user, test_order):
        self.client = api_client
        self.user = test_user
        self.order = test_order
        self.client.force_authenticate(user=self.user)

    def test_orders_list_returns_own_orders_paginated(
        self, test_address, test_payment_method
    ):
        Order.objects.create(
            buyer=self.user,
            number="ORD-SKU-001",
            status=OrderStatus.PAID,
            address=test_address,
            payment_method=test_payment_method,
        )
        Order.objects.create(
            buyer=self.user,
            number="ORD-SKU-002",
            status=OrderStatus.PAID,
            address=test_address,
            payment_method=test_payment_method,
        )

        response = self.client.get(f"{self.ORDERS_LIST_URL}?limit=2&offset=0")
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert "items" in response.json()
        assert len(response.json()["items"]) == 2

        response = self.client.get(f"{self.ORDERS_LIST_URL}?limit=2&offset=2")
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert "items" in response.json()
        assert len(response.json()["items"]) == 1

    def test_order_detail_shows_prices_from_order_item_unit_price(self):
        response = self.client.get(reverse("order-detail", args=[self.order.id]))
        assert response.status_code == status.HTTP_200_OK
        order_data = response.json()
        assert "items" in order_data
        for item in order_data["items"]:
            order_item = OrderItem.objects.get(sku_id=item["sku_id"])
            assert float(item["unit_price"]) == float(order_item.unit_price)
            order_item.unit_price = 101020
            order_item.save()

        response = self.client.get(reverse("order-detail", args=[self.order.id]))
        assert response.status_code == status.HTTP_200_OK, response.json()
        order_data = response.json()
        assert "items" in order_data
        for item in order_data["items"]:
            order_item = OrderItem.objects.get(sku_id=item["sku_id"])
            assert float(item["unit_price"]) == float(order_item.unit_price)

    def test_other_user_order_returns_404_not_403(
        self, test_address, test_payment_method
    ):
        test_second_user = User.objects.create(username="test", password="test")
        other_user_order = Order.objects.create(
            buyer=test_second_user,
            number="ORD-OTHER-USER",
            status=OrderStatus.PAID,
            address=test_address,
            payment_method=test_payment_method,
        )

        response = self.client.get(reverse("order-detail", args=[other_user_order.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
        assert response.json()["code"] == "NOT_FOUND"
        assert response.json()["message"] == "Order not found"
