from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee, Organization, Role, UserProfile
from .serializers import EmployeeSerializer, UserProfileSerializer


class RegisterAPIView(CreateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        # Create a new user profile and generate a token

        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            user = response.data
            token, _ = Token.objects.get_or_create(user_id=user["id"])
            user["token"] = token.key
            return Response(user, status=status.HTTP_201_CREATED)
        return response


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # Authenticate user and return a token

        data = request.data
        username = data.get("username")
        password = data.get("password")
        user = get_object_or_404(UserProfile, username=username)
        if user.check_password(password):
            serializer = UserProfileSerializer(user)
            token, _ = Token.objects.get_or_create(user_id=user.id)
            return Response(
                {"user": serializer.data, "token": token.key}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # Delete user's authentication token to log them out

        request.user.auth_token.delete()
        return Response(
            {"Message": "User logged out successfully"}, status=status.HTTP_200_OK
        )


class CreateEmployeeAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        # Create a new employee

        data = request.data

        # Check if employee with the given ID already exists
        employee_id = data.get("employee_id")
        if employee_id and Employee.objects.filter(employee_id=employee_id).exists():
            error_message = f"Employee with ID {employee_id} already exists"
            return Response(
                {"msg": error_message, "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_data = data["user"]
        email = user_data["email"]
        username = user_data["username"]
        user_profile, created = UserProfile.objects.get_or_create(
            email=email, username=username
        )
        user_profile.phone_number = user_data.get(
            "phone_number", user_profile.phone_number
        )
        user_profile.address = user_data.get("address", user_profile.address)
        user_profile.save()

        role_name = data["role"]["name"]
        role, created = Role.objects.get_or_create(name=role_name)

        organization_name = data["organization"]["name"]
        organization, created = Organization.objects.get_or_create(
            name=organization_name
        )

        try:
            # Create the employee
            employee = Employee.objects.create(
                employee_id=employee_id,
                user=user_profile,
                role=role,
                organization=organization,
                date_of_joining=data.get("date_of_joining"),
                created_by=request.user,
            )
        except Exception as e:
            error_message = f"Failed to create employee: {str(e)}"
            return Response(
                {"msg": error_message, "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EmployeeSerializer(employee)
        response_data = {
            "msg": "Employee successfully created.",
            "data": serializer.data,
            "success": True,
        }
        return Response(data=response_data, status=status.HTTP_201_CREATED)
