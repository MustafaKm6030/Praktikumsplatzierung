from django.contrib import admin
from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin interface for System Settings."""
    list_display = [
        'current_academic_year',
        'is_active',
        'total_anrechnungsstunden_budget'
    ]
    list_filter = ['is_active']
    fieldsets = (
        ('Academic Year', {
            'fields': ('current_academic_year', 'is_active')
        }),
        ('Budget Configuration', {
            'fields': (
                'total_anrechnungsstunden_budget',
                'gs_budget_percentage',
                'ms_budget_percentage'
            )
        }),
        ('Deadlines', {
            'fields': (
                'pdp_i_demand_deadline',
                'pl_assignment_deadline',
                'winter_semester_adjustment_date'
            )
        }),
        ('University Information', {
            'fields': (
                'university_name',
                'contact_email',
                'contact_phone'
            )
        }),
    )
