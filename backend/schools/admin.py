from django.contrib import admin
from django.contrib import messages
from .models import School
from .services import geocode_school
import time


def geocode_selected_schools(modeladmin, request, queryset):
    """Admin action to geocode selected schools."""
    schools_to_geocode = queryset.filter(geocoding_status__in=["pending", "failed"])
    count = schools_to_geocode.count()
    
    if count == 0:
        modeladmin.message_user(
            request,
            "No schools selected that need geocoding (must be 'pending' or 'failed' status).",
            messages.WARNING
        )
        return
    
    success = 0
    failed = 0
    
    for school in schools_to_geocode:
        if geocode_school(school):
            success += 1
        else:
            failed += 1
        time.sleep(1.1)
    
    modeladmin.message_user(
        request,
        f"Geocoding complete: {success} successful, {failed} failed out of {count} schools.",
        messages.SUCCESS if failed == 0 else messages.WARNING
    )

geocode_selected_schools.short_description = "Geocode selected schools"


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
        "geocoding_status",
        "has_coordinates",
        "is_active",
    ]
    list_filter = ["school_type", "zone", "district", "geocoding_status", "is_active"]
    search_fields = ["name", "city", "district"]
    actions = [geocode_selected_schools]
    
    fieldsets = (
        ("Basic Information", {"fields": ("name", "school_type", "is_active")}),
        ("Location", {"fields": ("city", "district")}),
        ("Zones & Travel (From CSV)", {"fields": ("zone", "opnv_code", "distance_km")}),
        ("Geocoding", {"fields": ("latitude", "longitude", "geocoding_status")}),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
    )
    
    def has_coordinates(self, obj):
        """Display if school has coordinates."""
        return bool(obj.latitude and obj.longitude)
    has_coordinates.short_description = "Has Coords"
    has_coordinates.boolean = True