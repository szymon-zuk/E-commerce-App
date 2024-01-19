from rest_framework import serializers
from .models import Product, Order, OrderItem
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from copy import deepcopy


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model, used for regular serialization.
    """

    class Meta:
        model = Product
        fields = "__all__"


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Product instance, including thumbnail creation logic.
    """

    class Meta:
        model = Product
        fields = ("name", "description", "price", "category", "image")

    def create(self, validated_data):
        """
        Create a new Product instance with the logic of 200x200 thumbnail generation.
        """
        thumbnail_size = (200, 200)
        image = validated_data.pop("image", None)

        product = Product.objects.create(**validated_data)
        if image:
            image = Image.open(image)

            image_copy = deepcopy(image)
            image_copy.thumbnail(thumbnail_size)

            unique_id = uuid.uuid4().hex

            # Thumbnail save
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

            # Original image save
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
    """
    Serializer for retrieving, updating, or destroying a Product instance, including image and thumbnail handling.
    """

    class Meta:
        model = Product
        fields = ("name", "description", "price", "category", "image")

    def update(self, instance, validated_data):
        """
        Update a Product instance with the functionality of updating image and generating new thumbnail.
        """
        thumbnail_size = (200, 200)
        image = validated_data.pop("image", None)

        old_image = instance.image
        old_thumbnail = instance.thumbnail
        if old_image:
            old_image.delete()
        if old_thumbnail:
            old_thumbnail.delete()

        # Model fields update
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.price = validated_data.get("price", instance.price)
        instance.category = validated_data.get("category", instance.category)

        if image:
            image = Image.open(image)

            # Creating a copy before modification
            image_copy = image.copy()
            image_copy.thumbnail(thumbnail_size)

            unique_id = uuid.uuid4().hex

            # Thumbnail save
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

            # Original image save
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
    """
    Serializer for the OrderItem model.
    """

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.Serializer):
    """
    Serializer for Order data, used for creating new orders.
    """

    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)
    delivery_address = serializers.CharField()
    products = OrderItemSerializer(many=True)
    aggregate_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    payment_due_date = serializers.DateTimeField(read_only=True)


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Order instances.
    """

    class Meta:
        model = Order
        fields = "__all__"


class ProductStatsSerializer(serializers.Serializer):
    """
    Serializer for product statistics, showing the product name and total orders of this product.
    """

    product_name = serializers.CharField(source="product__name")
    total_orders = serializers.IntegerField()


class ProductStatsInputSerializer(serializers.Serializer):
    """
    Serializer for input data required for generating product statistics.
    """

    start_date = serializers.DateField()
    end_date = serializers.DateField()
    number_of_products = serializers.IntegerField()
