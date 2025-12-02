1. Dashboard
Purpose: Provide a high-level overview of the system's status, key statistics, and quick access to critical actions.
Target User: System administrators, coordinators, and anyone needing a quick pulse check.
UI Description:
The dashboard features several customizable widgets, offering a snapshot of the current academic year's planning status. It uses a clean, modern design with clear data visualizations.
* Header: System title ("Praktikumsverwaltung Universität Passau") and user profile/settings.
* Navigation Sidebar: Consistent navigation menu for all main pages.
* Main Content Area (Widgets):
o "Praktika Status Overview" Card:
* Displays progress bars for: "PDP I Allocated (X%)", "PDP II Allocated (Y%)", "SFP Allocated (Z%)", "ZSP Allocated (A%)".
* Quick link: "View All Praktika".
o "Current Year's Budget" Card:
* "Total Budget: 210 Anrechnungsstd."
* "Allocated: 169 GS-PLs, 41 MS-PLs" (with visual breakdown, e.g., a pie chart or stacked bar).
* "Remaining: X Anrechnungsstd."
* Quick link: "Manage Budget".
o "Student Demand Snapshot" Card:
* "Total Students: ~1000"
* "Unplaced Students: X" (Highlighting urgency)
* Breakdown by program: "GS Students: Y", "MS Students: Z"
* Quick link: "View Student List".
o "Praktikumslehrkräfte (PLs) Status" Card:
* "Total Active PLs: X"
* "Available PLs (unassigned): Y"
* "Overloaded PLs: Z" (Alerting to potential issues)
* Quick link: "Manage PLs".
o "Upcoming Deadlines/Tasks" Card:
* A simple list of important dates (e.g., "PDP I demand finalization: 01.05.YYYY", "PL assignments due: 15.06.YYYY").
* Can integrate with a calendar feature.
o "System Alerts" Card:
* Notifications for critical issues (e.g., "Low remaining budget", "Unmatched student subjects").
Visual Elements:
* Clean cards with distinct titles.
* Intuitive icons for quick understanding.
* Color-coding for status (e.g., green for good, yellow for warning, red for critical).
* Minimalist charts (progress bars, small pie charts) for data visualization.

2. Student Management
Purpose: To manage student records, their declared Praktika preferences, subjects, and current placement status.
Target User: Coordinators responsible for student enrollment and placement.
UI Description:
A comprehensive table view with filtering, searching, and bulk action capabilities. Each student has a detailed profile page.
* Header: "Student Management" title.
* Action Bar:
o "Add New Student" button.
o "Import Students (CSV/Excel)" button (for bulk enrollment).
o Search bar (by Name, Student ID, Program).
o Filter dropdowns: "Program (GS/MS)", "Praktikum Type (PDP I, PDP II, SFP, ZSP)", "Placement Status (Placed, Unplaced, In Review)", "Subjects".
o "Export Student List" button.
* Student List Table:
o Columns: Student ID, Name, Program (GS/MS), Primary Subject, Declared Praktika (e.g., "PDP I, SFP"), Placement Status, Actions.
o Action Column: "View Profile" (link), "Edit", "Delete".
o Rows are clickable to open a detailed student profile.
* Student Profile Page (Opened by clicking a student in the list):
o Header: Student Name, Student ID.
o Tabs: "General Info", "Praktikum Preferences", "Placement History", "Notes".
o "General Info" Tab:
* Basic details: Name, Student ID, Email, Phone, Program (GS/MS).
* University details: Enrollment date, Major.
* Address/Region (for geographical matching).
o "Praktikum Preferences" Tab:
* List of declared Praktika types.
* For each Praktikum: Declared Subjects, Preferred Region/Schools (if applicable), Availability (e.g., "I.d.R. im Herbst" for PDP I).
* Status for each Praktikum: "Requested", "Assigned", "Completed".
* Option to edit preferences (with workflow approval if needed).
o "Placement History" Tab:
* A chronological list of all Praktika the student has been placed in.
* For each entry: Praktikum Type, Assigned School, Assigned PL, Dates, Status, Evaluation (link to external system, if any).
o "Notes" Tab: Free-form text area for internal notes about the student.
Visual Elements:
* Clear table headings with sorting arrows.
* Distinct button styles for actions.
* Well-structured forms for data entry in student profiles.
* Icons for quick identification of program type (e.g., small GS/MS badges).

3. Praktikumslehrkräfte (PLs) Management
Purpose: To meticulously manage PL profiles, their specific subject qualifications (as shown in the Excel matrix), their availability for different Praktika types, allocated "Anrechnungsstunden," and their assigned Schulamt. This page is the primary data entry point for PL capabilities.
UI Description:
* PL List Table:
o Columns: PL ID, Name, School, School Type (GS/MS), Main Subject, Prefer. Praktika (e.g., "PDP I, SFP, ZSP"), Current Anrechnungsstd., Schulamt, Available Capacity, Assigned Students (count), Actions.
* PL Profile Page (Opened by clicking a PL):
o Header: PL Name, School, Schulamt.
o Tabs: "General Info", "Subject & Praktikum Availability", "Assigned Praktika", "Anrechnungsstunden & History", "Notes".
o "General Info" Tab:
* Basic details: Name, Email, Phone, School, School Type (GS/MS).
* Geographical Data: Address (auto-populate coordinates), Entfernungszone (Distance Zone), OPNV-Zone (Public Transport Zone).
o "Subject & Praktikum Availability" Tab:
* This tab directly visualizes and allows editing of the Excel's subject matrix and Praktikum availability.
* Table/Matrix View:
* Row Header: Praktikum Type (e.g., PDP I, PDP II, SFP, ZSP).
* Column Headers: All defined subjects (DA, D, SSE, MA, SP, MU, KRE, HSC, GEL, WI, GE, Kunst, Musik, Kath. Religion, HSU, Deutsch, Geschichte, etc.).
* Cells: Checkboxes or dropdowns to indicate "Available" (equivalent to "hier" or specific subject listing).
* Example: For "PDP I" and "Deutsch", a checkbox. If checked, the PL can supervise PDP I students in Deutsch.
* Special Cases: For SFP/ZSP, some cells might directly list the subject (e.g., "Kunst," "Musik"). This needs to be captured.
* Capacity/Max Students: For each Praktikum type (PDP I/II, SFP/ZSP), a field to enter max students.
* "Besonderheiten" (Special Notes) Field: A rich-text editor or specific input field to capture notes like "2 Mittwochs-Praktika," or other conditions from the Excel.
* Availability toggle: "Available for PDP I, PDP II, SFP, ZSP" (can tick multiple, reflecting "bevorzugte Praktika" column from Excel).
o "Anrechnungsstunden & History" Tab:
* "Current Year's Allocated Anrechnungsstunden": Displayed value (e.g., "1").
* Associated "Schulamt" (e.g., "Regen," "Passau-Land").
* History of allocation.

4. School Management
Purpose: To maintain a database of participating schools, their geographical location, available Praktikum slots, and OPNV accessibility.
Target User: Coordinators managing school partnerships and capacities.
UI Description:
A map-centric view combined with a list view for schools.
* Header: "School Management" title.
* Action Bar:
o "Add New School" button.
o "Import Schools (CSV/Excel)" button.
o Search bar (by School Name, District, City).
o Filter dropdowns: "District", "School Type (GS/MS)", "OPNV Accessibility (Zone 1, Zone 2, Zone 3)", "Has Active PLs".
o "Export School List" button.
* School View Toggle: "Map View" | "List View".
* Map View (Default or Prominent):
o Interactive map of the Niederbayern region.
o Schools represented as pins/markers.
o Color-coded markers based on status (e.g., green for high capacity, red for full, blue for OPNV accessible).
o Clicking a pin reveals a mini-card with school name, type, and quick stats (e.g., "Available slots: X").
o Option to draw a radius around Passau or student locations to visualize "Heimatnah" or "Passau-nahe" schools.
o Overlay for OPNV zones (Zone 1, 2, 3).
* List View (Table):
o Columns: School Name, School Type (GS/MS), District, Address, Total PLs, Available Slots (Blockpraktikum), Available Slots (Mittwochspraktikum), OPNV Zone, Actions.
o Action Column: "View Profile" (link), "Edit", "Delete".
o Rows are clickable to open a detailed school profile.
* School Profile Page (Opened by clicking a school in the list/map):
o Header: School Name, School ID.
o Tabs: "General Info", "Capacity & Slots", "Assigned PLs", "Notes".
o "General Info" Tab:
* Basic details: Name, Address, Contact Person, Phone, Email, School Type (GS/MS).
* Geographical coordinates (auto-populated from address).
* OPNV Zone (1, 2, 3) and specific travel times/notes.
o "Capacity & Slots" Tab:
* "Max Blockpraktikum Slots (PDP I/II)": X
* "Max Mittwochspraktikum Slots (SFP/ZSP)": Y
* "Current Available Slots (Block)": Z
* "Current Available Slots (Mittwoch)": A
* Ability to adjust these numbers for each academic year.
o "Assigned PLs" Tab:
* List of all Praktikumslehrkräfte affiliated with this school.
* Columns: PL Name, Program (GS/MS), Supervises Praktikum Type.
* Link to PL's profile.
o "Notes" Tab: Free-form text area for internal notes about the school.
Visual Elements:
* Interactive map with zooming and panning.
* Color-coded pins for easy identification of school status or type.
* Clear forms for school data entry.

5. Praktika Planning & Allocation
Purpose: This is the core workflow page where student demand is matched with available PLs and school slots, adhering to all defined rules and constraints.
Target User: The primary user for performing allocations.
UI Description:
This page is designed as a multi-step wizard or a consolidated dashboard specifically for the allocation process. It needs to provide powerful tools for automated matching, manual adjustments, and conflict resolution.
* Header: Praktika Planning & Allocation" title with clear progress steps (e.g., "1. Demand Overview", "2. Run Auto-Allocation", "3. Review & Adjust", "4. Finalize").
* Workflow Steps/Tabs (suggested):
1. Demand Overview
2. Initial Matching (Automated)
3. Review & Adjustments
4. Finalization
Detailed Breakdown of each step/tab:
Step 1: Demand Overview
* Purpose: Visualize the cumulated demand for each Praktikum type and subject.
* UI Elements:
o Summary cards: "Total PDP I Demand: X students", "Total SFP Demand: Y students".
o Interactive charts (bar charts, heatmaps) showing demand distribution by:
* Praktikum T
* ype & Subject (e.g., "PDP I - Deutsch: 50 students", "SFP - Englisch: 30 students").
* Student Program (GS vs. MS).
* Region/District (to inform geographical allocation).
o "View Unmatched Demand" button, leading to a filtered student list.
* Step 2: Run Auto-Allocation (CRITICAL NEW CAPABILITY):
o Algorithm Configuration Panel:
* This is where the user defines the priority and weights for the automated matching, directly reflecting the Excel's hidden logic.
* Matching Criteria Checkboxes/Sliders:
* "Subject Match (Exact/Partial)" (HIGH Priority - from Excel matrix)
* "Praktikum Type Match (PDP I, SFP, etc.)" (HIGH Priority - from "bevorzugte Praktika" and availability columns)
* "Student Program (GS/MS) vs. PL Program (GS/MS)" (MUST MATCH)
* "Heimatnah (Distance Zone 1/2 for Blockpraktikum)"
* "Passau-nahe (OPNV Zone 1/2 for Mittwochspraktikum)"
* "Balance PL Workload"
* "Utilize Anrechnungsstunden Budget Efficiently"
* "Respect 'Besonderheiten' (e.g., '2 Mittwochs-Praktika')"
* "Run Allocation" Button: Initiates a sophisticated algorithm that attempts to match students to PLs and schools based on ALL these Excel-derived criteria simultaneously.
* Progress Indicator & Initial Results: Shows how many students were matched, how many are in conflict, and an estimate of budget usage.
Step 3: Review & Adjustments
* Split View (Left: Conflicts, Right: Interactive Grid):
o Left Panel: Unplaced Students / Conflicts List:
* List of students with a clear "Reason for Conflict" (e.g., "No PL available for Deutsch in PDP I in Zone 2," "PL budget limit exceeded," "Subject mismatch for PL X"). These reasons directly stem from the detailed Excel data.
* Clicking a student highlights potential partial matches in the grid and suggests alternative PLs/schools, even if they don't meet all criteria.
o Right Panel: Allocation Grid (Similar to previous design but with more granular PL data):
* Rows: Students (unplaced or assigned).
* Columns: Praktikumslehrkräfte (PLs) with their School, School Type (GS/MS), and a quick summary of their available Praktika types and subjects (e.g., "PDP I: D,MA; SFP: MU").
* Drag-and-drop: Student "cards" can be dragged onto PL cells.
* Real-time Validation: As a student is dragged, cells change color:
* Green: Perfect match (all criteria met, including subject availability from Excel).
* Yellow: Partial match (e.g., PL available for Praktikum type but not the exact subject, or geographical mismatch).
* Red: Conflict (e.g., PL capacity full, PL cannot supervise that Praktikum type or subject, GS student assigned to MS PL).
* Contextual Details on Hover: Hovering over a PL cell shows detailed information about their subject availability for that Praktikum type, remaining capacity, and geographical zone.
* "Besonderheiten" Alerts: If a PL has a "Besonderheit" (e.g., "2 Mittwochs-Praktika"), the system alerts if this rule is violated or optimally utilized.
* Manual Assignment Modal: If a drag-and-drop is too complex, a modal can open for precise selection: "Select Student," "Select Praktikum Type," "Select School," "Select PL." Crucially, this modal will show only valid PLs based on subject, Praktikum type, and capacity.
* "Validate All Assignments" Button: Re-checks all current assignments against all rules derived from the Excel data.
o "Generate Confirmation Letters" Button: Creates personalized letters for students, PLs, and schools.
o "Generate Official Reports" Button: Outputs final reports for the university/Schulamt.
o "Archive This Planning Period" button (to move to historical data).
Visual Elements:
* Intuitive drag-and-drop interfaces for assignments.
* Color-coding for different Praktikum types.
* Clear feedback messages for conflicts or successful matches.
* Performance indicators (e.g., "X students assigned out of Y").

6. Budget & Reporting
Purpose: To monitor the allocation of "Anrechnungsstunden," generate various reports, and analyze historical data.
Target User: Administrators, coordinators, and stakeholders requiring data insights.
UI Description:
A dashboard-like page with customizable reports and clear data visualizations.
* Header: "Budget & Reporting" title.
* Budget Overview Card:
o "Total Anrechnungsstunden Budget: 210"
o "Allocated to GS-PLs: X (Y%)"
o "Allocated to MS-PLs: A (B%)"
o "Remaining Budget: Z"
o Pie chart or stacked bar chart for visual distribution.
* "Budget Distribution by School/District" Chart:
o Interactive bar chart showing total "Anrechnungsstunden" allocated per school or district.
o Allows drill-down.
* Reporting Section:
o "Pre-defined Reports" List:
* "Student Placement Report (Current Year)"
* "PL Workload & Anrechnungsstunden Report"
* "School Capacity & Utilization Report"
* "Unplaced Students Report"
* "Historical Allocation Trends (per Praktikum type)"
* "Budget Utilization Trends"
o "Custom Report Builder" (Advanced Feature):
* Allows users to select data fields, filters, and chart types to create their own reports.
* Report Viewer:
o Displays selected reports with options to "Print", "Export (PDF, CSV, Excel)".
o Interactive charts and sortable tables.
* Historical Data Access:
o Dropdown to select "Academic Year" to view past reports and allocations.
Visual Elements:
* Professional charts (bar, line, pie) for data visualization.
* Clear table formats for detailed data.
* Export icons prominently displayed.

7. Settings
Purpose: To configure system-wide parameters, user roles, and core data.
Target User: System administrators.
UI Description:
A standard settings page with various sections.
* Header: "System Settings" title.
* Sections/Tabs:
o "General Settings":
* Current Academic Year.
* Default Praktikum Dates/Deadlines (can be overridden).
* University Name, Contact Info.
o "User & Permissions":
* Manage users (Add, Edit, Delete).
* Assign roles (Admin, Coordinator, Viewer).
* Define permissions for each role.
o "Praktikum Types & Rules":
* Define/Edit Praktikum types (PDP I, PDP II, SFP, ZSP).
* Edit associated rules (e.g., "PDP I/II Heimatnah priority", "SFP/ZSP Passau-nahe").
* Define "Anrechnungsstunden" values for different Praktikum types/combinations.
* Manage subject lists (Deutsch, Englisch, etc.).
o "Geographical Data":
* Define/Edit Districts (Landkreise) in Niederbayern.
* Manage OPNV Zones and associated travel time parameters.
* Import/Update regional map data.
o "Notifications & Alerts":
* Configure system alerts (e.g., "Budget usage threshold", "Unplaced student alerts").
* Email notification settings.
o "Integrations":
* Settings for potential integrations with university student systems or learning platforms.
o "Audit Log":
* View a log of all significant system actions (who did what, when).
Visual Elements:
* Clear forms and toggle switches for settings.
* Structured tables for user management.

