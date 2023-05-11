import uuid

from address.models import AddressField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework_simplejwt.tokens import RefreshToken


class UserProfile(AbstractUser):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = PhoneNumberField(
        verbose_name=_("Phone number"), blank=True, null=True
    )
    address = models.TextField(verbose_name=_("Address"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class Role(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), unique=True, max_length=50, blank=True, null=True
    )
    responsibilities = models.TextField(
        verbose_name=_("Responsibilities"), blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="created_roles"
    )


class Organization(models.Model):
    name = models.CharField(verbose_name=_("Name"), unique=True, max_length=255)
    about = models.TextField(verbose_name=_("About"), blank=True, null=True)
    email = models.EmailField(
        max_length=255, unique=True, db_index=True, blank=True, null=True
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Phone number"), blank=True, null=True
    )
    address = AddressField(verbose_name=_("Address"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_organizations",
    )


class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    date_of_joining = models.DateField(
        verbose_name=_("Date of Joining"), blank=True, null=True
    )

    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_employees",
    )

    def __str__(self):
        return self.employee_id
