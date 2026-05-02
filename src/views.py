import logging
import traceback
import uuid
from typing import Literal

from django.http import JsonResponse
from rest_framework.views import APIView

from src.services.categories.get import get_category, get_tree_categories


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
