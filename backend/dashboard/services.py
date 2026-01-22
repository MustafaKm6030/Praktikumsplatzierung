# in dashboard/services.py

from django.db.models import Sum, Count, Q
from students.models import Student
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from assignments.services import aggregate_demand
from assignments.models import Assignment


def get_dashboard_summary_data():
    """
    Aggregates all data needed for the main dashboard overview.
    Returns a dictionary with student summary, budget summary, and entity counts.
    """
    student_summary = get_student_summary()
    budget_summary = get_budget_summary()
    entity_counts = get_entity_counts()

    return {
        "student_summary": student_summary,
        "budget_summary": budget_summary,
        "entity_counts": entity_counts,
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
