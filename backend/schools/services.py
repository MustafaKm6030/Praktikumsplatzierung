from .models import School
from praktikums_lehrkraft.models import PraktikumsLehrkraft


def get_schools_by_zone(zone):
    return School.objects.filter(zone=zone, is_active=True)


def get_schools_by_type(school_type):
    return School.objects.filter(school_type=school_type, is_active=True)


def get_school_capacity(school_id: int) -> dict:
    """
    Calculates the dynamic capacity of a school by summing the capacities
    of all active mentors assigned to it.
    """
    active_pls = PraktikumsLehrkraft.objects.filter(school_id=school_id, is_active=True)

    total_capacity = 0
    for pl in active_pls:
        total_capacity += pl.capacity

    return {
        "school_id": school_id,
        "active_mentors": active_pls.count(),
        "total_available_slots": total_capacity,
    }


def get_schools_for_wednesday_praktika():
    """
    Returns all schools that are logistically feasible for Wednesday internships (SFP/ZSP).

    Business Logic (from slides):
    - Must be in Zone 1 or Zone 2.
    - Must have a valid ÖPNV code ('4a' or '4b').
    """
    return School.objects.filter(
        zone__in=[1, 2], opnv_code__in=["4a", "4b"], is_active=True
    )
