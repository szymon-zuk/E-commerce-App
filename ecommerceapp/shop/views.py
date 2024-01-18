import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework import generics, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Product, Order, OrderItem
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductRetrieveUpdateDestroySerializer,
    OrderSerializer,
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


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def calculate_aggregate_price(self, order):
        total_price = 0
        order_items = OrderItem.objects.filter(order=order)

        for order_item in order_items:
            product_price = order_item.product.price
            total_price += product_price * order_item.quantity

        return total_price

    def send_confirmation_email(self, order):
        subject = "Order Confirmation"
        html_message = render_to_string("confirmation_email.html", {"order": order})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [self.request.user.email]

        send_mail(
            subject,
            plain_message,
            from_email,
            to_email,
            html_message=html_message,
            fail_silently=False,
        )

    def perform_create(self, serializer):
        delivery_address = serializer.validated_data["delivery_address"]
        products_data = serializer.validated_data["products"]

        payment_due_date = datetime.datetime.now() + datetime.timedelta(days=5)

        order = Order.objects.create(
            customer=self.request.user,
            delivery_address=delivery_address,
            payment_due_date=payment_due_date,
        )

        for product_data in products_data:
            product = product_data["product"]
            quantity = product_data["quantity"]

            if isinstance(product, Product):
                product_instance = product
            else:
                product_instance = Product.objects.get(pk=product)

            OrderItem.objects.create(
                order=order, product=product_instance, quantity=quantity
            )

        order.aggregate_price = self.calculate_aggregate_price(order)
        order.save()

        self.send_confirmation_email(order)

        return order
