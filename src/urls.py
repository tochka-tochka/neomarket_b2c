from django.urls import path

from src.services.catalog.views import CatalogFacetsView
from src.services.catalog.views import CatalogProductsView
from src.services.categories.views import CategoryView, CategoryFilterView, CategoriesView

urlpatterns = [
    path("categories", CategoriesView.as_view()),
    path("categories/<uuid:id>", CategoryView.as_view()),
    path("categories/<uuid:id>/filters", CategoryFilterView.as_view()),
    path("catalog/facets", CatalogFacetsView.as_view()),
    path("catalog/products", CatalogProductsView.as_view())
]
