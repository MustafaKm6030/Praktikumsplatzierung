from collections import defaultdict
from system_settings.services import get_active_settings
from subjects.models import Subject
import re


def add_soft_subject_caps(model, assignment_vars, objective_terms, core_subjects):
    """
    SOFT CONSTRAINT: 'Diminishing Returns'
    - The first N assignments are free (and earn bonuses).
    - The (N+1)th assignment triggers a massive penalty.
    """
    # 1. CONFIGURATION
    STANDARD_CAP = 20
    CORE_CAP = 30

    OVERFLOW_PENALTY = -70

    CORE_SUBJECTS = set(core_subjects) if core_subjects else {"D", "MA"}

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
    Orchestrator for the objective function.
    Aggregates scores from individual assignments, diversity bonuses, and penalties.
    """
    objective_terms = []

    settings = get_active_settings()
    core_subjects_list = (
        settings.core_subjects if settings.core_subjects else ["D", "MA"]
    )
    core_subjects_set = set(core_subjects_list)

    config = {
        "UTILIZATION_WEIGHT": 100,
        "DIVERSITY_WEIGHT": 70,
        "SCARCITY_WEIGHT": 10,
        "SPECIFIC_SUBJECT_BONUS": 45,
        "CORE_SUBJECT_WEIGHT": 15,
        "SAME_SUBJECT_PENALTY": -35,
        "WEDNESDAY_BONUS": 30,
        "MIXED_TYPE_BONUS": 20,
        "CONTINUITY_BONUS": 70,
        "CORE_SUBJECTS": core_subjects_set,
    }

    _add_individual_scores(objective_terms, assignment_vars, mentor_data, config)

    _add_school_diversity_bonus(
        model, objective_terms, assignment_vars, mentor_data, config
    )

    _add_mentor_subject_penalty(model, objective_terms, assignment_vars, config)

    _add_mentor_mixing_bonus(
        model, objective_terms, assignment_vars, mentor_data, config
    )

    _add_continuity_scores(objective_terms, assignment_vars, mentor_data, config)

    add_soft_subject_caps(model, assignment_vars, objective_terms, core_subjects_list)

    model.Maximize(sum(objective_terms))


def _add_individual_scores(objective_terms, assignment_vars, mentor_data, config):
    """Calculates the base score for every possible assignment."""

    # Calculate Supply for Scarcity Logic
    subject_potential_supply = defaultdict(int)
    for m_data in mentor_data.values():
        for _, scode in m_data["eligibilities"]:
            if scode != "N/A":
                subject_potential_supply[scode] += 1

    for key, var in assignment_vars.items():
        _, practicum_type, subject_code = key

        score = config["UTILIZATION_WEIGHT"]

        # Subject-specific Bonuses
        if subject_code != "N/A":
            score += config["SPECIFIC_SUBJECT_BONUS"]

            # Scarcity Bonus
            supply_count = subject_potential_supply.get(subject_code, 1)
            raw_scarcity = int((100 / supply_count) * config["SCARCITY_WEIGHT"])
            score += min(raw_scarcity, 50)

            if subject_code in config["CORE_SUBJECTS"]:
                score += config["CORE_SUBJECT_WEIGHT"]

        # Wednesday Bonus
        if practicum_type in ["SFP", "ZSP"]:
            score += config["WEDNESDAY_BONUS"]

        objective_terms.append(var * score)


def _add_school_diversity_bonus(
    model, objective_terms, assignment_vars, mentor_data, config
):
    """Rewards schools that host multiple different types of practicums."""
    school_vars = defaultdict(lambda: defaultdict(list))

    for key, var in assignment_vars.items():
        mentor_id, ptype, _ = key
        school_id = mentor_data[mentor_id]["object"].school_id
        school_vars[school_id][ptype].append(var)

    for school_id, types_dict in school_vars.items():
        for ptype, vars_list in types_dict.items():
            school_has_type = model.NewBoolVar(f"school_{school_id}_has_{ptype}")

            # Link boolean to existence of assignments
            model.Add(sum(vars_list) > 0).OnlyEnforceIf(school_has_type)
            model.Add(sum(vars_list) == 0).OnlyEnforceIf(school_has_type.Not())

            objective_terms.append(school_has_type * config["DIVERSITY_WEIGHT"])


def _add_mentor_subject_penalty(model, objective_terms, assignment_vars, config):
    """Penalizes assigning the exact same subject twice to the same mentor."""
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

            objective_terms.append(is_duplicated * config["SAME_SUBJECT_PENALTY"])


def _add_mentor_mixing_bonus(
    model, objective_terms, assignment_vars, mentor_data, config
):
    """Rewards mentors who take a mix of Block (PDP) and Wednesday (SFP/ZSP) types."""
    block_types = {"PDP_I", "PDP_II"}
    wed_types = {"SFP", "ZSP"}

    for m_id in mentor_data.keys():
        # Get all variables for this mentor
        m_vars = {k: v for k, v in assignment_vars.items() if k[0] == m_id}
        if not m_vars:
            continue

        block_vars = [v for k, v in m_vars.items() if k[1] in block_types]
        wed_vars = [v for k, v in m_vars.items() if k[1] in wed_types]

        has_block = model.NewBoolVar(f"{m_id}_has_block")
        has_wed = model.NewBoolVar(f"{m_id}_has_wed")

        # Define has_block
        if block_vars:
            model.Add(sum(block_vars) > 0).OnlyEnforceIf(has_block)
            model.Add(sum(block_vars) == 0).OnlyEnforceIf(has_block.Not())
        else:
            model.Add(has_block == 0)

        # Define has_wed
        if wed_vars:
            model.Add(sum(wed_vars) > 0).OnlyEnforceIf(has_wed)
            model.Add(sum(wed_vars) == 0).OnlyEnforceIf(has_wed.Not())
        else:
            model.Add(has_wed == 0)

        # Define Mixed State
        is_mixed = model.NewBoolVar(f"{m_id}_is_mixed")
        model.AddBoolAnd([has_block, has_wed]).OnlyEnforceIf(is_mixed)
        model.AddBoolOr([has_block.Not(), has_wed.Not()]).OnlyEnforceIf(is_mixed.Not())

        objective_terms.append(is_mixed * config["MIXED_TYPE_BONUS"])


def _build_subject_name_map():
    """Builds a cache to map 'deutsch' -> 'D', 'mathematik' -> 'MA', etc."""
    if SUBJECT_NAME_TO_CODE_MAP:
        return
    for subject in Subject.objects.all():
        SUBJECT_NAME_TO_CODE_MAP[subject.name.lower()] = subject.code


def _get_historical_subject_code(history_text: str) -> str:
    """Parses messy history text to find a specific subject code."""
    text = history_text.lower()
    for name, code in SUBJECT_NAME_TO_CODE_MAP.items():
        if re.search(r"\b" + re.escape(name) + r"\b", text):
            return code
    return ""


SUBJECT_NAME_TO_CODE_MAP = {}


def _add_continuity_scores(objective_terms, assignment_vars, mentor_data, config):
    """Reward assignments that match the mentor's history."""
    if not SUBJECT_NAME_TO_CODE_MAP:
        _build_subject_name_map()

    bonus_value = config["CONTINUITY_BONUS"]

    for (mentor_id, ptype, subject_code), var in assignment_vars.items():
        mentor_obj = mentor_data[mentor_id]["object"]
        history_value = _get_raw_history(mentor_obj, ptype)

        if history_value and _is_continuity_match(history_value, ptype, subject_code):
            objective_terms.append(var * bonus_value)


def _get_raw_history(mentor_obj, ptype):
    """Maps project type to the corresponding mentor attribute."""
    mapping = {
        "PDP_I": mentor_obj.history_pdp1,
        "PDP_II": mentor_obj.history_pdp2,
        "SFP": mentor_obj.history_sfp,
        "ZSP": mentor_obj.history_zsp,
    }
    return mapping.get(ptype, "")


def _is_continuity_match(history_value, ptype, subject_code):
    """Determines if the history string constitutes a match."""
    val_lower = history_value.lower().strip()

    # Quick exit for negatives
    if any(kw in val_lower for kw in ["nicht", "nein", "keine"]):
        return False

    # Generic markers
    is_generic = val_lower in ["ja", "hier", "x"]

    if ptype in ["PDP_I", "PDP_II"]:
        return subject_code == "N/A" and is_generic

    # Specific Subject Match for SFP/ZSP
    historical_code = _get_historical_subject_code(history_value)
    return (historical_code == subject_code) if historical_code else is_generic
