from datetime import timedelta
import pytest
from django.utils import timezone
from users.models import UserRole
from shop.models import ProductCategory, Product, Order, OrderItem
from rest_framework.test import APIClient
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


def create_authenticated_client(user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    return client


@pytest.fixture
def client_unauthenticated():
    return APIClient()


@pytest.fixture
def client_customer(user_customer):
    return create_authenticated_client(user_customer)


@pytest.fixture
def client_seller(user_seller):
    return create_authenticated_client(user_seller)


@pytest.fixture
def client_admin(user_admin):
    return create_authenticated_client(user_admin)


@pytest.fixture
def user_customer():
    return UserRole.objects.create_user(
        username="testcustomer",
        first_name="test",
        last_name="test",
        email="testcustomer@gmail.com",
        password="test12345",
        role="customer",
    )


@pytest.fixture
def user_seller():
    return UserRole.objects.create_user(
        username="testseller",
        first_name="test",
        last_name="test",
        email="testseller@gmail.com",
        password="test12345",
        role="seller",
    )


@pytest.fixture
def user_admin():
    return UserRole.objects.create_user(
        username="testadmin",
        first_name="test",
        last_name="test",
        email="testadmin@gmail.com",
        password="test12345",
        role="admin",
    )


@pytest.fixture
def product_category():
    category_instance = ProductCategory.objects.create(id=1, name="Test Category")
    return category_instance


@pytest.fixture
def product(product_category):
    product_instance = Product.objects.create(
        id=1,
        name="Test Product",
        description="Test Description",
        price="123.12",
        category=product_category,
    )
    return product_instance


@pytest.fixture
def product2(product_category):
    product_instance = Product.objects.create(
        id=2,
        name="Test Product",
        description="Test Description",
        price="3.29",
        category=product_category,
    )
    return product_instance


@pytest.fixture
def order_data(user_customer, product, product2):
    return {
        "id": 1,
        "customer": user_customer,
        "delivery_address": "test delivery address",
        "payment_due_date": timezone.now() + timedelta(days=5),
        "aggregate_price": float(product.price) + float(product2.price),
    }


@pytest.fixture
def order(order_data, product, product2):
    order_instance = Order.objects.create(**order_data)

    OrderItem.objects.create(order=order_instance, product=product, quantity=1)
    OrderItem.objects.create(order=order_instance, product=product2, quantity=1)

    return order_instance


@pytest.fixture
def product_serializer(product_data):
    return ProductSerializer(product_data).data
