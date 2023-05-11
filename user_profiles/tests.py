from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class EmployeeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        url = reverse("register")
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_login(self):
        url = reverse("login")
        data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

    def test_logout(self):
        url = reverse("logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"Message": "User logged out successfully"})

    def test_create_employee(self):
        url = reverse("create-employee")
        data = {
            "employee_id": "123",
            "user": {
                "email": "employee@example.com",
                "username": "employeeuser",
                "phone_number": "1234567890",
                "address": "Employee Address",
            },
            "role": {
                "name": "Employee Role",
            },
            "organization": {
                "name": "Employee Organization",
            },
            "date_of_joining": "2023-01-01",
        }
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("data", response.data)
        self.assertIn("success", response.data)
        self.assertEqual(response.data["success"], True)

    def test_create_employee_duplicate_id(self):
        url = reverse("create-employee")
        data = {
            "employee_id": "123",
            "user": {
                "email": "employee@example.com",
                "username": "employeeuser",
            },
            "role": {
                "name": "Employee Role",
            },
            "organization": {
                "name": "Employee Organization",
            },
            "date_of_joining": "2023-01-01",
        }
        self.client.login(username="testuser", password="testpassword")
        response1 = self.client.post(url, data, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post(url, data, format="json")
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.data["success"], False)
        self.assertIn("Employee with ID 123 already exists", response2.data["msg"])
from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from user_profiles.models import Employee, Organization, Role, UserProfile


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123"
        )

        self.user_profile = UserProfile.objects.create(
            user=self.user, email="testuser@example.com", phone_number="+1234567890"
        )

    def test_user_profile_string_representation(self):
        self.assertEqual(str(self.user_profile), self.user.username)

    def test_user_profile_has_tokens_method(self):
        self.assertTrue(hasattr(self.user_profile, "tokens"))

    def test_user_profile_tokens_method_returns_tokens(self):
        tokens = self.user_profile.tokens()
        self.assertTrue("refresh" in tokens)
        self.assertTrue("access" in tokens)


class RoleTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123"
        )

        self.role = Role.objects.create(
            name="Test Role",
            responsibilities="Test Responsibilities",
            created_by=self.user,
        )

    def test_role_string_representation(self):
        self.assertEqual(str(self.role), self.role.name)


class OrganizationTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123"
        )

        self.organization = Organization.objects.create(
            name="Test Organization",
            about="Test About",
            email="testorg@example.com",
            phone_number="+1234567890",
            address={
                "street": "Test Street",
                "city": "Test City",
                "state": "Test State",
                "zip": "Test Zip",
            },
            created_by=self.user,
        )

    def test_organization_string_representation(self):
        self.assertEqual(str(self.organization), self.organization.name)


class EmployeeTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123"
        )

        self.role = Role.objects.create(
            name="Test Role",
            responsibilities="Test Responsibilities",
            created_by=self.user,
        )

        self.organization = Organization.objects.create(
            name="Test Organization",
            about="Test About",
            email="testorg@example.com",
            phone_number="+1234567890",
            address={
                "street": "Test Street",
                "city": "Test City",
                "state": "Test State",
                "zip": "Test Zip",
            },
            created_by=self.user,
        )

        self.employee = Employee.objects.create(
            user=self.user,
            role=self.role,
            organization=self.organization,
            created_by=self.user,
            date_of_joining=datetime.now(),
        )

    def test_employee_string_representation(self):
        self.assertEqual(str(self.employee), str(self.employee.employee_id))

    def test_employee_has_date_of_joining(self):
        self.assertTrue(hasattr(self.employee, "date_of_joining"))
