import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from restaurants.models import Menu, Restaurant
from restaurants.serializers import (MenuSerializer, RestaurantSerializer,
                                     UploadMenuSerializer)
from user_profiles.models import UserProfile


class CreateRestaurantAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_restaurant(self):
        url = reverse("restaurant:create-restaurant")
        data = {
            "name": "Restaurant Hill View",
            "description": "Since 1978. Serves Lebanss food",
            "address": "al quiyada, dubai, UAE",
            "phone_number": "+971567678900",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 1)
        restaurant = Restaurant.objects.get()
        self.assertEqual(restaurant.name, "Restaurant Hill View")

    def test_create_restaurant_missing_fields(self):
        url = reverse("restaurant:create-restaurant")
        data = {}  # Missing required fields
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Restaurant.objects.count(), 0)


class RestaurantListAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_get_restaurant_list(self):
        Restaurant.objects.create(name="Restaurant 1")
        Restaurant.objects.create(name="Restaurant 2")
        url = reverse("restaurant:restaurant-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class UploadMenuAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        file_content = b"Mock file content"
        self.file = SimpleUploadedFile(
            "menu.pdf", file_content, content_type="application/pdf"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_upload_menu(self):
        url = reverse("restaurant:upload-menu")
        data = {
            "restaurant": self.restaurant.id,
            "file": self.file,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.count(), 1)
        menu = Menu.objects.get()
        self.assertEqual(menu.restaurant, self.restaurant)

    def test_upload_menu_already_uploaded(self):
        Menu.objects.create(
            restaurant=self.restaurant, created_at=datetime.date.today()
        )
        url = reverse("restaurant:upload-menu")
        data = {
            "restaurant": self.restaurant.id,
            # Add other required fields for UploadMenuSerializer here
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Menu.objects.count(), 1)


class GetCurrentDayMenuAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.menu1 = Menu.objects.create(
            restaurant=Restaurant.objects.create(name="Restaurant 1"),
            created_at=datetime.date.today(),
        )
        self.menu2 = Menu.objects.create(
            restaurant=Restaurant.objects.create(name="Restaurant 2"),
            created_at=datetime.date.today(),
        )

    def test_get_current_day_menu(self):
        url = reverse("restaurant:get-current-day-menu")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        serializer = MenuSerializer([self.menu1, self.menu2], many=True)
        self.assertListEqual(response.data["data"], serializer.data)
