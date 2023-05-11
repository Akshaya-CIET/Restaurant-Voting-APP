from rest_framework import serializers

from .models import Menu, Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
            "description",
            "address",
            "phone_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UploadMenuSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False)
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())

    class Meta:
        model = Menu
        fields = ["restaurant", "file"]


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "restaurant", "file", "votes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
