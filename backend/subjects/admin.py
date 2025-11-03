from django.contrib import admin
from .models import PraktikumType, Subject


@admin.register(PraktikumType)
class PraktikumTypeAdmin(admin.ModelAdmin):
    """Admin interface for Praktikum Types."""
    list_display = [
        'code', 
        'name', 
        'is_block_praktikum',
        'is_active'
    ]
    list_filter = ['is_block_praktikum', 'is_active']
    search_fields = ['code', 'name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for Subjects."""
    list_display = ['code', 'name', 'subject_group', 'is_active']
    list_filter = ['subject_group', 'is_active']
    search_fields = ['code', 'name']
