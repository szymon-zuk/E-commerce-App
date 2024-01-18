from rest_framework import serializers
from .models import Product, Order, OrderItem
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from copy import deepcopy


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "description", "price", "category", "image")

    def create(self, validated_data):
        thumbnail_size = (200, 200)
        image = validated_data.pop("image", None)

        product = Product.objects.create(**validated_data)
        if image:
            image = Image.open(image)

            image_copy = deepcopy(image)
            image_copy.thumbnail(thumbnail_size)

            unique_id = uuid.uuid4().hex

            # Zapis miniatury
            thumbnail_io = BytesIO()
            image_copy.save(thumbnail_io, format="JPEG")
            thumbnail = InMemoryUploadedFile(
                thumbnail_io,
                None,
                f"thumbnail_{unique_id}.jpg",
                "image/jpeg",
                thumbnail_io.tell(),
                None,
            )
            product.thumbnail.save(f"thumbnail_{unique_id}.jpg", thumbnail)

            # Zapis oryginalnego obrazu
            image_io = BytesIO()
            image.save(image_io, format="JPEG")
            image = InMemoryUploadedFile(
                image_io,
                None,
                f"image_{unique_id}.jpg",
                "image/jpeg",
                image_io.tell(),
                None,
            )
            product.image.save(f"image_{unique_id}.jpg", image)

        return product


class ProductRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "description", "price", "category", "image")

    def update(self, instance, validated_data):
        thumbnail_size = (200, 200)
        image = validated_data.pop("image", None)

        old_image = instance.image
        old_thumbnail = instance.thumbnail
        if old_image:
            old_image.delete()
        if old_thumbnail:
            old_thumbnail.delete()

        # Aktualizacja pól modelu
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.price = validated_data.get("price", instance.price)
        instance.category = validated_data.get("category", instance.category)

        if image:
            image = Image.open(image)

            # Kopiowanie obrazu przed modyfikacją
            image_copy = image.copy()
            image_copy.thumbnail(thumbnail_size)

            unique_id = uuid.uuid4().hex

            # Zapis miniatury
            thumbnail_io = BytesIO()
            image_copy.save(thumbnail_io, format="JPEG")
            thumbnail = InMemoryUploadedFile(
                thumbnail_io,
                None,
                f"thumbnail_{unique_id}.jpg",
                "image/jpeg",
                thumbnail_io.tell(),
                None,
            )
            instance.thumbnail.save(f"thumbnail_{unique_id}.jpg", thumbnail)

            # Zapis oryginalnego obrazu
            image_io = BytesIO()
            image.save(image_io, format="JPEG")
            image = InMemoryUploadedFile(
                image_io,
                None,
                f"image_{unique_id}.jpg",
                "image/jpeg",
                image_io.tell(),
                None,
            )
            instance.image.save(f"image_{unique_id}.jpg", image)

        instance.save()

        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)
    delivery_address = serializers.CharField()
    products = OrderItemSerializer(many=True)
    aggregate_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    payment_due_date = serializers.DateTimeField(read_only=True)


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class ProductStatsSerializer(serializers.Serializer):
    product_name = serializers.CharField(source="product__name")
    total_orders = serializers.IntegerField()


class ProductStatsInputSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    number_of_products = serializers.IntegerField()
