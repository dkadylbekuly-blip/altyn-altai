from django.contrib import admin
from .models import Mineral


@admin.register(Mineral)
class MineralAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "category", "created_at")
    search_fields = ("title", "slug", "formula", "description")
    list_filter = ("category",)
    ordering = ("title",)