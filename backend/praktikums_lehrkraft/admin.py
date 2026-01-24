from django.contrib import admin
from .models import PraktikumsLehrkraft


@admin.register(PraktikumsLehrkraft)
class PraktikumsLehrkraftAdmin(admin.ModelAdmin):
    """Admin interface for Praktikumslehrkräfte."""

    list_display = [
        "last_name",
        "first_name",
        "school",
        "program",
        "anrechnungsstunden",
        "capacity",
        "is_active",
        "history_pdp1",
        "history_pdp2",
        "history_sfp",
        "history_zsp",
    ]
    list_filter = ["program", "is_active", "school__school_type"]
    search_fields = ["first_name", "last_name", "email", "school__name"]
    filter_horizontal = ["available_praktikum_types", "available_subjects"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("first_name", "last_name", "email", "phone", "csv_id")},
        ),
        ("School Assignment", {"fields": ("school", "program", "main_subject")}),
        (
            "Capabilities",
            {
                "fields": (
                    "available_praktikum_types",
                    "preferred_praktika_raw",
                    "available_subjects",
                )
            },
        ),
        ("Capacity & Budget", {"fields": ("anrechnungsstunden", "schulamt")}),
        (
            "Constraints & Overrides",
            {
                "fields": (
                    "current_year_notes",
                    "is_active",
                    "notes",
                ),
                "classes": ("collapse",),
            },
        ),
    )
