import pytest
import responses
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status

from src.models.orders import Order, OrderItem, OrderStatus
from src.tests.fixtures import test_address, test_payment_method


@pytest.fixture
def mock_b2b_unreserve():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        b2b_url = "http://localhost:8010/api/v1/inventory/unreserve"
        rsps.add(
            method=responses.POST,
            url=b2b_url,
            json={
                "unreserved": True,
                "items": [
                    {
                        "sku_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                        "unreserved_quantity": 2,
                        "remaining_stock": 10,
                    },
                    {
                        "sku_id": "8a4e3f9c-1a2b-4c8d-9e5f-6b7a8c9d0e1f",
                        "unreserved_quantity": 1,
                        "remaining_stock": 5,
                    },
                ],
            },
            status=200,
        )
        yield rsps


@pytest.fixture
def order(request, test_user, test_address, test_payment_method):

    status = getattr(request, "param", OrderStatus.PAID)

    order = Order.objects.create(
        address=test_address,
        number="ORD-SKU",
        payment_method=test_payment_method,
        status=status,
        buyer=test_user,
    )
    OrderItem.objects.create(
        id="00000000-0000-0000-0000-000000000000",
        order=order,
        sku_id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
        product_id="00000000-0000-0060-0000-000000000000",
        name="test_name",
        quantity=2,
        unit_price=10,
        line_total=20,
        image_url="some_bucket/1.png",
    )
    OrderItem.objects.create(
        id="00000000-0000-0000-0000-000000000001",
        order=order,
        sku_id="8a4e3f9c-1a2b-4c8d-9e5f-6b7a8c9d0e1f",
        product_id="00000200-0000-0000-0000-000000000000",
        name="test_name",
        quantity=1,
        unit_price=10,
        line_total=10,
        image_url="some_bucket/1.png",
    )
    return order


@pytest.mark.django_db
class TestCancelOrder:
    def test_cancel_paid_order_transitions_to_cancelled(
        self, jwt_client, order, mock_b2b_unreserve
    ):

        url = reverse("order-detail", args=[order.id])

        response = jwt_client.delete(url)

        order.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert order.status == OrderStatus.CANCELED

    def test_unreserve_failure_transitions_to_cancel_pending(self, jwt_client, order):

        url = reverse("order-detail", args=[order.id])

        response = jwt_client.delete(url)

        order.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert order.status == OrderStatus.CANCEL_PENDING

    @pytest.mark.parametrize("order", [OrderStatus.DELIVERED], indirect=True)
    def test_cancel_assembling_order_returns_409(
        self, jwt_client, order, mock_b2b_unreserve
    ):

        url = reverse("order-detail", args=[order.id])

        response = jwt_client.delete(url)

        order.refresh_from_db()
        assert response.status_code == status.HTTP_409_CONFLICT, response.json()
        assert response.json()["current_status"] == OrderStatus.DELIVERED
        assert order.status == OrderStatus.DELIVERED

    def test_user_order_returns_404(self, jwt_client, mock_b2b_unreserve, test_address, test_payment_method):
        another_buyer = User.objects.create(
            username="another_user", email="another@example.com", password="12345"
        )
        order = Order.objects.create(
            address=test_address,
            number="ORD-SKU",
            payment_method=test_payment_method,
            status=status,
            buyer=another_buyer,
        )

        url = reverse("order-detail", args=[order.id])

        response = jwt_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
