from django.db import transaction
from ortools.sat.python import cp_model
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from assignments.models import Assignment
from subjects.models import Subject, PraktikumType
from .services import (
    aggregate_demand,
    calculate_eligibility_for_pl,
    get_mentor_capacity,
)

# Import extracted logic
from .constraints import (
    add_capacity_constraints,
    add_valid_pairs_constraints,
    add_minimum_coverage_constraints,
)
from .objectives import set_objective_function


def run_solver():
    print("\n=== 🕵️ STARTING PERMISSIVE SOLVER (Supply-Only MVP) ===")
    model = cp_model.CpModel()

    # 1. Fetch Data
    all_mentors = (
        PraktikumsLehrkraft.objects.filter(is_active=True)
        .select_related("school")
        .prefetch_related("available_praktikum_types", "available_subjects")
    )

    # 2. Prepare Supply (Variables & Validation)
    assignment_vars, mentor_data, trackers = _prepare_supply_variables(
        model, all_mentors
    )
    all_ids, skipped_ids = trackers

    print(f"\n1. SUPPLY ANALYSIS ({len(all_mentors)} Mentors found):")
    print(f"Active Mentors in Solver: {len(mentor_data)}")
    print(f"Skipped Mentors (Data Errors): {len(skipped_ids)}")

    # 3. Prepare Demand
    demand_map = _prepare_demand_map()

    # 4. Apply Logic (Constraints & Objective)
    add_capacity_constraints(model, assignment_vars, mentor_data)
    add_valid_pairs_constraints(model, assignment_vars, mentor_data)

    # --- Hard Coverage Constraint ---
    add_minimum_coverage_constraints(model, assignment_vars, mentor_data)

    # --- Objective Function with Soft Caps ---
    set_objective_function(model, assignment_vars, mentor_data, demand_map)

    # 5. Solve & Process
    print("\n--- Solving ---")
    solver = cp_model.CpSolver()
    # solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    return _process_solver_results(
        status, solver, assignment_vars, mentor_data, all_ids, skipped_ids
    )


def _prepare_supply_variables(model, all_mentors):
    """
    Iterates through mentors, validates data, and creates optimization variables.
    """
    assignment_vars = {}
    mentor_data = {}
    all_ids = set()
    skipped_ids = set()

    for mentor in all_mentors:
        all_ids.add(mentor.id)
        capacity = get_mentor_capacity(mentor)
        eligibilities = calculate_eligibility_for_pl(mentor)

        if not _validate_mentor_data(mentor, capacity, eligibilities):
            skipped_ids.add(mentor.id)
            continue

        mentor_data[mentor.id] = {
            "capacity": capacity,
            "eligibilities": eligibilities,
            "object": mentor,
        }

        for practicum_type, subject_code in eligibilities:
            var_key = mentor.id, practicum_type, subject_code
            assignment_vars[var_key] = model.NewBoolVar(
                f"assign_{mentor.id}_{practicum_type}_{subject_code}"
            )

    return assignment_vars, mentor_data, (all_ids, skipped_ids)


def _prepare_demand_map():
    demand_data = aggregate_demand()
    demand_map = {}
    for d in demand_data:
        key = d["practicum_type"], d["program_type"], d["subject_code"]
        demand_map[key] = d["required_slots"]
    return demand_map


def _process_solver_results(
    status, solver, assignment_vars, mentor_data, all_ids, skipped_ids
):
    results = {
        "status": "FAILURE",
        "assignments": [],
        "unassigned": [],
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"✅ Solution found in {solver.WallTime()}s!")

        with transaction.atomic():
            assignments_created, assigned_ids = _save_assignments_to_db(
                solver, assignment_vars, mentor_data
            )
            print(f"Saved {len(assignments_created)} assignments to database.")

            unassigned_data = _get_unassigned_mentors_report(
                all_ids, assigned_ids, skipped_ids, mentor_data, assignment_vars, solver
            )

            results["status"] = "SUCCESS"
            results["assignments"] = assignments_created
            results["unassigned"] = unassigned_data
    else:
        print("❌ No solution found.")

    return results


def _validate_mentor_data(mentor, capacity, eligibilities):
    if len(eligibilities) == 0:
        print(f"⚠️ Skipping Mentor {mentor.id}: No eligibility options found.")
        return False
    return True


def _save_assignments_to_db(solver, assignment_vars, mentor_data):
    Assignment.objects.all().delete()

    subjects_map = {s.code: s for s in Subject.objects.all()}
    ptypes_map = {p.code: p for p in PraktikumType.objects.all()}

    assignments_created = []
    assigned_mentor_ids = set()

    for key, var in assignment_vars.items():
        if solver.Value(var) != 1:
            continue

        mentor_id, ptype_code, subject_code = key
        mentor_obj = mentor_data[mentor_id]["object"]
        assigned_mentor_ids.add(mentor_id)

        Assignment.objects.create(
            mentor=mentor_obj,
            practicum_type=ptypes_map.get(ptype_code),
            subject=subjects_map.get(subject_code),
            school=mentor_obj.school,
            academic_year="2025/26",
        )

        assignments_created.append(
            {
                "mentor_name": f"{mentor_obj.last_name}, {mentor_obj.first_name}",
                "practicum_type": ptype_code,
                "subject": subject_code,
            }
        )

    return assignments_created, assigned_mentor_ids


def _get_unassigned_mentors_report(
    all_ids, assigned_ids, skipped_ids, mentor_data, assignment_vars, solver
):
    unassigned_data = []

    fully_unassigned_ids = all_ids - assigned_ids
    if fully_unassigned_ids:
        unassigned_objs = PraktikumsLehrkraft.objects.filter(
            id__in=fully_unassigned_ids
        )
        for pl in unassigned_objs:
            reason = "Solver Optimization (Leftover)"
            if pl.id in skipped_ids:
                reason = "DATA ERROR: No valid eligibilities found."

            unassigned_data.append(
                {
                    "id": pl.id,
                    "name": f"{pl.last_name}, {pl.first_name}",
                    "email": pl.email,
                    "reason": reason,
                    "school": pl.school.name,
                }
            )

    for mentor_id in assigned_ids:
        mentor_obj = mentor_data[mentor_id]["object"]
        capacity = mentor_data[mentor_id]["capacity"]

        actual_count = 0
        for key, var in assignment_vars.items():
            if key[0] == mentor_id and solver.Value(var) == 1:
                actual_count += 1

        if actual_count < capacity:
            missing_slots = capacity - actual_count
            unassigned_data.append(
                {
                    "id": mentor_obj.id,
                    "name": f"{mentor_obj.last_name}, {mentor_obj.first_name}",
                    "email": mentor_obj.email,
                    "reason": f"Partial Assignment: {actual_count}/{capacity} slots filled. Missing {missing_slots}.",
                    "school": mentor_obj.school.name,
                }
            )

    return unassigned_data
