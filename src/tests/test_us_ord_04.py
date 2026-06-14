import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
from src.models.cart import CartItem
from src.models.events import ProcessedEvent
from src.models.orders import Order, OrderItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_id():
    return str(uuid.uuid4())


@pytest.fixture
def sku_id():
    return str(uuid.uuid4())


@pytest.fixture
def service_key(settings):
    settings.B2B_SERVICE_KEY = "test-service-key"
    return "test-service-key"


@pytest.fixture
def user():
    from src.models.user import User
    return User.objects.create_user(
        username=f'user_{uuid.uuid4().hex[:8]}',
        password='testpass',
    )


def make_product_response(product_id, sku_ids):
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {
        'id': product_id,
        'skus': [{'id': sku_id} for sku_id in sku_ids],
    }
    return mock


def make_event_payload(event_type, payload, idempotency_key=None):
    return {
        'event_type': event_type,
        'idempotency_key': str(idempotency_key or uuid.uuid4()),
        'occurred_at': '2025-01-01T00:00:00Z',
        'payload': payload,
    }


@pytest.mark.django_db
def test_product_blocked_marks_cart_items_unavailable(api_client, product_id, sku_id, service_key):
    CartItem.objects.create(sku_id=sku_id, user_id=uuid.uuid4())

    with patch('src.services.events.events.get_product_card') as mock_product:
        mock_product.return_value = make_product_response(product_id, [sku_id])

        response = api_client.post(
            '/api/v1/b2b/events',
            make_event_payload('PRODUCT_BLOCKED', {'product_id': product_id}),
            format='json',
            headers={'X-Service-Key': service_key},
        )

    assert response.status_code == 202
    item = CartItem.objects.get(sku_id=sku_id)
    assert item.unavailable_reason == 'PRODUCT_BLOCKED'


@pytest.mark.django_db
def test_orders_not_affected_by_product_blocked(api_client, product_id, sku_id, service_key, user):
    CartItem.objects.create(sku_id=sku_id, user_id=user.id)

    order = Order.objects.create(
        buyer=user,
        number='ORD-001',
        status='PAID',
        delivery_cost=0,
    )
    OrderItem.objects.create(
        sku_id=sku_id,
        product_id=product_id,
        name='Test Product',
        quantity=1,
        unit_price=10000,
        line_total=10000,
        image_url='',
        order=order,
    )

    with patch('src.services.events.events.get_product_card') as mock_product:
        mock_product.return_value = make_product_response(product_id, [sku_id])

        response = api_client.post(
            '/api/v1/b2b/events',
            make_event_payload('PRODUCT_BLOCKED', {'product_id': product_id}),
            format='json',
            headers={'X-Service-Key': service_key},
        )

    assert response.status_code == 202
    assert CartItem.objects.get(sku_id=sku_id).unavailable_reason == 'PRODUCT_BLOCKED'

    order.refresh_from_db()
    assert order.status == 'PAID'
    order_item = OrderItem.objects.get(sku_id=sku_id, order=order)
    assert order_item.unit_price == 10000


@pytest.mark.django_db
def test_idempotent_event_no_side_effects(api_client, product_id, sku_id, service_key):
    idempotency_key = uuid.uuid4()
    CartItem.objects.create(sku_id=sku_id, user_id=uuid.uuid4())
    ProcessedEvent.objects.create(idempotency_key=idempotency_key)

    with patch('src.services.events.events.get_product_card') as mock_product:
        mock_product.return_value = make_product_response(product_id, [sku_id])

        response = api_client.post(
            '/api/v1/b2b/events',
            make_event_payload('PRODUCT_BLOCKED', {'product_id': product_id}, idempotency_key),
            format='json',
            headers={'X-Service-Key': service_key},
        )

    assert response.status_code == 409
    mock_product.assert_not_called()
    item = CartItem.objects.get(sku_id=sku_id)
    assert item.unavailable_reason is None


@pytest.mark.django_db
def test_missing_service_key_returns_401(api_client, product_id):
    response = api_client.post(
        '/api/v1/b2b/events',
        make_event_payload('PRODUCT_BLOCKED', {'product_id': product_id}),
        format='json',
    )

    assert response.status_code == 401
