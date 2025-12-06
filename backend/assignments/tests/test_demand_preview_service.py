"""
Service layer tests for Demand Preview functions.
Business Logic: Verify individual service functions work correctly.
"""
from django.test import TestCase
from datetime import date

from assignments.services import (
    get_demand_preview_data,
    _calculate_available_pls_for_demand_item,
    _build_detailed_breakdown,
    _calculate_total_pl_capacity,
    _calculate_summary_cards,
)
from .factories import (
    create_test_subjects,
    create_test_school,
    create_test_pl,
    create_test_student,
)


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
        self.assertEqual(count, 2)

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
        self.assertEqual(count, 1)

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
        self.assertEqual(count, 2)

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
        self.assertEqual(count, 1)

    def test_calculate_total_pl_capacity_empty(self):
        """Test capacity calculation with no PLs."""
        capacity = _calculate_total_pl_capacity()
        self.assertEqual(capacity, 0)

    def test_calculate_total_pl_capacity_multiple_pls(self):
        """Test capacity calculation with multiple PLs."""
        create_test_pl("PL1", "pl1@test.de", self.school_gs, "GS", 1.0)
        create_test_pl("PL2", "pl2@test.de", self.school_gs, "GS", 2.0)

        inactive = create_test_pl("PL3", "pl3@test.de", self.school_gs, "GS", 1.5)
        inactive.is_active = False
        inactive.save()

        capacity = _calculate_total_pl_capacity()
        self.assertEqual(capacity, 6)

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
        self.assertEqual(summary["total_pdp_demand"], 25)
        self.assertEqual(summary["total_wednesday_demand"], 25)
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

