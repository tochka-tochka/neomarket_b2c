import uuid

import requests.exceptions
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from src.errors import NeomarketServiceError, NeomarketRequestError, NeomarketNotFoundError
from src.services.catalog.facets import get_catalog_facets
from src.services.catalog.products import get_catalog_products, get_similar_products, escape_search_query
from src.services.catalog.utils import parse_query_filters
from src.services.categories.get import get_breadcrumbs
from src.serializers.products import SimilarProductsSerializer


class CatalogProductsView(APIView):
    def get(self, request: Request):
        search_query = request.query_params.get("q", "")

        if search_query and len(search_query) < 3:
            return Response(
                {"code": "INVALID_REQUEST", "message": "Search query must be at least 3 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(search_query) > 200:
            return Response(
                {"code": "INVALID_REQUEST", "message": "Search query must be at most 200 characters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        safe_search = escape_search_query(search_query)

        try:
            products = get_catalog_products(
                limit=request.query_params.get("limit", 20),
                offset=request.query_params.get("offset", 0),
                q=safe_search,
                sort=request.query_params.get("sort", "price_asc"),
                filters=parse_query_filters("filter", request.query_params)
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {"code": "SERVICE_UNAVAILABLE", "message": "Catalog temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except ValueError:
            return Response(
                {"code": "INVALID_REQUEST", "message": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            products,
            status=status.HTTP_200_OK
        )


class CatalogFacetsView(APIView):
    def get(self, request):
        category_id = request.GET.get('category_id')
        filters = parse_query_filters('filter', request.GET)
        return JsonResponse(get_catalog_facets(category_id, filters), safe=False)


class SimilarProductsView(APIView):
    def get(self, request, product_id):
        try:
            limit = int(request.GET.get('limit', 10))
        except ValueError:
            limit = 10
        limit = min(limit, 8)

        try:
            response = get_similar_products(product_id, limit)
        except Exception:
            return Response(
                {"code": "SERVICE_UNAVAILABLE", "message": "Catalog temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if response.status_code == 404:
            return Response(
                {"code": "NOT_FOUND", "message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        b2b_data = response.json()

        if not b2b_data:
            return Response([], status=status.HTTP_200_OK)

        for product in b2b_data:
            if product.get('discount', 0) > 0:
                product['old_price'] = product['min_price']
                product['min_price'] = product['min_price'] - product['discount']
            else:
                product['old_price'] = None

            if 'title' in product and 'name' not in product:
                product['name'] = product.pop('title')

        serializer = SimilarProductsSerializer(data=b2b_data, many=True)

        if not serializer.is_valid():
            print(f"Validation error for similar products: {serializer.errors}")
            return Response(
                {"code": "INVALID_DATA", "message": "Invalid products data from catalog"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class BreadcrumbsView(APIView):
    def get(self, request: Request):
        category_id: uuid.UUID = request.query_params.get('category_id')
        product_id: uuid.UUID = request.query_params.get('product_id')
        if (not category_id and not product_id) or (category_id and product_id):
            raise NeomarketRequestError("only one of category_id or product_id must be provided")
        breadcrumbs = get_breadcrumbs(category_id, bool(product_id))
        if breadcrumbs is None:
            raise NeomarketNotFoundError("Product or category not found", "NOT_FOUND")
        return JsonResponse(breadcrumbs, safe=False)

