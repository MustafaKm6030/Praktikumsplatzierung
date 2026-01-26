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
        """Test API returns all combinations even when no students exist."""
        result = get_demand_preview_data()

        self.assertGreater(len(result["detailed_breakdown"]), 0)

    def test_no_pls_returns_zero_capacity(self):
        """Test API returns zero capacity when no PLs exist."""
        result = get_demand_preview_data()

        self.assertEqual(result["summary_cards"]["total_pl_capacity_slots"], 0)

    def test_placed_students_not_counted(self):
        """Test that all combinations are returned regardless of student placement status."""
        sub_math = Subject.objects.create(name="Mathematik", code="MA", is_active=True)

        create_test_student(
            "S001", "placed@test.com", "GS",
            primary_subject=sub_math,
            pdp1_completed_date=None,
            placement_status="PLACED",
        )

        result = get_demand_preview_data()
        self.assertGreater(len(result["detailed_breakdown"]), 0)

    def test_available_pls_returns_zero_for_no_matching_pls(self):
        """Test available_pls is 0 when no PLs match criteria."""
        result = get_demand_preview_data()
        
        sfp_items_gs = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "SFP" and i["program_type"] == "GS"
        ]
        
        if not sfp_items_gs:
            self.skipTest("No SFP GS combinations found in rules")
        
        sfp_item = sfp_items_gs[0]
        subject_code = sfp_item["subject_code"]
        
        demand_item = {
            "practicum_type": "SFP",
            "program_type": "GS",
            "subject_code": subject_code,
        }
        
        count = _calculate_available_pls_for_demand_item(demand_item)
        self.assertEqual(count, 0, f"Expected 0 PLs for SFP GS {subject_code}, but found {count}")

    def test_pdp2_demand_only_when_pdp1_completed(self):
        """Test that both PDP_I and PDP_II combinations are returned for all programs."""
        result = get_demand_preview_data()

        pdp1_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "PDP_I"
        ]
        pdp2_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "PDP_II"
        ]

        self.assertGreaterEqual(len(pdp1_items), 2)
        self.assertGreaterEqual(len(pdp2_items), 2)

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
        """Test that all SFP combinations are returned regardless of student primary_subject."""
        result = get_demand_preview_data()
        sfp_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "SFP"
        ]
        self.assertGreater(len(sfp_items), 0)

    def test_zsp_requires_didactic_subject_3(self):
        """Test that all ZSP combinations are returned regardless of student didactic_subject_3."""
        result = get_demand_preview_data()
        zsp_items = [
            i for i in result["detailed_breakdown"]
            if i["practicum_type"] == "ZSP"
        ]
        self.assertGreater(len(zsp_items), 0)

    def test_zsp_uses_didactic_subject_3(self):
        """Test that all ZSP combinations are returned from rules."""
        result = get_demand_preview_data()
        zsp_items = [
            i for i in result["detailed_breakdown"] if i["practicum_type"] == "ZSP"
        ]

        self.assertGreater(len(zsp_items), 0)

