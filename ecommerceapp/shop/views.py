from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import Product
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductRetrieveUpdateDestroySerializer,
)
from .permissions import IsSellerOrAdmin
from rest_framework.parsers import MultiPartParser, FormParser


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "category__name", "description", "price"]
    ordering_fields = ["name", "category__name", "price"]


class ProductDetailsView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [IsSellerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(
            image=self.request.data.get("image"),
            thumbnail=self.request.data.get("thumbnail"),
        )


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductRetrieveUpdateDestroySerializer
    permission_classes = [IsSellerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        serializer.save(
            image=self.request.data.get("image"),
            thumbnail=self.request.data.get("thumbnail"),
        )
