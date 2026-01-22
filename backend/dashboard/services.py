# in dashboard/services.py

from django.db.models import Sum, Count, Q
from students.models import Student
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from assignments.services import aggregate_demand
from assignments.models import Assignment


def get_dashboard_summary_data():
    """
    Aggregates all data needed for the main dashboard overview.
    Returns a dictionary with assignment status, budget summary, and entity counts.
    """
    assignment_status = get_assignment_status()
    budget_summary = get_budget_summary()
    entity_counts = get_entity_counts()
    student_summary = _build_student_summary(entity_counts)

    return {
        "assignment_status": assignment_status,
        "student_summary": student_summary,
        "budget_summary": budget_summary,
        "entity_counts": entity_counts,
    }


def _build_student_summary(entity_counts):
    """
    Builds student summary from entity counts for frontend compatibility.
    """
    return {
        "total_students": entity_counts.get("total_students", 0),
        "assigned_students": entity_counts.get("placed_students", 0),
        "unassigned_students": entity_counts.get("unplaced_students", 0),
    }


def get_student_summary():
    """
    Calculates total students, assigned students, and unassigned students.
    Returns a dictionary with student assignment statistics.
    """
    total_students = Student.objects.count()
    assigned_students = Student.objects.filter(placement_status="PLACED").count()
    unassigned_students = Student.objects.filter(placement_status="UNPLACED").count()

    return {
        "total_students": total_students,
        "assigned_students": assigned_students,
        "unassigned_students": unassigned_students,
    }


def get_budget_summary():
    """
    Calculates budget summary from active PL records.
    Total budget is a constant, distributed budget is calculated from active PLs.
    """
    TOTAL_BUDGET = 210  # Constant total budget

    active_pls = PraktikumsLehrkraft.objects.filter(is_active=True)

    # Calculate distributed budget by program
    budget_by_program = active_pls.values("program").annotate(
        total_hours=Sum("anrechnungsstunden")
    )

    distributed_gs = 0
    distributed_ms = 0

    for item in budget_by_program:
        hours = float(item["total_hours"] or 0)
        if item["program"] == "GS":
            distributed_gs = hours
        elif item["program"] == "MS":
            distributed_ms = hours

    total_distributed = distributed_gs + distributed_ms
    remaining_budget = TOTAL_BUDGET - total_distributed

    return {
        "total_budget": TOTAL_BUDGET,
        "distributed_gs": distributed_gs,
        "distributed_ms": distributed_ms,
        "remaining_budget": remaining_budget,
    }


def get_entity_counts():
    """
    Calculates entity counts using conditional aggregation.
    Reduces DB queries from 8 to 2 and satisfies line count limits.
    """
    # Query 1: Fetch all Student metrics at once
    student_stats = Student.objects.aggregate(
        total_students=Count("id"),
        unplaced_students=Count("id", filter=Q(placement_status="UNPLACED")),
        placed_students=Count("id", filter=Q(placement_status="PLACED")),
        unplaced_students_gs=Count(
            "id", filter=Q(placement_status="UNPLACED", program="GS")
        ),
        unplaced_students_ms=Count(
            "id", filter=Q(placement_status="UNPLACED", program="MS")
        ),
        placed_students_gs=Count(
            "id", filter=Q(placement_status="PLACED", program="GS")
        ),
        placed_students_ms=Count(
            "id", filter=Q(placement_status="PLACED", program="MS")
        ),
    )

    # Query 2: Fetch all PL metrics at once
    pl_stats = PraktikumsLehrkraft.objects.filter(is_active=True).aggregate(
        active_pls_total=Count("id"),
        active_pls_gs=Count("id", filter=Q(program="GS")),
        active_pls_ms=Count("id", filter=Q(program="MS")),
    )

    return {**student_stats, **pl_stats}


def get_assignment_status():
    """
    Calculates assignment status for all practicum types.
    Returns a list of dictionaries with demand, assigned, and unassigned slots.
    """
    demand_list = aggregate_demand()
    practicum_totals = _convert_demand_to_totals(demand_list)
    return build_assignment_status_list(practicum_totals)


def _convert_demand_to_totals(demand_list):
    """
    Converts demand list from aggregate_demand() to dict of totals by practicum type.
    """
    totals = {}
    for item in demand_list:
        ptype = item.get("practicum_type", "")
        count = item.get("required_slots", 0)
        totals[ptype] = totals.get(ptype, 0) + count
    return totals


def build_assignment_status_list(practicum_totals):
    """
    Builds assignment status list from practicum totals.
    Applies real assignment data from database.
    """
    practicum_types = {
        "PDP_I": "PDP I",
        "PDP_II": "PDP II",
        "SFP": "SFP",
        "ZSP": "ZSP",
    }

    result = []
    for code, display_name in practicum_types.items():
        demand_slots = practicum_totals.get(code, 0)
        assigned_slots = _get_assigned_slots(code)
        unassigned_slots = max(0, demand_slots - assigned_slots)

        result.append(
            {
                "practicum_type": display_name,
                "demand_slots": demand_slots,
                "assigned_slots": assigned_slots,
                "unassigned_slots": unassigned_slots,
            }
        )

    return result


def _get_assigned_slots(practicum_type_code):
    """
    Helper: Gets count of assigned slots for a practicum type.
    """
    return Assignment.objects.filter(practicum_type__code=practicum_type_code).count()
