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


# ==================== TEST DATA FACTORY HELPERS ====================

def create_test_subjects():
    """Create standard test subjects."""
    return {
        "math": Subject.objects.create(name="Mathematik", code="MA", is_active=True),
        "german": Subject.objects.create(name="Deutsch", code="D", is_active=True),
        "hsu": Subject.objects.create(
            name="Heimat- und Sachunterricht", code="HSU", is_active=True
        ),
    }


def create_test_praktikum_types():
    """Create standard test praktikum types."""
    return {
        "pdp1": PraktikumType.objects.create(
            code="PDP_I", name="PDP I", is_block_praktikum=True, is_active=True
        ),
        "pdp2": PraktikumType.objects.create(
            code="PDP_II", name="PDP II", is_block_praktikum=True, is_active=True
        ),
        "sfp": PraktikumType.objects.create(
            code="SFP", name="SFP", is_block_praktikum=False, is_active=True
        ),
        "zsp": PraktikumType.objects.create(
            code="ZSP", name="ZSP", is_block_praktikum=False, is_active=True
        ),
    }


def create_test_school(name, school_type, zone=1, opnv_code="4a"):
    """Create a test school with specified parameters."""
    return School.objects.create(
        name=name,
        school_type=school_type,
        city="Passau",
        district="Passau-Land",
        zone=zone,
        opnv_code=opnv_code,
        is_active=True,
    )


def create_test_pl(first_name, email, school, program, anrechnungsstunden=1.0):
    """Create a test PraktikumsLehrkraft."""
    return PraktikumsLehrkraft.objects.create(
        first_name=first_name,
        last_name="Test",
        email=email,
        school=school,
        program=program,
        is_active=True,
        anrechnungsstunden=anrechnungsstunden,
    )


def create_test_student(student_id, email, program, **kwargs):
    """Create a test student with specified completion dates."""
    defaults = {
        "first_name": f"S{student_id}",
        "last_name": "Test",
        "placement_status": "UNPLACED",
    }
    defaults.update(kwargs)
    return Student.objects.create(
        student_id=student_id, email=email, program=program, **defaults
    )


# ==================== API TESTS ====================

class DemandPreviewAPITests(APITestCase):
    """
    Test suite for the Demand Preview API endpoint.
    Business Logic: Verify the API returns correct summary cards
    and detailed breakdown of demand vs supply.
    """

    def setUp(self):
        """Set up test data for demand preview tests."""
        self._create_subjects()
        self._create_praktikum_types()
        self._create_schools()
        self._create_pls()
        self._create_students()

    def _create_subjects(self):
        """Create test subjects."""
        subjects = create_test_subjects()
        self.sub_math = subjects["math"]
        self.sub_german = subjects["german"]
        self.sub_hsu = subjects["hsu"]

    def _create_praktikum_types(self):
        """Create test praktikum types."""
        types = create_test_praktikum_types()
        self.pdp1 = types["pdp1"]
        self.pdp2 = types["pdp2"]
        self.sfp = types["sfp"]
        self.zsp = types["zsp"]

    def _create_schools(self):
        """Create test schools."""
        self.school_gs = create_test_school("Test GS", "GS")
        self.school_ms = create_test_school("Test MS", "MS")

    def _create_pls(self):
        """Create test PLs with different configurations."""
        self.pl_gs_1 = create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS", 1.0)
        self.pl_gs_1.available_praktikum_types.add(
            self.pdp1, self.pdp2, self.sfp, self.zsp
        )
        self.pl_gs_1.available_subjects.add(self.sub_math, self.sub_german)

        self.pl_gs_2 = create_test_pl("PL2", "pl2@test.de", self.school_gs, "GS", 2.0)
        self.pl_gs_2.available_praktikum_types.add(self.pdp1, self.sfp)
        self.pl_gs_2.available_subjects.add(self.sub_math)

    def _create_students(self):
        """Create test students with various needs."""
        completed = date(2023, 1, 1)

        # Student 1: Needs PDP I only
        self.student_1 = create_test_student(
            "S001", "s1@test.com", "GS",
            pdp1_completed_date=None,
            pdp2_completed_date=completed,
            sfp_completed_date=completed,
            zsp_completed_date=completed,
        )

        # Student 2: Needs PDP II only
        self.student_2 = create_test_student(
            "S002", "s2@test.com", "GS",
            pdp1_completed_date=completed,
            pdp2_completed_date=None,
            sfp_completed_date=completed,
            zsp_completed_date=completed,
        )

        # Student 3: Needs SFP (with primary_subject)
        self.student_3 = create_test_student(
            "S003", "s3@test.com", "GS",
            primary_subject=self.sub_math,
            pdp1_completed_date=completed,
            pdp2_completed_date=completed,
            sfp_completed_date=None,
            zsp_completed_date=completed,
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


# ==================== SERVICE TESTS ====================

class DemandPreviewServiceTests(TestCase):
    """
    Test suite for Demand Preview service functions.
    Business Logic: Verify individual service functions work correctly.
    """

    def setUp(self):
        """Set up test data for service tests."""
        subjects = create_test_subjects()
        self.sub_math = subjects["math"]
        self.sub_german = subjects["german"]

        self.school_gs = create_test_school("Test GS", "GS")
        self.school_ms = create_test_school("Test MS", "MS")

    def test_calculate_available_pls_for_pdp(self):
        """Test PL count for PDP (program match only, no subject filter)."""
        create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS")
        create_test_pl("PL2", "pl2@test.de", self.school_gs, "GS")
        create_test_pl("PL3", "pl3@test.de", self.school_ms, "MS")

        demand_item = {
            "practicum_type": "PDP_I",
            "program_type": "GS",
            "subject_code": "N/A",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 2)  # Only GS PLs

    def test_calculate_available_pls_for_sfp_with_subject(self):
        """Test PL count for SFP (requires subject match)."""
        pl1 = create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS")
        pl1.available_subjects.add(self.sub_math)

        pl2 = create_test_pl("PL2", "pl2@test.de", self.school_gs, "GS")
        pl2.available_subjects.add(self.sub_german)

        demand_item = {
            "practicum_type": "SFP",
            "program_type": "GS",
            "subject_code": "MA",
        }

        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 1)  # Only PL1 has MA

    def test_calculate_available_pls_for_zsp_with_subject(self):
        """Test PL count for ZSP (requires subject match)."""
        pl1 = create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS")
        pl1.available_subjects.add(self.sub_math, self.sub_german)

        pl2 = create_test_pl("PL2", "pl2@test.de", self.school_gs, "GS")
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
        create_test_pl("Active", "active@test.de", self.school_gs, "GS")
        inactive_pl = create_test_pl("Inactive", "inactive@test.de", self.school_gs, "GS")
        inactive_pl.is_active = False
        inactive_pl.save()

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
        create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS", 1.0)  # capacity=2
        create_test_pl("PL2", "pl2@test.de", self.school_gs, "GS", 2.0)  # capacity=4

        inactive = create_test_pl("PL3", "pl3@test.de", self.school_gs, "GS", 1.5)
        inactive.is_active = False
        inactive.save()

        capacity = _calculate_total_pl_capacity()
        self.assertEqual(capacity, 6)  # 2 + 4

    def test_build_detailed_breakdown_adds_available_pls(self):
        """Test that build_detailed_breakdown adds available_pls field."""
        pl1 = create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS")
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
        pl1 = create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS", 1.5)
        pl1.available_subjects.add(self.sub_math)

        create_test_student(
            "S001", "s1@test.com", "GS",
            primary_subject=self.sub_math,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,
            zsp_completed_date=date(2023, 1, 1),
        )

        result = get_demand_preview_data()

        self.assertIn("summary_cards", result)
        self.assertIn("detailed_breakdown", result)
        self.assertEqual(result["summary_cards"]["total_pl_capacity_slots"], 3)

        for item in result["detailed_breakdown"]:
            self.assertIn("available_pls", item)
            self.assertIn("required_slots", item)


# ==================== EDGE CASE TESTS ====================

class DemandPreviewEdgeCaseTests(TestCase):
    """
    Test suite for edge cases in Demand Preview feature.
    Business Logic: Verify correct behavior with boundary conditions.
    """

    def setUp(self):
        """Set up test data for edge case tests."""
        self.school = create_test_school("Test School", "GS")

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

        create_test_student(
            "S001", "placed@test.com", "GS",
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

        pl = create_test_pl("PL", "pl@test.de", self.school, "GS")
        pl.available_subjects.add(sub_german)

        create_test_student(
            "S001", "s1@test.com", "GS",
            primary_subject=sub_math,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,
            zsp_completed_date=date(2023, 1, 1),
        )

        result = get_demand_preview_data()
        sfp_item = next(
            (i for i in result["detailed_breakdown"] if i["practicum_type"] == "SFP"),
            None,
        )

        self.assertIsNotNone(sfp_item)
        self.assertEqual(sfp_item["available_pls"], 0)

    def test_pdp2_demand_only_when_pdp1_completed(self):
        """Test PDP II demand requires PDP I to be completed."""
        create_test_student(
            "S001", "s1@test.com", "GS",
            pdp1_completed_date=None,
            pdp2_completed_date=None,
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
        )

        result = get_demand_preview_data()

        pdp1_demand = sum(
            i["required_slots"]
            for i in result["detailed_breakdown"]
            if i["practicum_type"] == "PDP_I"
        )
        pdp2_demand = sum(
            i["required_slots"]
            for i in result["detailed_breakdown"]
            if i["practicum_type"] == "PDP_II"
        )

        self.assertEqual(pdp1_demand, 1)
        self.assertEqual(pdp2_demand, 0)

    def test_distinct_pl_count_no_duplicates(self):
        """Test that PL count is distinct (no duplicates)."""
        sub_math = Subject.objects.create(name="Mathematik", code="MA", is_active=True)

        pl = create_test_pl("PL", "pl@test.de", self.school, "GS")
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
        create_test_student(
            "S001", "s1@test.com", "GS",
            primary_subject=None,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,
            zsp_completed_date=date(2023, 1, 1),
        )

        result = get_demand_preview_data()
        sfp_demand = sum(
            i["required_slots"]
            for i in result["detailed_breakdown"]
            if i["practicum_type"] == "SFP"
        )
        self.assertEqual(sfp_demand, 0)

    def test_zsp_requires_didactic_subject_3(self):
        """Test ZSP demand is not generated when didactic_subject_3 is None."""
        create_test_student(
            "S001", "s1@test.com", "GS",
            didactic_subject_3=None,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,
        )

        result = get_demand_preview_data()
        zsp_demand = sum(
            i["required_slots"]
            for i in result["detailed_breakdown"]
            if i["practicum_type"] == "ZSP"
        )
        self.assertEqual(zsp_demand, 0)

    def test_zsp_uses_didactic_subject_3(self):
        """Test ZSP demand correctly uses didactic_subject_3."""
        sub_music = Subject.objects.create(name="Musik", code="MU", is_active=True)

        create_test_student(
            "S001", "s1@test.com", "GS",
            didactic_subject_3=sub_music,
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,
        )

        result = get_demand_preview_data()
        zsp_items = [
            i for i in result["detailed_breakdown"] if i["practicum_type"] == "ZSP"
        ]

        self.assertEqual(len(zsp_items), 1)
        self.assertEqual(zsp_items[0]["required_slots"], 1)
