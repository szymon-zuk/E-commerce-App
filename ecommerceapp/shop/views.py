from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import Product
from .serializers import ProductListSerializer, ProductDetailsSerializer


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "category__name", "description", "price"]
    ordering_fields = ["name", "category__name", "price"]


class ProductDetailsView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer
