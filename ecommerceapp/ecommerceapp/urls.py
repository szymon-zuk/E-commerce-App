"""
URL configuration for ecommerceapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from shop.views import (
    ProductListView,
    ProductDetailsView,
    ProductCreateView,
    ProductRetrieveUpdateDestroyView,
    OrderCreateView,
    OrderProductsStatisticsView,
    OrderListView,
)
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("dj_rest_auth.urls")),
    path("accounts/register/", include("dj_rest_auth.registration.urls")),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("product/<int:pk>/", ProductDetailsView.as_view(), name="product-details"),
    path("product/create/", ProductCreateView.as_view(), name="create-product"),
    path(
        "product/modify/<int:pk>/",
        ProductRetrieveUpdateDestroyView.as_view(),
        name="retrieve-update-delete-product",
    ),
    path("order/create/", OrderCreateView.as_view(), name="create-order"),
    path(
        "order/statistics/",
        OrderProductsStatisticsView.as_view(),
        name="order-statistics",
    ),
    path("order/list/", OrderListView.as_view(), name="order-list"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/docs/",
        SpectacularSwaggerView.as_view(),
        name="swagger-documentation",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
