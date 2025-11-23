from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import PraktikumsLehrkraft
from schools.models import School
from subjects.models import Subject, PraktikumType


class PraktikumsLehrkraftModelTests(TestCase):
    """
    Tests for PraktikumsLehrkraft model.
    Business Logic: Validate model creation and relationships.
    """

    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name="Test Grundschule",
            school_type="GS",
            district="Passau",
            city="Passau",
            zone=1,
            opnv_code="4a",
        )

        self.subject = Subject.objects.create(code="MATH", name="Mathematik")
        self.pt_pdp1 = PraktikumType.objects.create(code="PDP_I", name="PDP I")

        self.pl = PraktikumsLehrkraft.objects.create(
            first_name="Max",
            last_name="Mustermann",
            email="max@test.de",
            school=self.school,
            program="GS",
            main_subject=self.subject,
            anrechnungsstunden=1.0,
            is_active=True,
        )

        self.pl.available_praktikum_types.add(self.pt_pdp1)
        self.pl.available_subjects.add(self.subject)

    def test_pl_creation_and_capacity(self):
        self.assertEqual(self.pl.anrechnungsstunden, 1.0)
        self.assertEqual(self.pl.capacity, 2)

    def test_4_for_2_capacity(self):
        pl_high_cap = PraktikumsLehrkraft.objects.create(
            first_name="Super",
            last_name="Mentor",
            school=self.school,
            program="GS",
            anrechnungsstunden=2.0,
            current_year_notes="4 für 2 lt. E-Mail",
        )
        self.assertEqual(pl_high_cap.capacity, 4)

    def test_subject_availability(self):
        self.assertIn(self.subject, self.pl.available_subjects.all())

    def test_overrides_storage(self):
        self.pl.current_year_notes = "nur Blockpraktika; Elternzeit"
        self.pl.save()
        self.assertEqual(self.pl.current_year_notes, "nur Blockpraktika; Elternzeit")


class PLAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(
            name="Test School", school_type="GS", zone=1, city="Passau"
        )
        self.subject = Subject.objects.create(code="MA", name="Math")
        self.pl = PraktikumsLehrkraft.objects.create(
            first_name="Max",
            last_name="Test",
            email="test@test.de",
            school=self.school,
            program="GS",
            anrechnungsstunden=1.0,
        )

    def test_create_pl(self):
        data = {
            "first_name": "New",
            "last_name": "Teacher",
            "email": "new@test.de",
            "school": self.school.id,
            "program": "GS",
            "anrechnungsstunden": 2.0,
            "current_year_notes": "Test Note",
        }
        response = self.client.post("/api/pls/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["capacity"], 4)
