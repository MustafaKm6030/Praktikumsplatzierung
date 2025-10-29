
Hard constraints:
-	GS students must be assigned to GS mentors/schools; MS students to MS mentors/schools.
-	The mentor's teaching subject must match the subject of the internship (for SFP and ZSP).
-	Every PL must supervise exactly 2 internships per year. 
-	A PL can only be assigned valid pairs of internships (e.g., PDP I + SFP, SFP + ZSP, etc.).
-	A PL may only supervise internships offered in their school
-	A PL’s available credit-hour budget must cover both assigned internships
-	If a PL is the only mentor for a subject at their school, they must be assigned where their subject is required
-	Subject group matching for GS and MS must use the correct grouping rules (they differ)
-	Demand quotas per internship must be satisfied exactly (You cannot over-assign or under-assign PLs. Example: SFP-German requires exactly 12 PLs, not 11 or 13.)
-	the assignment can be adjusted in the winter semester

-	PLs that were unavailable for some reason after they were assigned in the winter semester shall be reassigned 

-	reassignments should take place within the same internship category structure

-	PL assignments must adapt to changes in cumulative demand caused by students switching programs or subjects.

-	PLs unavailable due to illness or other absence must be removed from assignments;

-	For Block internships (PDP I and PDP II) Students must be assigned to a school within an acceptable distance from their home area.  Schools in Zone 3 or Zone 2 can be used if no closer school is available.
-	For Wednesday internships (SFP and ZSP) Students must be assigned to a school within Zone 1 or 2 (close to university) so they can return the same day.  Maximum travel time: ½ hour for 4a schools (all internships), 1 hour for 4b schools (SFP & ZSP only).
-	Only assign students to schools that are reachable by bus/train within the defined time limits.
-	  PLs cannot be assigned to schools marked “nicht” in the assignment columns.
-	 PLs may be assigned to schools marked “leer” in the assignment columns.
-	Total internships assigned to a PL must not exceed their fixed credited hours as specified by the ministry.
-	Only the current school of a PL is relevant for assignment; previous school locations are ignored.
-	A PL supervising multiple students in the same internship session does not increase their workload, as long as the supervision occurs in the same time slot (i.e., one SFP group or one ZSP group).
→ It is still counted as one internship assignment, regardless of whether they supervise 1, 2, or 3
-	No mid-year school transfers: A PL cannot switch schools during the semester. The school listed is fixed for the planning year.
-	The Excel dataset used for planning is authoritative: Planning must start from the provided list combined with last year's plan.
-	Planning must use the official Excel list as the single source of truth.
All teacher data (school, subjects, practicums, hours) must be taken exactly from this list, and last year’s assignment plan is used only as a reference/starting template
-	PL availability and subject eligibility come from official declarations: Only the practicums and subjects recorded in their PL profile may be assigned.
-	Subject distributions matter only for Wednesday practicums (SFP/ZSP): Subject-group matching must follow the Wednesday internship subject rules when calculating demand.
-	Red/yellow marked cells in the exel indicate mandatory planning constraints for the current school year and must be respected.
-	No data entry interface is needed: The system must use the existing Excel input format; no new input workflows for students or schools may be introduced.

Soft constraints:
-	PLs at the same school should be spread across internship types
-	Avoid placing a PL in two internships that overlap in calendar time
-	Try to assign PLs to internships they prefer when possible
-	When reassigning PLs, try to minimize changes from original PDP I / ZSP assignments unless absolutely necessary.
-	Prefer closest school within allowed zone
-	Avoid excessive travel for Wednesday internships: Minimize cumulative travel time when multiple students are assigned to the same PL.
-	Prefer schools/PLs used last year to reduce administrative effort and maintain continuity.
-	Avoid clustering all students in a single distant school (Zone 3) if multiple nearer schools are available.
-	Historical allocation (last year’s plan) should be used as a reference to guide assignments and maintain continuity.
-	Subject demand forecasting for PDP practicums is based on total student count, not detailed subject distributions — exact matching can be flexible if capacity allows.  (needs further clarification from slides)
-	Student data attributes and detailed student-to-PL assignment rules may be clarified later, meaning algorithm should allow future extension.
-	


Recommended:
-	Minimize changes from last year
-	Balance subject load across PLs
-	Minimize travel/placement distance
-	account for public transport schedules

Notes: 
-	Unlike other universities, reachability by public transport is a real hard constraint for uni Passau
-	The Passau-specific “Zone 1–3” system makes sense because students cannot easily commute long distances.
-	This also explains why historical assignments and balancing across zones are important.
-	Longer block internships can tolerate more distant schools.
-	Short Wednesday internships require near-university placement we must reinforce hard constraint on travel times.
-	Customer doesn’t want interfaces for schools or students to enter data as stated by them in answered questions
-	210 credited hours corresponds to 210 mentors and each supervise 2 praktikum
-	The possible teaching assignments of each teacher (subjects, practicums) are collected in writing when they begin their role as a practicum mentor. The credited hours are communicated in writing by the Ministry of Education
