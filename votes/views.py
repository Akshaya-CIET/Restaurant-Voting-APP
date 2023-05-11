from datetime import date

from django.db.models import F, Max
from rest_framework import generics, status, versioning
from rest_framework.response import Response
from rest_framework.views import APIView

from restaurants.models import Menu
from restaurants.serializers import MenuSerializer
from user_profiles.models import Employee

from .models import Vote


class VoteMenuAPIView(generics.GenericAPIView):
    serializer_class = MenuSerializer
    versioning_class = versioning.AcceptHeaderVersioning

    def post(self, request, format=None):
        # Check the 'Build-Version' header in the request
        build_version = request.META.get("HTTP_BUILD_VERSION")

        # Process the request based on the build version
        if build_version == "old":
            return self.vote_single_menu(request)
        elif build_version == "new":
            return self.vote_multiple_menus(request)

        # Return an error response for invalid API version
        return Response(
            {"error": "Invalid API version"}, status=status.HTTP_400_BAD_REQUEST
        )

    def vote_single_menu(self, request):
        # Get the menu ID and employee ID from the request data
        menu_id = request.data.get("menu_id")
        employee_id = request.data.get("employee_id")

        # Retrieve the menu instance with the given menu ID
        menu = Menu.objects.filter(id=menu_id).first()

        # Check if the menu exists
        if not menu:
            return Response(
                {"error": "Invalid menu ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the employee exists
        if not Employee.objects.filter(id=employee_id).exists():
            return Response(
                {"error": "Provide a valid employee ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the employee has already voted for the current day and menu
        if Vote.objects.filter(
            menu=menu, employee_id=employee_id, voted_date=date.today()
        ).exists():
            return Response(
                {"error": "You have already voted for this menu today"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Increment the votes count for the menu
        menu.votes = F("votes") + 1
        menu.save()

        # Create a vote record for the employee
        Vote.objects.create(menu=menu, employee_id=employee_id)

        return Response(
            {"message": "Vote recorded successfully"}, status=status.HTTP_200_OK
        )

    def vote_multiple_menus(self, request):
        # Get the vote data and employee ID from the request data
        vote_data = request.data.get("votes")
        employee_id = request.data.get("employee_id")

        # Check if the vote data is valid
        if not isinstance(vote_data, list) or len(vote_data) != 3:
            return Response(
                {"error": "Invalid vote data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the employee exists
        if not Employee.objects.filter(id=employee_id).exists():
            return Response(
                {"error": "Provide a valid employee ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Process each vote in the vote data
        for vote in vote_data:
            menu_id = vote.get("menu_id")
            points = vote.get("points")

            # Check if the vote data is valid
            if (
                not menu_id
                or not points
                or not isinstance(points, int)
                or points < 1
                or points > 3
            ):
                return Response(
                    {"error": "Invalid vote data"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Retrieve the menu instance with the given menu ID
            menu = Menu.objects.filter(id=menu_id).first()

            # Check if the menu exists
            if not menu:
                return Response(
                    {"error": "Invalid menu ID"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the employee has already voted for the current day and menu
            if Vote.objects.filter(
                menu=menu, employee_id=employee_id, voted_date=date.today()
            ).exists():
                return Response(
                    {"error": "You have already voted for this menu today"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Increment the votes count for the menu
            menu.votes = F("votes") + points
            menu.save()

            # Create a vote record for the employee
            Vote.objects.create(menu=menu, employee_id=employee_id)

        return Response(
            {"message": "Votes recorded successfully"}, status=status.HTTP_200_OK
        )


class VoteResultsForCurrentDayAPIView(APIView):
    def get(self, request):
        # Get the menu with the maximum votes for the current day
        max_votes = Menu.objects.filter(created_at__date=date.today()).aggregate(
            Max("votes")
        )["votes__max"]

        # Retrieve the highly voted menus for the current day
        highly_voted_menus = Menu.objects.filter(
            created_at__date=date.today(), votes=max_votes
        )

        if highly_voted_menus.exists():
            # Serialize the highly voted menus
            serializer = MenuSerializer(highly_voted_menus, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "msg": "No winning menu found for the current day.",
                    "data": None,
                    "success": False,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
