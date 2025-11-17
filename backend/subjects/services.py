"""
Business logic for Subjects and PraktikumTypes.
Keep views thin by moving complex logic here.
"""

import json
from pathlib import Path
from .models import Subject, PraktikumType


_rules= {}

try:
    rules_path= Path(__file__).parent / "data" / "subject_grouping_rules.json"
    with open(rules_path, 'r', encoding='utf-8') as f:
        _rules= json.load(f)
except FileNotFoundError:
    # If the file is missing, the rules dict will be empty.
    print("WARNING: subject_grouping_rules.json not found. Subject grouping will not be applied.")
    pass

def apply_subject_grouping(program_type: str, practicum_type: str, subject: str) -> str:
    """
    Applies the official subject grouping rules for SFP and ZSP internships.

    If no specific rule is found for a subject, it returns the original subject name.

    Args:
        program_type: The student's program, e.g., 'GS' or 'MS'.
        practicum_type: The internship type, e.g., 'SFP' or 'ZSP'.
        subject: The raw subject from the student data (e.g., 'Biologie').

    Returns:
        The grouped subject name (e.g., 'Heimat- und Sachunterricht (HSU)') or the original subject.
    """
    try:
        # Navigate through the rules dictionary to find the mapping.
        # The .get(subject, subject) is the key: it tries to find the subject,
        # but if it fails, it returns the original subject itself.
        return _rules[program_type][practicum_type].get(subject, subject)
    except KeyError:
        # This handles cases where a program_type or practicum_type might not be in the rules file.
        # It safely defaults to returning the original subject.
        return subject

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

