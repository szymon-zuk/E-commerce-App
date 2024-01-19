import pytest
from users.models import UserRole
from shop.models import ProductCategory, Product
from rest_framework.test import APIClient
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def client(user_seller):
    refresh = RefreshToken.for_user(user_seller)
    access_token = str(refresh.access_token)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    return client


@pytest.fixture
def user_customer():
    return UserRole.objects.create_user(
        username="testcustomer",
        email="testemail@gmail.com",
        password="test12345",
        role="customer",
    )


@pytest.fixture
def user_seller():
    return UserRole.objects.create(
        username="testseller",
        email="testemail@gmail.com",
        password="test12345",
        role="seller",
    )


@pytest.fixture
def user_admin():
    return UserRole.objects.create(
        username="testadmin",
        email="testemail@gmail.com",
        password="test12345",
        role="admin",
    )


@pytest.fixture
def product_category():
    category_instance = ProductCategory.objects.create(id=1, name="Test Category")
    return category_instance


@pytest.fixture
def product(client, product_category):
    product_instance = Product.objects.create(
        id=1,
        name="Test Product",
        description="Test Description",
        price="10.99",
        category=product_category,
    )
    return product_instance


@pytest.fixture
def order_data(user):
    return {
        "customer": user,
        "products": [{"product": 1, "quantity": 1}, {"product": 2, "quantity": 2}],
        "delivery_address": "Test Address",
        "payment_due_date": "2024-01-31T12:00:00Z",
        "aggregate_price": 20.99,
    }


@pytest.fixture
def order(order_data, product):
    order_instance = Order.objects.create(**order_data)
    OrderItem.objects.create(order=order_instance, product=product, quantity=2)
    return order_instance


@pytest.fixture
def product_serializer(product_data):
    # Return a serialized representation of the product data
    return ProductSerializer(product_data).data
