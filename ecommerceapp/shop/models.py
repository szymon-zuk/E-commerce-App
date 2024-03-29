from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ProductCategory(models.Model):
    """
    Model representing a product category.
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model representing a single product.
    """

    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/", null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to="product_thumbnails/", null=True, blank=True
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Model representing an order in relation to customer and products it contains.
    """

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    products = models.ManyToManyField(Product, through="OrderItem")
    order_date = models.DateTimeField(auto_now_add=True)
    payment_due_date = models.DateTimeField()
    aggregate_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return f"Order {self.id} - Customer {self.customer}"


class OrderItem(models.Model):
    """
    Model representing the quantity and specific products included in an order.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
