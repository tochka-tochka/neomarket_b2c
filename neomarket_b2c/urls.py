"""
URL configuration for neomarket_b2c project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from src.views.catalog import CatalogFacetsView, CatalogProductsView, BreadcrumbsView, SimilarProductsView
from src.views.reg import RegisterView
from src.views.category import CategoriesView, CategoryView, CategoryFilterView, CategoriesTreeView
from src.views.orders import OrdersView, OrdersDetailView, OrderDeleteView
from src.views.cart import CartView, CartItemView, CartValidateView, CartMergeView
from src.views.product_card import ProductCardView
from src.views.favorite import FavoritesView, FavoriteDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/reg', RegisterView.as_view(), name='register'),
    path('api/v1/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/login/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/v1/catalog/categories", CategoriesView.as_view()),
    path("api/v1/catalog/categories/tree", CategoriesTreeView.as_view()),
    path("api/v1/catalog/categories/<uuid:id>", CategoryView.as_view()),
    path("api/v1/catalog/categories/<uuid:id>/filters", CategoryFilterView.as_view()),
    path("api/v1/catalog/breadcrumbs", BreadcrumbsView.as_view()),
    path("api/v1/catalog/facets", CatalogFacetsView.as_view()),
    path("api/v1/catalog/products", CatalogProductsView.as_view()),
    path("api/v1/catalog/products/<uuid:id>", ProductCardView.as_view()),
    path("api/v1/catalog/products/<uuid:product_id>/similar", SimilarProductsView.as_view()),

    path("api/v1/orders", OrdersView.as_view(), name="orders"),
    path("api/v1/orders/<uuid:id>", OrdersDetailView.as_view(), name="order-detail"),
    path("api/v1/orders/<uuid:id>/cancel", OrderDeleteView.as_view(), name="order-cancel"),

    path("api/v1/cart", CartView.as_view()),
    path("api/v1/cart/items", CartItemView.as_view()),
    path("api/v1/cart/items/<uuid:sku_id>", CartItemView.as_view()),
    path("api/v1/cart/validate", CartValidateView.as_view()),
    path("api/v1/cart/merge", CartMergeView.as_view()),

    path("api/v1/favorites", FavoritesView.as_view()),
    path("api/v1/favorites/<uuid:product_id>", FavoriteDetailView.as_view())
]
