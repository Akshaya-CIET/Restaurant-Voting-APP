from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from restaurants.models import Menu
from user_profiles.models import Employee


class Vote(models.Model):
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="acquired_votes"
    )
    votes = models.IntegerField(default=1)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    voted_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Votes for Menu {self.menu.id} by Employee {self.employee.id}"
