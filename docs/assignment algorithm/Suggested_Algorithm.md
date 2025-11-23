Complete Algorithm Plan: Hybrid Optimization for Lehramt Student Assignments
Our goal is to Develop an efficient, scalable, and robust system to assign Lehramt students from Uni Passau to practicum mentors (PLs) at various schools, satisfying all hard constraints and optimizing for soft constraints, with adaptability for dynamic changes.
Phase 1: Data Preparation and Pre-processing (Enhanced for Scalability)
1.	Parse and Validate Excel Data:
o	Load all data from the official Excel sheets (PL profiles, school information, student demand, previous year's assignments).
o	Validate data integrity (e.g., ensure all required fields, correct formats).
o	Identify and mark "nicht" (cannot assign) and "leer" (can assign) cells in the assignment columns for each PL.
o	Data Model Creation: Establish a structured internal data model for:
	PLs: Unique ID, School ID, Program Type (GS/MS eligibility), Subjects taught (primary, secondary), Practicum Eligibility (PDP I, PDP II, SFP, ZSP), Declared Available Credit Hours (implies Max 2 Internships), Last Year's Assignments (Practicum Type, School).
	Schools: Unique ID, Name, Type (GS/MS), Location (Zone 1/2/3), Relevant Public Transport Hubs, Available Mentors per Subject & Practicum Type, Historical Assignments.
	Students (Current Demand): Unique ID, Program Type (GS/MS), Primary/Secondary/Specialized Subjects, Home Location (for block internships), Preferred Practicum Type, and any collected preferences.
	Internship Demand: For each unique combination of (Practicum Type, Program Type, Subject), the exact number of PLs required (e.g., SFP-GS-German: 12 PLs). This accounts for subject grouping rules for SFP/ZSP.
2.	Calculate Derived Data (Precomputed for Efficiency):
o	PL Eligibility Matrix/Sets: For every PL, precompute a comprehensive list of all (Practicum Type, Subject, School_ID) combinations they are eligible to supervise. This must incorporate:
	GS/MS match (mentor program type == student program type).
	Mentor's teaching subject matches internship subject (for SFP/ZSP).
	PL's school matches School_ID.
	PL is marked eligible for the Practicum Type.
	PL is not marked "nicht" for that Practicum Type in their school's column.
	PL is not currently assigned 2 internships (initial state).
o	School Capacity & Offerings: For every school, for every (Practicum Type, Subject) combination, precompute the set of eligible PLs available at that school:
	School_Offerings[School_ID][PracticumType][Subject] = { PL_ID_1, PL_ID_2, ... }.
o	Travel Times & Reachability Matrix:
	Precompute and store public transport travel times:
	From Uni Passau to all schools (for Wednesday internships).
	From common student home areas to all schools (for block internships).
	Zone & Time Constraint Marking: For each school and for each practicum type, mark if it's reachable within the specified time limits and zones:
	SFP/ZSP (Wednesday): School must be Zone 1 or 2, max 30 mins (4a schools) / 60 mins (4b schools) travel from Uni. Mark School_SFP_ZSP_Reachable[School_ID] = True/False.
	PDP I/II (Block): School within acceptable distance (Zone 1/2/3) from student home areas. Mark School_PDP_Reachable[School_ID] = True/False.
	Public Transport-Only Constraint: Ensure reachability is strictly by public transport.
o	Subject Groupings: Store the specific rules for GS and MS subject grouping that apply to Wednesday practicums (SFP/ZSP).
Phase 2: Hard Constraint Enforcement (Hybrid Optimization with CP-SAT/ILP Solver)
This phase focuses on finding an assignment that strictly adheres to all hard constraints.
1.	Initialize Solver Model (OR-Tools CP-SAT or ILP):
o	Variables:
	assign[PL_ID][PracticumType][Subject][School_ID]: Binary variable (0 or 1) indicating if a specific PL is assigned to a specific practicum type and subject at a specific school.
	num_internships[PL_ID]: Integer variable representing the number of internships assigned to a PL.
	pair_valid[PL_ID][PType1][PType2]: Binary variable indicating if a PL's two assigned internships form a valid pair.
o	Hard Constraints (Translate to Solver Constraints):
	GS/MS Match: assign[pl][pt][sub][school] implies pl.program_type == student_demand.program_type and school.type == student_demand.program_type.
	Mentor Subject Match (SFP/ZSP): assign[pl][SFP/ZSP][sub][school] implies pl.teaches_subject(sub).
	Every PL Supervises Exactly 2 Internships: num_internships[pl] == 2 for all PLs that can take 2. (Alternatively: num_internships[pl] <= 2 if some PLs might only take 1, and ensure the sum(X_pl_*) over all internships for a PL meets demand). The input states "each supervise 2 praktikum", so num_internships[pl] == 2 for assigned PLs.
	Valid Internship Pairs: If num_internships[pl] == 2, then pair_valid[pl][PType1][PType2] == 1 for the assigned types. Define allowed pairs explicitly.
	PL at Own School: assign[pl][pt][sub][school] implies pl.school_id == school_id.
	Credit Hour Budget: Implicitly handled by "2 internships per PL," as 210 credited hours covers 2 internships per PL.
	Single Subject Mentor Priority (Mandatory): If pl is the sole mentor for sub at school, and demand[pt][sub] exists, force assign[pl][pt][sub][school] = 1.
	Subject Group Matching (GS/MS): Apply the pre-defined subject grouping rules for SFP/ZSP demand.
	Demand Quotas Exactly Satisfied: For each (Practicum Type, Program Type, Subject) demand: sum(assign[pl][pt][sub][school]) for all pl, school == Demand_Count.
	Reassignments within Category Structure: When reassigning, new assignments must respect original practicum type (if possible, or a closely related type if flexibility is allowed).
	Travel Times & Public Transport:
	For SFP/ZSP: If assign[pl][SFP/ZSP][sub][school] == 1, then School_SFP_ZSP_Reachable[school_id] == True.
	For PDP I/II: If assign[pl][PDP I/II][sub][school] == 1, then School_PDP_Reachable[school_id] == True (considering student home locations if students are assigned directly).
	"Nicht" Schools: If PL is marked "nicht" for a practicum type at their school, then assign[pl][pt][sub][pl.school_id] == 0.
	No Mid-Year School Transfers: PL's school is fixed from the input data.
	Red/Yellow Marked Cells: Force these assignments: assign[specific_pl][specific_pt][specific_sub][specific_school] = 1.
2.	Initial Feasible Solution (Optional Greedy Warm Start):
o	A greedy heuristic can be used to generate an initial feasible solution (satisfying hard constraints) before invoking the solver. This can speed up solver execution.
o	Greedy Strategy (if used):
1.	Prioritize Fixed Assignments: Process all Red/Yellow cells and Single Subject Mentor assignments first.
2.	Constraint Propagation: As assignments are made, immediately update eligibility and capacity for other PLs and schools.
3.	Prioritized PL Selection: Use a priority queue to select the next PL to assign based on the fewest remaining eligible options. This tackles the most constrained choices first.
4.	Limited Backtracking: If a greedy assignment leads to an immediate hard constraint violation or an unfillable demand slot, attempt to reverse the last conflicting assignment and try the next available option. This is a shallow back-off.
3.	Solver Execution:
o	Feed the model (variables, hard constraints, and potentially the initial greedy solution) into the OR-Tools CP-SAT or ILP solver.
o	The solver's primary goal in this sub-phase is to find any feasible solution that satisfies all hard constraints.
Phase 3: Soft Constraint Optimization (Solver-Driven with Explicit Weighting)
Once a hard-constrained feasible solution is found, the solver optimizes it against soft constraints.
1.	Soft Constraint Weighting: Assign explicit numeric weights to each soft constraint, reflecting their priority. Higher weights mean higher importance.
o	W_min_travel_time_cum (for Wednesday, e.g., 1000) - Minimize total travel time for students assigned to same PL.
o	W_min_changes_last_year (e.g., 800) - Maximize continuity for PLs.
o	W_balance_subject_load (e.g., 600) - Distribute subject responsibilities evenly.
o	W_prefer_closest_school (e.g., 400) - For students, choose nearest school within allowed zone.
o	W_spread_internship_types_school (e.g., 300) - Distribute internship types within a school.
o	W_avoid_overlap (e.g., -200, as a penalty) - Minimize overlaps in calendar time for a PL.
o	W_avoid_clustering_zone3 (e.g., 150) - Distribute assignments across zones, avoiding over-reliance on Zone 3.
o	W_pl_preference (e.g., 100) - Assign PLs to preferred internships if possible.
2.	Objective Function (for Solver):
o	Define a linear objective function that the solver will maximize. This function is a sum of terms, where each term represents a soft constraint multiplied by its weight.
o	Example: Maximize (W_min_travel_time_cum * (1 - TotalTravelTime)) + (W_min_changes_last_year * NumMatchesLastYear) + ... (Note: "minimize" goals are converted to "maximize" by (max_value - actual_value)).
3.	Solver Execution: The solver re-runs, using the previously found feasible solution as a starting point, to find the assignment that maximizes this weighted objective function while still satisfying all hard constraints.
Phase 4: Dynamic Changes & Reassignments (Iterative Solver Application)
This phase handles changes that occur after an initial assignment, such as at the winter semester or due to unforeseen circumstances.
1.	Input Current Plan & Changes:
o	Load the existing assignment plan.
o	Receive updates:
	Unavailable PLs (illness, absence).
	Students switching programs/subjects, affecting demand quotas.
	New demand/supply.
o	"Unassign" Affected Slots: Mark PLs as removed, and decrement demand quotas for affected practicums.
2.	Solver Re-run (Adjustments):
o	Re-initialize the solver model with the updated set of PLs and demand.
o	Constraint: Minimize Changes: Add a strong soft constraint (with a very high weight) to minimize changes from original PDP I / ZSP assignments unless absolutely necessary. This will guide the solver to preserve as many existing stable assignments as possible.
o	Reassignment Constraint: Ensure reassignments occur within the same internship category structure.
o	Run the solver (Phase 2 & 3) again to find a new optimal solution given the changes.

Phase 5: Output, Visualization & Reporting (Comprehensive)
1.	Generate Final Assignment Plan:
o	Output a clear, structured list of all PL_ID → (Practicum_Type, Subject, School_ID, Assigned_Students) assignments.
2.	Comprehensive Reporting:
o	Assignment Matrix: A visual matrix showing PL_ID x Practicum_Type x School_ID and indicating Assigned/Not Assigned.
o	Unmet Demand/Conflicts: Explicitly list any demand quotas that could not be fully met by the solver (indicating an infeasible problem given hard constraints). Highlight these for manual review and potential modification of constraints.
o	PL Workload Summary: For each PL, detail assigned practicums, subjects, and confirmation of 2 internships (or 1 if credit hours allow, or if no valid second pair found).
o	School Load Summary: For each school, list all assigned practicums, involved PLs, and student counts.
o	Soft Constraint Achievement: Report on the final objective function score. For each soft constraint, provide a metric (e.g., "X% of PLs assigned to same school as last year," "Average travel time for Wednesday internships: Y minutes," "Z schools have balanced internship types").
o	Travel Time Analysis (Student Level - if implemented): If individual student assignments are part of the model, report travel times for each student, especially for Wednesday internships, flagging any near the maximum limits.
o	Comparison to Last Year: Show statistics on how many assignments changed compared to the previous year.

Important notes:
•	Precomputation of eligibility sets and using a solver (like OR-Tools) are crucial for handling a large number of PLs, schools, and students efficiently.
•	Student-Level Assignment:
o	To implement this, the solver model would need to include variables for assign_student[Student_ID][PL_ID][PracticumType].
o	Additional constraints would be needed for student-specific preferences, home location-based travel for PDP, and ensuring a PL isn't overbooked beyond their single (SFP group) or (ZSP group) capacity.
o	The W_min_travel_time_cum soft constraint would be specifically applied here to groups of students assigned to the same PL.
•	Input Data Flexibility: Ensure the Excel parser is robust to minor variations in input structure, though the constraint is to use the "official Excel list as the single source of truth."
•	Public Transport Schedules: We need to account for these by integrating external timetable data or by pre-calculating realistic travel times based on known schedules. This strengthens the "public transport is a hard constraint."

