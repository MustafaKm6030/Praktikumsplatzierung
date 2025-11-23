from django.db.models import Q, Count
from .models import PraktikumsLehrkraft


def get_pls_by_school(school_id):
    """
    Returns all PLs for a specific school.
    Business Logic: Filter active PLs by school for assignment.
    """
    return PraktikumsLehrkraft.objects.filter(
        school_id=school_id, is_active=True
    ).select_related("school", "main_subject")


def get_pls_by_program(program):
    """
    Returns all PLs for a specific program (GS or MS).
    Business Logic: Filter PLs by program for student matching.
    """
    return PraktikumsLehrkraft.objects.filter(
        program=program, is_active=True
    ).select_related("school", "main_subject")


def search_pls(search_term):
    """Search PLs by name, school name, or PL ID."""
    query = (
        Q(first_name__icontains=search_term)
        | Q(last_name__icontains=search_term)
        | Q(email__icontains=search_term)
        | Q(school__name__icontains=search_term)
    )

    if search_term.isdigit():
        query |= Q(id=int(search_term))

    return (
        PraktikumsLehrkraft.objects.filter(query)
        .select_related("school", "main_subject")
        .distinct()
    )


def get_available_pls_for_praktikum(praktikum_type_id, subject_id=None):
    """
    Returns PLs available for a specific praktikum type and optionally subject.
    """
    queryset = PraktikumsLehrkraft.objects.filter(
        is_active=True, available_praktikum_types__id=praktikum_type_id
    )

    # Optional subject filter: PL must have this subject in their 'x' list
    if subject_id:
        queryset = queryset.filter(available_subjects__id=subject_id)

    return queryset.select_related("school", "main_subject").distinct()


def get_pl_capacity_info(pl_id):
    """
    Returns capacity information for a PL based on Anrechnungsstunden.
    """
    pl = PraktikumsLehrkraft.objects.get(id=pl_id)
    return {
        "anrechnungsstunden": float(pl.anrechnungsstunden),
        "total_capacity": pl.capacity,
        "current_assignments": 0,  # Placeholder for future assignment count
        "remaining_capacity": pl.capacity,  # Placeholder
    }


def get_pls_by_subject(subject_id, praktikum_type_id=None):
    """
    Returns PLs who can teach a specific subject (have 'x' in that column).
    """
    return (
        PraktikumsLehrkraft.objects.filter(
            available_subjects__id=subject_id, is_active=True
        )
        .select_related("school", "main_subject")
        .distinct()
    )
