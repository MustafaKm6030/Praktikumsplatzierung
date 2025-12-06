# backend/assignments/admin.py
from django.contrib import admin
from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = "mentor", "practicum_type", "subject", "school", "academic_year"
    list_filter = "practicum_type", "academic_year", "school__school_type"
    search_fields = "mentor__last_name", "school__name", "subject__name"
