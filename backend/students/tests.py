from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date
from subjects.models import Subject

# We now only import the Student model
from .models import Student


class StudentModelTests(TestCase):
    def setUp(self):
        self.deutsch = Subject.objects.create(code="DE", name="Deutsch")

        self.student = Student.objects.create(
            student_id="12345",
            first_name="Max",
            last_name="Mustermann",
            email="max.mustermann@uni-passau.de",
            program="GS",
            primary_subject=self.deutsch,
            home_address="Test Street 123, 94032 Passau",
            semester_address="Innstrasse 40, 94032 Passau",
        )

    def test_student_creation(self):
        """Test the basic creation of a student."""
        self.assertEqual(self.student.student_id, "12345")
        self.assertEqual(self.student.first_name, "Max")
        self.assertEqual(self.student.program, "GS")
        self.assertEqual(self.student.home_address, "Test Street 123, 94032 Passau")

    def test_internship_completion_status(self):
        """Test that internship completion dates work as a checklist."""
        # By default, all should be None (not completed)
        self.assertIsNone(self.student.pdp1_completed_date)
        self.assertIsNone(self.student.sfp_completed_date)

        # Mark an internship as completed
        self.student.sfp_completed_date = date(2025, 8, 1)
        self.student.save()

        self.assertIsNotNone(self.student.sfp_completed_date)
        self.assertEqual(self.student.sfp_completed_date.year, 2025)

    def test_placement_status_default(self):
        """Test that a new student is 'UNPLACED' by default."""
        self.assertEqual(self.student.placement_status, "UNPLACED")


class StudentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject = Subject.objects.create(code="MA", name="Mathematik")

        self.student1 = Student.objects.create(
            student_id="ST001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            program="GS",
            primary_subject=self.subject,
            home_address="Home Address 1",
        )

        self.student2 = Student.objects.create(
            student_id="ST002",
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            program="MS",
            home_address="Home Address 2",
        )

    def test_get_students_list(self):
        response = self.client.get("/api/students/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_student_detail(self):
        response = self.client.get(f"/api/students/{self.student1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_id"], "ST001")
        # This confirms the new field is present in the API
        self.assertIn("pdp1_completed_date", response.data)

    def test_create_student(self):
        data = {
            "student_id": "ST003",
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob@test.com",
            "program": "GS",
        }
        response = self.client.post("/api/students/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 3)

    def test_update_student_completion_status(self):
        """Test that we can update completion status via the API."""
        data = {"sfp_completed_date": "2025-09-15"}
        response = self.client.patch(
            f"/api/students/{self.student1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student1.refresh_from_db()
        self.assertEqual(str(self.student1.sfp_completed_date), "2025-09-15")
