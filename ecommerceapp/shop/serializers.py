from rest_framework import serializers
from .models import Product
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
from copy import deepcopy


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductDetailsSerializer(serializers.ModelSerializer):
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

            # Kopiowanie obrazu przed zastosowaniem thumbnail
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
