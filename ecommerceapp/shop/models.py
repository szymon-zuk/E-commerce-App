from django.db import models
from django_resized import ResizedImageField
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/product_images/", null=True, blank=True)
    thumbnail = ResizedImageField(
        size=[200, 200], upload_to="media/product_thumbnails/", null=True, blank=True
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_address = models.TextField()
    products = models.ManyToManyField(Product, through="OrderItem")
    order_date = models.DateTimeField(auto_now_add=True)
    payment_due_date = models.DateTimeField()
    aggregate_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} - Customer {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
