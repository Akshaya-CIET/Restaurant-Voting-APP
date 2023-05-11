from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Employee, Organization, Role, UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "tokens"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    employee_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "user",
            "role",
            "organization",
            "date_of_joining",
            "created_by",
        ]
