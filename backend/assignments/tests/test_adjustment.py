# in backend/assignments/tests/test_adjustment.py

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from subjects.models import Subject, PraktikumType
from assignments.models import Assignment


class AssignmentAdjustmentAPITests(APITestCase):
    def setUp(self):
        """Set up a complete scenario for testing manual adjustments."""
        self.client = APIClient()

        # --- Create the world ---
        school = School.objects.create(
            name="Test School", school_type="GS", zone=1, city="Passau", opnv_code="4a"
        )

        # Subjects
        self.sub_d = Subject.objects.create(code="D", name="Deutsch")
        self.sub_m = Subject.objects.create(code="MA", name="Mathematik")
        self.sub_hsu = Subject.objects.create(code="HSU", name="HSU")

        # Praktikum Types
        self.pt_pdp1 = PraktikumType.objects.create(
            code="PDP_I", name="PDP I", is_block_praktikum=True
        )
        self.pt_sfp = PraktikumType.objects.create(
            code="SFP", name="SFP", is_block_praktikum=False
        )
        self.pt_zsp = PraktikumType.objects.create(
            code="ZSP", name="ZSP", is_block_praktikum=False
        )

        # --- Create the Mentor ---
        self.mentor = PraktikumsLehrkraft.objects.create(
            first_name="Julia",
            last_name="Fischer",
            email="julia@test.com",
            school=school,
            program="GS",
            anrechnungsstunden=1.0,
            preferred_praktika_raw="PDP I, SFP, ZSP",
        )
        self.mentor.available_praktikum_types.add(
            self.pt_pdp1, self.pt_sfp, self.pt_zsp
        )
        self.mentor.available_subjects.add(self.sub_d, self.sub_m, self.sub_hsu)

        # --- Create Initial Solver Assignment ---
        self.initial_assignment_1 = Assignment.objects.create(
            mentor=self.mentor, practicum_type=self.pt_pdp1, subject=None, school=school
        )
        self.initial_assignment_2 = Assignment.objects.create(
            mentor=self.mentor,
            practicum_type=self.pt_sfp,
            subject=self.sub_d,
            school=school,
        )

    def test_get_adjustment_data(self):
        """
        Verify GET /api/pls/{id}/adjustment-data/ returns the correct structure.
        """
        url = reverse(
            "pl-adjustment-data", kwargs={"pk": self.mentor.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["mentor_id"], self.mentor.id)
        self.assertEqual(data["capacity"], 2)

        # Check current assignments
        self.assertEqual(len(data["current_assignments"]), 2)
        self.assertIn(
            {"practicum_type": "PDP_I", "subject_code": "N/A"},
            data["current_assignments"],
        )
        self.assertIn(
            {"practicum_type": "SFP", "subject_code": "D"}, data["current_assignments"]
        )

        # Check all possible eligibilities
        # PDP_I, SFP(D), SFP(MA), ZSP(D), ZSP(MA), ZSP(HSU) = 6 total
        # Note: HSU is not allowed for SFP in GS program, only for ZSP
        self.assertEqual(len(data["all_eligibilities"]), 6)
        self.assertIn(
            {"practicum_type": "ZSP", "subject_code": "MA"}, data["all_eligibilities"]
        )

    def test_adjust_assignment_success(self):
        """
        Verify POST /api/assignments/adjust/ successfully updates assignments.
        """
        url = reverse("assignment-adjust")
        payload = {
            "mentor_id": self.mentor.id,
            "force_override": False,
            "proposed_assignments": [
                {"practicum_type": "PDP_I", "subject_code": "N/A"},
                {
                    "practicum_type": "ZSP",
                    "subject_code": "MA",
                },  # Changed SFP-D to ZSP-MA
            ],
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the database was updated
        self.assertEqual(Assignment.objects.filter(mentor=self.mentor).count(), 2)
        self.assertTrue(
            Assignment.objects.filter(
                mentor=self.mentor, practicum_type__code="ZSP", subject__code="MA"
            ).exists()
        )
        self.assertFalse(
            Assignment.objects.filter(
                mentor=self.mentor, practicum_type__code="SFP"
            ).exists()
        )

    def test_adjust_assignment_fails_on_invalid_pair(self):
        """
        Verify the adjustment fails if `force_override` is false and the pair is invalid.
        """
        url = reverse("assignment-adjust")
        payload = {
            "mentor_id": self.mentor.id,
            "force_override": False,
            "proposed_assignments": [
                {"practicum_type": "SFP", "subject_code": "D"},
                {
                    "practicum_type": "SFP",
                    "subject_code": "MA",
                },  # Invalid pair: SFP + SFP
            ],
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid Pair", response.data["error"])

    def test_adjust_assignment_succeeds_with_force_override(self):
        """
        Verify the adjustment succeeds with an invalid pair IF `force_override` is true.
        """
        url = reverse("assignment-adjust")
        payload = {
            "mentor_id": self.mentor.id,
            "force_override": True,  # Forcing the invalid pair
            "proposed_assignments": [
                {"practicum_type": "SFP", "subject_code": "D"},
                {"practicum_type": "SFP", "subject_code": "MA"},
            ],
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Assignment.objects.filter(
                mentor=self.mentor, practicum_type__code="SFP"
            ).count(),
            2,
        )
