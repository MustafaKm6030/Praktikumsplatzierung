from collections import defaultdict
from students.models import StudentPraktikumPreference
from subjects.services import get_subject_code, get_subject_display_name


def _fetch_unplaced_preferences():
    """Helper function to query the database for all active preferences."""
    return StudentPraktikumPreference.objects.filter(status="UNPLACED").select_related(
        "student", "praktikum_type", "student__primary_subject"
    )


def _format_demand_output(demand_counts: defaultdict) -> list:
    """Helper function to format the aggregated counts into the final API structure."""
    formatted_demand = []
    for (ptype, pprog, psub_code, psub_display), count in demand_counts.items():
        formatted_demand.append(
            {
                "practicum_type": ptype,
                "program_type": pprog,
                "subject_code": psub_code,
                "subject_display_name": psub_display,
                "required_slots": count,
            }
        )
    return formatted_demand


def aggregate_demand():
    """
    Calculates the total demand for practicum slots, providing both a machine-readable
    code (for the solver) and a human-readable name (for the dashboard).
    """
    demand_counts = defaultdict(int)
    preferences = _fetch_unplaced_preferences()

    for pref in preferences:
        practikum_type = pref.praktikum_type.code
        program_type = pref.student.program
        original_subject = (
            pref.student.primary_subject.name if pref.student.primary_subject else "N/A"
        )

        subject_code = "N/A"
        subject_display_name = "N/A"

        if not pref.praktikum_type.is_block_praktikum:
            subject_code = get_subject_code(
                program_type, practikum_type, original_subject
            )
            subject_display_name = get_subject_display_name(
                program_type, practikum_type, original_subject
            )

        demand_key = (practikum_type, program_type, subject_code, subject_display_name)
        demand_counts[demand_key] += 1

    return _format_demand_output(demand_counts)
