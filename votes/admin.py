from django.contrib import admin

from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("menu", "votes", "employee", "voted_date")
    list_filter = ("menu", "employee", "voted_date")
    search_fields = ("menu__restaurant__name", "employee__username")
    readonly_fields = ("menu", "votes", "employee", "voted_date")
    date_hierarchy = "voted_date"
    ordering = ("-voted_date",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
