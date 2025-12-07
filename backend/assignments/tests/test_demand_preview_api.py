"""
API tests for the Demand Preview endpoint.
Business Logic: Verify the API returns correct response structure and data.
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import date

from .factories import (
    create_test_subjects,
    create_test_praktikum_types,
    create_test_school,
    create_test_pl,
    create_test_student,
)
from praktikums_lehrkraft.models import PraktikumsLehrkraft


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

        self.student_1 = create_test_student(
            "S001", "s1@test.com", "GS",
            pdp1_completed_date=None,
            pdp2_completed_date=completed,
            sfp_completed_date=completed,
            zsp_completed_date=completed,
        )

        self.student_2 = create_test_student(
            "S002", "s2@test.com", "GS",
            pdp1_completed_date=completed,
            pdp2_completed_date=None,
            sfp_completed_date=completed,
            zsp_completed_date=completed,
        )

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
        """Test total_pdp_demand returns count of PLs who can supervise PDP_I and PDP_II."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        pls_with_pdp = PraktikumsLehrkraft.objects.filter(
            is_active=True,
            available_praktikum_types__code__in=['PDP_I', 'PDP_II']
        ).distinct().count()

        self.assertEqual(
            response.data["summary_cards"]["total_pdp_demand"], pls_with_pdp
        )

    def test_demand_preview_wednesday_demand_calculation(self):
        """Test total_wednesday_demand returns count of PLs who can supervise SFP and ZSP."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        pls_with_wednesday = PraktikumsLehrkraft.objects.filter(
            is_active=True,
            available_praktikum_types__code__in=['SFP', 'ZSP']
        ).distinct().count()

        self.assertEqual(
            response.data["summary_cards"]["total_wednesday_demand"], pls_with_wednesday
        )

    def test_demand_preview_pl_capacity_calculation(self):
        """Test total_pl_capacity_slots equals sum of all PL capacities."""
        url = reverse("demand-preview-api")
        response = self.client.get(url)

        self.assertEqual(response.data["summary_cards"]["total_pl_capacity_slots"], 6)

