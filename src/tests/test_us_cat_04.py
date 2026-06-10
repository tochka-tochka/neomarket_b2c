import pytest
import uuid
from rest_framework.test import APIClient
from unittest.mock import Mock, patch
import src.views.catalog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def product_id():
    return str(uuid.uuid4())


@pytest.fixture
def category_id():
    return str(uuid.uuid4())


@pytest.mark.django_db
def test_similar_returns_up_to_8_from_same_category(api_client, product_id, category_id):

    mock_similar_response_data = [
        {
            "id": str(uuid.uuid4()),
            "title": f"Similar Product {i}",
            "slug": f"similar-product-{i}",
            "min_price": 1000 + i * 100,
            "has_stock": True,
            "images": [
                {"id": str(uuid.uuid4()), "url": f"https://cdn.neomarket.ru/img{i}.jpg", "ordering": 0}
            ],
            "category": {
                "id": category_id,
                "name": "Electronics",
                "level": 1,
                "path": ["Electronics"]
            },
            "seller": {
                "id": str(uuid.uuid4()),
                "display_name": "Test Seller"
            }
        }
        for i in range(1, 9)
    ]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_similar_response_data

    with patch.object(src.views.catalog, 'get_similar_products', return_value=mock_response):
        url = f'/api/v1/catalog/products/{product_id}/similar'
        response = api_client.get(url, {'limit': 8})

    assert response.status_code == 200
    assert len(response.json()) <= 8
    assert all(item['id'] != product_id for item in response.json())


@pytest.mark.django_db
def test_empty_category_returns_200_empty_list(api_client, product_id):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = []

    with patch.object(src.views.catalog, 'get_similar_products', return_value=mock_response):
        url = f'/api/v1/catalog/products/{product_id}/similar'
        response = api_client.get(url)

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_unknown_product_returns_404(api_client, product_id):

    mock_response = Mock()
    mock_response.status_code = 404

    with patch.object(src.views.catalog, 'get_similar_products', return_value=mock_response):
        url = f'/api/v1/catalog/products/{product_id}/similar'
        response = api_client.get(url)

    assert response.status_code == 404
