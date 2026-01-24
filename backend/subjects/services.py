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


def get_all_subjects_from_rules():
    """
    Extract all unique subjects from subject_grouping_rules.json.
    Returns a list of unique subjects with code and display_name.
    """
    subjects_dict = {}

    for school_type in _rules.values():
        for praktikum_type in school_type.values():
            for _subject_name, rule in praktikum_type.items():
                code = rule.get("code")
                display_name = rule.get("display_name")
                if code and display_name:
                    subjects_dict[code] = {
                        "code": code,
                        "name": display_name,
                        "display_name": display_name,
                    }

    return list(subjects_dict.values())


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


def get_filtered_subjects_for_assignment(praktikum_type: str, school_type: str) -> list:
    """
    Get filtered subjects based on praktikum type and school type.

    Business Logic:
    - For ZSP/SFP: filter by both praktikum type AND school type
    - For PDP (PDP1/PDP2): filter only by school type

    Args:
        praktikum_type: One of 'ZSP', 'SFP', 'PDP1', 'PDP2', 'PDP_I', 'PDP_II'
        school_type: One of 'GS', 'MS', 'GMS'

    Returns:
        List of dicts with subject id, code, name and display name
    """
    # Normalize praktikum_type codes (handle both frontend and backend formats)
    code_mapping = {
        "PDP1": "PDP_I",
        "PDP2": "PDP_II",
        "PDP_I": "PDP_I",
        "PDP_II": "PDP_II",
        "SFP": "SFP",
        "ZSP": "ZSP",
    }
    normalized_type = code_mapping.get(praktikum_type, praktikum_type)

    # Normalize praktikum_type for PDP variants
    if normalized_type in ["PDP_I", "PDP_II"]:
        # For PDP, we only filter by school type, no praktikum-specific rules
        praktikum_key = None
    else:
        praktikum_key = normalized_type

    # For GMS schools, include both GS and MS subjects
    if school_type == "GMS":
        school_types_to_check = ["GS", "MS"]
    else:
        school_types_to_check = [school_type]

    # Collect unique subjects
    subjects_dict = {}

    for st in school_types_to_check:
        if st in _rules:
            if praktikum_key:
                # ZSP/SFP: use specific praktikum rules
                type_rules = _rules.get(st, {}).get(praktikum_key, {})
                for subject_name, rule in type_rules.items():
                    code = rule.get("code")
                    display_name = rule.get("display_name")
                    if code and display_name:
                        # Use code as key to avoid duplicates
                        subjects_dict[code] = {
                            "name": subject_name,
                            "code": code,
                            "display_name": display_name,
                        }
            else:
                # PDP: collect all subjects from both ZSP and SFP for the school type
                for pt in ["ZSP", "SFP"]:
                    type_rules = _rules.get(st, {}).get(pt, {})
                    for subject_name, rule in type_rules.items():
                        code = rule.get("code")
                        display_name = rule.get("display_name")
                        if code and display_name:
                            subjects_dict[code] = {
                                "name": subject_name,
                                "code": code,
                                "display_name": display_name,
                            }

    # Now match with actual Subject models to get IDs
    subject_codes = list(subjects_dict.keys())
    db_subjects = Subject.objects.filter(code__in=subject_codes, is_active=True)

    # Map codes to IDs
    code_to_id = {s.code: s.id for s in db_subjects}

    # Build final list with IDs
    subjects_list = []
    for code, info in subjects_dict.items():
        if code in code_to_id:
            subjects_list.append(
                {
                    "id": code_to_id[code],
                    "name": info["name"],
                    "code": code,
                    "display_name": info["display_name"],
                }
            )

    # Sort by display name
    subjects_list.sort(key=lambda x: x["display_name"])

    return subjects_list
