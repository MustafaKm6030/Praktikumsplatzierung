"""
Business logic for School management.
"""
from .models import School


def get_schools_by_zone(zone):
    """
    Get schools filtered by OPNV zone.
    Business Logic: Used for geographical matching of students.
    """
    return School.objects.filter(opnv_zone=zone, is_active=True)


def get_schools_by_type(school_type):
    """
    Get schools filtered by type (GS or MS).
    Business Logic: GS students must go to GS schools.
    """
    return School.objects.filter(school_type=school_type, is_active=True)


def calculate_school_capacity(school):
    """
    Calculate available capacity for a school.
    Business Logic: Check how many slots are still available.
    """
    # TODO: Implement capacity calculation based on assignments
    return {
        'block_available': school.max_block_praktikum_slots,
        'wednesday_available': school.max_wednesday_praktikum_slots,
    }


def get_schools_within_travel_time(max_minutes):
    """
    Get schools within specified travel time from university.
    Business Logic: Used for Wednesday Praktikum restrictions.
    """
    return School.objects.filter(
        travel_time_minutes__lte=max_minutes,
        is_active=True
    )

