from django.contrib import admin
from .models import Student, StudentPraktikumPreference


class StudentPraktikumPreferenceInline(admin.TabularInline):
    """Inline for Student Praktikum Preferences."""
    model = StudentPraktikumPreference
    extra = 1
    filter_horizontal = ['preferred_subjects', 'preferred_schools']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Students."""
    list_display = [
        'student_id',
        'last_name',
        'first_name',
        'program',
        'primary_subject'
    ]
    list_filter = ['program', 'primary_subject']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    filter_horizontal = ['additional_subjects']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'student_id', 'first_name', 'last_name',
                'email', 'phone'
            )
        }),
        ('Program & Subjects', {
            'fields': (
                'program', 'major', 'enrollment_date',
                'primary_subject', 'additional_subjects'
            )
        }),
        ('Geographical Information', {
            'fields': (
                'home_address', 'home_region', 'preferred_zone'
            )
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(StudentPraktikumPreference)
class StudentPraktikumPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for Student Praktikum Preferences."""
    list_display = ['student', 'praktikum_type', 'status']
    list_filter = ['praktikum_type', 'status']
    search_fields = ['student__student_id', 'student__last_name']
    filter_horizontal = ['preferred_subjects', 'preferred_schools']
