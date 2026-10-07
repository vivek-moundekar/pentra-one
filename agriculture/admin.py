from django.contrib import admin
from .models import Crop


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "scientific_name",
        "season",
        "is_active",
    )

    list_filter = (
        "season",
        "is_active",
    )

    search_fields = (
        "name",
        "scientific_name",
        "description",
    )