from django.urls import path

from src import views

urlpatterns = [
    path("categories", views.CategoriesView.as_view()),
    path("categories/<uuid:id>", views.CategoryView.as_view())
]
