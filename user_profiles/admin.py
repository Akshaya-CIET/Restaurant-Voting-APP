from django.contrib import admin

from .models import *

# Register your models here.


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "employee_id", "user", "organization", "role", "created_by")


admin.site.register(Employee, EmployeeAdmin)
