from django.urls import path

from .views import (CreateEmployeeAPIView, LoginAPIView, LogoutAPIView,
                    RegisterAPIView)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("create-employee/", CreateEmployeeAPIView.as_view(), name="create-employee"),
]
