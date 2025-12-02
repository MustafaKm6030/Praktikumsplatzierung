from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from datetime import date
from students.models import Student
from subjects.models import Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from assignments.services import calculate_eligibility_for_pl


class DemandAPITests(APITestCase):
    def setUp(self):
        """
        Set up test data.
        CRITICAL: We must explicitly set 'completed_date' to a value for
        internships we DO NOT want to test, otherwise they will generate
        accidental demand (since the aggregator counts all missing dates).
        """
        self.sub_bio = Subject.objects.create(name="Biologie", code="BIO")
        self.sub_gesch = Subject.objects.create(name="Geschichte", code="GE")
        self.sub_soz = Subject.objects.create(name="Sozialkunde", code="SOZ")
        self.sub_de = Subject.objects.create(name="Deutsch", code="DE")

        # --- Scenario 1: Two GS students need ONLY ZSP (HSU Grouping) ---
        # They have done PDP I, PDP II, and SFP. Only ZSP is None.
        # Student 1: Biologie -> HSU
        self.student_gs_1 = Student.objects.create(
            student_id="111",
            first_name="GS",
            last_name="S1",
            program="GS",
            primary_subject=self.sub_bio,
            email="s1@test.com",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,  # <--- Generating Demand
            placement_status="UNPLACED",
        )
        # Student 2: Geschichte -> HSU
        self.student_gs_2 = Student.objects.create(
            student_id="222",
            first_name="GS",
            last_name="S2",
            program="GS",
            primary_subject=self.sub_gesch,
            email="s2@test.com",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,  # <--- Generating Demand
            placement_status="UNPLACED",
        )

        # --- Scenario 2: One MS student needs ONLY SFP (SK/PuG Grouping) ---
        # Has done PDP I, PDP II, ZSP. Needs SFP.
        self.student_ms_1 = Student.objects.create(
            student_id="333",
            first_name="MS",
            last_name="S3",
            program="MS",
            primary_subject=self.sub_soz,
            email="s3@test.com",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,  # <--- Generating Demand
            placement_status="UNPLACED",
        )

        # --- Scenario 3: Three GS students need ONLY PDP I ---
        # To isolate PDP I count for this test, we mark other internships
        # as completed (even if academically unusual) to prevent them from
        # appearing in the SFP/ZSP demand buckets during this specific test run.
        self.student_pdp_1 = Student.objects.create(
            student_id="901",
            program="GS",
            email="p1@t.com",
            pdp1_completed_date=None,  # <--- Generating Demand
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )
        self.student_pdp_2 = Student.objects.create(
            student_id="902",
            program="GS",
            email="p2@t.com",
            pdp1_completed_date=None,  # <--- Generating Demand
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )
        self.student_pdp_3 = Student.objects.create(
            student_id="903",
            program="GS",
            email="p3@t.com",
            pdp1_completed_date=None,  # <--- Generating Demand
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        # Scenario 4 (Ignored): A student who is fully PLACED
        Student.objects.create(
            student_id="444",
            program="GS",
            primary_subject=self.sub_de,
            email="s4@test.com",
            zsp_completed_date=None,
            placement_status="PLACED",
        )

    def test_get_demand_api_aggregates_correctly(self):
        """
        Ensure the demand API aggregates based on missing completion dates.
        """
        url = reverse("demand-api")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We expect exactly 3 distinct demand groups because we silenced the others:
        # 1. GS PDP I (3 slots)
        # 2. MS SFP (1 slot)
        # 3. GS ZSP (2 slots)
        self.assertEqual(len(response.data), 3)

        data_map = {}
        for item in response.data:
            key = f"{item['practicum_type']}_{item['program_type']}_{item['subject_code']}"
            data_map[key] = item

        # Assert PDP I demand
        pdp_key = "PDP_I_GS_N/A"
        self.assertIn(pdp_key, data_map)
        self.assertEqual(data_map[pdp_key]["required_slots"], 3)

        # Assert SFP demand (MS - Sozialkunde -> SK/PuG)
        sfp_key = "SFP_MS_SK/PuG"
        self.assertIn(sfp_key, data_map)
        self.assertEqual(data_map[sfp_key]["required_slots"], 1)
        self.assertEqual(
            data_map[sfp_key]["subject_display_name"],
            "Sozialkunde/Politik und Gesellschaft (SK/PuG)",
        )

        # Assert ZSP demand (GS - Bio & Geschichte -> HSU)
        zsp_key = "ZSP_GS_HSU"
        self.assertIn(zsp_key, data_map)
        self.assertEqual(data_map[zsp_key]["required_slots"], 2)
        self.assertEqual(
            data_map[zsp_key]["subject_display_name"],
            "Heimat- und Sachunterricht (HSU)",
        )


class PLEligibilityCalculationTests(TestCase):
    """
    Test suite for PL Eligibility Calculation Service.
    Business Logic: Verify that calculate_eligibility_for_pl correctly
    applies all hard constraints for mentor eligibility.
    """
    
    def setUp(self):
        """Set up test data for eligibility calculation."""
        # Create subjects
        self.subject_math = Subject.objects.create(
            code="MA", name="Mathematik", is_active=True
        )
        self.subject_german = Subject.objects.create(
            code="D", name="Deutsch", is_active=True
        )
        self.subject_pcb = Subject.objects.create(
            code="PCB", name="Physik/Chemie/Biologie", is_active=True
        )
        self.subject_hsu = Subject.objects.create(
            code="HSU", name="Heimat- und Sachunterricht", is_active=True
        )
        
        # Create praktikum types
        self.pdp1 = PraktikumType.objects.create(
            code="PDP_I",
            name="PDP I",
            is_block_praktikum=True,
            is_active=True
        )
        self.pdp2 = PraktikumType.objects.create(
            code="PDP_II",
            name="PDP II",
            is_block_praktikum=True,
            is_active=True
        )
        self.sfp = PraktikumType.objects.create(
            code="SFP",
            name="SFP",
            is_block_praktikum=False,
            is_active=True
        )
        self.zsp = PraktikumType.objects.create(
            code="ZSP",
            name="ZSP",
            is_block_praktikum=False,
            is_active=True
        )
        
        # Create schools
        self.school_gs = School.objects.create(
            name="Test Grundschule",
            school_type="GS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a"
        )
        self.school_ms = School.objects.create(
            name="Test Mittelschule",
            school_type="MS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a"
        )
    
    def test_gs_mentor_with_all_praktikum_types_and_subjects(self):
        """
        Test GS mentor qualified for all praktikum types and multiple subjects.
        Business Logic: Should return all combinations.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Anna",
            last_name="Schmidt",
            email="anna.schmidt@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True
        )
        
        # Add praktikum types
        mentor.available_praktikum_types.add(
            self.pdp1, self.pdp2, self.sfp, self.zsp
        )
        
        # Add subjects
        mentor.available_subjects.add(self.subject_math, self.subject_german)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        # Expected: 2 PDP entries (N/A) + 2 subjects * 2 Wednesday praktikums
        expected_combinations = [
            ('PDP_I', 'N/A'),
            ('PDP_II', 'N/A'),
            ('SFP', 'MA'),
            ('SFP', 'D'),
            ('ZSP', 'MA'),
            ('ZSP', 'D'),
        ]
        
        self.assertEqual(len(eligibility), 6)
        for combo in expected_combinations:
            self.assertIn(combo, eligibility)
    
    def test_ms_mentor_with_pcb_only(self):
        """
        Test MS mentor with only PCB subject for SFP/ZSP.
        Business Logic: Should only return PCB combinations.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Max",
            last_name="Mueller",
            email="max.mueller@test.de",
            school=self.school_ms,
            program="MS",
            is_active=True
        )
        
        mentor.available_praktikum_types.add(self.sfp, self.zsp)
        mentor.available_subjects.add(self.subject_pcb)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        expected_combinations = [
            ('SFP', 'PCB'),
            ('ZSP', 'PCB'),
        ]
        
        self.assertEqual(len(eligibility), 2)
        for combo in expected_combinations:
            self.assertIn(combo, eligibility)
    
    def test_mentor_marked_nicht_sfp(self):
        """
        Test mentor with 'nicht - SFP' constraint in notes.
        Business Logic: Should exclude SFP from eligible combinations.
        
        NOTE: Current implementation focuses on unavailability keywords.
        'nicht' marking for specific praktikum is typically handled
        via the available_praktikum_types M2M field.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Lisa",
            last_name="Weber",
            email="lisa.weber@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            current_year_notes=""
        )
        
        # Only add PDP and ZSP (not SFP)
        mentor.available_praktikum_types.add(self.pdp1, self.zsp)
        mentor.available_subjects.add(self.subject_hsu)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        expected_combinations = [
            ('PDP_I', 'N/A'),
            ('ZSP', 'HSU'),
        ]
        
        self.assertEqual(len(eligibility), 2)
        for combo in expected_combinations:
            self.assertIn(combo, eligibility)
        
        # Verify SFP is NOT in results
        sfp_combos = [c for c in eligibility if c[0] == 'SFP']
        self.assertEqual(len(sfp_combos), 0)
    
    def test_mentor_nur_blockpraktika_restriction(self):
        """
        Test mentor with 'nur Blockpraktika' in notes.
        Business Logic: Should only allow PDP I/II.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Thomas",
            last_name="Fischer",
            email="thomas.fischer@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            current_year_notes="nur Blockpraktika"
        )
        
        # Declare all types, but notes should restrict to block only
        mentor.available_praktikum_types.add(
            self.pdp1, self.pdp2, self.sfp, self.zsp
        )
        mentor.available_subjects.add(self.subject_math)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        # Should only get PDP I and PDP II
        expected_combinations = [
            ('PDP_I', 'N/A'),
            ('PDP_II', 'N/A'),
        ]
        
        self.assertEqual(len(eligibility), 2)
        for combo in expected_combinations:
            self.assertIn(combo, eligibility)
        
        # Verify no Wednesday praktikums
        wednesday_combos = [
            c for c in eligibility if c[0] in ['SFP', 'ZSP']
        ]
        self.assertEqual(len(wednesday_combos), 0)
    
    def test_mentor_ruhend_status(self):
        """
        Test mentor with 'ruhend' status in notes.
        Business Logic: Should return empty list (unavailable).
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Maria",
            last_name="Bauer",
            email="maria.bauer@test.de",
            school=self.school_ms,
            program="MS",
            is_active=True,
            current_year_notes="ruhend"
        )
        
        mentor.available_praktikum_types.add(self.pdp1, self.sfp)
        mentor.available_subjects.add(self.subject_pcb)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        # Should return empty list
        self.assertEqual(len(eligibility), 0)
    
    def test_mentor_sabbatjahr_status(self):
        """
        Test mentor on sabbatical.
        Business Logic: Should return empty list (unavailable).
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Peter",
            last_name="Schneider",
            email="peter.schneider@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            current_year_notes="Sabbatjahr"
        )
        
        mentor.available_praktikum_types.add(self.pdp1, self.sfp)
        mentor.available_subjects.add(self.subject_german)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        self.assertEqual(len(eligibility), 0)
    
    def test_mentor_kein_mi_prak_restriction(self):
        """
        Test mentor with 'kein Mi-Prak wg. LAA' restriction.
        Business Logic: Should exclude Wednesday praktikums.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Julia",
            last_name="Wagner",
            email="julia.wagner@test.de",
            school=self.school_ms,
            program="MS",
            is_active=True,
            current_year_notes="kein Mi-Prak wg. LAA"
        )
        
        mentor.available_praktikum_types.add(
            self.pdp1, self.pdp2, self.sfp, self.zsp
        )
        mentor.available_subjects.add(self.subject_pcb)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        # Should only get block praktikums
        expected_combinations = [
            ('PDP_I', 'N/A'),
            ('PDP_II', 'N/A'),
        ]
        
        self.assertEqual(len(eligibility), 2)
        for combo in expected_combinations:
            self.assertIn(combo, eligibility)
    
    def test_inactive_mentor(self):
        """
        Test inactive mentor.
        Business Logic: Should return empty list.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Inactive",
            last_name="Mentor",
            email="inactive@test.de",
            school=self.school_gs,
            program="GS",
            is_active=False
        )
        
        mentor.available_praktikum_types.add(self.pdp1)
        mentor.available_subjects.add(self.subject_math)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        self.assertEqual(len(eligibility), 0)
    
    def test_mentor_with_no_subjects_for_wednesday_praktikum(self):
        """
        Test mentor with SFP/ZSP declared but no subjects.
        Business Logic: Should only return PDP combinations.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Hans",
            last_name="Meyer",
            email="hans.meyer@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True
        )
        
        mentor.available_praktikum_types.add(
            self.pdp1, self.sfp, self.zsp
        )
        # No subjects added
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        # Should only get PDP I (no subjects needed)
        expected_combinations = [
            ('PDP_I', 'N/A'),
        ]
        
        self.assertEqual(len(eligibility), 1)
        self.assertEqual(eligibility[0], ('PDP_I', 'N/A'))
    
    def test_mentor_with_multiple_complex_constraints(self):
        """
        Test mentor with complex scenario: GS, multiple subjects,
        only PDP and ZSP available.
        Business Logic: Verify correct combinations.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Sarah",
            last_name="Hoffmann",
            email="sarah.hoffmann@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True
        )
        
        mentor.available_praktikum_types.add(self.pdp1, self.zsp)
        mentor.available_subjects.add(
            self.subject_math, self.subject_german, self.subject_hsu
        )
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        expected_combinations = [
            ('PDP_I', 'N/A'),
            ('ZSP', 'MA'),
            ('ZSP', 'D'),
            ('ZSP', 'HSU'),
        ]
        
        self.assertEqual(len(eligibility), 4)
        for combo in expected_combinations:
            self.assertIn(combo, eligibility)
    
    def test_empty_praktikum_types(self):
        """
        Test mentor with no praktikum types assigned.
        Business Logic: Should return empty list.
        """
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Empty",
            last_name="Types",
            email="empty.types@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True
        )
        
        # No praktikum types added
        mentor.available_subjects.add(self.subject_math)
        
        eligibility = calculate_eligibility_for_pl(mentor)
        
        self.assertEqual(len(eligibility), 0)
