from django.contrib import admin
from .models import PraktikumsLehrkraft, PLSubjectAvailability


class PLSubjectAvailabilityInline(admin.TabularInline):
    """Inline for PL Subject Availability in PL Admin."""
    model = PLSubjectAvailability
    extra = 1
    autocomplete_fields = ['subject', 'praktikum_type']


@admin.register(PraktikumsLehrkraft)
class PraktikumsLehrkraftAdmin(admin.ModelAdmin):
    """Admin interface for Praktikumslehrkräfte."""
    list_display = [
        'last_name',
        'first_name',
        'school',
        'program',
        'is_available'
    ]
    list_filter = ['program', 'is_available', 'school__school_type']
    search_fields = ['first_name', 'last_name', 'email', 'school__name']
    filter_horizontal = ['available_praktikum_types']
    inlines = [PLSubjectAvailabilityInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('School Assignment', {
            'fields': ('school', 'program', 'main_subject')
        }),
        ('Praktikum Availability', {
            'fields': ('available_praktikum_types',)
        }),
        ('Administrative', {
            'fields': ('schulamt',)
        }),
        ('Capacity', {
            'fields': (
                'max_students_per_praktikum',
                'max_simultaneous_praktikum'
            )
        }),
        ('Special Notes', {
            'fields': ('besonderheiten', 'is_available', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PLSubjectAvailability)
class PLSubjectAvailabilityAdmin(admin.ModelAdmin):
    """Admin interface for PL Subject Availability matrix."""
    list_display = ['pl', 'subject', 'praktikum_type', 'is_available']
    list_filter = ['praktikum_type', 'is_available', 'subject']
    search_fields = ['pl__last_name', 'pl__first_name', 'subject__name']
    autocomplete_fields = ['pl', 'subject', 'praktikum_type']
