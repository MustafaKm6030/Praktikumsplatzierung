from collections import defaultdict
from students.models import StudentPraktikumPreference  # The correct model to query
from subjects.services import get_subject_code


def aggregate_demand():
    """
    Calculates the total demand for practicum slots based on all unplaced
    student practicum preferences.

    - For SFP/ZSP, demand is grouped by (Practicum Type, Program Type, Subject Code).
    - For PDP I/II, demand is grouped by (Practicum Type, Program Type) only.

    Returns:
        A list of dictionaries representing each unique demand group, ready for
        the assignment algorithm.
    """
    demand_counts = defaultdict(int)

    # .select_related() is a performance optimization. It fetches the related
    # student and praktikum_type in a single, efficient database query.
    preferences = StudentPraktikumPreference.objects.filter(
        status="UNPLACED"
    ).select_related("student", "praktikum_type", "student__primary_subject")

    for pref in preferences:
        practikum_code = pref.praktikum_type.code
        program_type = pref.student.program
        primary_subject_name = (
            pref.student.primary_subject.name if pref.student.primary_subject else "N/A"
        )

        subject_key = "N/A"
        if not pref.praktikum_type.is_block_praktikum:
            subject_key = get_subject_code(
                program_type, practikum_code, primary_subject_name
            )

        # Create the key for our dictionary and increment the count
        demand_key = (practikum_code, program_type, subject_key)
        demand_counts[demand_key] += 1

    # Format the aggregated data for the API response
    formatted_demand = []
    for (ptype, pprog, psub), count in demand_counts.items():
        formatted_demand.append(
            {
                "practicum_type": ptype,
                "program_type": pprog,
                "subject": psub,
                "required_slots": count,
            }
        )

    return formatted_demand
