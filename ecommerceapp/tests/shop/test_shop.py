import pytest
from rest_framework.reverse import reverse

from shop.models import Product


@pytest.mark.django_db
def test_product_list_view(client, product_data):
    url = reverse("product-list")
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.data) == Product.objects.count()
    for product_entry, expected_product_data in response.data:
        assert product_entry["id"] == expected_product_data["id"]
        assert product_entry["name"] == expected_product_data["name"]
        assert product_entry["description"] == expected_product_data["description"]
        assert product_entry["price"] == expected_product_data["price"]
        assert product_entry["image"] == expected_product_data["image"]
        assert product_entry["thumbnail"] == expected_product_data["thumbnail"]
        assert product_entry["category"] == expected_product_data["category"]
