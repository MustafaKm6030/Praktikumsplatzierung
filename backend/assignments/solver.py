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


def run_solver():
    print("\n=== 🕵️ STARTING PERMISSIVE SOLVER (MVP MODE) ===")
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
    set_objective_function(model, assignment_vars, mentor_data, demand_map)

    # 5. Solve & Process
    print("\n--- Solving ---")
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    return _process_solver_results(
        status, solver, assignment_vars, mentor_data, all_ids, skipped_ids
    )


def _prepare_supply_variables(model, all_mentors):
    """
    Iterates through mentors, validates data, and creates optimization variables.
    Returns: assignment_vars, mentor_data, (all_ids, skipped_ids)
    """
    assignment_vars = {}
    mentor_data = {}
    all_ids = set()
    skipped_ids = set()

    for mentor in all_mentors:
        all_ids.add(mentor.id)
        capacity = get_mentor_capacity(mentor)
        eligibilities = calculate_eligibility_for_pl(mentor)

        # Validation Check
        if not _validate_mentor_data(mentor, capacity, eligibilities):
            skipped_ids.add(mentor.id)
            continue

        mentor_data[mentor.id] = {
            "capacity": capacity,
            "eligibilities": eligibilities,
            "object": mentor,
        }

        # Create Variables
        for practicum_type, subject_code in eligibilities:
            var_key = mentor.id, practicum_type, subject_code
            assignment_vars[var_key] = model.NewBoolVar(
                f"assign_{mentor.id}_{practicum_type}_{subject_code}"
            )

    return assignment_vars, mentor_data, (all_ids, skipped_ids)


def _prepare_demand_map():
    """Aggregates demand into a lookup dictionary."""
    demand_data = aggregate_demand()
    demand_map = {}
    for d in demand_data:
        key = d["practicum_type"], d["program_type"], d["subject_code"]
        demand_map[key] = d["required_slots"]
    return demand_map


def _process_solver_results(
    status, solver, assignment_vars, mentor_data, all_ids, skipped_ids
):
    """Handles the solver outcome, saves to DB, and generates the report."""
    results = {
        "status": "FAILURE",
        "assignments": [],
        "unassigned": [],
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"✅ Solution found in {solver.WallTime()}s!")

        with transaction.atomic():
            # Save assignments
            assignments_created, assigned_ids = _save_assignments_to_db(
                solver, assignment_vars, mentor_data
            )
            print(f"Saved {len(assignments_created)} assignments to database.")

            # Calculate report
            unassigned_data = _get_unassigned_mentors_report(
                all_ids, assigned_ids, skipped_ids
            )

            results["status"] = "SUCCESS"
            results["assignments"] = assignments_created
            results["unassigned"] = unassigned_data
    else:
        print("❌ No solution found.")

    return results


def _validate_mentor_data(mentor, capacity, eligibilities):
    """Checks if mentor has enough subjects/types to meet capacity constraints."""
    if len(eligibilities) < capacity:
        print(f"⚠️ Skipping Mentor {mentor.id}: Not enough eligibility options.")
        return False

    unique_types = set(e[0] for e in eligibilities)
    if capacity == 2 and len(unique_types) < 2:
        print(f"⚠️ Skipping Mentor {mentor.id}: Capacity 2 requires 2 different types.")
        return False

    return True


def _save_assignments_to_db(solver, assignment_vars, mentor_data):
    """Extracts results from the solver and saves them to the DB."""
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


def _get_unassigned_mentors_report(all_ids, assigned_ids, skipped_ids):
    """Generates the report list for unassigned mentors."""
    unassigned_ids = all_ids - assigned_ids
    unassigned_data = []

    if unassigned_ids:
        unassigned_objs = PraktikumsLehrkraft.objects.filter(id__in=unassigned_ids)
        for pl in unassigned_objs:
            reason = "Solver Optimization (Leftover)"
            if pl.id in skipped_ids:
                reason = "DATA ERROR: Invalid Capacity/Subjects"

            unassigned_data.append(
                {
                    "id": pl.id,
                    "name": f"{pl.last_name}, {pl.first_name}",
                    "email": pl.email,
                    "reason": reason,
                    "school": pl.school.name,
                }
            )

    return unassigned_data


def add_capacity_constraints(model, assignment_vars, mentor_data):
    for mentor_id, data in mentor_data.items():
        mentor_vars = [
            var for key, var in assignment_vars.items() if key[0] == mentor_id
        ]
        if mentor_vars:
            model.Add(sum(mentor_vars) == data["capacity"])


def add_valid_pairs_constraints(model, assignment_vars, mentor_data):
    valid_pairs = [
        ("PDP_I", "PDP_II"),
        ("PDP_I", "SFP"),
        ("PDP_I", "ZSP"),
        ("PDP_II", "SFP"),
        ("PDP_II", "ZSP"),
        ("SFP", "ZSP"),
    ]
    all_types = ["PDP_I", "PDP_II", "SFP", "ZSP"]

    for mentor_id, data in mentor_data.items():
        if data["capacity"] == 2:
            _constrain_mentor_to_valid_pair(
                model, mentor_id, assignment_vars, all_types, valid_pairs
            )


def _constrain_mentor_to_valid_pair(
    model, mentor_id, assignment_vars, all_types, valid_pairs
):
    mentor_has = {}
    for ptype in all_types:
        mentor_has[ptype] = model.NewBoolVar(f"mentor_{mentor_id}_has_{ptype}")
        type_vars = [
            var
            for key, var in assignment_vars.items()
            if key[0] == mentor_id and key[1] == ptype
        ]

        if not type_vars:
            model.Add(mentor_has[ptype] == 0)
        else:
            model.Add(sum(type_vars) > 0).OnlyEnforceIf(mentor_has[ptype])
            model.Add(sum(type_vars) == 0).OnlyEnforceIf(mentor_has[ptype].Not())

    model.Add(sum(mentor_has.values()) == 2)

    valid_pair_clauses = []
    for p1, p2 in valid_pairs:
        is_pair = model.NewBoolVar(f"mentor_{mentor_id}_is_{p1}_{p2}")
        model.AddBoolAnd([mentor_has[p1], mentor_has[p2]]).OnlyEnforceIf(is_pair)
        model.AddBoolOr([mentor_has[p1].Not(), mentor_has[p2].Not()]).OnlyEnforceIf(
            is_pair.Not()
        )
        valid_pair_clauses.append(is_pair)

    model.Add(sum(valid_pair_clauses) == 1)


def set_objective_function(model, assignment_vars, mentor_data, demand_map):
    DEMAND_WEIGHT = 10
    DIVERSITY_WEIGHT = 5
    objective_terms = []

    # 1. Prioritize Demand
    for key, var in assignment_vars.items():
        mentor_id, practicum_type, subject_code = key
        mentor_program = mentor_data[mentor_id]["object"].program
        demand_key = practicum_type, mentor_program, subject_code
        student_count = demand_map.get(demand_key, 0)

        if student_count > 0:
            objective_terms.append(var * (student_count * DEMAND_WEIGHT))

    # 2. Diversity
    school_vars = {}
    for key, var in assignment_vars.items():
        mentor_id, ptype, _ = key
        school_id = mentor_data[mentor_id]["object"].school_id
        if school_id not in school_vars:
            school_vars[school_id] = {}
        if ptype not in school_vars[school_id]:
            school_vars[school_id][ptype] = []
        school_vars[school_id][ptype].append(var)

    for school_id, types_dict in school_vars.items():
        for ptype, vars_list in types_dict.items():
            school_has_type = model.NewBoolVar(f"school_{school_id}_has_{ptype}")
            model.Add(sum(vars_list) > 0).OnlyEnforceIf(school_has_type)
            model.Add(sum(vars_list) == 0).OnlyEnforceIf(school_has_type.Not())
            objective_terms.append(school_has_type * DIVERSITY_WEIGHT)

    model.Maximize(sum(objective_terms))
