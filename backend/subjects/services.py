"""
Business logic for Subjects and PraktikumTypes.
Keep views thin by moving complex logic here.
"""
from .models import Subject, PraktikumType


def get_active_subjects():
    """
    Get all active subjects.
    Business Logic: Only return subjects that are active.
    """
    return Subject.objects.filter(is_active=True)


def get_subjects_by_group(subject_group):
    """
    Get subjects filtered by subject group.
    Business Logic: Filter subjects by group for GS/MS matching.
    """
    return Subject.objects.filter(
        subject_group=subject_group,
        is_active=True
    )


def get_block_praktikum_types():
    """
    Get all block Praktikum types (PDP I, PDP II).
    Business Logic: Block Praktika allow Zone 3 schools.
    """
    return PraktikumType.objects.filter(
        is_block_praktikum=True,
        is_active=True
    )


def get_wednesday_praktikum_types():
    """
    Get all Wednesday Praktikum types (SFP, ZSP).
    Business Logic: Wednesday Praktika restricted to Zone 1/2.
    """
    return PraktikumType.objects.filter(
        is_block_praktikum=False,
        is_active=True
    )

