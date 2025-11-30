# in dashboard/services.py

from django.db.models import Sum, Count, Q
from students.models import Student
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from assignments.services import aggregate_demand


def get_dashboard_summary_data():
    """
    Aggregates all data needed for the main dashboard overview.
    Returns a dictionary with assignment status, budget summary, and entity counts.
    """
    assignment_status = get_assignment_status()
    budget_summary = get_budget_summary()
    entity_counts = get_entity_counts()
    
    return {
        "assignment_status": assignment_status,
        "budget_summary": budget_summary,
        "entity_counts": entity_counts,
    }


def get_assignment_status():
    """
    Calculates assignment status by practicum type.
    Uses aggregate_demand service for demand calculation.
    Assigned/unassigned slots are mocked for parallel frontend development.
    """
    demand_data = aggregate_demand()
    
    # Aggregate demand by practicum type (sum across all programs and subjects)
    practicum_totals = {}
    for entry in demand_data:
        ptype = entry["practicum_type"]
        required = entry["required_slots"]
        
        if ptype not in practicum_totals:
            practicum_totals[ptype] = 0
        practicum_totals[ptype] += required
    
    # Build assignment status with mocked assigned values
    return build_assignment_status_list(practicum_totals)


def build_assignment_status_list(practicum_totals):
    """
    Builds the assignment status list with mocked assignment data.
    """
    assignment_status = []
    
    # Mock assignment data (realistic placeholders)
    mock_data = {
        "PDP_I": {"assigned": None, "unassigned": 0},
        "PDP_II": {"assigned": None, "unassigned": 0},
        "SFP": {"assigned": -2, "unassigned": 2},
        "ZSP": {"assigned": None, "unassigned": 0},
    }
    
    for ptype in ["PDP_I", "PDP_II", "SFP", "ZSP"]:
        demand = practicum_totals.get(ptype, 0)
        mock = mock_data.get(ptype, {"assigned": None, "unassigned": 0})
        
        # If assigned is None, it means fully assigned
        assigned = demand + mock["assigned"] if mock["assigned"] is not None else demand
        unassigned = mock["unassigned"]
        
        assignment_status.append({
            "practicum_type": ptype.replace("_", " "),
            "demand_slots": demand,
            "assigned_slots": assigned,
            "unassigned_slots": unassigned,
        })
    
    return assignment_status


def get_budget_summary():
    """
    Calculates budget summary from active PL records.
    Total budget is a constant, distributed budget is calculated from active PLs.
    """
    TOTAL_BUDGET = 210  # Constant total budget
    
    active_pls = PraktikumsLehrkraft.objects.filter(is_active=True)
    
    # Calculate distributed budget by program
    budget_by_program = active_pls.values('program').annotate(
        total_hours=Sum('anrechnungsstunden')
    )
    
    distributed_gs = 0
    distributed_ms = 0
    
    for item in budget_by_program:
        hours = float(item['total_hours'] or 0)
        if item['program'] == 'GS':
            distributed_gs = hours
        elif item['program'] == 'MS':
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
    Calculates entity counts for students and active PLs.
    Uses efficient count() and aggregate() queries.
    """
    # Student counts
    total_students = Student.objects.count()
    unplaced_students = Student.objects.filter(
        placement_status='UNPLACED'
    ).count()
    
    # Active PL counts
    active_pls = PraktikumsLehrkraft.objects.filter(is_active=True)
    active_pls_total = active_pls.count()
    
    # PL counts by program
    pl_by_program = active_pls.values('program').annotate(
        count=Count('id')
    )
    
    active_pls_gs = 0
    active_pls_ms = 0
    
    for item in pl_by_program:
        if item['program'] == 'GS':
            active_pls_gs = item['count']
        elif item['program'] == 'MS':
            active_pls_ms = item['count']
    
    return {
        "total_students": total_students,
        "unplaced_students": unplaced_students,
        "active_pls_total": active_pls_total,
        "active_pls_gs": active_pls_gs,
        "active_pls_ms": active_pls_ms,
    }



