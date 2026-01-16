from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import School
from .services import (
    get_reachable_schools,
    geocode_school,
    geocode_schools_batch,
)
from unittest.mock import patch, MagicMock
from decimal import Decimal


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
        self.assertEqual(self.gs_school.geocoding_status, "pending")
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
        cls._setup_valid_wednesday_schools()
        cls._setup_valid_block_schools()
        cls._setup_invalid_schools()

    @classmethod
    def _setup_valid_wednesday_schools(cls):
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

    @classmethod
    def _setup_valid_block_schools(cls):
        # School C: Only valid for Block internships (Zone 3)
        cls.school_c = School.objects.create(
            name="School C (Block, Z3)",
            school_type="GS",
            zone=3,
            opnv_code="",
            is_active=True,
            city="C",
        )

    @classmethod
    def _setup_invalid_schools(cls):
        # School D: Valid for Wednesday (Zone 1, even without ÖPNV due to permissive logic)
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
        Verify that Wednesday Praktika (SFP, ZSP) are filtered by Zone 1/2.
        Updated: We now allow empty ÖPNV codes if the Zone is correct.
        """
        # Test for SFP
        reachable_sfp = get_reachable_schools("SFP")

        # Should include A, B, AND D (Zone 1 with empty ÖPNV)
        self.assertEqual(reachable_sfp.count(), 3)
        self.assertIn(self.school_a, reachable_sfp)
        self.assertIn(self.school_b, reachable_sfp)
        self.assertIn(self.school_d, reachable_sfp)  # This is now valid

        # Should NOT include Zone 3 or Inactive
        self.assertNotIn(self.school_c, reachable_sfp)
        self.assertNotIn(self.school_e, reachable_sfp)

        # Test for ZSP (should have the same result)
        reachable_zsp = get_reachable_schools("ZSP")
        self.assertEqual(reachable_zsp.count(), 3)
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


class GeocodingServicesTests(TestCase):
    """
    Tests for the geocoding logic in schools/services.py.
    Uses mocking to simulate external API calls.
    """

    def setUp(self):
        # A school that needs geocoding
        self.school_pending = School.objects.create(
            name="Test School Pending",
            city="Passau",
            school_type="GS",
            zone=1,
            geocoding_status="pending",
            latitude=None,  # Explicitly null
            longitude=None,
        )

        # A school that has already been geocoded
        self.school_success = School.objects.create(
            name="Test School Success",
            city="Regen",
            school_type="GS",
            zone=3,
            geocoding_status="success",
            latitude=48.97,
            longitude=13.12,
        )

        # A school that previously failed
        self.school_failed = School.objects.create(
            name="Test School Failed",
            city="Nowhere",
            school_type="MS",
            zone=2,
            geocoding_status="failed",
            latitude=None,
            longitude=None,
        )

    @patch("schools.services.Nominatim")
    def test_geocode_school_success(self, MockNominatim):
        """
        Verify that a pending school is successfully geocoded.
        """
        # --- 1. MOCK SETUP ---
        # Create a mock geolocator instance
        mock_geolocator = MockNominatim.return_value

        # Create a mock location object that the geocode method will return
        mock_location = MagicMock()
        mock_location.latitude = 48.5714
        mock_location.longitude = 13.4632

        # Configure the mock to return our location object
        mock_geolocator.geocode.return_value = mock_location

        # --- 2. EXECUTE ---
        result = geocode_school(self.school_pending)

        # --- 3. ASSERT ---
        self.assertTrue(result)

        # Refresh the object from the DB to see the saved changes
        self.school_pending.refresh_from_db()

        self.assertEqual(self.school_pending.latitude, Decimal("48.5714"))
        self.assertEqual(self.school_pending.longitude, Decimal("13.4632"))
        self.assertEqual(self.school_pending.geocoding_status, "success")

        # Ensure the geocode method was called with the correct address
        mock_geolocator.geocode.assert_called_once_with(
            "Test School Pending, Passau, Germany", timeout=10
        )

    @patch("schools.services.Nominatim")
    def test_geocode_school_no_results(self, MockNominatim):
        """
        Verify that a school's status is set to 'failed' if no location is found.
        """
        # Configure the mock to return None (no results)
        mock_geolocator = MockNominatim.return_value
        mock_geolocator.geocode.return_value = None

        result = geocode_school(self.school_failed)

        self.assertFalse(result)
        self.school_failed.refresh_from_db()
        self.assertEqual(self.school_failed.geocoding_status, "failed")
        self.assertIsNone(self.school_failed.latitude)  # Coordinates should remain null

    @patch("schools.services.Nominatim")
    def test_geocode_school_skips_already_successful(self, MockNominatim):
        """
        Verify that the geocoding service is not called for a school already marked as 'success'.
        """
        mock_geolocator = MockNominatim.return_value

        result = geocode_school(self.school_success)

        self.assertTrue(result)
        # The key assertion: the external API was never called
        mock_geolocator.geocode.assert_not_called()
        self.school_success.refresh_from_db()
        # Status should remain 'success'
        self.assertEqual(self.school_success.geocoding_status, "success")

    @patch("schools.services.geocode_school")
    def test_geocode_schools_batch(self, mock_geocode_school):
        """
        Verify the batch processing function calls the single geocode function for pending/failed schools.
        """
        # We want to test the batch logic, not the actual geocoding, so we mock the inner function
        mock_geocode_school.return_value = True  # Assume success for every call

        # Create another pending school for the batch
        School.objects.create(
            name="Another Pending",
            city="City",
            school_type="GS",
            zone=1,
            geocoding_status="pending",
        )

        # The batch should find the 2 pending schools
        schools_to_process = School.objects.filter(geocoding_status="pending")
        self.assertEqual(schools_to_process.count(), 2)

        stats = geocode_schools_batch(
            schools_queryset=schools_to_process, delay_between_requests=0
        )

        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["success"], 2)
        self.assertEqual(stats["failed"], 0)

        # Check that the mocked function was called twice
        self.assertEqual(mock_geocode_school.call_count, 2)
