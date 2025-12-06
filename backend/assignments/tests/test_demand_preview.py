"""
Test suite for the Demand Preview API endpoint and service functions.
Business Logic: Verify the API returns correct summary cards
and detailed breakdown of demand vs supply for allocation planning.
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.test import TestCase
from datetime import date
from students.models import Student
from subjects.models import Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from assignments.services import (
    get_demand_preview_data,
    _calculate_available_pls_for_demand_item,
    _build_detailed_breakdown,
    _calculate_total_pl_capacity,
    _calculate_summary_cards,
)


class DemandPreviewAPITests(APITestCase):
    """
    Test suite for the Demand Preview API endpoint.
    Business Logic: Verify the API returns correct summary cards
    and detailed breakdown of demand vs supply.
    """

    def setUp(self):
        """Set up test data for demand preview tests."""
        # Create subjects
        self.sub_math = Subject.objects.create(
            name="Mathematik", code="MA", is_active=True
        )
        self.sub_german = Subject.objects.create(
            name="Deutsch", code="D", is_active=True
        )
        self.sub_hsu = Subject.objects.create(
            name="Heimat- und Sachunterricht", code="HSU", is_active=True
        )

        # Create praktikum types
        self.pdp1 = PraktikumType.objects.create(
            code="PDP_I", name="PDP I", is_block_praktikum=True, is_active=True
        )
        self.pdp2 = PraktikumType.objects.create(
            code="PDP_II", name="PDP II", is_block_praktikum=True, is_active=True
        )
        self.sfp = PraktikumType.objects.create(
            code="SFP", name="SFP", is_block_praktikum=False, is_active=True
        )
        self.zsp = PraktikumType.objects.create(
            code="ZSP", name="ZSP", is_block_praktikum=False, is_active=True
        )

        # Create schools (zone=1 for SFP/ZSP eligibility)
        self.school_gs = School.objects.create(
            name="Test GS",
            school_type="GS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a",
            is_active=True,
        )
        self.school_ms = School.objects.create(
            name="Test MS",
            school_type="MS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a",
            is_active=True,
        )

        # Create PLs with different configurations
        self.pl_gs_1 = PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="GS",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=1.0,  # capacity = 2
        )
        self.pl_gs_1.available_praktikum_types.add(
            self.pdp1, self.pdp2, self.sfp, self.zsp
        )
        self.pl_gs_1.available_subjects.add(self.sub_math, self.sub_german)

        self.pl_gs_2 = PraktikumsLehrkraft.objects.create(
            first_name="PL2",
            last_name="GS",
            email="pl2@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=2.0,  # capacity = 4
        )
        self.pl_gs_2.available_praktikum_types.add(self.pdp1, self.sfp)
        self.pl_gs_2.available_subjects.add(self.sub_math)

        # Create students with various needs
        # Student 1: Needs PDP I only
        self.student_1 = Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            pdp1_completed_date=None,
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        # Student 2: Needs PDP II only
        self.student_2 = Student.objects.create(
            student_id="S002",
            first_name="S2",
            last_name="Test",
            email="s2@test.com",
            program="GS",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=None,
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        # Student 3: Needs SFP (with primary_subject for SFP)
        self.student_3 = Student.objects.create(
            student_id="S003",
            first_name="S3",
            last_name="Test",
            email="s3@test.com",
            program="GS",
            primary_subject=self.sub_math,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

    def test_demand_preview_api_returns_200(self):
        """Test that the API endpoint returns HTTP 200."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_demand_preview_api_response_structure(self):
        """Test that response has correct top-level structure."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        self.assertIn("summary_cards", response.data)
        self.assertIn("detailed_breakdown", response.data)

    def test_demand_preview_summary_cards_structure(self):
        """Test summary_cards contains all required fields."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        summary = response.data["summary_cards"]
        self.assertIn("total_demand_slots", summary)
        self.assertIn("total_pl_capacity_slots", summary)
        self.assertIn("total_pdp_demand", summary)
        self.assertIn("total_wednesday_demand", summary)

    def test_demand_preview_detailed_breakdown_structure(self):
        """Test detailed_breakdown items contain all required fields."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        for item in response.data["detailed_breakdown"]:
            self.assertIn("practicum_type", item)
            self.assertIn("program_type", item)
            self.assertIn("subject_code", item)
            self.assertIn("subject_display_name", item)
            self.assertIn("required_slots", item)
            self.assertIn("available_pls", item)

    def test_demand_preview_total_demand_calculation(self):
        """Test total_demand_slots is sum of all required_slots."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        breakdown = response.data["detailed_breakdown"]
        expected_total = sum(item["required_slots"] for item in breakdown)

        self.assertEqual(
            response.data["summary_cards"]["total_demand_slots"], expected_total
        )

    def test_demand_preview_pdp_demand_calculation(self):
        """Test total_pdp_demand includes only PDP_I and PDP_II."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        breakdown = response.data["detailed_breakdown"]
        expected_pdp = sum(
            item["required_slots"]
            for item in breakdown
            if item["practicum_type"] in ["PDP_I", "PDP_II"]
        )

        self.assertEqual(
            response.data["summary_cards"]["total_pdp_demand"], expected_pdp
        )

    def test_demand_preview_wednesday_demand_calculation(self):
        """Test total_wednesday_demand includes only SFP and ZSP."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        breakdown = response.data["detailed_breakdown"]
        expected_wednesday = sum(
            item["required_slots"]
            for item in breakdown
            if item["practicum_type"] in ["SFP", "ZSP"]
        )

        self.assertEqual(
            response.data["summary_cards"]["total_wednesday_demand"], expected_wednesday
        )

    def test_demand_preview_pl_capacity_calculation(self):
        """Test total_pl_capacity_slots equals sum of all PL capacities."""
        # Total capacity: PL1 (2) + PL2 (4) = 6
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        self.assertEqual(response.data["summary_cards"]["total_pl_capacity_slots"], 6)


class DemandPreviewServiceTests(TestCase):
    """
    Test suite for Demand Preview service functions.
    Business Logic: Verify individual service functions work correctly.
    """

    def setUp(self):
        """Set up test data for service tests."""
        # Create subjects
        self.sub_math = Subject.objects.create(
            name="Mathematik", code="MA", is_active=True
        )
        self.sub_german = Subject.objects.create(
            name="Deutsch", code="D", is_active=True
        )

        # Create schools (zone=1 for SFP/ZSP)
        self.school_gs = School.objects.create(
            name="Test GS",
            school_type="GS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a",
            is_active=True,
        )
        self.school_ms = School.objects.create(
            name="Test MS",
            school_type="MS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a",
            is_active=True,
        )

    def test_calculate_available_pls_for_pdp(self):
        """Test PL count for PDP (program match only, no subject filter)."""
        # Create GS PLs
        pl1 = PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="Test",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl2 = PraktikumsLehrkraft.objects.create(
            first_name="PL2",
            last_name="Test",
            email="pl2@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        # Create MS PL (should not be counted for GS)
        pl3 = PraktikumsLehrkraft.objects.create(
            first_name="PL3",
            last_name="Test",
            email="pl3@test.de",
            school=self.school_ms,
            program="MS",
            is_active=True,
        )

        demand_item = {
            "practicum_type": "PDP_I",
            "program_type": "GS",
            "subject_code": "N/A",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 2)  # Only GS PLs

    def test_calculate_available_pls_for_sfp_with_subject(self):
        """Test PL count for SFP (requires subject match)."""
        pl1 = PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="Test",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl1.available_subjects.add(self.sub_math)

        pl2 = PraktikumsLehrkraft.objects.create(
            first_name="PL2",
            last_name="Test",
            email="pl2@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl2.available_subjects.add(self.sub_german)  # Different subject

        demand_item = {
            "practicum_type": "SFP",
            "program_type": "GS",
            "subject_code": "MA",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 1)  # Only PL1 has MA

    def test_calculate_available_pls_for_zsp_with_subject(self):
        """Test PL count for ZSP (requires subject match)."""
        pl1 = PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="Test",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl1.available_subjects.add(self.sub_math, self.sub_german)

        pl2 = PraktikumsLehrkraft.objects.create(
            first_name="PL2",
            last_name="Test",
            email="pl2@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl2.available_subjects.add(self.sub_math)

        demand_item = {
            "practicum_type": "ZSP",
            "program_type": "GS",
            "subject_code": "MA",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 2)  # Both PLs have MA

    def test_calculate_available_pls_excludes_inactive(self):
        """Test that inactive PLs are not counted."""
        pl1 = PraktikumsLehrkraft.objects.create(
            first_name="Active",
            last_name="PL",
            email="active@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl2 = PraktikumsLehrkraft.objects.create(
            first_name="Inactive",
            last_name="PL",
            email="inactive@test.de",
            school=self.school_gs,
            program="GS",
            is_active=False,
        )

        demand_item = {
            "practicum_type": "PDP_I",
            "program_type": "GS",
            "subject_code": "N/A",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 1)  # Only active PL

    def test_calculate_total_pl_capacity_empty(self):
        """Test capacity calculation with no PLs."""
        capacity = _calculate_total_pl_capacity()
        self.assertEqual(capacity, 0)

    def test_calculate_total_pl_capacity_multiple_pls(self):
        """Test capacity calculation with multiple PLs."""
        PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="Test",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=1.0,  # capacity = 2
        )
        PraktikumsLehrkraft.objects.create(
            first_name="PL2",
            last_name="Test",
            email="pl2@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=2.0,  # capacity = 4
        )
        PraktikumsLehrkraft.objects.create(
            first_name="PL3",
            last_name="Test",
            email="pl3@test.de",
            school=self.school_gs,
            program="GS",
            is_active=False,
            anrechnungsstunden=1.5,  # inactive, should not be counted
        )

        capacity = _calculate_total_pl_capacity()
        self.assertEqual(capacity, 6)  # 2 + 4

    def test_build_detailed_breakdown_adds_available_pls(self):
        """Test that build_detailed_breakdown adds available_pls field."""
        pl1 = PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="Test",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        pl1.available_subjects.add(self.sub_math)

        raw_demand = [
            {
                "practicum_type": "SFP",
                "program_type": "GS",
                "subject_code": "MA",
                "subject_display_name": "Mathematik (MA)",
                "required_slots": 5,
            }
        ]

        breakdown = _build_detailed_breakdown(raw_demand)

        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0]["available_pls"], 1)
        self.assertEqual(breakdown[0]["required_slots"], 5)

    def test_calculate_summary_cards_with_mixed_types(self):
        """Test summary cards calculation with different practicum types."""
        detailed_breakdown = [
            {"practicum_type": "PDP_I", "required_slots": 10},
            {"practicum_type": "PDP_II", "required_slots": 15},
            {"practicum_type": "SFP", "required_slots": 20},
            {"practicum_type": "ZSP", "required_slots": 5},
        ]

        summary = _calculate_summary_cards(detailed_breakdown, 100)

        self.assertEqual(summary["total_demand_slots"], 50)
        self.assertEqual(summary["total_pdp_demand"], 25)  # 10 + 15
        self.assertEqual(summary["total_wednesday_demand"], 25)  # 20 + 5
        self.assertEqual(summary["total_pl_capacity_slots"], 100)

    def test_calculate_summary_cards_empty_breakdown(self):
        """Test summary cards calculation with empty breakdown."""
        summary = _calculate_summary_cards([], 50)

        self.assertEqual(summary["total_demand_slots"], 0)
        self.assertEqual(summary["total_pdp_demand"], 0)
        self.assertEqual(summary["total_wednesday_demand"], 0)
        self.assertEqual(summary["total_pl_capacity_slots"], 50)

    def test_get_demand_preview_data_integration(self):
        """Integration test for get_demand_preview_data function."""
        # Create PL
        pl1 = PraktikumsLehrkraft.objects.create(
            first_name="PL1",
            last_name="Test",
            email="pl1@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=1.5,  # capacity = 3
        )
        pl1.available_subjects.add(self.sub_math)

        # Create student needing SFP (uses primary_subject)
        Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            primary_subject=self.sub_math,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        result = get_demand_preview_data()

        # Verify structure
        self.assertIn("summary_cards", result)
        self.assertIn("detailed_breakdown", result)

        # Verify capacity
        self.assertEqual(result["summary_cards"]["total_pl_capacity_slots"], 3)

        # Verify breakdown has required fields
        for item in result["detailed_breakdown"]:
            self.assertIn("available_pls", item)
            self.assertIn("required_slots", item)


class DemandPreviewEdgeCaseTests(TestCase):
    """
    Test suite for edge cases in Demand Preview feature.
    Business Logic: Verify correct behavior with boundary conditions.
    """

    def setUp(self):
        """Set up test data for edge case tests."""
        self.school = School.objects.create(
            name="Test School",
            school_type="GS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a",
            is_active=True,
        )

    def test_no_students_returns_empty_breakdown(self):
        """Test API returns empty breakdown when no students exist."""
        result = get_demand_preview_data()

        self.assertEqual(result["detailed_breakdown"], [])
        self.assertEqual(result["summary_cards"]["total_demand_slots"], 0)

    def test_no_pls_returns_zero_capacity(self):
        """Test API returns zero capacity when no PLs exist."""
        result = get_demand_preview_data()

        self.assertEqual(result["summary_cards"]["total_pl_capacity_slots"], 0)

    def test_placed_students_not_counted(self):
        """Test that PLACED students are not included in demand."""
        sub_math = Subject.objects.create(name="Mathematik", code="MA", is_active=True)

        # Create PLACED student (should be ignored)
        Student.objects.create(
            student_id="S001",
            first_name="Placed",
            last_name="Student",
            email="placed@test.com",
            program="GS",
            primary_subject=sub_math,
            pdp1_completed_date=None,
            placement_status="PLACED",
        )

        result = get_demand_preview_data()

        self.assertEqual(result["summary_cards"]["total_demand_slots"], 0)

    def test_available_pls_returns_zero_for_no_matching_pls(self):
        """Test available_pls is 0 when no PLs match criteria."""
        sub_math = Subject.objects.create(name="Mathematik", code="MA", is_active=True)
        sub_german = Subject.objects.create(name="Deutsch", code="D", is_active=True)

        # Create PL with German subject only
        pl = PraktikumsLehrkraft.objects.create(
            first_name="PL",
            last_name="Test",
            email="pl@test.de",
            school=self.school,
            program="GS",
            is_active=True,
        )
        pl.available_subjects.add(sub_german)

        # Create student needing Math SFP (uses primary_subject)
        Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            primary_subject=sub_math,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        result = get_demand_preview_data()

        # Find the SFP MA item
        sfp_item = next(
            (
                item
                for item in result["detailed_breakdown"]
                if item["practicum_type"] == "SFP"
            ),
            None,
        )

        self.assertIsNotNone(sfp_item)
        self.assertEqual(sfp_item["available_pls"], 0)

    def test_pdp2_demand_only_when_pdp1_completed(self):
        """Test PDP II demand requires PDP I to be completed."""
        # Student with PDP I not completed - should only need PDP I
        Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            pdp1_completed_date=None,
            pdp2_completed_date=None,
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        result = get_demand_preview_data()

        # Should only have PDP_I demand, not PDP_II
        pdp1_demand = sum(
            item["required_slots"]
            for item in result["detailed_breakdown"]
            if item["practicum_type"] == "PDP_I"
        )
        pdp2_demand = sum(
            item["required_slots"]
            for item in result["detailed_breakdown"]
            if item["practicum_type"] == "PDP_II"
        )

        self.assertEqual(pdp1_demand, 1)
        self.assertEqual(pdp2_demand, 0)

    def test_distinct_pl_count_no_duplicates(self):
        """Test that PL count is distinct (no duplicates)."""
        sub_math = Subject.objects.create(name="Mathematik", code="MA", is_active=True)

        # Create PL with multiple subjects (shouldn't be counted twice)
        pl = PraktikumsLehrkraft.objects.create(
            first_name="PL",
            last_name="Test",
            email="pl@test.de",
            school=self.school,
            program="GS",
            is_active=True,
        )
        pl.available_subjects.add(sub_math)

        demand_item = {
            "practicum_type": "SFP",
            "program_type": "GS",
            "subject_code": "MA",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 1)

    def test_sfp_requires_primary_subject(self):
        """Test SFP demand is not generated when primary_subject is None."""
        # Student needs SFP but has no primary_subject
        Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            primary_subject=None,  # No primary subject
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,  # Needs SFP
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        result = get_demand_preview_data()

        # Should have no SFP demand (no primary_subject)
        sfp_demand = sum(
            item["required_slots"]
            for item in result["detailed_breakdown"]
            if item["practicum_type"] == "SFP"
        )
        self.assertEqual(sfp_demand, 0)

    def test_zsp_requires_didactic_subject_3(self):
        """Test ZSP demand is not generated when didactic_subject_3 is None."""
        # Student needs ZSP but has no didactic_subject_3
        Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            didactic_subject_3=None,  # No didactic subject 3
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,  # Needs ZSP
            placement_status="UNPLACED",
        )

        result = get_demand_preview_data()

        # Should have no ZSP demand (no didactic_subject_3)
        zsp_demand = sum(
            item["required_slots"]
            for item in result["detailed_breakdown"]
            if item["practicum_type"] == "ZSP"
        )
        self.assertEqual(zsp_demand, 0)

    def test_zsp_uses_didactic_subject_3(self):
        """Test ZSP demand correctly uses didactic_subject_3."""
        sub_music = Subject.objects.create(name="Musik", code="MU", is_active=True)

        # Student needs ZSP with didactic_subject_3
        Student.objects.create(
            student_id="S001",
            first_name="S1",
            last_name="Test",
            email="s1@test.com",
            program="GS",
            didactic_subject_3=sub_music,  # ZSP uses this
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,  # Needs ZSP
            placement_status="UNPLACED",
        )

        result = get_demand_preview_data()

        # Should have ZSP demand with Music subject
        zsp_items = [
            item
            for item in result["detailed_breakdown"]
            if item["practicum_type"] == "ZSP"
        ]

        self.assertEqual(len(zsp_items), 1)
        self.assertEqual(zsp_items[0]["required_slots"], 1)

