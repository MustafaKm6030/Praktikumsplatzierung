# in assignments/services.py

from collections import defaultdict
from students.models import Student
from subjects.services import get_subject_code, get_subject_display_name
from subjects.models import PraktikumType, Subject
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
    # --- EDITED: Only reads from the 'besonderheiten' field ---
    notes_text = mentor.current_year_notes.lower() if mentor.current_year_notes else ""

    constraints = {
        "is_unavailable": False,
        "force_capacity": None,
        "allowed_types": None,
        "forbidden_combinations": set(),
    }

    if not notes_text:
        return constraints

    # --- Global Unavailability ---
    unavailable_keywords = ["ruhend", "sabbatjahr", "mobil", "elternzeit", "krank"]
    if any(keyword in notes_text for keyword in unavailable_keywords):
        constraints["is_unavailable"] = True
        return constraints

    # --- Capacity Overrides ---
    if "nur 1 prak" in notes_text:
        constraints["force_capacity"] = 1

    # --- Type Restrictions ---
    if (
        "nur blockpraktika" in notes_text
        or "nur pdp" in notes_text
        or "kein mi-prak" in notes_text
    ):
        constraints["allowed_types"] = ["PDP_I", "PDP_II"]
    elif "nur mi-prak" in notes_text or "wg. tz nur mi-prak" in notes_text:
        constraints["allowed_types"] = ["SFP", "ZSP"]

    # --- Specific Combination Restrictions ---
    if "sfp nicht in geschichte" in notes_text:
        constraints["forbidden_combinations"].add(("SFP", "GE"))
    if (
        "englisch nicht möglich" in notes_text
        or "englisch wird heuer nicht unterrichtet" in notes_text
    ):
        constraints["forbidden_combinations"].add(("SFP", "E"))
        constraints["forbidden_combinations"].add(("ZSP", "E"))
    if "heuer kein krel" in notes_text:
        constraints["forbidden_combinations"].add(("SFP", "KRel"))
        constraints["forbidden_combinations"].add(("ZSP", "KRel"))

    return constraints


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
