from datetime import date
from django.test import TestCase
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from assignments.models import Assignment
from assignments.solver import run_solver
from schools.models import School
from subjects.models import Subject, PraktikumType
from students.models import Student


class SolverHardConstraintsTests(TestCase):
    # --- Static Data Definitions ---
    SUBJECT_CODES = ["D", "MA", "E", "MU", "SP", "HSU"]
    TYPE_CODES = ["PDP_I", "PDP_II", "SFP", "ZSP"]

    SCHOOLS_DATA = [
        (
            "Grundschule Passau-Innstadt",
            "GS",
            "Passau",
            "Passau",
            1,
            "4a",
            5,
            48.57,
            13.46,
            True,
        ),
        (
            "Mittelschule Vilshofen",
            "MS",
            "Passau-Land",
            "Vilshofen",
            1,
            "4a",
            23,
            48.62,
            13.38,
            True,
        ),
        ("Grundschule Regen", "GS", "Regen", "Regen", 3, "", 71, 48.97, 13.12, False),
        (
            "Grundschule Deggendorf",
            "GS",
            "Deggendorf",
            "Deggendorf",
            2,
            "4b",
            53,
            48.83,
            12.96,
            True,
        ),
        (
            "Mittelschule Straubing",
            "MS",
            "Straubing",
            "Straubing",
            3,
            "",
            85,
            48.87,
            12.57,
            True,
        ),
    ]

    @classmethod
    def setUpTestData(cls):
        """
        Populates the test database with the specific scenario:
        - Supply: 8 Slots (Michael=4, Sarah=2, Julia=2)
        - Demand: 8 Slots (Anna=2, Max=3, Sophie=2, Lukas=1)
        """
        print("\n--- Setting up Test Data ---")

        # 1. Setup Dependencies
        subjects_map = cls._setup_subjects()
        types_map = cls._setup_types()
        schools_map = cls._setup_schools()

        # 2. Create PLs
        cls._setup_pls(schools_map, subjects_map, types_map)

        # 3. Create Students
        cls._setup_students(subjects_map)

    @classmethod
    def _setup_subjects(cls):
        subjects = {}
        for code in cls.SUBJECT_CODES:
            sub, _ = Subject.objects.get_or_create(code=code, defaults={"name": code})
            subjects[code] = sub
        return subjects

    @classmethod
    def _setup_types(cls):
        types = {}
        for code in cls.TYPE_CODES:
            pt, _ = PraktikumType.objects.get_or_create(
                code=code, defaults={"name": code}
            )
            types[code] = pt
        return types

    @classmethod
    def _setup_schools(cls):
        schools = {}
        for row in cls.SCHOOLS_DATA:
            name = row[0]
            school, _ = School.objects.get_or_create(
                name=name,
                defaults={
                    "school_type": row[1],
                    "district": row[2],
                    "city": row[3],
                    "zone": row[4],
                    "opnv_code": row[5],
                    "distance_km": row[6],
                    "latitude": row[7],
                    "longitude": row[8],
                    "is_active": row[9],
                },
            )
            schools[name] = school
        return schools

    @classmethod
    def _setup_pls(cls, schools, subjects, ptypes):
        pls_data = [
            # Inactive
            {
                "email": "anna.schmidt@schule.de",
                "first_name": "Anna",
                "last_name": "Schmidt",
                "school": schools["Grundschule Regen"],
                "program": "GS",
                "main_subject": subjects["D"],
                "schulamt": "Regen",
                "anrechnungsstunden": 1.0,
                "is_active": False,
                "preferred_praktika_raw": "PDP I, SFP",
                "p_codes": ["PDP_I", "SFP"],
                "s_codes": ["D", "MA"],
            },
            # Active: Michael (Capacity 4) - MS
            {
                "email": "michael.mueller@schule.de",
                "first_name": "Michael",
                "last_name": "Müller",
                "school": schools["Mittelschule Vilshofen"],
                "program": "MS",
                "main_subject": subjects["MA"],
                "schulamt": "Passau-Land",
                "anrechnungsstunden": 2.0,
                "is_active": True,
                "preferred_praktika_raw": "PDP I, PDP II, SFP, ZSP",
                "current_year_notes": "4 für 2",
                "p_codes": ["PDP_I", "PDP_II", "SFP", "ZSP"],
                "s_codes": ["MA", "SP", "E"],
            },
            # Active: Sarah (Capacity 2) - GS
            {
                "email": "sarah.weber@schule.de",
                "first_name": "Sarah",
                "last_name": "Weber",
                "school": schools["Grundschule Deggendorf"],
                "program": "GS",
                "main_subject": subjects["MU"],
                "schulamt": "Deggendorf",
                "anrechnungsstunden": 1.0,
                "is_active": True,
                "preferred_praktika_raw": "SFP, ZSP",
                "current_year_notes": "nur Mi-Prak.",
                "p_codes": ["SFP", "ZSP"],
                "s_codes": ["MU", "D", "MA"],
            },
            # Inactive
            {
                "email": "thomas.bauer@schule.de",
                "first_name": "Thomas",
                "last_name": "Bauer",
                "school": schools["Mittelschule Straubing"],
                "program": "MS",
                "main_subject": subjects["SP"],
                "schulamt": "Straubing",
                "anrechnungsstunden": 0.0,
                "is_active": False,
                "preferred_praktika_raw": "PDP I, PDP II",
                "p_codes": [],
                "s_codes": [],
            },
            # Active: Julia (Capacity 2) - GS
            {
                "email": "julia.fischer@schule.de",
                "first_name": "Julia",
                "last_name": "Fischer",
                "school": schools["Grundschule Passau-Innstadt"],
                "program": "GS",
                "main_subject": subjects["HSU"],
                "schulamt": "Passau",
                "anrechnungsstunden": 1.0,
                "is_active": True,
                "preferred_praktika_raw": "PDP I, SFP, ZSP",
                "p_codes": ["PDP_I", "SFP", "ZSP"],
                "s_codes": ["HSU", "D", "MA"],
            },
        ]

        for data in pls_data:
            p_codes = data.pop("p_codes")
            s_codes = data.pop("s_codes")
            pl, _ = PraktikumsLehrkraft.objects.get_or_create(
                email=data["email"], defaults=data
            )

            if p_codes:
                pl.available_praktikum_types.set([ptypes[c] for c in p_codes])
            if s_codes:
                pl.available_subjects.set([subjects[c] for c in s_codes])

    @classmethod
    def _setup_students(cls, subjects):
        students_data = [
            # Anna (GS): Needs PDP I, SFP (2 Slots)
            {
                "student_id": "ST-001",
                "first_name": "Anna",
                "last_name": "Hofmann",
                "email": "anna.hofmann@test.com",
                "program": "GS",
                "primary_subject": subjects["D"],
                "didactic_subject_3": subjects["MA"],
                "pdp1_completed_date": None,
                "sfp_completed_date": None,
                "zsp_completed_date": date(2023, 7, 15),
                "placement_status": "UNPLACED",
                "home_region": "Niederbayern",
            },
            # Max (MS): Needs PDP II, SFP, ZSP (3 Slots)
            {
                "student_id": "ST-002",
                "first_name": "Max",
                "last_name": "Schneider",
                "email": "max.schneider@test.com",
                "program": "MS",
                "primary_subject": subjects["E"],
                "didactic_subject_3": subjects["SP"],
                "pdp1_completed_date": date(2023, 3, 15),
                "pdp2_completed_date": None,
                "sfp_completed_date": None,
                "zsp_completed_date": None,
                "placement_status": "UNPLACED",
                "home_region": "Oberpfalz",
            },
            # Sophie (GS): Needs SFP, ZSP (2 Slots)
            {
                "student_id": "ST-003",
                "first_name": "Sophie",
                "last_name": "Wagner",
                "email": "sophie.wagner@test.com",
                "program": "GS",
                "primary_subject": subjects["D"],
                "didactic_subject_3": subjects["MA"],
                "pdp1_completed_date": date(2023, 3, 15),
                "pdp2_completed_date": date(2023, 9, 15),
                "sfp_completed_date": None,
                "zsp_completed_date": None,
                "placement_status": "UNPLACED",
                "home_region": "Oberbayern",
            },
            # Lukas (MS): Needs PDP I (1 Slot)
            {
                "student_id": "ST-004",
                "first_name": "Lukas",
                "last_name": "Becker",
                "email": "lukas.becker@test.com",
                "program": "MS",
                "primary_subject": subjects["MA"],
                "didactic_subject_3": subjects["MA"],
                "pdp1_completed_date": None,
                "sfp_completed_date": date(2024, 2, 1),
                "zsp_completed_date": date(2024, 7, 1),
                "placement_status": "UNPLACED",
                "home_region": "Oberbayern",
            },
        ]

        for s_data in students_data:
            Student.objects.get_or_create(
                student_id=s_data["student_id"], defaults=s_data
            )

    def test_solver_finds_valid_solution_with_sample_data(self):
        """
        Runs the solver against the injected scenario.
        Verifies that Supply (8) meets Demand (8) perfectly.
        """
        # --- Run the Solver ---
        print("\n--- Running Solver in Test ---")
        results = run_solver()

        # --- Assertions ---
        # 1. Status
        self.assertEqual(results["status"], "SUCCESS", "Solver should succeed.")

        # 2. Total Assignments in DB
        # Expected: Michael(4) + Sarah(2) + Julia(2) = 8
        total_assignments = Assignment.objects.count()
        self.assertEqual(
            total_assignments, 8, f"Expected 8 assignments, found {total_assignments}"
        )

        # 3. Check Michael (MS, Cap 4)
        michael = PraktikumsLehrkraft.objects.get(email="michael.mueller@schule.de")
        michael_count = Assignment.objects.filter(mentor=michael).count()
        self.assertEqual(
            michael_count, 4, "Michael must have 4 assignments (Full Capacity)."
        )

        # 4. Check Sarah (GS, Cap 2)
        sarah = PraktikumsLehrkraft.objects.get(email="sarah.weber@schule.de")
        sarah_count = Assignment.objects.filter(mentor=sarah).count()
        self.assertEqual(sarah_count, 2, "Sarah must have 2 assignments.")

        # 5. Check Julia (GS, Cap 2)
        julia = PraktikumsLehrkraft.objects.get(email="julia.fischer@schule.de")
        julia_count = Assignment.objects.filter(mentor=julia).count()
        self.assertEqual(julia_count, 2, "Julia must have 2 assignments.")

        # 6. Verify Specific Logic: Lukas (MS) must go to Michael (MS)
        # Lukas needs PDP I. Only Michael offers PDP I for MS.
        # Note: We can't filter Assignment by Student easily yet (not in model),
        # so we assume if Capacity is full and Types align, it worked.

        # Verify Michael has at least one PDP_I assignment
        michael_pdp_i = Assignment.objects.filter(
            mentor=michael, practicum_type__code="PDP_I"
        ).exists()
        self.assertTrue(
            michael_pdp_i, "Michael should have assigned a PDP I student (Lukas)."
        )

        print("✅ Test Passed: 8 Assignments created successfully.")
