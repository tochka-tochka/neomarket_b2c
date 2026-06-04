import pytest
import responses
from src.models.user import User
from django.urls import reverse
from rest_framework import status

from src.models.orders import Order, OrderItem, OrderStatus
from src.tests.fixtures import test_address, test_payment_method


@pytest.fixture
def mock_b2b_unreserve(responses):
    b2b_url = "http://localhost:8010/api/v1/inventory/unreserve"
    responses.add(
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
    return responses


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

@pytest.fixture
def mock_b2b_connection_error(responses):
    b2b_url = "http://localhost:8010/api/v1/inventory/unreserve"
    responses.add(
        method=responses.POST,
        url=b2b_url,
        status=503
    )
    return responses


@pytest.mark.django_db
class TestCancelOrder:
    def test_cancel_paid_order_transitions_to_cancelled(
        self, jwt_client, order, mock_b2b_unreserve
    ):

        url = reverse("order-cancel", args=[order.id])

        response = jwt_client.post(url)

        order.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert order.status == OrderStatus.CANCELLED

    def test_unreserve_failure_transitions_to_cancel_pending(self, jwt_client, order, mock_b2b_connection_error):

        url = reverse("order-cancel", args=[order.id])

        response = jwt_client.post(url)

        order.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert order.status == OrderStatus.CANCEL_PENDING

    @pytest.mark.parametrize("order", [OrderStatus.DELIVERED], indirect=True)
    def test_cancel_delivered_order_returns_409(
        self, jwt_client, order
    ):

        url = reverse("order-cancel", args=[order.id])

        response = jwt_client.post(url)

        order.refresh_from_db()
        assert response.status_code == status.HTTP_409_CONFLICT, response.json()
        assert response.json()["current_status"] == OrderStatus.DELIVERED
        assert order.status == OrderStatus.DELIVERED

    def test_user_order_returns_404(self, jwt_client, test_address, test_payment_method):
        another_buyer = User.objects.create(
            username="another_user", email="another@example.com", password="12345"
        )
        order = Order.objects.create(
            address=test_address,
            number="ORD-SKU",
            payment_method=test_payment_method,
            status=OrderStatus.PAID,
            buyer=another_buyer,
        )

        url = reverse("order-cancel", args=[order.id])

        response = jwt_client.post(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
