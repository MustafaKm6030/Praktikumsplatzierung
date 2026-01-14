The "Adjust Assignment" plan
Clicking "Anpassen" on an assignment for "Julia Fischer" opens this modal.
•	Title: "Adjust Assignments for Julia Fischer"
•	Content: It shows ALL assignments for that specific mentor (1 or 2 slots for standard mentors, up to 4 for "4 for 2" mentors).
o	Slot 1: [Dropdown with PDP I]
o	Slot 2: [Dropdown with SFP-Deutsch]
Assuming she’s currently assigned PDP I and SFP-Deutsch
•	The Dropdown Logic:
o	The options in each dropdown are populated by the results of the calculate_eligibility_for_pl(julia) service.
o	This guarantees the user can only select from a list of assignments that are already known to be legal for that mentor (correct Program, Subject, Zone, etc.).
•	The "Force" Option: A checkbox at the bottom labeled "Override warnings (e.g., allow same subject twice)".
•	Action Buttons: "Save Changes" and "Cancel".
1.	The Backend API
•	Fetching Data for the Modal:
Endpoint: GET /api/pls/{id}/adjustment-data/
Response Body:
{
"mentor_id": 123,
"mentor_name": "Julia Fischer",
"capacity": 2,
"current_assignments": [
{"practicum_type": "PDP_I", "subject_code": "N/A" },
{ "practicum_type": "SFP", "subject_code": "D" }
],
"all_eligibilities": [
{ "practicum_type": "PDP_I", "subject_code": "N/A" },
{ "practicum_type": "SFP", "subject_code": "D" },
{ "practicum_type": "ZSP", "subject_code": "MA" }
]
}
•	Saving the Adjustment:
Endpoint: POST /api/assignments/adjust/
Request Body:
{
"mentor_id": 123,
"force_override": false,
"proposed_assignments": [
{ "practicum_type": "PDP_I", "subject_code": "N/A" },
{ "practicum_type": "ZSP", "subject_code": "MA" }
]
}
Success Response (200 OK): Returns the newly saved list of assignments for that mentor.
Error Response (400 Bad Request): Returns a clear error message (e.g., "Invalid Pair: SFP + SFP").
•	Backend Service Logic (adjust_assignment(data)):
1.	Fetch Mentor: Get the PraktikumsLehrkraft object.
2.	Validate Capacity: Check if len(proposed_assignments) <= mentor.capacity. If not, return an error.
3.	Run Constraint Checks (IF force_override is False):
	Valid Pairs: Check if the combination of types in proposed_assignments is a valid pair. If not, return an error (e.g., "Invalid Pair: SFP + SFP").
	Subject Variety: Check if any subjects are duplicated. If so, return a warning (e.g., "Warning: This mentor is assigned the same subject twice.").
4.	Database Transaction:
	Start a transaction.atomic().
	Delete all existing Assignment objects for this mentor_id.
	Create new Assignment objects based on the proposed_assignments.
5.	Return Success: If all checks pass, return a 200 OK with the updated assignment list for that mentor.
Final Step: The "Unassigned/Partial" List
This list is displayed alongside the main assignment table.
•	Functionality: Clicking a name on this list (e.g., "Sarah Wagner - Partial Assignment") should also open the "Adjust Assignment" Modal for that mentor, pre-filled with her one existing assignment and an empty slot, allowing the administrator to complete her schedule.

