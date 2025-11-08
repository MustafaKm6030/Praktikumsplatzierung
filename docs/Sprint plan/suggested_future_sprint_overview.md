Sprint 1: Foundation & Data Ingestion
Goal: Establish core data models, UI framework, and initial data ingestion for PLs, Schools, and Students.
* Frontend Focus:
o UI Scaffold & Navigation: Implement basic layout, navigation menus (Dashboard, Students, Schools, PLs, Settings), and placeholder pages based on mockups. (Dashboard, Students, Schools, PL Management, System Settings shells).
o System Settings UI: Build the UI for "System Settings" (Academic Year, Uni Info, Deadlines).
o School Management UI (List View): Develop the table view, search, and filtering for "School Management" UI.
o PL Management UI (List View): Develop the table view, search, and filtering for "PL Management" UI.
o Student Management UI (List View): Develop the table view, search, and filtering for "Student Management" UI.
* Backend Focus:
o Database Setup: Design and implement the initial database schema for Schools, PLs, Students, and System Settings.
o API Endpoints - Schools: Create REST API endpoints for Schools (CRUD operations - Add, Get All, Get by ID, Update, Delete). Implement "Import/Export School List" backend.
o API Endpoints - PLs: Create REST API endpoints for PLs (CRUD operations).
o API Endpoints - Students: Create REST API endpoints for Students (CRUD operations). Implement "Import/Export Students" backend.
o API Endpoints - System Settings: Create API endpoints for saving/retrieving System Settings.
DoD: Core database schema implemented. Backend APIs for Schools, PLs, Students, and System Settings are functional (Create/Read/Update/Delete). Frontend UIs for these sections display static/mock data but are structured to consume API data. Basic UI navigation works.

Sprint 2: Demand, Eligibility & Basic Dashboard
Goal: Implement algorithm's pre-processing for eligibility and reachability, and integrate the "Demand Overview" UI with actual data.
* Frontend Focus:
o Demand Overview UI: Implement the "Demand Overview" UI (Praktika Planning & Allocation mockup - Step 1), including charts for Total Demand, Demand by Practikum Type, Demand by Subject, Demand Distribution Details.
o Dashboard - Practicum Status: Implement the "Practicum Status Overview" widget on the Dashboard, pulling dynamic data for allocated percentages.
o School Management UI (Map View Basic): Implement the map component for the "School Management" UI, showing school locations (without dynamic capacity colors yet).
* Backend Focus:
o Student Demand Aggregation: Implement logic to aggregate student data and calculate the Total Demand by (Practicum Type, Program Type, Subject). Create API for this.
o PL Eligibility Pre-calculation: Implement the backend logic for PL Eligibility Sets (Algorithm Phase 1), considering school type, PL subjects, PL program type, and "nicht" markings. Create an API to expose this.
o School Reachability Pre-calculation: Implement logic for Travel Times & Reachability Matrix (Algorithm Phase 1). This is a complex task:
* Focus on defining the data structures for storing travel times and implementing the core logic for zone-based reachability (Zone 1/2/3) and public transport limits (1/2 hour, 1 hour).
* Focus on initial setup for external mapping/public transport API integration (e.g., configuring API keys, making initial test calls, defining data input/output for future detailed integration).
o Subject Grouping Logic: Implement backend logic for GS/MS subject grouping rules for SFP/ZSP.
o Dashboard API: Create API endpoints to provide data for the "Practicum Status Overview" widget.
DoD: Demand calculations displayed in the UI are dynamic and accurate. PL eligibility and school reachability are correctly computed on the backend. Subject grouping logic is active. Dashboard practicum status shows real data. Basic map view is functional.
Sprint 3: Core Assignment Engine - Hard Constraints
Goal: Integrate the CP-SAT solver and implement all hard constraints to produce the first feasible assignment solution.
* Frontend Focus:
o Praktika Planning & Allocation Workflow: Build the skeletal UI for the multi-step "Praktika Planning & Allocation" workflow (Steps 1, 2, 3, 4).
o "Run Auto-Allocation" Button: Implement the "Run Auto-Allocation" button (Step 2) and connect it to a backend API endpoint.
o Basic Assignment Results Display: Design and implement a basic, read-only UI component (table or list) to display the assignments returned by the solver (initially showing only PL ID, Practicum Type, School ID).
o Loading/Processing States: Implement visual feedback for when the solver is running.
* Backend Focus:
o Solver Integration:
* Integrate the OR-Tools CP-SAT solver library. Create the solver model, define variables (assign[PL][PT][Sub][School]), and num_internships[PL].
* Implement the API endpoint for "Run Auto-Allocation," which triggers the solver.
o Hard Constraint Implementation - Part 1 (Core Matching):
*  Implement solver constraints for: GS/MS matching, Mentor's subject match (SFP/ZSP), PL at own school, "nicht" schools.
* Implement solver constraints for: Red/Yellow marked cells (fixed assignments), valid internship pairs, and the num_internships[PL] == 2 constraint for assigned PLs.
o Hard Constraint Implementation - Part 2 (Demand, Capacity, Travel):
* Implement solver constraints for exact demand quotas (sum(assignments) == Demand_Count).
* Implement solver constraints for SFP/ZSP travel time/zone limits using the precomputed reachability data.
DoD: The CP-SAT solver can be invoked via the UI button. All critical hard constraints are modeled in the solver. The solver successfully finds a feasible solution that respects all hard constraints and the basic assignment results are displayed in the UI.
Sprint 4: Optimization & Initial Reporting
Goal: Integrate soft constraints into the solver, implement the optimization objective, and populate key dashboard and reporting widgets.
* Frontend Focus:
o Budget Overview Dashboard: Implement the "Budget Overview" widget (Budget & Reporting mockup) (Total, Allocated, Remaining, Utilization, Pie Chart).
o Budget Distribution by School: Implement the bar chart for "Budget Distribution by School."
o PL Management - Capacity Display: Update the "PL Management" table to display Kapazität and Zugewiesene Studierende dynamically.
o Assignment Configuration UI: Create a UI for viewing/editing soft constraint weights (e.g., a "Configuration" tab within "Praktika Planning & Allocation" or a dedicated "Assignment Settings" under "Settings").
* Backend Focus:
o Soft Constraint Modeling (Initial):
* Model W_min_changes_last_year (requires tracking last year's assignments) and W_avoid_overlap (requires basic time slot data, can be simple at first).
* Model W_min_travel_time_cum (for SFP/ZSP, requires aggregating travel times if multiple students are assigned to a PL, assuming student-level assignment is implicit for demand) and W_prefer_closest_school.
o Solver Objective Function: Define the solver's objective function as the weighted sum of implemented soft constraints.
o Budget Data API: Create API endpoints to provide data for the "Budget Overview" and "Budget Distribution by School" widgets.
o PL Capacity API: Create API endpoints to provide data for PL Kapazität and Zugewiesene Studierende.
o Configuration API: Create API endpoints for soft constraint weights.
DoD: The solver produces an optimized solution based on soft constraint weights. All dashboard budget widgets are accurately displayed. PL capacity and assigned students are visible. Soft constraint weights can be configured.

Sprint 5: Dynamic Adjustments & Comprehensive Reports
Goal: Implement dynamic reassignment logic, comprehensive reporting, and the finalization steps for an assignment cycle.
* Frontend Focus:
o "Review & Adjust" UI Enhancements: Improve the "Review & Adjust" UI (Step 3) to allow for basic manual overrides or flagging of assignments. (Note: Full manual adjustment workflow might be a later sprint depending on complexity).
o "Apply Winter Semester Changes" UI: Implement the UI trigger for dynamic reassignments.
o System Alerts: Implement the "System Alerts" widget on the Dashboard (e.g., Low Remaining Budget, Students Without Placement).
o Student Placement Status: Update the "Students" table to accurately display "Placement Status" (Placed, Unplaced, In Review) based on solver output.
o School Management Map View (Capacity): Implement dynamic color-coding for schools on the map based on capacity status (High, Medium, Low, Full).
o Reports & Analytics UI: Implement the UI for the "Reports & Analytics" section with functional "View" buttons (even if reports are simple lists initially).
* Backend Focu:
o Dynamic Reassignment Logic:
* Implement the backend logic for identifying unavailable PLs and updated demand. Implement the process for "unassigning" affected slots.
*  Enhance the solver model with the "minimize changes from original assignments" strong soft constraint and enforce "reassignment within category structure." Create the API endpoint for triggering reassignments.
o Reporting APIs: Create backend logic and APIs to generate data for all predefined reports:
* Student Placement Report.
* PL Workload & Anrechnungsstunden Report.
* School Capacity & Utilization Report.
* Unplaced Students Report (identifying reasons for unplacement).
* Historical Allocation Trends (per Praktikum typ) - requires archiving past plans.
* Budget Utilization Trends.
o Finalize Assignment: Implement API to "lock" an assignment plan, archive it, and prepare for a new cycle.
DoD: The system can handle dynamic changes and re-optimize. All listed reports are accessible and show relevant data. System alerts are functional. Map view reflects dynamic capacity. Assignment plans can be finalized.

