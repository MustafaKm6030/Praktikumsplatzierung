from collections import defaultdict
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


def add_capacity_constraints(model, assignment_vars, mentor_data):
    """
    Constraint: Assignments <= Capacity.
    Relaxed to allow partial assignments for MVP.
    """
    for mentor_id, data in mentor_data.items():
        mentor_vars = [
            var for key, var in assignment_vars.items() if key[0] == mentor_id
        ]
        if mentor_vars:
            # This is correct.
            model.Add(sum(mentor_vars) <= data["capacity"])


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
        if data["capacity"] != 2:
            continue

        mentor_vars = [
            var for key, var in assignment_vars.items() if key[0] == mentor_id
        ]
        if not mentor_vars:
            continue

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

        is_fully_assigned = model.NewBoolVar(f"mentor_{mentor_id}_full")
        model.Add(sum(mentor_vars) == 2).OnlyEnforceIf(is_fully_assigned)
        model.Add(sum(mentor_vars) != 2).OnlyEnforceIf(is_fully_assigned.Not())

        valid_pair_clauses = []
        for p1, p2 in valid_pairs:
            is_pair = model.NewBoolVar(f"mentor_{mentor_id}_is_{p1}_{p2}")
            model.AddBoolAnd([mentor_has[p1], mentor_has[p2]]).OnlyEnforceIf(is_pair)
            model.AddBoolOr([mentor_has[p1].Not(), mentor_has[p2].Not()]).OnlyEnforceIf(
                is_pair.Not()
            )
            valid_pair_clauses.append(is_pair)

        model.Add(sum(valid_pair_clauses) == 1).OnlyEnforceIf(is_fully_assigned)


def add_minimum_coverage_constraints(model, assignment_vars, mentor_data):
    """
    HARD CONSTRAINT: Ensure every unique (Subject + Program + Type) combination
    that IS POSSIBLE is assigned at least once.
    """
    vars_by_bucket = defaultdict(list)

    for key, var in assignment_vars.items():
        mentor_id, ptype, subject_code = key

        # We only force coverage for specific subjects (SFP/ZSP)
        if subject_code != "N/A":
            # Lookup the program (GS/MS)
            program = mentor_data[mentor_id]["object"].program

            # Create a granular bucket
            bucket_key = (ptype, program, subject_code)
            vars_by_bucket[bucket_key].append(var)

    for bucket_key, vars_list in vars_by_bucket.items():
        if vars_list:
            model.Add(sum(vars_list) >= 1)


# --- NEW: SOFT CAPACITY LOGIC ---
def add_soft_subject_caps(model, assignment_vars, objective_terms):
    """
    SOFT CONSTRAINT: 'Diminishing Returns'
    - The first N assignments are free (and earn bonuses).
    - The (N+1)th assignment triggers a massive penalty.
    """
    # 1. CONFIGURATION
    STANDARD_CAP = 20  # Limit for Music, Sport, Art, etc.
    CORE_CAP = 30  # Limit for Math (MA), German (D)

    # Must be > (Specific Bonus + Scarcity Bonus) to stop assignment effectively
    OVERFLOW_PENALTY = -70

    CORE_SUBJECTS = {"D", "MA"}

    # 2. GROUP VARIABLES BY SUBJECT
    vars_by_subject = defaultdict(list)
    for key, var in assignment_vars.items():
        _, _, subject_code = key
        if subject_code != "N/A":
            vars_by_subject[subject_code].append(var)

    # 3. APPLY THE LOGIC
    for subject_code, vars_list in vars_by_subject.items():
        if not vars_list:
            continue

        limit = CORE_CAP if subject_code in CORE_SUBJECTS else STANDARD_CAP

        # Count actual assignments
        total_assignments = model.NewIntVar(0, len(vars_list), f"sum_{subject_code}")
        model.Add(total_assignments == sum(vars_list))

        # Calculate Excess
        excess = model.NewIntVar(0, len(vars_list), f"excess_{subject_code}")
        model.Add(excess >= total_assignments - limit)
        model.Add(excess >= 0)

        # Apply the Fine
        objective_terms.append(excess * OVERFLOW_PENALTY)


def set_objective_function(model, assignment_vars, mentor_data, demand_map):
    """
    OBJECTIVE: High Priority on Diversity (Sport/Art), Controlled by Caps.
    """
    UTILIZATION_WEIGHT = 100
    DIVERSITY_WEIGHT = 70

    # LOW SCARCITY: Don't let Supply Size dictate priority
    SCARCITY_WEIGHT = 10

    # HIGH BONUS: Force Sport/Art to be assigned initially
    SPECIFIC_SUBJECT_BONUS = 45

    # LOW CORE: Let Math fill slots, but rely on the higher CAP (55) to get volume
    CORE_SUBJECT_WEIGHT = 15

    # LOW PENALTY: Allow double-assignments for valid subjects
    SAME_SUBJECT_PENALTY = -35

    WEDNESDAY_BONUS = 30
    MIXED_TYPE_BONUS = 20

    CORE_SUBJECTS = {"D", "MA", "E", "AL/WiB"}
    objective_terms = []

    # --- STEP 1: CALCULATE SUBJECT SCARCITY ---
    subject_potential_supply = defaultdict(int)
    for m_data in mentor_data.values():
        for _, scode in m_data["eligibilities"]:
            if scode != "N/A":
                subject_potential_supply[scode] += 1

    # --- STEP 3: BUILD INDIVIDUAL SCORES ---
    for key, var in assignment_vars.items():
        _, practicum_type, subject_code = key

        # 1. Base Score
        score = UTILIZATION_WEIGHT

        # 2. Scarcity & Subject Bonuses
        if subject_code != "N/A":
            score += SPECIFIC_SUBJECT_BONUS

            supply_count = subject_potential_supply.get(subject_code, 1)
            raw_scarcity = int((100 / supply_count) * SCARCITY_WEIGHT)
            score += min(raw_scarcity, 50)

            if subject_code in CORE_SUBJECTS:
                score += CORE_SUBJECT_WEIGHT

        # --- Wednesday Bonus ---
        if practicum_type in ["SFP", "ZSP"]:
            score += WEDNESDAY_BONUS

        objective_terms.append(var * score)

    # --- STEP 4: SCHOOL DIVERSITY ---
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

    # --- STEP 5: MENTOR SUBJECT VARIETY ---
    mentor_subject_vars = defaultdict(lambda: defaultdict(list))
    for key, var in assignment_vars.items():
        m_id, _, s_code = key
        if s_code != "N/A":
            mentor_subject_vars[m_id][s_code].append(var)

    for m_id, subjects_dict in mentor_subject_vars.items():
        for s_code, vars_list in subjects_dict.items():
            is_duplicated = model.NewBoolVar(f"dup_{m_id}_{s_code}")
            model.Add(sum(vars_list) > 1).OnlyEnforceIf(is_duplicated)
            model.Add(sum(vars_list) <= 1).OnlyEnforceIf(is_duplicated.Not())
            objective_terms.append(is_duplicated * SAME_SUBJECT_PENALTY)

    # --- STEP 6: MENTOR TYPE MIXING ---
    for m_id in mentor_data.keys():
        m_vars = [k for k in assignment_vars.keys() if k[0] == m_id]
        if not m_vars:
            continue

        has_block = model.NewBoolVar(f"{m_id}_has_block")
        has_wed = model.NewBoolVar(f"{m_id}_has_wed")

        block_vars = [assignment_vars[k] for k in m_vars if k[1] in ["PDP_I", "PDP_II"]]
        wed_vars = [assignment_vars[k] for k in m_vars if k[1] in ["SFP", "ZSP"]]

        if block_vars:
            model.Add(sum(block_vars) > 0).OnlyEnforceIf(has_block)
            model.Add(sum(block_vars) == 0).OnlyEnforceIf(has_block.Not())
        else:
            model.Add(has_block == 0)

        if wed_vars:
            model.Add(sum(wed_vars) > 0).OnlyEnforceIf(has_wed)
            model.Add(sum(wed_vars) == 0).OnlyEnforceIf(has_wed.Not())
        else:
            model.Add(has_wed == 0)

        is_mixed = model.NewBoolVar(f"{m_id}_is_mixed")
        model.AddBoolAnd([has_block, has_wed]).OnlyEnforceIf(is_mixed)
        model.AddBoolOr([has_block.Not(), has_wed.Not()]).OnlyEnforceIf(is_mixed.Not())
        objective_terms.append(is_mixed * MIXED_TYPE_BONUS)

    # --- STEP 7: APPLY SOFT CAPS (The new Equalizer) ---
    add_soft_subject_caps(model, assignment_vars, objective_terms)

    model.Maximize(sum(objective_terms))
