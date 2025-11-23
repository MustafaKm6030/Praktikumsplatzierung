# in assignments/services.py

from collections import defaultdict
from students.models import Student
from subjects.services import get_subject_code, get_subject_display_name


def aggregate_demand():
    """
    Calculates the total forecasted demand for the upcoming academic year.
    It counts every internship a student is currently eligible for and has not yet completed,
    respecting that PDP II requires PDP I to be completed first.
    """
    demand_counts = defaultdict(int)
    code_to_display_map = {"N/A": "N/A"}

    unplaced_students = Student.objects.filter(
        placement_status="UNPLACED"
    ).select_related("primary_subject")

    for student in unplaced_students:
        program_type = student.program
        original_subject = (
            student.primary_subject.name if student.primary_subject else "N/A"
        )

        # --- Rule 1: Check for PDP I ---
        if student.pdp1_completed_date is None:
            key = ("PDP_I", program_type, "N/A")
            demand_counts[key] += 1

        # --- Rule 2: Check for PDP II (The only conditional check) ---
        # A student is ONLY eligible for PDP II if PDP I is already done.
        if (
            student.pdp1_completed_date is not None
            and student.pdp2_completed_date is None
        ):
            key = ("PDP_II", program_type, "N/A")
            demand_counts[key] += 1

        # --- Rule 3: Check for SFP (No prerequisite) ---
        if student.sfp_completed_date is None:
            code = get_subject_code(program_type, "SFP", original_subject)
            display = get_subject_display_name(program_type, "SFP", original_subject)
            code_to_display_map[code] = display
            key = ("SFP", program_type, code)
            demand_counts[key] += 1

        # --- Rule 4: Check for ZSP (No prerequisite) ---
        if student.zsp_completed_date is None:
            code = get_subject_code(program_type, "ZSP", original_subject)
            display = get_subject_display_name(program_type, "ZSP", original_subject)
            code_to_display_map[code] = display
            key = ("ZSP", program_type, code)
            demand_counts[key] += 1

    # --- Formatting the output (no changes here) ---
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
