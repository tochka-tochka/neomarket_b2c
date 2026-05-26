import logging
import re
import traceback
import uuid
from collections import defaultdict
from typing import Literal

from django.http import JsonResponse, QueryDict
from rest_framework.views import APIView

from src.services.categories.get import get_category, get_tree_categories, get_category_filter, get_catalog_facets


class CategoryView(APIView):
    def get(self, request, id: uuid.UUID):
        try:
            include_product_count: bool = request.GET.get("include_product_count") == "true"
            lang: Literal["ru", "en"] = request.GET.get("lang", "ru")
            category = get_category(id, include_product_count, lang)
            return JsonResponse(category, status=200)
        except Exception as e:
            logging.error('\n'.join(traceback.format_exception(e)))
            return JsonResponse({"message": "Category service temporarily unavailable"}, status=503)


class CategoriesView(APIView):
    def get(self, request):
        return JsonResponse(get_tree_categories(), safe=False)


class CategoryFilterView(APIView):
    def get(self, request, id: uuid.UUID):
        return JsonResponse(get_category_filter(id), safe=False)


def parse_query_filters(filter_param_name: str, query_dict: QueryDict) -> dict[str, list[str]]:
    result = defaultdict(list)
    for key in query_dict:
        r = re.search(filter_param_name + r"\[(\w+)\]", key)
        if r:
            result[r.group(1)].append(query_dict[key])

    return result


class CatalogFacets(APIView):
    def get(self, request):
        category_id = request.GET.get('category_id')
        filters = parse_query_filters('filters', request.GET)
        return JsonResponse(get_catalog_facets(category_id, filters), safe=False)
