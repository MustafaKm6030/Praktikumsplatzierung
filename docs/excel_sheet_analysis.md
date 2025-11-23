Official Documentation: The PL Assignment CSV (New Microsoft Excel Worksheet.csv)
Group 1: Mentor & School Identity (Columns A - E)
These columns identify the person (PL) and their fixed place of work for the planning year.
Column Header
Real-World Meaning
Algorithmic Impact
Nachname
The mentor's last name.
Identifier. Used for reporting.
Vor-name
The mentor's first name.
Identifier. Used for reporting.
LA
Lehramt (Teaching Credential). GS = Grundschule, MS = Mittelschule.
CRITICAL HARD CONSTRAINT. The primary filter for matching mentors to student demand (GS students must go to GS mentors).
Schulart
The specific name and type of the school (e.g., Ritter-Tuschl-Grundschule, Grund- und Mittelschule). This field often contains the unique school name.
CRITICAL IDENTIFIER. Must be combined with Schulort to create a unique school_id for grouping mentors and managing school-specific constraints. The generic type (Grundschule, Mittelschule) within the name also serves to confirm the mentor's LA eligibility.
Schulort
The city/town where the school is located.
Identifier & Logistical. Used for distance/zone calculations and reporting.



Note: there is no column for the name of the school but as can be observed the name is provided in the Schulart field







Group 2: Mentor Capabilities & Qualifications (Columns F - AE)
These columns define what the mentor is qualified and willing to supervise. An x or X marks a capability.
Column Header
Real-World Meaning & German Name
Algorithmic Impact
bevorzugte Praktika der PL
A text field listing the internship types the mentor prefers/is eligible for (e.g., "PDP I, SFP").
Hard Constraint. A mentor can only be assigned to an internship type listed here.
Haupt-fach
Main subject area (Informational).
Low impact, informational.
Schul-päd.
Schulpädagogik (School Pedagogy). A specific internship type.
Capability Flag. If demand for this exists, filter for x.
DaZ
Deutsch als Zweitsprache (German as a Second Language).
Capability Flag. Matches demand for DaZ.
D
Deutsch (German).
Capability Flag. Matches demand for D.
SSE
Schriftspracherwerb (Literacy Acquisition). A specialized GS topic.
Capability Flag. Matches demand for SSE.
MA
Mathematik (Math).
Capability Flag. Matches demand for MA.
SP
Sport (Physical Education).
Capability Flag. Matches demand for SP.
SK /PuG
Sozialkunde / Politik und Gesellschaft (Social Studies / Politics & Society).
Capability Flag. Matches SK/PuG demand. 
MU
Musik (Music).
Capability Flag. Matches demand for MU.
KE
Kunsterziehung (Art Education).
Capability Flag. Matches demand for KE.
KRel
Katholische Religion (Catholic Religion).
Capability Flag. Matches KRel demand ( pools Protestant demand too).
HSU
Heimat- und Sachunterricht (Local & General Studies). GS-specific integrated subject.
Capability Flag. Matches HSU demand (for GS ZSP, this is the target for science/history/geography).
GEO
Geographie (Geography).
Capability Flag. Matches GEO demand.
AL/WiB
Arbeitslehre / Wirtschaft und Beruf (Work Studies / Economics & Career). MS-specific.
Capability Flag. Matches AL/WiB demand.
GE
Geschichte (History).
Capability Flag. Matches GE demand.
E
Englisch (English).
Capability Flag. Matches E demand.
GU
Grundlegender Unterricht (Foundational Instruction). Integrated D+MA for GS grades 1/2.
Capability Flag. A mentor with GU is eligible for both D and MA internships in GS.
PCB
Physik/Chemie/Biologie (Physics/Chemistry/Biology). MS-specific integrated science.
Capability Flag. Matches demand for any of the three sciences in MS.
IT
Informationstechnik (IT / Computer Science). MS-specific.
Capability Flag. Matches demand for IT.
GSE/GPG
Geschichte/Sozialkunde/Erdkunde (Integrated History/Social Studies/Geography). MS-specific.
Capability Flag. A mentor with GSE/GPG is eligible for GE, GEO, and SK/PuG internships in MS.


Important Notes:
-  The bevorzugte Praktika der PL is already processed we don’t need to calculate (We should also ask to be 100% sure)
- Schul-päd. (Schulpädagogik) represents a unique internship focused on the science of teaching and school organization, rather than a specific classroom subject. Mentors marked with an 'x' in this column are qualified to supervise students who are analyzing lesson structures, classroom management, and the school as a whole.
- For our system we will not take it into consideration as you can see in the sheet there is never an x in this field and it was never mentioned in the documents. So it’s probably a very rare case
- The columns from DaZ to GSE/GPG are the mentor's approved supervision capabilities for the year, where an 'x' means "YES" and a blank means "NO". We must treat these flags as hard constraints, only assigning a mentor to a subject-specific internship if their corresponding column is marked with an 'x'.
- Q: Why can a mentor supervise subjects (like Math) that are different from their listed Haupt-fach (like Geography)?
A: Because Haupt-fach is just their original university major. German teachers are qualified to teach several subjects, and most importantly, they can only supervise what they are actively teaching in the current school year.
- Q: So, what is the rule for our algorithm?
A: We always ignore the Haupt-fach for eligibility. The 'x' columns are the only source of truth; they represent the final, approved list of what a mentor can and will supervise this year.
- Q: What do the Nachname 2, Vorname 2, etc., columns represent? Are they students? 
A: No, they are not students. They are other teachers (mentors) at the same school who act as secondary contacts or subject specialists.
- Q: Why are they in the file if the primary mentor is the one being assigned? (Must validate this)
A: For administrative convenience. It allows the Internship Office to have a single main contact for a school (the primary mentor) while keeping a note of which other colleagues are also involved in supervising.
- Q: How should my algorithm handle these columns?
A: the algorithm must IGNORE them for all assignment decisions and only assign students to the primary mentor in each row. The secondary names should only be preserved and displayed in the final report as "Additional School Contacts" for human reference.
- Q: If Nachname 2 columns represent other teachers, how does it fit the fact that each PL (Primary Mentor) has a number of credited hours (Anre-Std.) if they were going to give the work to someone else? (Must validate this)
A: The credited hour (Anre-Std.) is officially assigned to the Primary Mentor listed in the row. This person acts as the single point of contact for the university. The actual distribution of work and credit is then handled internally by the school's administration and is outside the scope of the assignment system.

Group 3: Logistical & Travel Constraints (Columns AF - AI)
These columns define the physical constraints of placing a student at this mentor's school, a core part of the Passau-specific problem.
Column Header
Real-World Meaning
Algorithmic Impact
Entfernungs km
The distance in kilometers from the university.
Informational/Soft Constraint. Used to prioritize closer schools.
Zone 1
The university's official travel zone for the school (1=closest, 3=farthest).
Hard Constraint. Wednesday internships (SFP/ZSP) are only allowed in Zones 1 and 2.
ÖPNV
Öffentlicher Personennahverkehr (Public Transport). Contains codes like 4a, 4b.
CRITICAL HARD CONSTRAINT. Defines reachability for Wednesday internships. 4a = Reachable within 30 min. 4b = Reachable within 60 min. The system must filter schools based on these codes for SFP/ZSP.
Status
The mentor's overall availability status. ok is the default.
Hard Constraint. If status is ruhend (dormant), Elternzeit (parental leave), krank (sick), the mentor is unavailable and must be excluded.
Notes:
- The Zone 1 column categorizes each school's distance from the university (1=closest, 3=farthest), acting as a critical hard constraint for the algorithm. Wednesday internships (SFP/ZSP) are strictly limited to schools in Zone 1 or 2, while block internships (PDP) can be assigned to all three zones.

- WE DO NOT need to perform any distance or travel time calculations.


Group 4: Capacity, Overrides & Notes (Columns AJ - AL)
These columns contain critical, human-entered data that overrides standard rules.
Column Header
Real-World Meaning
Algorithmic Impact
Besonderheiten SJ 25_26
"Special Circumstances for School Year 25/26". This is a free-text note column that belongs specifically to the planning block for the 2025/2026 school year. It is used by the administrator to record any critical, year-specific rule, constraint, or piece of information that will affect the assignments for that year.
HIGHEST PRIORITY HARD CONSTRAINT. When your algorithm is running the plan for the 25/26 school year, the text in this column must be parsed and its instructions followed above all else. It overrides any general information found in Bemerkung2, Rückmeldung, or the structured columns. <br><br> Examples of Rules to Parse: <br> - "nur PDP" (Only PDP internships are allowed this year). <br> - "kein Mi-Prak wg. LAA" (No Wednesday internships due to a student teacher). <br> - "mobil" (Mentor is a mobile reserve this year and is unavailable). <br> - "Sabbatjahr" (Mentor is on sabbatical and is unavailable). <br><br> For any other year (e.g., when planning for 24/25), this column is treated as historical/future data and is ignored.


Group 5: Planning & Assignment History (Columns AM onwards)
This is a repeating block of columns for each school year (SJ). They are the OUTPUT of past planning cycles and the INPUT/WORKSPACE for the current one.
Column Header Pattern
Real-World Meaning
Algorithmic Impact
PDP I/II / SFP / ZSP SJ XX_XX
The assignment for a specific internship in a specific year.
Primary Workspace. The planner uses these columns to build the new assignment. The values mean: ja (Available), nein (Unavailable), nicht (Do Not Assign), a Subject Name (This is the assignment!), or hier (A planner's mark meaning "Plan this person here").
Anre-Std. SJ XX_XX
Anrechnungsstunde (Credited Hour). The mentor's credited workload for that year.
CRITICAL CAPACITY RULE. This is the budget. 1 means they must supervise 2 internships. 2 means 4 internships. 0.5 means 1 internship. 0 means they are unavailable or a volunteer.


Notes: 
- Nicht in the sfp and zsp columns means "DO NOT ASSIGN."
- nicht - [Subject] means "Do not assign this slot (nicht), and the reason is related to the subject Geography (- Geographie).". The text that follows nicht is valuable context for human review but does not change the hard constraint for the algorithm.
- 


Group 6: Administrative Information (Final Column)
Column Header
Code
Real-World Meaning
Algorithmic Impact
Schul-amt
Schulamt
The responsible School Authority District (e.g., Passau-Land, Regen).
Informational/Grouping. Can be used for reporting or balancing assignments across districts.


Notes: 
- THIS FILE IS THE FINAL ASSIGNMENT TO THE PLS TO THE PRAKTIKUM
- We don’t need to calculate the distances of the schools (Zone 1 column) and we also already know which Praktikums each PL can supervise ( the bevorzugte Praktikum column) and what they can teach (the subjects columns)
-  We feed all the relevant columns to the algorithm as input. The assignment columns IN the previous year ( PDP | , PDP ||, SFP,  ZSP) are ONLY FOR CONTINUITY SOFT CONSTRAINTS. The assignment columns IN the current year (re-assignment during WS) are hard constraints
- The Students must Complete all 4 Praktikum to pass the Staatsexamen system
- Stundent’s preferences are actually their requirements 

Important Explanation about other Docs:
The  2_Meldung SchA Rottal-Inn_25_26.pdf: This PDF is one of the first inputs the Praktikumsamt (Internship Office) receives when starting a new planning cycle. Our system will not process this PDF directly. Instead, an administrator uses this document to update your "Single Source of Truth" Excel file. We have no direct technical work to do with this PDF. However it helps in validating our algorithm.

