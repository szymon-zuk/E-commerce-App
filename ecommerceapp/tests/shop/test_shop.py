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
    url = reverse("create-product")

    payload = {
        "name": "New Product",
        "description": "Product description",
        "price": "29.99",
        "category": product_category.id,
    }

    response = client.post(url, data=payload)
    assert response.status_code == 201
    assert response.data["name"] == payload["name"]
    assert response.data["description"] == payload["description"]
    assert response.data["price"] == payload["price"]
    assert response.data["category"] == product_category.id


@pytest.mark.django_db
def test_product_update_view_method_get(client, product):
    url = reverse("retrieve-update-delete-product", kwargs={"pk": product.id})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_update_view_method_put(client, product, product_category):
    url = reverse("retrieve-update-delete-product", kwargs={"pk": product.id})
    payload = {
        "name": "New Product",
        "description": "Product description",
        "price": "29.99",
        "category": product_category.id,
    }
    response = client.put(url, data=payload)
    assert response.status_code == 200


@pytest.mark.django_db
def test_product_update_view_method_delete(client, product):
    url = reverse("retrieve-update-delete-product", kwargs={"pk": product.id})
    response = client.delete(url)
    assert response.status_code == 204
    assert not Product.objects.filter(id=product.id).exists()
