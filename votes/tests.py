from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from restaurants.models import Menu, Restaurant
from restaurants.serializers import MenuSerializer
from user_profiles.models import Employee, Organization, Role, UserProfile

from .models import Vote


class VoteMenuAPIViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data
        self.user = UserProfile.objects.create(username="tester@example.com")
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.menu = Menu.objects.create(restaurant=self.restaurant, votes=0)
        self.organization = Organization.objects.create(name="Test org")
        self.role = Role.objects.create(name="Test org")
        self.employee = Employee.objects.create(
            employee_id="tester",
            user=self.user,
            organization_id=self.organization.id,
            role_id=self.role.id,
        )

        # Create and set the token for authentication
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_vote_single_menu(self):
        url = reverse("vote-menu")
        headers = {"HTTP_BUILD_VERSION": "old"}  # Add the build_version header

        data = {
            "menu_id": self.menu.id,
            "employee_id": self.employee.id,
        }

        response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Vote recorded successfully"})

        # Verify the vote record and menu votes count
        self.assertTrue(
            Vote.objects.filter(
                menu=self.menu, employee_id=self.employee.id, voted_date=date.today()
            ).exists()
        )
        self.menu.refresh_from_db()
        self.assertEqual(self.menu.votes, 1)

    def test_vote_multiple_menus(self):
        url = reverse("vote-menu")
        headers = {"HTTP_BUILD_VERSION": "new"}  # Add the build_version header
        menu1 = Menu.objects.create(restaurant=self.restaurant, votes=5)
        menu2 = Menu.objects.create(restaurant=self.restaurant, votes=3)
        menu3 = Menu.objects.create(restaurant=self.restaurant, votes=5)

        data = {
            "votes": [
                {"menu_id": menu1.id, "points": 1},
                {"menu_id": menu2.id, "points": 2},
                {"menu_id": menu3.id, "points": 3},
            ],
            "employee_id": self.employee.id,
        }

        response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Votes recorded successfully"})

        # Verify the vote records and menu votes count
        self.assertTrue(
            Vote.objects.filter(
                menu=menu1.id, employee_id=self.employee.id, voted_date=date.today()
            ).exists()
        )
        menu1.refresh_from_db()
        self.assertEqual(menu1.votes, 6)

    def test_vote_invalid_menu_id(self):
        url = reverse("vote-menu")
        headers = {"HTTP_BUILD_VERSION": "old"}  # Add the build_version header

        data = {
            "menu_id": 999,  # Invalid menu ID
            "employee_id": self.employee.id,
        }

        response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid menu ID"})

    def test_vote_invalid_employee_id(self):
        url = reverse("vote-menu")
        headers = {"HTTP_BUILD_VERSION": "old"}  # Add the build_version header

        data = {
            "menu_id": self.menu.id,
            "employee_id": 999,  # Invalid employee ID
        }

        response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Provide a valid employee ID"})

    def test_vote_results_for_current_day(self):
        # Create multiple menus for the current day
        menu1 = Menu.objects.create(restaurant=self.restaurant, votes=5)
        menu2 = Menu.objects.create(restaurant=self.restaurant, votes=3)
        menu3 = Menu.objects.create(restaurant=self.restaurant, votes=5)

        url = reverse("winning-menu")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = MenuSerializer([menu1, menu3], many=True).data
        self.assertEqual(response.data, expected_data)
