from address.models import AddressField
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        verbose_name=_("Name"), unique=True, max_length=50, blank=True, null=True
    )

    description = models.TextField(verbose_name=_("Description"))

    phone_number = PhoneNumberField(
        verbose_name=_("Phone number"), blank=True, null=True
    )
    address = models.TextField(verbose_name=_("Address"), blank=True, null=True)

    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = _("Restaurants")

    def __str__(self):
        return self.name


class Menu(models.Model):
    restaurant = models.ForeignKey(
        Restaurant, null=False, blank=False, on_delete=models.CASCADE
    )

    file = models.FileField(upload_to="menus/")

    votes = models.IntegerField(default=0)

    created_at = models.DateTimeField(verbose_name=_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Updated at"), auto_now=True)

    def __str__(self):
        return f"Menu-{self.id}"
