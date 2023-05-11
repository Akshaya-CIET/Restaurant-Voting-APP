import datetime

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Menu, Restaurant
from .serializers import (MenuSerializer, RestaurantSerializer,
                          UploadMenuSerializer)


class CreateRestaurantAPIView(APIView):
    def post(self, request):
        # Create a new restaurant

        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "msg": "Restaurant created successfully.",
                "data": serializer.data,
                "success": True,
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {"msg": serializer.errors, "data": None, "success": False}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)


class RestaurantListAPIView(generics.ListAPIView):
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        # Retrieve the list of restaurants

        return Restaurant.objects.order_by("name")


class UploadMenuAPIView(APIView):
    def post(self, request):
        # Upload a new menu for a restaurant

        today = datetime.date.today()
        restaurant_id = request.data.get("restaurant")
        menu_exists = Menu.objects.filter(
            restaurant__id=restaurant_id, created_at__date=today
        ).exists()

        if menu_exists:
            # Menu for the restaurant already exists for today
            response_data = {
                "msg": "Menu for this restaurant has already been uploaded for today.",
                "success": False,
                "data": None,
            }
            return Response(data=response_data, status=status.HTTP_200_OK)

        serializer = UploadMenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "msg": "Menu uploaded successfully.",
                "data": serializer.data,
                "success": True,
            }
            return Response(data=response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {"msg": serializer.errors, "data": None, "success": False}
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)


class GetCurrentDayMenuAPIView(APIView):
    def get(self, request):
        # Retrieve the current day's menu

        today = datetime.date.today()
        menu = Menu.objects.filter(created_at__date=today)
        serializer = MenuSerializer(menu, many=True)
        response_data = {
            "msg": "Current day's menu retrieved successfully.",
            "data": serializer.data,
            "success": True,
        }
        return Response(data=response_data, status=status.HTTP_200_OK)
