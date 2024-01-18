from datetime import datetime

from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, filters, status, serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Order, OrderItem
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductRetrieveUpdateDestroySerializer,
    OrderSerializer,
    ProductStatsInputSerializer,
    ProductStatsSerializer,
    OrderListSerializer,
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        delivery_address = serializer.validated_data["delivery_address"]
        products_data = serializer.validated_data["products"]
        user_first_name = serializer.validated_data["first_name"]
        user_last_name = serializer.validated_data["last_name"]

        payment_due_date = timezone.now() + timezone.timedelta(days=5)

        if (
            user_first_name == self.request.user.first_name
            and user_last_name == self.request.user.last_name
        ):
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
        else:
            raise serializers.ValidationError("Incorrect first name or last name.")

        self.send_confirmation_email(order)

        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "status": "Order created successfully",
                "aggregate_price": order.aggregate_price,
                "payment_due_date": order.payment_due_date,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsSellerOrAdmin]
    queryset = Order.objects.all()


class OrderProductsStatisticsView(APIView):
    permission_classes = [IsSellerOrAdmin]
    serializer_class = ProductStatsInputSerializer
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=ProductStatsInputSerializer,
        responses={200: ProductStatsSerializer(many=True)},
    )
    def post(self, request):
        input_serializer = ProductStatsInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        start_date = input_serializer.validated_data["start_date"]
        end_date = input_serializer.validated_data["end_date"]
        number_of_products = input_serializer.validated_data["number_of_products"]

        most_ordered_products = (
            OrderItem.objects.filter(order__order_date__range=(start_date, end_date))
            .values("product__name")
            .annotate(total_orders=Count("product"))
            .order_by("-total_orders")[:number_of_products]
        )
        result_data = [
            {
                "product_name": product_stat["product__name"],
                "total_orders": product_stat["total_orders"],
            }
            for product_stat in most_ordered_products
        ]

        return Response(result_data, status=status.HTTP_200_OK)
