import requests.exceptions
from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from src.services.catalog.facets import get_catalog_facets
from src.services.catalog.products import get_catalog_products
from src.services.catalog.utils import parse_query_filters


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
            return JsonResponse(
                {"message": "Catalog unavailable"},
                status=503,
                safe=False,
            )
        except ValueError as e:
            return JsonResponse(
                {"message": str(e)},
                status=400,
                safe=False,
            )
        return JsonResponse(
            products,
            safe=False
        )


class CatalogFacetsView(APIView):
    def get(self, request):
        category_id = request.GET.get('category_id')
        filters = parse_query_filters('filters', request.GET)
        return JsonResponse(get_catalog_facets(category_id, filters), safe=False)
