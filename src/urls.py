from django.urls import path

from src import views

urlpatterns = [
    path("categories", views.CategoriesView.as_view()),
    path("categories/<uuid:id>", views.CategoryView.as_view()),
    path("categories/<uuid:id>/filters", views.CategoryFilterView.as_view()),
    path("catalog/facets", views.CatalogFacets.as_view())
]
