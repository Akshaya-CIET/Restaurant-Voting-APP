from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_profiles.models import UserProfile


class RegisterAPIViewTest(APITestCase):
    def test_register_user(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "testuser@123",
            "phone_number": "+971504414746",
            "address": "Al Qiyada, Dubai",
            "first_name": "Tester1",
            "last_name": "user",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("token", response.data)
        self.assertEqual(UserProfile.objects.count(), 1)
        user = UserProfile.objects.get()
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testuser@123"))
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_register_user_missing_fields(self):
        url = reverse("register")
        data = {}  # Missing required fields
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(UserProfile.objects.count(), 0)


class LoginAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword",
        )

    def test_login(self):
        url = reverse("login")
        data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        url = reverse("login")
        data = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)


class LogoutAPIViewTest(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.token = Token.objects.create(user=self.user)

    def test_logout(self):
        url = reverse("logout")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"Message": "User logged out successfully"})
        self.assertFalse(Token.objects.filter(user=self.user).exists())
