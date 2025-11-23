from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import School


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
