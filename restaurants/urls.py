from django.urls import path

from .views import (CreateRestaurantAPIView, GetCurrentDayMenuAPIView,
                    RestaurantListAPIView, UploadMenuAPIView)

app_name = "restaurant"

urlpatterns = [
    path("create/", CreateRestaurantAPIView.as_view(), name="create-restaurant"),
    path("upload-menu/", UploadMenuAPIView.as_view(), name="upload-menu"),
    path("restaurants/", RestaurantListAPIView.as_view(), name="restaurant-list"),
    path(
        "get-current-day-menus/",
        GetCurrentDayMenuAPIView.as_view(),
        name="get-current-day-menu",
    ),
]
