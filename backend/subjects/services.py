"""
Business logic for Subjects and PraktikumTypes.
Keep views thin by moving complex logic here.
"""

import json
from pathlib import Path
from typing import Optional, Dict
from .models import Subject, PraktikumType


_rules: Dict = {}

try:
    rules_path = Path(__file__).parent / "data" / "subject_grouping_rules.json"
    with open(rules_path, "r", encoding="utf-8") as f:
        _rules = json.load(f)
except FileNotFoundError:
    # If the file is missing, the rules dict will be empty.
    print(
        "WARNING: subject_grouping_rules.json not found. Subject grouping will not be applied."
    )
    pass
except json.JSONDecodeError:
    print(
        "ERROR: Could not decode subject_grouping_rules.json. Check for syntax errors."
    )
    pass


def _get_subject_rule(
    program_type: str, practicum_type: str, subject: str
) -> Optional[Dict[str, str]]:
    """
    Internal helper function to look up the complete rule object for a given subject.

    Returns the rule object (e.g., {'code': 'HSU', 'display_name': '...'}) or None if no rule is found.
    """
    try:
        # .get(subject) will return the rule object or None if the subject key is not found
        return _rules.get(program_type, {}).get(practicum_type, {}).get(subject)
    except Exception:
        # Broad except to catch any unexpected issues with the rules file structure
        return None


def get_subject_code(program_type: str, practicum_type: str, subject: str) -> str:
    """
    Applies grouping rules to get the machine-readable SOLVER CODE for a subject.

    This is used to match student demand with the correct column in the Excel file.
    If no specific rule is found, it returns the original subject name as a fallback.

    Args:
        program_type: The student's program, e.g., 'GS' or 'MS'.
        practicum_type: The internship type, e.g., 'SFP' or 'ZSP'.
        subject: The raw subject from the student data (e.g., 'Biologie').

    Returns:
        The machine-readable code (e.g., 'HSU') or the original subject name.
    """
    rule = _get_subject_rule(program_type, practicum_type, subject)
    if rule and "code" in rule:
        return rule["code"]
    return subject


def get_subject_display_name(
    program_type: str, practicum_type: str, subject: str
) -> str:
    """
    Applies grouping rules to get the human-readable DISPLAY NAME for a subject.

    This is used for generating reports and displaying information in the UI.
    If no specific rule is found, it returns the original subject name as a fallback.

    Args:
        program_type: The student's program, e.g., 'GS' or 'MS'.
        practicum_type: The internship type, e.g., 'SFP' or 'ZSP'.
        subject: The raw subject from the student data (e.g., 'Biologie').

    Returns:
        The full display name (e.g., 'Heimat- und Sachunterricht (HSU)') or the original subject.
    """
    rule = _get_subject_rule(program_type, practicum_type, subject)
    if rule and "display_name" in rule:
        return rule["display_name"]
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
    return Subject.objects.filter(subject_group=subject_group, is_active=True)


def get_block_praktikum_types():
    """
    Get all block Praktikum types (PDP I, PDP II).
    Business Logic: Block Praktika allow Zone 3 schools.
    """
    return PraktikumType.objects.filter(is_block_praktikum=True, is_active=True)


def get_wednesday_praktikum_types():
    """
    Get all Wednesday Praktikum types (SFP, ZSP).
    Business Logic: Wednesday Praktika restricted to Zone 1/2.
    """
    return PraktikumType.objects.filter(is_block_praktikum=False, is_active=True)


def get_allowed_subject_codes(program_type: str, practicum_type: str) -> set:
    """
    Returns a set of valid Subject Codes (e.g., {'D', 'MA', 'HSU'}) for a
    given Program and Internship Type based on the JSON rules.
    """
    allowed_codes = set()

    # 1. Get the specific section from the rules
    # e.g., _rules['GS']['SFP']
    type_rules = _rules.get(program_type, {}).get(practicum_type, {})

    # 2. Collect all the target codes
    for rule in type_rules.values():
        if "code" in rule:
            allowed_codes.add(rule["code"])

    return allowed_codes
