from django.db.models import Q, Count
from .models import PraktikumsLehrkraft, PLSubjectAvailability


def get_pls_by_school(school_id):
    """
    Returns all PLs for a specific school.
    Business Logic: Filter active PLs by school for assignment.
    """
    return PraktikumsLehrkraft.objects.filter(
        school_id=school_id,
        is_available=True
    ).select_related('school', 'main_subject')


def get_pls_by_program(program):
    """
    Returns all PLs for a specific program (GS or MS).
    Business Logic: Filter PLs by program for student matching.
    """
    return PraktikumsLehrkraft.objects.filter(
        program=program,
        is_available=True
    ).select_related('school', 'main_subject')


def search_pls(search_term):
    """
    Search PLs by name, school name, or PL ID.
    Business Logic: Enables flexible search across multiple fields.
    """
    query = Q(first_name__icontains=search_term) | \
            Q(last_name__icontains=search_term) | \
            Q(email__icontains=search_term) | \
            Q(school__name__icontains=search_term)
    
    # Add ID search only if search term is a digit
    if search_term.isdigit():
        query |= Q(id=int(search_term))
    
    return PraktikumsLehrkraft.objects.filter(query).select_related(
        'school', 'main_subject'
    ).distinct()


def get_available_pls_for_praktikum(praktikum_type_id, subject_id=None):
    """
    Returns PLs available for a specific praktikum type and optionally subject.
    Business Logic: Filter PLs based on availability matrix.
    """
    queryset = PraktikumsLehrkraft.objects.filter(
        is_available=True,
        available_praktikum_types__id=praktikum_type_id
    )
    
    if subject_id:
        queryset = queryset.filter(
            subject_availabilities__subject_id=subject_id,
            subject_availabilities__praktikum_type_id=praktikum_type_id,
            subject_availabilities__is_available=True
        )
    
    return queryset.select_related('school', 'main_subject').distinct()


def get_pl_capacity_info(pl_id):
    """
    Returns capacity information for a PL.
    Business Logic: Calculate current and max capacity.
    """
    pl = PraktikumsLehrkraft.objects.get(id=pl_id)
    # TODO: Add assignment counting when assignment models are created
    return {
        'max_students_per_praktikum': pl.max_students_per_praktikum,
        'max_simultaneous_praktikum': pl.max_simultaneous_praktikum,
        'current_assignments': 0,  # Placeholder
        'available_capacity': pl.max_simultaneous_praktikum,  # Placeholder
    }


def create_pl_subject_availability(pl_id, subject_id, praktikum_type_id, is_available=True):
    """
    Creates or updates PL subject availability.
    Business Logic: Manage the matrix of PL-Subject-Praktikum relationships.
    """
    availability, created = PLSubjectAvailability.objects.update_or_create(
        pl_id=pl_id,
        subject_id=subject_id,
        praktikum_type_id=praktikum_type_id,
        defaults={'is_available': is_available}
    )
    return availability


def get_pls_by_subject(subject_id, praktikum_type_id=None):
    """
    Returns PLs who can teach a specific subject.
    Business Logic: Find qualified PLs for subject matching.
    """
    queryset = PraktikumsLehrkraft.objects.filter(
        available_subjects__id=subject_id,
        is_available=True
    )
    
    if praktikum_type_id:
        queryset = queryset.filter(
            subject_availabilities__subject_id=subject_id,
            subject_availabilities__praktikum_type_id=praktikum_type_id,
            subject_availabilities__is_available=True
        )
    
    return queryset.select_related('school', 'main_subject').distinct()

