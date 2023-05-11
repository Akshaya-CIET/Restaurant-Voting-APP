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
        return Response(
            {"error": "Invalid API version"}, status=status.HTTP_400_BAD_REQUEST
        )

    def vote_single_menu(self, request):
        menu_id = request.data.get("menu_id")
        menu = Menu.objects.filter(id=menu_id).first()
        employee_id = request.data.get("employee_id")

        if not menu:
            return Response(
                {"error": "Invalid menu ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not Employee.objects.filter(id=employee_id).exists():
            return Response(
                {"error": "Provide a valid employee ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Vote.objects.filter(
            menu=menu, employee_id=employee_id, voted_date=date.today()
        ).exists():
            return Response(
                {"error": "You have already voted for this menu today"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        menu.votes = F("votes") + 1
        menu.save()

        # Create a vote record for the employee
        Vote.objects.create(menu=menu, employee_id=employee_id)

        return Response(
            {"message": "Vote recorded successfully"}, status=status.HTTP_200_OK
        )

    def vote_multiple_menus(self, request):
        vote_data = request.data.get("votes")
        employee_id = request.data.get("employee_id")
        if not isinstance(vote_data, list) or len(vote_data) != 3:
            return Response(
                {"error": "Invalid vote data"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not Employee.objects.filter(id=employee_id).exists():
            return Response(
                {"error": "Provide a valid employee ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for vote in vote_data:
            menu_id = vote.get("menu_id")
            points = vote.get("points")

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

            menu = Menu.objects.filter(id=menu_id).first()

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
        highly_voted_menus = Menu.objects.filter(
            created_at__date=date.today(), votes=max_votes
        )

        if highly_voted_menus.exists():
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
