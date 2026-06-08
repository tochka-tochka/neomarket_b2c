import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import patch
from src.models.cart import CartItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def session_id():
    return str(uuid.uuid4())


@pytest.fixture
def sku_id():
    return str(uuid.uuid4())


@pytest.fixture
def product_id():
    return str(uuid.uuid4())


@pytest.mark.django_db
def test_add_sku_increments_quantity_if_already_in_cart(api_client, session_id, sku_id, product_id):
    """Повторное добавление того же SKU увеличивает quantity"""

    with patch('src.views.cart.get_sku_by_id') as mock_get_sku:
        mock_get_sku.return_value = {
            'id': sku_id,
            'product_id': product_id,
            'name': 'Test Product',
            'price': 10000,
            'discount': 1000,
            'active_quantity': 100,
            'article': 'TEST-001',
            'images': [],
            'characteristics': []
        }

        api_client.credentials(HTTP_X_SESSION_ID=session_id)
        url = '/api/v1/cart/items'

        response1 = api_client.post(url, {
            'sku_id': sku_id,
            'quantity': 2
        }, format='json')

        assert response1.status_code == 201
        assert response1.data['items_count'] == 2

        cart_items = CartItem.objects.filter(session_id=session_id)
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 2

        response2 = api_client.post(url, {
            'sku_id': sku_id,
            'quantity': 3
        }, format='json')

        assert response2.status_code == 200
        assert response2.data['items_count'] == 5

        cart_items = CartItem.objects.filter(session_id=session_id)
        assert cart_items.count() == 1
        assert cart_items.first().quantity == 5


@pytest.mark.django_db
def test_get_cart_enriched_with_b2b_data(api_client, session_id, sku_id, product_id):
    """GET /cart обогащает данные из B2B"""

    CartItem.objects.create(
        session_id=session_id,
        sku_id=sku_id,
        quantity=2
    )

    with patch('src.views.cart.get_skus_batch') as mock_get_skus:
        mock_get_skus.return_value = {
            sku_id: {
                'id': sku_id,
                'product_id': product_id,
                'name': 'Test SKU',
                'price': 10000,
                'discount': 1500,
                'active_quantity': 10,
                'article': 'TEST-ART-001',
                'images': [
                    {'id': 'img1', 'url': 'https://example.com/img1.jpg', 'ordering': 0}
                ],
                'characteristics': []
            }
        }

        api_client.credentials(HTTP_X_SESSION_ID=session_id)
        url = '/api/v1/cart'
        response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['id'] == session_id
    assert response.data['items_count'] == 2
    assert response.data['subtotal'] == 17000

    item = response.data['items'][0]
    assert item['sku_id'] == sku_id
    assert item['product_id'] == product_id
    assert item['name'] == 'Test SKU'
    assert item['quantity'] == 2
    assert item['unit_price'] == 8500
    assert item['line_total'] == 17000
    assert item['available_quantity'] == 10
    assert item['is_available'] is True
    assert item['sku_code'] == 'TEST-ART-001'
    assert item['image'] is not None
    assert item['image']['url'] == 'https://example.com/img1.jpg'


@pytest.mark.django_db
def test_unavailable_sku_shown_with_reason(api_client, session_id, sku_id, product_id):

    CartItem.objects.create(
        session_id=session_id,
        sku_id=sku_id,
        quantity=2
    )

    with patch('src.views.cart.get_skus_batch') as mock_get_skus:
        mock_get_skus.return_value = {
            sku_id: {
                'id': sku_id,
                'product_id': product_id,
                'name': 'Test SKU Out of Stock',
                'price': 10000,
                'discount': 1000,
                'active_quantity': 0,
                'article': 'TEST-OOS-001',
                'images': [],
                'characteristics': []
            }
        }

        api_client.credentials(HTTP_X_SESSION_ID=session_id)
        url = '/api/v1/cart'
        response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['id'] == session_id
    assert response.data['items_count'] == 2
    assert response.data['subtotal'] == 0
    assert response.data['is_valid'] is False

    item = response.data['items'][0]
    assert item['sku_id'] == sku_id
    assert item['product_id'] == product_id
    assert item['name'] == 'Test SKU Out of Stock'
    assert item['quantity'] == 2
    assert item['unit_price'] == 9000
    assert item['line_total'] == 0
    assert item['available_quantity'] == 0
    assert item['is_available'] is False



@pytest.fixture
def user_id():
    return str(uuid.uuid4())


@pytest.fixture
def sku_id_1():
    return str(uuid.uuid4())


@pytest.fixture
def sku_id_2():
    return str(uuid.uuid4())


@pytest.fixture
def product_id_1():
    return str(uuid.uuid4())


@pytest.fixture
def product_id_2():
    return str(uuid.uuid4())


@pytest.mark.django_db
def test_guest_cart_merged_on_login(api_client, session_id, user_id, sku_id_1, sku_id_2, product_id_1, product_id_2):

    CartItem.objects.create(session_id=session_id, sku_id=sku_id_1, quantity=2)
    CartItem.objects.create(session_id=session_id, sku_id=sku_id_2, quantity=1)
    CartItem.objects.create(user_id=user_id, sku_id=sku_id_2, quantity=3)

    with patch('src.views.cart.get_user_id_from_jwt') as mock_get_user, \
            patch('src.views.cart.get_session_id') as mock_get_session:
        mock_get_user.return_value = user_id
        mock_get_session.return_value = session_id

        api_client.credentials(HTTP_X_SESSION_ID=session_id)

        response = api_client.post('/api/v1/cart/merge', format='json')

    assert response.status_code == 200
    assert CartItem.objects.filter(session_id=session_id).count() == 0

    user_items = CartItem.objects.filter(user_id=user_id, session_id__isnull=True)
    assert user_items.count() == 2
    assert user_items.get(sku_id=sku_id_1).quantity == 2
    assert user_items.get(sku_id=sku_id_2).quantity == 3
