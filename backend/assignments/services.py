# in assignments/services.py

from collections import defaultdict
from students.models import Student
from subjects.services import get_subject_code, get_subject_display_name
from subjects.models import PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
import re
from schools.services import get_reachable_schools


def aggregate_demand():
    """
    Calculates the total forecasted demand for the upcoming academic year.
    """
    demand_counts = defaultdict(int)
    code_to_display_map = {"N/A": "N/A"}

    unplaced_students = Student.objects.filter(
        placement_status="UNPLACED"
    ).select_related("primary_subject", "didactic_subject_3")

    for student in unplaced_students:
        process_student_demand(student, demand_counts, code_to_display_map)

    return format_demand(demand_counts, code_to_display_map)


def process_student_demand(student, demand_counts, code_to_display_map):
    """Processes a single student and updates demand counts and display mapping."""
    program_type = student.program

    # Get the specific subject for each practicum type
    sfp_subject_name = (
        student.primary_subject.name if student.primary_subject else "N/A"
    )
    zsp_subject_name = (
        student.didactic_subject_3.name if student.didactic_subject_3 else "N/A"
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
    if student.sfp_completed_date is None and sfp_subject_name != "N/A":
        add_practicum_demand(
            "SFP", program_type, sfp_subject_name, demand_counts, code_to_display_map
        )

    # --- Rule 4: ZSP ---
    if student.zsp_completed_date is None and zsp_subject_name != "N/A":
        add_practicum_demand(
            "ZSP", program_type, zsp_subject_name, demand_counts, code_to_display_map
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


def _parse_constraints_from_notes(mentor: PraktikumsLehrkraft) -> dict:
    """
    Parses the 'besonderheiten' field for hard constraints and returns a structured dict.
    """
    notes_text = (mentor.current_year_notes or "").lower()

    if not notes_text:
        return {
            "is_unavailable": False,
            "force_capacity": None,
            "allowed_types": None,
            "forbidden_combinations": set(),
        }

    # 1. Global Unavailability (Critical Check)
    if _is_mentor_unavailable(notes_text):
        return {
            "is_unavailable": True,
            "force_capacity": None,
            "allowed_types": None,
            "forbidden_combinations": set(),
        }

    # 2. specific constraints
    return {
        "is_unavailable": False,
        "force_capacity": _parse_capacity_override(notes_text),
        "allowed_types": _parse_allowed_types(notes_text),
        "forbidden_combinations": _parse_forbidden_combinations(notes_text),
    }


def _is_mentor_unavailable(text: str) -> bool:
    """Checks for keywords indicating the mentor cannot take students."""
    unavailable_keywords = ["ruhend", "sabbatjahr", "mobil", "elternzeit", "krank"]
    return any(keyword in text for keyword in unavailable_keywords)


def _parse_capacity_override(text: str):
    """Checks if the notes specify a strict capacity limit."""
    if "nur 1 prak" in text:
        return 1
    return None


def _parse_allowed_types(text: str):
    """Determines if the mentor is restricted to specific internship types."""
    if "nur blockpraktika" in text or "nur pdp" in text or "kein mi-prak" in text:
        return ["PDP_I", "PDP_II"]

    if "nur mi-prak" in text or "wg. tz nur mi-prak" in text:
        return ["SFP", "ZSP"]

    return None


def _parse_forbidden_combinations(text: str) -> set:
    """Identifies specific Subject+Type combinations that are banned."""
    forbidden = set()

    if "sfp nicht in geschichte" in text:
        forbidden.add(("SFP", "GE"))

    if (
        "englisch nicht möglich" in text
        or "englisch wird heuer nicht unterrichtet" in text
    ):
        forbidden.add(("SFP", "E"))
        forbidden.add(("ZSP", "E"))

    if "heuer kein krel" in text:
        forbidden.add(("SFP", "KRel"))
        forbidden.add(("ZSP", "KRel"))

    return forbidden


def calculate_eligibility_for_pl(mentor: PraktikumsLehrkraft) -> list:
    """
    Calculates the complete set of valid (Practicum Type Code, Subject Code)
    combinations for a given mentor, applying constraints from the 'besonderheiten' field.
    """
    # 1. Get all constraints from the 'besonderheiten' field
    constraints = _parse_constraints_from_notes(mentor)
    if not mentor.is_active or constraints.get("is_unavailable"):
        return []

    # 2. Determine base set of applicable internship types
    applicable_types = mentor.available_praktikum_types.all()
    if constraints.get("allowed_types"):
        applicable_types = applicable_types.filter(
            code__in=constraints["allowed_types"]
        )

    # 3. Generate all potential combinations
    potential_combinations = set()
    for p_type in applicable_types:
        reachable_schools = get_reachable_schools(p_type.code)
        # If the mentor's school is NOT in this list, they are not eligible for this type
        if mentor.school not in reachable_schools:
            continue

        if p_type.is_block_praktikum:
            potential_combinations.add((p_type.code, "N/A"))
        else:  # SFP/ZSP
            for subject in mentor.available_subjects.all():
                potential_combinations.add((p_type.code, subject.code))

    # 4. Filter out forbidden combinations found in the notes
    final_combinations = [
        combo
        for combo in potential_combinations
        if combo not in constraints["forbidden_combinations"]
    ]

    return final_combinations


def get_mentor_capacity(mentor: PraktikumsLehrkraft) -> int:
    """
    Gets the final capacity for a mentor, considering text-based overrides
    from the 'besonderheiten' field.
    """
    constraints = _parse_constraints_from_notes(mentor)
    if constraints.get("force_capacity") is not None:
        return constraints["force_capacity"]

    # Default to the capacity from Anrechnungsstunden
    return mentor.capacity
