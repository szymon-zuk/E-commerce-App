from django.contrib import admin
from .models import Product, ProductCategory, Order, OrderItem
from django.contrib.auth.models import User

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(Order)
admin.site.register(OrderItem)
