# backend/assignments/admin.py
from django.contrib import admin
from .models import Assignment, StudentAssignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = "mentor", "practicum_type", "subject", "school", "academic_year"
    list_filter = "practicum_type", "academic_year", "school__school_type"
    search_fields = "mentor__last_name", "school__name", "subject__name"


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "mentor",
        "practicum_type",
        "subject",
        "school",
        "assignment_status",
        "assignment_date",
    ]
    list_filter = [
        "assignment_status",
        "practicum_type",
        "academic_year",
        "assignment_date",
    ]
    search_fields = [
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "mentor__last_name",
        "school__name",
    ]
    readonly_fields = ["assignment_date", "created_at", "updated_at"]
    
    fieldsets = (
        (
            "Assignment Details",
            {
                "fields": (
                    "student",
                    "mentor",
                    "school",
                    "practicum_type",
                    "subject",
                )
            },
        ),
        (
            "Status & Timeline",
            {
                "fields": (
                    "assignment_status",
                    "assignment_date",
                    "academic_year",
                )
            },
        ),
        ("Additional Information", {"fields": ("notes",)}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
