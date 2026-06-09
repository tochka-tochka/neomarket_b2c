import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import patch, Mock


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_id():
    return str(uuid.uuid4())


@pytest.fixture
def sku_id():
    return str(uuid.uuid4())


@pytest.mark.django_db
def test_product_card_returns_full_data_with_skus(api_client, product_id, sku_id):

    mock_b2b_response_data = {
        "id": product_id,
        "name": "iPhone 15 Pro Max",
        "slug": "iphone-15-pro-max",
        "description": "Флагманский смартфон с чипом A17 Pro",
        "min_price": 12999000,
        "has_stock": True,
        "images": [
            {"id": "img-1", "url": "https://cdn.neomarket.ru/iphone15.jpg", "ordering": 0}
        ],
        "attributes": {"Бренд": "Apple", "Цвет": "Черный"},
        "skus": [
            {
                "id": sku_id,
                "name": "256GB Black",
                "price": 12999000,
                "discount": 0,
                "active_quantity": 10,
                "attributes": {"Память": "256GB", "Цвет": "Черный"},
                "images": []
            }
        ]
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_b2b_response_data

    with patch('src.views.product_card.get_product_card') as mock_get_product:
        mock_get_product.return_value = mock_response

        url = f'/api/v1/catalog/products/{product_id}'
        response = api_client.get(url)

    assert response.status_code == 200

    data = response.json()
    assert data['id'] == product_id
    assert data['name'] == "iPhone 15 Pro Max"
    assert data['description'] == "Флагманский смартфон с чипом A17 Pro"
    assert data['min_price'] == 12999000
    assert data['has_stock'] is True
    assert len(data['images']) == 1
    assert len(data['skus']) == 1

    sku = data['skus'][0]
    assert sku['id'] == sku_id
    assert sku['name'] == "256GB Black"
    assert sku['price'] == 12999000
    assert sku['old_price'] is None
    assert sku['available_quantity'] == 10
    assert sku['attributes'] == {"Память": "256GB", "Цвет": "Черный"}


@pytest.mark.django_db
def test_cost_price_absent_in_response(api_client, product_id, sku_id):

    mock_b2b_response_data = {
        "id": product_id,
        "name": "Test Product",
        "description": "Test description",
        "min_price": 100000,
        "has_stock": True,
        "images": [],
        "attributes": {},
        "skus": [
            {
                "id": sku_id,
                "name": "Test SKU",
                "price": 100000,
                "discount": 0,
                "active_quantity": 5,
                "attributes": {},
                "images": []
            }
        ]
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_b2b_response_data

    with patch('src.views.product_card.get_product_card') as mock_get_product:
        mock_get_product.return_value = mock_response

        url = f'/api/v1/catalog/products/{product_id}'
        response = api_client.get(url)

    assert response.status_code == 200

    data = response.json()
    assert 'cost_price' not in data
    assert 'reserved_quantity' not in data
    assert 'cost_price' not in data['skus'][0]
    assert 'reserved_quantity' not in data['skus'][0]


@pytest.mark.django_db
def test_blocked_product_returns_404(api_client, product_id):

    mock_response = Mock()
    mock_response.status_code = 404

    with patch('src.views.product_card.get_product_card') as mock_get_product:
        mock_get_product.return_value = mock_response

        url = f'/api/v1/catalog/products/{product_id}'
        response = api_client.get(url)

    assert response.status_code == 404
    assert response.json()['code'] == 'NOT_FOUND'
    assert response.json()['message'] == 'Product not found'


@pytest.mark.django_db
def test_sku_without_stock_is_shown_as_unavailable(api_client, product_id, sku_id):

    mock_b2b_response_data = {
        "id": product_id,
        "name": "Test Product",
        "description": "Test description",
        "min_price": 100000,
        "has_stock": False,
        "images": [],
        "attributes": {},
        "skus": [
            {
                "id": sku_id,
                "name": "Out of Stock SKU",
                "price": 100000,
                "discount": 0,
                "active_quantity": 0,
                "attributes": {},
                "images": []
            }
        ]
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_b2b_response_data

    with patch('src.views.product_card.get_product_card') as mock_get_product:
        mock_get_product.return_value = mock_response

        url = f'/api/v1/catalog/products/{product_id}'
        response = api_client.get(url)

    assert response.status_code == 200

    data = response.json()
    assert len(data['skus']) == 1
    assert data['skus'][0]['available_quantity'] == 0
    assert data['has_stock'] is False
