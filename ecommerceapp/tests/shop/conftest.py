import pytest
from users.models import UserRole
from shop.models import ProductCategory, Product
from rest_framework.test import APIClient

client = APIClient()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user_customer():
    return UserRole.objects.create(
        username="test",
        email="testemail@gmail.com",
        password="test1234",
        role="customer",
    )


@pytest.fixture
def user_customer():
    return UserRole.objects.create(
        username="test", email="testemail@gmail.com", password="test1234", role="seller"
    )


@pytest.fixture
def user_customer():
    return UserRole.objects.create(
        username="test", email="testemail@gmail.com", password="test1234", role="admin"
    )


@pytest.fixture
def product_category_data():
    return {"name": "Test Category"}


@pytest.fixture
def product_category(product_category_data):
    category_instance = ProductCategory.objects.create(**product_category_data)
    return category_instance


@pytest.fixture
def product_data(product_category):
    return {
        "name": "Test Product",
        "description": "Test Description",
        "price": 10.99,
        "category": product_category,
    }


@pytest.fixture
def product(client, product_data):
    product_instance = Product.objects.create(**product_data)
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
