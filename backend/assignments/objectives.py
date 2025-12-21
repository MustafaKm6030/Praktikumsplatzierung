from collections import defaultdict


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

    CORE_SUBJECTS = {"D", "MA"}
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
