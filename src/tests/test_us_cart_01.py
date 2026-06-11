import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import patch
from src.models.favorite import Favorite


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
        'old_price': None,
        'has_stock': True,
        'rating': 4.5,
        'reviews_count': 10,
        'images': [],
        'category': None,
        'seller': None,
    }


@pytest.mark.django_db
def test_add_to_favorites_returns_201(api_client, user_id, product_id):
    """PUT /favorites/{product_id} — добавление по контракту возвращает 204"""

    with patch('src.views.favorite.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.favorite.get_products_batch') as mock_b2b:

        mock_jwt.return_value = user_id
        mock_b2b.return_value = {product_id: make_b2b_product(product_id)}

        response = api_client.put(f'/api/v1/favorites/{product_id}')

    assert response.status_code == 204
    assert Favorite.objects.filter(user_id=user_id, product_id=product_id).count() == 1


@pytest.mark.django_db
def test_repeat_add_returns_200_not_duplicate(api_client, user_id, product_id):
    """Повторное добавление по контракту → 204, в БД одна запись"""

    Favorite.objects.create(user_id=user_id, product_id=product_id)

    with patch('src.views.favorite.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.favorite.get_products_batch') as mock_b2b:

        mock_jwt.return_value = user_id
        mock_b2b.return_value = {product_id: make_b2b_product(product_id)}

        response = api_client.put(f'/api/v1/favorites/{product_id}')

    assert response.status_code == 204
    assert Favorite.objects.filter(user_id=user_id, product_id=product_id).count() == 1


@pytest.mark.django_db
def test_blocked_product_excluded_from_list(api_client, user_id, product_id):

    Favorite.objects.create(user_id=user_id, product_id=product_id)

    with patch('src.views.favorite.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.favorite.get_products_batch') as mock_b2b:

        mock_jwt.return_value = user_id
        mock_b2b.return_value = {}

        response = api_client.get('/api/v1/favorites')

    assert response.status_code == 200
    assert response.data['items'] == []
    assert response.data['total_count'] == 1
    assert response.data['limit'] == 20
    assert response.data['offset'] == 0


@pytest.mark.django_db
def test_user_id_from_query_is_ignored(api_client, user_id, product_id):

    other_user_id = str(uuid.uuid4())
    Favorite.objects.create(user_id=user_id, product_id=product_id)

    with patch('src.views.favorite.get_user_id_from_jwt') as mock_jwt, \
         patch('src.views.favorite.get_products_batch') as mock_b2b:

        mock_jwt.return_value = user_id
        mock_b2b.return_value = {product_id: make_b2b_product(product_id)}

        response = api_client.get(f'/api/v1/favorites?user_id={other_user_id}')

    assert response.status_code == 200
    assert len(response.data['items']) == 1
    assert response.data['items'][0]['id'] == product_id
