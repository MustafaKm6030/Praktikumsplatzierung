# in assignments/services.py

from collections import defaultdict
from students.models import Student
from subjects.services import get_subject_code, get_subject_display_name


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
