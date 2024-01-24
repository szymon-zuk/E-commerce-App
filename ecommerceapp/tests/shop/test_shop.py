from datetime import timedelta
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.utils import json
from shop.models import Product, Order
from unittest.mock import Mock


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture",
    ["client_customer", "client_seller", "client_admin", "client_unauthenticated"],
)
@pytest.mark.parametrize("expected_status_code", [status.HTTP_200_OK])
def test_product_list_view(request, client_fixture, product, expected_status_code):
    client = request.getfixturevalue(client_fixture)

    url = reverse("product-list")
    response = client.get(url)

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        assert len(response.data) == Product.objects.count()

        for product_entry in response.data:
            assert product_entry["id"] == product.id
            assert product_entry["name"] == product.name
            assert product_entry["description"] == product.description
            assert product_entry["price"] == product.price
            assert product_entry["image"] == product.image
            assert product_entry["thumbnail"] == product.thumbnail
            assert product_entry["category"] == product.category.id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture",
    ["client_customer", "client_seller", "client_admin", "client_unauthenticated"],
)
@pytest.mark.parametrize("expected_status_code", [status.HTTP_200_OK])
def test_product_detail_view(request, product, client_fixture, expected_status_code):
    client = request.getfixturevalue(client_fixture)

    url = reverse("product-details", kwargs={"pk": product.id})
    response = client.get(url)

    assert response.status_code == expected_status_code
    assert response.data["id"] == product.id
    assert response.data["name"] == product.name
    assert response.data["description"] == product.description
    assert response.data["price"] == product.price
    assert response.data["image"] == product.image
    assert response.data["thumbnail"] == product.thumbnail
    assert response.data["category"] == product.category.id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_403_FORBIDDEN),
        ("client_seller", status.HTTP_201_CREATED),
        ("client_admin", status.HTTP_201_CREATED),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_product_create_view(
    request, client_fixture, product_category, expected_status_code
):
    client = request.getfixturevalue(client_fixture)

    url = reverse("create-product")

    payload = {
        "name": "New Product",
        "description": "Product description",
        "price": "29.99",
        "category": product_category.id,
    }

    response = client.post(url, data=payload)

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_201_CREATED:
        assert response.data["name"] == payload["name"]
        assert response.data["description"] == payload["description"]
        assert response.data["price"] == payload["price"]
        assert response.data["category"] == product_category.id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_403_FORBIDDEN),
        ("client_seller", status.HTTP_200_OK),
        ("client_admin", status.HTTP_200_OK),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_product_update_view_method_get(
    request, client_fixture, product, expected_status_code
):
    client = request.getfixturevalue(client_fixture)
    url = reverse("retrieve-update-delete-product", kwargs={"pk": product.id})
    response = client.get(url)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_403_FORBIDDEN),
        ("client_seller", status.HTTP_200_OK),
        ("client_admin", status.HTTP_200_OK),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_product_update_view_method_put(
    request, client_fixture, product, expected_status_code, product_category
):
    client = request.getfixturevalue(client_fixture)
    url = reverse("retrieve-update-delete-product", kwargs={"pk": product.id})
    payload = {
        "name": "New Product",
        "description": "Product description",
        "price": "29.99",
        "category": product_category.id,
    }
    response = client.put(url, data=payload)
    assert response.status_code == expected_status_code


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_403_FORBIDDEN),
        ("client_seller", status.HTTP_204_NO_CONTENT),
        ("client_admin", status.HTTP_204_NO_CONTENT),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_product_update_view_method_delete(
    request, client_fixture, product, expected_status_code
):
    client = request.getfixturevalue(client_fixture)
    url = reverse("retrieve-update-delete-product", kwargs={"pk": product.id})
    response = client.delete(url)
    assert response.status_code == expected_status_code
    if expected_status_code == status.HTTP_204_NO_CONTENT:
        assert not Product.objects.filter(id=product.id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_201_CREATED),
        ("client_seller", status.HTTP_201_CREATED),
        ("client_admin", status.HTTP_201_CREATED),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_order_create_view(
    request, client_fixture, expected_status_code, product, product2, order_data, mocker
):
    client = request.getfixturevalue(client_fixture)
    url = reverse("create-order")
    initial_order_count = Order.objects.count()
    payload = {
        "first_name": "test",
        "last_name": "test",
        "delivery_address": "test delivery address",
        "products": [{"product": 2, "quantity": 1}, {"product": 1, "quantity": 1}],
    }
    mocker.patch("common.email_handler.EmailHandler.send_confirmation_email", Mock())
    mocker.patch(
        "common.email_handler.EmailHandler.send_payment_reminder_email", Mock()
    )
    response = client.post(
        url, data=json.dumps(payload), content_type="application/json"
    )
    print(response.content)
    assert response.status_code == expected_status_code
    if expected_status_code == status.HTTP_201_CREATED:
        assert response.data["status"] == "Order created successfully"
        expected_date = order_data["payment_due_date"]
        obtained_date = response.data["payment_due_date"]
        assert abs(expected_date - obtained_date) < timedelta(seconds=1)
        final_order_count = Order.objects.count()
        assert final_order_count == initial_order_count + 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_403_FORBIDDEN),
        ("client_seller", status.HTTP_200_OK),
        ("client_admin", status.HTTP_200_OK),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_order_list_view(request, client_fixture, expected_status_code):
    client = request.getfixturevalue(client_fixture)
    url = reverse("order-list")
    response = client.get(url)
    assert response.status_code == expected_status_code
    if expected_status_code == status.HTTP_200_OK:
        assert len(response.data) == Order.objects.count()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        ("client_customer", status.HTTP_403_FORBIDDEN),
        ("client_seller", status.HTTP_200_OK),
        ("client_admin", status.HTTP_200_OK),
        ("client_unauthenticated", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_order_product_statistics_view(
    request, client_fixture, expected_status_code, product, product2, order
):
    client = request.getfixturevalue(client_fixture)
    url = reverse("order-statistics")
    payload = {
        "start_date": "2020-01-01",
        "end_date": "2024-01-21",
        "number_of_products": 3,
    }
    response = client.post(url, data=payload)
    assert response.status_code == expected_status_code
