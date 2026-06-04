import uuid

import requests.exceptions
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from src.errors import NeomarketServiceError, NeomarketRequestError, NeomarketNotFoundError
from src.services.catalog.facets import get_catalog_facets
from src.services.catalog.products import get_catalog_products
from src.services.catalog.utils import parse_query_filters
from src.services.categories.get import get_breadcrumbs


class CatalogProductsView(APIView):
    def get(self, request: Request):
        try:
            products = get_catalog_products(
                limit=request.query_params.get("limit", 20),
                offset=request.query_params.get("offset", 0),
                q=request.query_params.get("q", ""),
                sort=request.query_params.get("sort", "price_asc"),
                filters=parse_query_filters("filter", request.query_params)
            )
        except requests.exceptions.ConnectionError:
            raise NeomarketServiceError("Category service temporarily unavailable", "B2B_UNAVAILABLE")
        except ValueError as e:
            raise NeomarketRequestError(str(e), "BAD_PARAM")
        return JsonResponse(
            products,
            safe=False
        )


class CatalogFacetsView(APIView):
    def get(self, request):
        category_id = request.GET.get('category_id')
        filters = parse_query_filters('filter', request.GET)
        return JsonResponse(get_catalog_facets(category_id, filters), safe=False)


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
