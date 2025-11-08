from django.contrib import admin
from .models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """Admin interface for Schools."""
    list_display = [
        'name',
        'school_type',
        'district',
        'opnv_zone',
        'is_active'
    ]
    list_filter = ['school_type', 'opnv_zone', 'district', 'is_active']
    search_fields = ['name', 'city', 'district']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'school_type', 'is_active')
        }),
        ('Location', {
            'fields': (
                'address', 'city', 'district',
                'latitude', 'longitude'
            )
        }),
        ('Zones & Travel', {
            'fields': (
                'opnv_zone', 'travel_time_minutes'
            )
        }),
        ('Capacity', {
            'fields': (
                'max_block_praktikum_slots',
                'max_wednesday_praktikum_slots'
            )
        }),
        ('Contact', {
            'fields': ('contact_person', 'phone', 'email')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
