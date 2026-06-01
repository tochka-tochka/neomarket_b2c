import logging
import traceback
import uuid
from typing import Literal

from django.http import JsonResponse
from rest_framework.views import APIView

from src.errors import NeomarketServiceError, NeomarketUnprocessableError
from src.services.categories.get import get_category, get_tree_categories, get_category_filter, get_flat_categories


class CategoryView(APIView):
    def get(self, request, id: uuid.UUID):
        try:
            include_product_count: bool = request.GET.get("include_product_count") == "true"
            lang: Literal["ru", "en"] = request.GET.get("lang", "ru")
            category = get_category(id, include_product_count, lang)
            return JsonResponse(category, status=200)
        except Exception as e:
            logging.error('\n'.join(traceback.format_exception(e)))
            raise NeomarketServiceError("Category service temporarily unavailable", "B2B_UNAVAILABLE")


class CategoriesView(APIView):
    def get(self, request):
        return JsonResponse(get_flat_categories(), safe=False)


class CategoriesTreeView(APIView):
    def get(self, request):
        try:
            return JsonResponse(get_tree_categories(), safe=False)
        except KeyError:
            raise NeomarketUnprocessableError("Broken category hierarchy", "BROKEN_HIERARCHY")


class CategoryFilterView(APIView):
    def get(self, request, id: uuid.UUID):
        return JsonResponse(get_category_filter(id), safe=False)
