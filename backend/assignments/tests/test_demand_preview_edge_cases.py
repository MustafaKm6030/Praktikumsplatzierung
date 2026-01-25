"""
Edge case tests for Demand Preview feature.
Business Logic: Verify correct behavior with boundary conditions.
"""
from django.test import TestCase
from datetime import date

from subjects.models import Subject
from assignments.services import (
    get_demand_preview_data,
    _calculate_available_pls_for_demand_item,
)
from .factories import create_test_school, create_test_pl, create_test_student


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
        self.assertEqual(len(result["detailed_breakdown"]), 0)

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

        pdp1_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "PDP_I"
        ]
        pdp2_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "PDP_II"
        ]

        self.assertEqual(len(pdp1_items), 1)
        self.assertEqual(len(pdp2_items), 0)

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
        sfp_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "SFP"
        ]
        self.assertEqual(len(sfp_items), 0)

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
        zsp_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "ZSP"
        ]
        self.assertEqual(len(zsp_items), 0)

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

