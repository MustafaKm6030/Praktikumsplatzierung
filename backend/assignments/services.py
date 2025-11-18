from collections import defaultdict
from students.models import StudentPraktikumPreference  # The correct model to query
from subjects.services import apply_subject_grouping  # Your existing function


def aggregate_demand():
    """
    Calculates the total demand for practicum slots based on all unplaced
    student practicum preferences.

    - For SFP/ZSP, demand is grouped by (Practicum Type, Program Type, Subject).
    - For PDP I/II, demand is grouped by (Practicum Type, Program Type) only.

    Returns:
        A list of dictionaries representing each unique demand group.
    """
    demand_counts = defaultdict(int)

    # This is the key change: Query the preferences for unplaced students.
    # .select_related() is a performance optimization. It fetches the related
    # student and praktikum_type in a single, efficient database query.
    preferences = StudentPraktikumPreference.objects.filter(
        status="UNPLACED"
    ).select_related("student", "praktikum_type", "student__primary_subject")

    for pref in preferences:
        # Get data from the related models
        practikum_code = pref.praktikum_type.code
        program_type = pref.student.program
        primary_subject_name = (
            pref.student.primary_subject.name if pref.student.primary_subject else "N/A"
        )

        # Determine the subject key based on the practicum type
        subject_key = None
        if not pref.praktikum_type.is_block_praktikum:  # It's an SFP or ZSP
            subject_key = apply_subject_grouping(
                program_type, practikum_code, primary_subject_name
            )
        else:  # It's a PDP I or PDP II
            subject_key = "N/A"  # Use a generic placeholder

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
