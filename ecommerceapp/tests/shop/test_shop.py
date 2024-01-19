import pytest
from rest_framework.reverse import reverse

from shop.models import Product


@pytest.mark.django_db
def test_product_list_view(client, product):
    url = reverse("product-list")
    response = client.get(url)
    assert response.status_code == 200
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
def test_product_detail_view(client, product):
    url = reverse("product-details", kwargs={"pk": product.id})
    response = client.get(url)
    assert response.status_code == 200
    assert response.data["id"] == product.id
    assert response.data["name"] == product.name
    assert response.data["description"] == product.description
    assert response.data["price"] == product.price
    assert response.data["image"] == product.image
    assert response.data["thumbnail"] == product.thumbnail
    assert response.data["category"] == product.category.id


@pytest.mark.django_db
def test_product_create_view(client, user_seller, product_category):
    create_product_url = reverse("create-product")

    payload = {
        "name": "New Product",
        "description": "Product description",
        "price": "29.99",
        "category": product_category.id,
    }

    response = client.post(create_product_url, data=payload)
    assert response.status_code == 201
    assert response.data["name"] == payload["name"]
    assert response.data["description"] == payload["description"]
    assert response.data["price"] == payload["price"]
    assert response.data["category"] == product_category.id
