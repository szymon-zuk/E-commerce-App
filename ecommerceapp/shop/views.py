from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, filters, status, serializers
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
from celery import shared_task
from celery.utils.log import get_task_logger
from .tasks import send_email_task


class ProductListView(generics.ListAPIView):
    """
    List all products with search, ordering, and pagination capabilities.

    Parameters:
    - `name` (str): Search for products by name.
    - `category__name` (str): Search for products by category name.
    - `description` (str): Search for products by description.
    - `price` (str): Search for products by price.

    Returns:
    - `List[ProductSerializer]`: A list of product details.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "category__name", "description", "price"]
    ordering_fields = ["name", "category__name", "price"]


class ProductDetailsView(generics.RetrieveAPIView):
    """
    Retrieve details of a specific product.

    Parameters:
    - `pk` (int): The primary key of the product.

    Returns:
    - `ProductSerializer`: Details of the specified product.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductCreateView(generics.CreateAPIView):
    """
    Create a new product, accessible to sellers and admins only.

    Parameters:
    - `name` (str): The name of the product.
    - `description` (str): The description of the product.
    - `price` (decimal): The price of the product.
    - `category` (int): The primary key of the product category.
    - `image` (file): The image file of the product.
    - `thumbnail` (file): The thumbnail image file of the product.

    Returns:
    - `ProductCreateSerializer`: Details of the created product.
    """

    serializer_class = ProductCreateSerializer
    permission_classes = [IsSellerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """
        Perform the creation of a new product and handle image and thumbnail uploads.

        Parameters:
        - `serializer` (ProductCreateSerializer): The serializer instance.

        Returns:
        - None
        """
        serializer.save(
            image=self.request.data.get("image"),
            thumbnail=self.request.data.get("thumbnail"),
        )


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a product, accessible to sellers and admins only.

    Parameters:
    - `pk` (int): The primary key of the product.

    Returns:
    - `ProductRetrieveUpdateDestroySerializer`: Details of the specified product.
    """

    queryset = Product.objects.all()
    serializer_class = ProductRetrieveUpdateDestroySerializer
    permission_classes = [IsSellerOrAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def perform_update(self, serializer):
        """
        Perform the update of a product and handle image and thumbnail uploads.

        Parameters:
        - `serializer` (ProductRetrieveUpdateDestroySerializer): The serializer instance.

        Returns:
        - None
        """
        serializer.save(
            image=self.request.data.get("image"),
            thumbnail=self.request.data.get("thumbnail"),
        )


class OrderCreateView(generics.CreateAPIView):
    """
    Create a new order, accessible to authenticated users.

    Parameters:
    - `first_name` (str): The first name of the customer.
    - `last_name` (str): The last name of the customer.
    - `delivery_address` (str): The delivery address for the order.
    - `products` (List[Dict[str, Union[int, Product]]]): List of products and quantities. Example products input:
    [{"products": 2, "quantity": 1}, {"products": 1, "quantity":2}]

    Returns:
    - `Response`: Order creation status and details.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def calculate_aggregate_price(self, order):
        """
        Calculate the aggregate price of an order based on its items.

        Parameters:
        - `order` (Order): The order instance.

        Returns:
        - float: The aggregate price of the order.
        """
        total_price = 0
        order_items = OrderItem.objects.filter(order=order)

        for order_item in order_items:
            product_price = order_item.product.price
            total_price += product_price * order_item.quantity

        return total_price

    def send_confirmation_email(self, order):
        """
        Send an order confirmation email to the user.

        Parameters:
        - `order` (Order): The order instance.

        Returns:
        - None
        """
        subject = "Order Confirmation"
        html_message = render_to_string("confirmation_email.html", {"order": order})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [self.request.user.email]

        send_email_task.delay(
            subject,
            plain_message,
            from_email,
            to_email,
            html_message=html_message,
        )

    def send_payment_reminder_email(self, order):
        subject = "Payment reminder"
        html_message = render_to_string("payment_reminder_email.html", {"order": order})
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [self.request.user.email]

        send_email_task.apply_async(
            args=(subject, plain_message, from_email, to_email),
            kwargs={"html_message": html_message},
            eta=order.payment_due_date - timezone.timedelta(days=1),
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new order and send a confirmation email to the user.

        Parameters:
        - `request` (Request): The HTTP request.

        Returns:
        - `Response`: {
                "status": "Order created successfully",
                "aggregate_price": order.aggregate_price,
                "payment_due_date": order.payment_due_date,
            }
        """
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
        self.send_payment_reminder_email(order)

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
    """
    List all orders, accessible to sellers and admins only.

    Returns:
    - `OrderListSerializer`: A list of order details.
    """

    serializer_class = OrderListSerializer
    permission_classes = [IsSellerOrAdmin]
    queryset = Order.objects.all()


class OrderProductsStatisticsView(APIView):
    """
    Calculate and retrieve statistics on the most ordered products within a specified date range.

    Parameters:
    - `start_date` (date): The start date of the analysis period.
    - `end_date` (date): The end date of the analysis period.
    - `number_of_products` (int): The number of top products to retrieve.

    Returns:
    - `Response`: {
        "product_name": (str) The name of the product,
        "total_orders": (int) The total number of orders for the product,
    }
    """

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
