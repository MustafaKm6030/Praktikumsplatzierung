# in assignments/services.py

from collections import defaultdict
from students.models import Student
from subjects.services import get_subject_code, get_subject_display_name
from subjects.models import PraktikumType, Subject
from praktikums_lehrkraft.models import PraktikumsLehrkraft
import re


def aggregate_demand():
    """
    Calculates the total forecasted demand for the upcoming academic year.
    """
    demand_counts = defaultdict(int)
    code_to_display_map = {"N/A": "N/A"}

    unplaced_students = Student.objects.filter(
        placement_status="UNPLACED"
    ).select_related("primary_subject")

    for student in unplaced_students:
        process_student_demand(student, demand_counts, code_to_display_map)

    return format_demand(demand_counts, code_to_display_map)


def process_student_demand(student, demand_counts, code_to_display_map):
    """Processes a single student and updates demand counts and display mapping."""
    program_type = student.program
    original_subject = (
        student.primary_subject.name if student.primary_subject else "N/A"
    )

    # --- Rule 1: PDP I ---
    if student.pdp1_completed_date is None:
        key = "PDP_I", program_type, "N/A"
        demand_counts[key] += 1

    # --- Rule 2: PDP II ---
    if student.pdp1_completed_date is not None and student.pdp2_completed_date is None:
        key = "PDP_II", program_type, "N/A"
        demand_counts[key] += 1

    # --- Rule 3: SFP ---
    if student.sfp_completed_date is None:
        add_practicum_demand(
            "SFP", program_type, original_subject, demand_counts, code_to_display_map
        )

    # --- Rule 4: ZSP ---
    if student.zsp_completed_date is None:
        add_practicum_demand(
            "ZSP", program_type, original_subject, demand_counts, code_to_display_map
        )


def add_practicum_demand(
    practicum_type, program_type, subject, demand_counts, code_to_display_map
):
    """Adds a practicum demand entry and updates display mapping."""
    code = get_subject_code(program_type, practicum_type, subject)
    display = get_subject_display_name(program_type, practicum_type, subject)
    code_to_display_map[code] = display
    key = practicum_type, program_type, code
    demand_counts[key] += 1


def format_demand(demand_counts, code_to_display_map):
    """Formats the aggregated demand into a list of dicts."""
    formatted_demand = []
    for (ptype, pprog, pcode), count in demand_counts.items():
        formatted_demand.append(
            {
                "practicum_type": ptype,
                "program_type": pprog,
                "subject_code": pcode,
                "subject_display_name": code_to_display_map.get(pcode, pcode),
                "required_slots": count,
            }
        )
    return formatted_demand

#PL Eligibility Calculation
def _check_mentor_availability(mentor):
    """
    Checks if mentor is available based on basic status flags.
    Business Logic: Mentor must be active and not in restricted status.
    
    Returns: bool indicating if mentor is available
    """
    if not mentor.is_active:
        return False
    
    # Check current_year_notes for restricted statuses
    if mentor.current_year_notes:
        restricted_keywords = _parse_restrictive_keywords(
            mentor.current_year_notes
        )
        if restricted_keywords.get("is_unavailable"):
            return False
    
    return True


def _parse_restrictive_keywords(notes_text):
    """
    Parses text-based constraints from notes fields.
    Business Logic: Extract keywords that restrict PL availability.
    
    Returns: dict with restriction flags
    """
    if not notes_text:
        return {}
    
    text_lower = notes_text.lower()
    
    # Keywords indicating complete unavailability
    unavailable_keywords = [
        "ruhend", "sabbatjahr", "mobil", "elternzeit", "krank"
    ]
    
    # Keywords restricting praktikum types
    block_only_keywords = ["nur blockpraktika", "nur pdp"]
    wednesday_only_keywords = ["nur mittwochspraktika", "kein mi-prak"]
    
    restrictions = {
        "is_unavailable": any(
            keyword in text_lower for keyword in unavailable_keywords
        ),
        "block_only": any(
            keyword in text_lower for keyword in block_only_keywords
        ),
        "no_wednesday": (
            "kein mi-prak" in text_lower or "keine mittwochspraktika" in text_lower
        ),
    }
    
    return restrictions


def _get_applicable_praktikum_types(mentor, restrictions):
    """
    Gets praktikum types PL can supervise based on restrictions.
    Business Logic: Filter praktikum types by text-based constraints.
    
    Returns: QuerySet of applicable PraktikumType objects
    """
    available_types = mentor.available_praktikum_types.filter(is_active=True)
    
    if restrictions.get("block_only"):
        # Only allow PDP I/II
        available_types = available_types.filter(is_block_praktikum=True)
    
    if restrictions.get("no_wednesday"):
        # Exclude SFP/ZSP
        available_types = available_types.filter(is_block_praktikum=True)
    
    return available_types


def _check_subject_requirement(praktikum_code, mentor, subject):
    """
    Checks if subject requirement is met for given praktikum.
    Business Logic: SFP/ZSP require subject match, PDP I/II don't.
    
    Returns: bool indicating if subject requirement is satisfied
    """
    # PDP I/II don't require subject matching
    if praktikum_code in ["PDP_I", "PDP_II"]:
        return True
    
    # SFP/ZSP require the mentor to have 'x' for this subject
    if praktikum_code in ["SFP", "ZSP"]:
        return mentor.available_subjects.filter(id=subject.id).exists()
    
    return False


def _get_valid_subjects_for_praktikum(praktikum_type, mentor):
    """
    Gets valid subjects for a given praktikum type.
    Business Logic: Return subjects based on praktikum requirements.
    
    Returns: QuerySet of valid Subject objects
    """
    # For PDP I/II, no specific subject is required (N/A)
    if praktikum_type.code in ["PDP_I", "PDP_II"]:
        # Return None to indicate N/A (no subject requirement)
        return None
    
    # For SFP/ZSP, return subjects mentor is qualified for
    if praktikum_type.code in ["SFP", "ZSP"]:
        return mentor.available_subjects.filter(is_active=True)
    
    return Subject.objects.none()

#main function to calculate PL Eligibility
def calculate_eligibility_for_pl(mentor):
    """
    Calculate complete set of valid (Practicum Type, Subject_Code) 
    combinations for a given mentor.
    
    Business Logic: This is the core pre-processing function for the 
    assignment algorithm. It applies all fundamental hard constraints:
    - Program Type Match (GS vs MS)
    - Subject Relevance (mandatory for SFP/ZSP, not for PDP I/II)
    - Mentor Availability (text-based constraints, status checks)
    - Declared Preferences (bevorzugte Praktika)
    
    Args:
        mentor: PraktikumsLehrkraft object
    
    Returns:
        list of tuples: [(praktikum_code, subject_code), ...]
        Example: [('PDP_I', 'N/A'), ('SFP', 'MA'), ('SFP', 'D')]
    """
    # Step 1: Check basic availability
    if not _check_mentor_availability(mentor):
        return []
    
    eligible_combinations = []
    
    # Step 2: Parse text-based restrictions
    restrictions = _parse_restrictive_keywords(mentor.current_year_notes)
    
    # Step 3: Get applicable praktikum types
    applicable_types = _get_applicable_praktikum_types(mentor, restrictions)
    
    # Step 4: For each praktikum type, determine valid subjects
    for praktikum_type in applicable_types:
        valid_subjects = _get_valid_subjects_for_praktikum(
            praktikum_type, mentor
        )
        
        # For PDP I/II (no subject requirement)
        if valid_subjects is None:
            eligible_combinations.append(
                (praktikum_type.code, "N/A")
            )
        # For SFP/ZSP (subject-specific)
        else:
            for subject in valid_subjects:
                eligible_combinations.append(
                    (praktikum_type.code, subject.code)
                )
    
    return eligible_combinations
