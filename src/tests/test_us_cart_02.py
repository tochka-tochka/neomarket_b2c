import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import patch
from src.models.subscriptions import ProductSubscription


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_id():
    return str(uuid.uuid4())


@pytest.fixture
def product_id():
    return str(uuid.uuid4())


def make_b2b_product(product_id):
    return {
        'id': product_id,
        'name': 'Test Product',
        'slug': 'test-product',
        'min_price': 10000,
        'has_stock': True,
        'images': [],
    }


@pytest.mark.django_db
def test_subscribe_returns_201_with_notify_on(api_client, user_id, product_id):

    with patch('src.views.subscriptions.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.subscriptions.get_product_card') as mock_product:

        mock_jwt.return_value = user_id
        mock_product.return_value = make_b2b_product(product_id)

        response = api_client.post(
            f'/api/v1/favorites/{product_id}/subscribe',
            {'events': ['BACK_IN_STOCK', 'PRICE_DROP']},
            format='json'
        )

    assert response.status_code == 204
    sub = ProductSubscription.objects.get(user_id=user_id, product_id=product_id)
    assert set(sub.events) == {'BACK_IN_STOCK', 'PRICE_DROP'}


@pytest.mark.django_db
def test_duplicate_subscription_returns_409(api_client, user_id, product_id):

    ProductSubscription.objects.create(
        user_id=user_id,
        product_id=product_id,
        events=['BACK_IN_STOCK'],
    )

    with patch('src.views.subscriptions.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.subscriptions.get_product_card') as mock_product:

        mock_jwt.return_value = user_id
        mock_product.return_value = make_b2b_product(product_id)

        response = api_client.post(
            f'/api/v1/favorites/{product_id}/subscribe',
            {'events': ['BACK_IN_STOCK']},
            format='json'
        )

    assert response.status_code == 409
    assert response.data['code'] == 'SUBSCRIPTION_ALREADY_EXISTS'
    assert ProductSubscription.objects.filter(user_id=user_id, product_id=product_id).count() == 1


@pytest.mark.django_db
def test_invalid_notify_on_returns_400(api_client, user_id, product_id):

    with patch('src.views.subscriptions.get_user_id_from_jwt') as mock_jwt:
        mock_jwt.return_value = user_id

        response = api_client.post(
            f'/api/v1/favorites/{product_id}/subscribe',
            {'events': ['INVALID_EVENT']},
            format='json'
        )

    assert response.status_code == 400
    assert response.data['code'] == 'INVALID_NOTIFY_ON'
    assert ProductSubscription.objects.filter(user_id=user_id, product_id=product_id).count() == 0


@pytest.mark.django_db
def test_subscribe_to_unknown_product_returns_404(api_client, user_id, product_id):

    with patch('src.views.subscriptions.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.subscriptions.get_product_card') as mock_product:

        mock_jwt.return_value = user_id
        mock_product.return_value = None

        response = api_client.post(
            f'/api/v1/favorites/{product_id}/subscribe',
            {'events': ['BACK_IN_STOCK']},
            format='json'
        )

    assert response.status_code == 404
    assert response.data['code'] == 'PRODUCT_NOT_FOUND'
    assert ProductSubscription.objects.filter(user_id=user_id, product_id=product_id).count() == 0