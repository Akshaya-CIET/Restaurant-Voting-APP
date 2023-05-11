from django.contrib import admin

from .models import Menu, Restaurant


class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "phone_number",
        "address",
        "created_at",
    )


class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "file", "votes", "created_at")


admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Menu, MenuAdmin)
