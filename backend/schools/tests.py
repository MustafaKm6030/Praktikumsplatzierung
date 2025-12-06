from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import School
from .services import get_reachable_schools


class SchoolModelTests(TestCase):
    def setUp(self):
        self.gs_school = School.objects.create(
            name="Grundschule Passau",
            school_type="GS",
            district="Passau",
            city="Passau",
            zone=1,
            opnv_code="4a",
            distance_km=7,
            is_active=True,
        )

    def test_school_creation(self):
        self.assertEqual(self.gs_school.name, "Grundschule Passau")
        self.assertEqual(self.gs_school.school_type, "GS")
        self.assertEqual(self.gs_school.zone, 1)
        self.assertEqual(self.gs_school.opnv_code, "4a")

    def test_school_string_representation(self):
        expected = "Grundschule Passau"
        self.assertEqual(str(self.gs_school), expected)


class SchoolServicesTests(TestCase):
    """Tests for business logic in schools/services.py."""

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase to test filtering logic."""
        # School A: Perfect for Wednesday internships (Zone 1, 4a)
        cls.school_a = School.objects.create(
            name="School A (Wed, Z1, 4a)",
            school_type="GS",
            zone=1,
            opnv_code="4a",
            is_active=True,
            city="A",
        )

        # School B: Good for Wednesday internships (Zone 2, 4b)
        cls.school_b = School.objects.create(
            name="School B (Wed, Z2, 4b)",
            school_type="MS",
            zone=2,
            opnv_code="4b",
            is_active=True,
            city="B",
        )

        # School C: Only valid for Block internships (Zone 3)
        cls.school_c = School.objects.create(
            name="School C (Block, Z3)",
            school_type="GS",
            zone=3,
            opnv_code="",
            is_active=True,
            city="C",
        )

        # School D: Invalid for Wednesday internships (Zone 1 but no ÖPNV code)
        cls.school_d = School.objects.create(
            name="School D (Block, Z1, no ÖPNV)",
            school_type="MS",
            zone=1,
            opnv_code="",
            is_active=True,
            city="D",
        )

        # School E: Inactive, should never be included in any results
        cls.school_e = School.objects.create(
            name="School E (Inactive)",
            school_type="GS",
            zone=1,
            opnv_code="4a",
            is_active=False,
            city="E",
        )

    def test_get_reachable_schools_for_block_praktikum(self):
        """
        Verify that Block Praktika (PDP_I, PDP_II) can be at any *active* school in any zone.
        """
        # Test for PDP_I
        reachable_pdp1 = get_reachable_schools("PDP_I")
        self.assertEqual(reachable_pdp1.count(), 4)  # A, B, C, D
        self.assertIn(self.school_c, reachable_pdp1)  # Zone 3 school must be included
        self.assertNotIn(
            self.school_e, reachable_pdp1
        )  # Inactive school must be excluded

        # Test for PDP_II (should have the same result)
        reachable_pdp2 = get_reachable_schools("PDP_II")
        self.assertEqual(reachable_pdp2.count(), 4)
        self.assertQuerysetEqual(reachable_pdp1, reachable_pdp2, ordered=False)

    def test_get_reachable_schools_for_wednesday_praktikum(self):
        """
        Verify that Wednesday Praktika (SFP, ZSP) are strictly filtered:
        - Must be Zone 1 or 2
        - Must have ÖPNV code '4a' or '4b'
        - Must be active
        """
        # Test for SFP
        reachable_sfp = get_reachable_schools("SFP")
        self.assertEqual(reachable_sfp.count(), 2)  # Only A and B
        self.assertIn(self.school_a, reachable_sfp)
        self.assertIn(self.school_b, reachable_sfp)
        self.assertNotIn(self.school_c, reachable_sfp)  # Exclude Zone 3
        self.assertNotIn(self.school_d, reachable_sfp)  # Exclude school with no ÖPNV
        self.assertNotIn(self.school_e, reachable_sfp)  # Exclude inactive school

        # Test for ZSP (should have the same result)
        reachable_zsp = get_reachable_schools("ZSP")
        self.assertEqual(reachable_zsp.count(), 2)
        self.assertQuerysetEqual(reachable_sfp, reachable_zsp, ordered=False)

    def test_get_reachable_schools_for_unknown_type(self):
        """
        Verify that an unknown praktikum type returns an empty queryset.
        """
        reachable_schools = get_reachable_schools("UNKNOWN_TYPE")
        self.assertEqual(reachable_schools.count(), 0)


class SchoolAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.school1 = School.objects.create(
            name="Test Grundschule",
            school_type="GS",
            district="Passau",
            city="Passau",
            zone=1,
            opnv_code="4a",
        )

    def test_get_schools_list(self):
        response = self.client.get("/api/schools/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Grundschule")

    def test_create_school(self):
        data = {
            "name": "New School",
            "school_type": "MS",
            "district": "Regen",
            "city": "Regen",
            "zone": 3,
            "opnv_code": "",  # Can be blank
            "distance_km": 80,
        }
        response = self.client.post("/api/schools/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 2)
