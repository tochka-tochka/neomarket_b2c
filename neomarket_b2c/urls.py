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
from src.views.reg import RegisterView
from src.views.category import CategoriesView, CategoryView, CategoryFilterView
from src.views.orders import OrdersView, OrdersDetailView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/reg', RegisterView.as_view(), name='register'),
    path('api/v1/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/login/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    path("api/v1/categories", CategoriesView.as_view()),
    path("api/v1/categories/<uuid:id>", CategoryView.as_view()),
    path("api/v1/categories/<uuid:id>/filters", CategoryFilterView.as_view()),

    path("api/v1/orders", OrdersView.as_view(), name="orders"),
    path("api/v1/orders/<uuid:id>", OrdersDetailView.as_view(), name="order-detail"),
]
