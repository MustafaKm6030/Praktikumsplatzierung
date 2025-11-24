from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Students."""

    list_display = [
        "student_id",
        "last_name",
        "first_name",
        "program",
        "primary_subject",
        "placement_status",
    ]
    list_filter = ["program", "placement_status", "primary_subject"]
    search_fields = ["student_id", "first_name", "last_name", "email"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("student_id", "first_name", "last_name", "email", "phone")},
        ),
        (
            "Program & Subjects",
            {"fields": ("program", "major", "enrollment_date", "primary_subject")},
        ),
        (
            "Internship Checklist",
            {
                "fields": (
                    "pdp1_completed_date",
                    "pdp2_completed_date",
                    "sfp_completed_date",
                    "zsp_completed_date",
                    "placement_status",
                )
            },
        ),
        ("Location", {"fields": ("home_address", "semester_address", "home_region")}),
        ("Notes", {"fields": ("notes",), "classes": ("collapse",)}),
    )
