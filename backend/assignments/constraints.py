from collections import defaultdict


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
        if data["capacity"] == 2:
            _enforce_mentor_pair_constraints(
                model, mentor_id, assignment_vars, valid_pairs, all_types
            )


def _enforce_mentor_pair_constraints(
    model, mentor_id, assignment_vars, valid_pairs, all_types
):
    """Helper method to enforce pair constraints for a single mentor."""
    mentor_vars = [v for k, v in assignment_vars.items() if k[0] == mentor_id]

    if not mentor_vars:
        return

    # 1. Determine which types the mentor currently has assigned
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
            # If any var of this type is active, mentor_has[ptype] is True
            model.Add(sum(type_vars) > 0).OnlyEnforceIf(mentor_has[ptype])
            model.Add(sum(type_vars) == 0).OnlyEnforceIf(mentor_has[ptype].Not())

    # 2. Check if mentor is at full capacity (2 assignments)
    is_fully_assigned = model.NewBoolVar(f"mentor_{mentor_id}_full")
    model.Add(sum(mentor_vars) == 2).OnlyEnforceIf(is_fully_assigned)
    model.Add(sum(mentor_vars) != 2).OnlyEnforceIf(is_fully_assigned.Not())

    # 3. Enforce that if full, they must match exactly one valid pair
    valid_pair_clauses = []
    for p1, p2 in valid_pairs:
        is_pair = model.NewBoolVar(f"mentor_{mentor_id}_is_{p1}_{p2}")

        # is_pair is TRUE if mentor has BOTH types
        model.AddBoolAnd([mentor_has[p1], mentor_has[p2]]).OnlyEnforceIf(is_pair)
        model.AddBoolOr([mentor_has[p1].Not(), mentor_has[p2].Not()]).OnlyEnforceIf(
            is_pair.Not()
        )

        valid_pair_clauses.append(is_pair)

    # Constraint: If fully assigned, exactly one valid pair configuration must apply
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
            bucket_key = ptype, program, subject_code
            vars_by_bucket[bucket_key].append(var)

    for _, vars_list in vars_by_bucket.items():
        if vars_list:
            model.Add(sum(vars_list) >= 1)
