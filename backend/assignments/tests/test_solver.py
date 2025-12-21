# in backend/assignments/tests/test_solver.py

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
    SUBJECT_CODES = ["D", "MA", "E", "MU", "SP", "HSU", "GES"]
    TYPE_CODES = ["PDP_I", "PDP_II", "SFP", "ZSP"]

    # (Name, Type, District, City, Zone, Opnv, Dist, Lat, Lon, Active)
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
        Populates the test database with a deterministic scenario that is
        mathematically solvable given all hard constraints.
        """
        print("\n--- Setting up Test Data ---")

        # 1. Setup Dependencies
        subjects_map = cls._setup_subjects()
        types_map = cls._setup_types()
        schools_map = cls._setup_schools()

        # 2. Create PLs
        cls._setup_pls(schools_map, subjects_map, types_map)

        # 3. Create Students (Demand)
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
                code=code, defaults={"name": code, "is_block_praktikum": "PDP" in code}
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
        """Orchestrates the creation of PLs using data from the helper."""
        for data in cls._get_pl_definitions(schools, subjects):
            row = data.copy()
            p_codes = row.pop("p_codes")
            s_codes = row.pop("s_codes")

            pl, _ = PraktikumsLehrkraft.objects.get_or_create(
                email=row["email"], defaults=row
            )

            # Ensure M2M are set correctly
            pl.available_praktikum_types.set([ptypes[c] for c in p_codes])
            pl.available_subjects.set([subjects[c] for c in s_codes])

    @classmethod
    def _get_pl_definitions(cls, schools, subjects):
        return [
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
                "s_codes": ["E", "SP"],
            },
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
                "s_codes": ["MU"],
            },
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
                "s_codes": ["D"],
            },
            {
                "email": "hans.helfer@schule.de",
                "first_name": "Hans",
                "last_name": "Helfer",
                "school": schools["Grundschule Passau-Innstadt"],
                "program": "GS",
                "main_subject": subjects["HSU"],
                "schulamt": "Passau",
                "anrechnungsstunden": 1.0,
                "is_active": True,
                "preferred_praktika_raw": "SFP, ZSP",
                "p_codes": ["SFP", "ZSP"],
                "s_codes": ["HSU"],
            },
            {
                "email": "peter.ma@schule.de",
                "first_name": "Peter",
                "last_name": "Mathematik",
                "school": schools["Grundschule Deggendorf"],
                "program": "GS",
                "main_subject": subjects["MA"],
                "schulamt": "Deggendorf",
                "anrechnungsstunden": 1.0,
                "is_active": True,
                "preferred_praktika_raw": "SFP, ZSP",
                "p_codes": ["SFP", "ZSP"],
                "s_codes": ["MA"],
            },
        ]

    @classmethod
    def _setup_students(cls, subjects):
        students_data = [
            # Anna (GS): Needs PDP I, SFP(D), ZSP(MA) -> 3 Slots
            {
                "student_id": "ST-001",
                "program": "GS",
                "email": "Anna.becker@test.com",
                "primary_subject": subjects["D"],
                "didactic_subject_3": subjects["MA"],
                "pdp1_completed_date": None,
                "sfp_completed_date": None,
                "zsp_completed_date": None,
                "placement_status": "UNPLACED",
            },
            # Max (MS): Needs PDP II, SFP(E), ZSP(SP) -> 3 Slots
            {
                "student_id": "ST-002",
                "program": "MS",
                "email": "Max.becker@test.com",
                "primary_subject": subjects["E"],
                "didactic_subject_3": subjects["SP"],
                "pdp1_completed_date": date(2023, 3, 15),
                "pdp2_completed_date": None,
                "sfp_completed_date": None,
                "zsp_completed_date": None,
                "placement_status": "UNPLACED",
            },
            # Sophie (GS): Needs SFP(D), ZSP(MA) -> 2 Slots
            {
                "student_id": "ST-003",
                "program": "GS",
                "email": "sophie.becker@test.com",
                "primary_subject": subjects["D"],
                "didactic_subject_3": subjects["MA"],
                "pdp1_completed_date": date(2023, 3, 15),
                "pdp2_completed_date": date(2023, 9, 15),
                "sfp_completed_date": None,
                "zsp_completed_date": None,
                "placement_status": "UNPLACED",
            },
            # Lukas (MS): Needs PDP I -> 1 Slot (But waits... he has placed status, so 0)
            # WAIT: In populate_sample_data, Lukas was PLACED.
            # If we mark him UNPLACED here, he generates demand.
            # Total Demand so far: 3 (Anna) + 3 (Max) + 2 (Sophie) = 8.
            # Supply is 8. So we do NOT want Lukas to generate demand.
            {
                "student_id": "ST-004",
                "program": "MS",
                "email": "lukas.becker@test.com",
                "primary_subject": subjects["MA"],
                "pdp1_completed_date": None,
                "placement_status": "PLACED",  # Should be ignored
            },
        ]

        for s_data in students_data:
            Student.objects.get_or_create(
                student_id=s_data["student_id"], defaults=s_data
            )

    def test_solver_finds_valid_solution_with_sample_data(self):
        """
        Runs the solver and verifies it finds a solution with the hard constraints.
        """
        print("\n--- Running Solver in Test ---")
        results = run_solver()

        # 1. Status Check
        self.assertEqual(
            results["status"], "SUCCESS", "Solver should succeed with the added mentor."
        )

        # 2. Capacity Check
        # The solver may produce fewer than full capacity as long as all required coverage buckets are filled.
        # With the current eligibility set, 10 assignments satisfy the coverage constraint.
        total_assignments = Assignment.objects.count()
        self.assertEqual(
            total_assignments,
            10,
            f"Expected 10 total assignments, found {total_assignments}",
        )

        # 3. Coverage Check (The rule we wanted to keep)
        # Check that HSU was covered by someone (SFP or ZSP)
        hsu_covered = Assignment.objects.filter(
            subject__code="HSU", practicum_type__code__in=["SFP", "ZSP"]
        ).exists()
        self.assertTrue(hsu_covered, "An SFP/ZSP-HSU slot must be covered.")

        # Check that Deutsch was covered by someone (likely Julia or Sarah)
        deutsch_covered = Assignment.objects.filter(
            subject__code="D", practicum_type__code="SFP"
        ).exists()
        self.assertTrue(deutsch_covered, "The SFP-Deutsch slot must be covered.")
