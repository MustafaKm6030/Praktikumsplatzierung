from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """Admin interface for Schools."""

    list_display = [
        "name",
        "school_type",
        "city",
        "district",
        "zone",
        "opnv_code",
        "is_active",
    ]
    list_filter = ["school_type", "zone", "district", "is_active"]
    search_fields = ["name", "city", "district"]
    fieldsets = (
        ("Basic Information", {"fields": ("name", "school_type", "is_active")}),
        ("Location", {"fields": ("city", "district")}),
        ("Zones & Travel (From CSV)", {"fields": ("zone", "opnv_code", "distance_km")}),
        (
            "Data Lineage",
            {"fields": ("csv_schulart", "csv_schulort"), "classes": ("collapse",)},
        ),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
    )
