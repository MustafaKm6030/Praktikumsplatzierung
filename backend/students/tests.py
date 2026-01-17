from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date
from subjects.models import Subject
from .models import Student


class StudentModelTests(TestCase):
    def setUp(self):
        self.deutsch = Subject.objects.create(code="DE", name="Deutsch")
        self.math = Subject.objects.create(code="MA", name="Mathematik")
        self.sport = Subject.objects.create(code="SP", name="Sport")
        self.english = Subject.objects.create(code="E", name="English")

        self.student = Student.objects.create(
            student_id="12345",
            first_name="Max",
            last_name="Mustermann",
            email="max.mustermann@uni-passau.de",
            program="GS",
            primary_subject=self.english,
            didactic_subject_1=self.deutsch,
            didactic_subject_2=self.math,
            didactic_subject_3=self.sport,
            home_address="Test Street 123, 94032 Passau",
            semester_address="Innstrasse 40, 94032 Passau",
        )

    def test_student_creation_and_subjects(self):
        """Test that student is created with correct subjects."""
        self.assertEqual(self.student.student_id, "12345")
        self.assertEqual(self.student.primary_subject.name, "English")
        self.assertEqual(self.student.didactic_subject_1.name, "Deutsch")
        self.assertEqual(self.student.didactic_subject_2.name, "Mathematik")
        self.assertEqual(self.student.didactic_subject_3.name, "Sport")

    def test_internship_completion_status(self):
        """Test that internship completion dates work as a checklist."""
        self.assertIsNone(self.student.sfp_completed_date)
        self.student.sfp_completed_date = date(2025, 8, 1)
        self.student.save()
        self.assertIsNotNone(self.student.sfp_completed_date)

    def test_placement_status_default(self):
        """Test that a new student is 'UNPLACED' by default."""
        self.assertEqual(self.student.placement_status, "UNPLACED")


class StudentAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject_de = Subject.objects.create(code="DE", name="Deutsch")
        self.subject_ma = Subject.objects.create(code="MA", name="Mathematik")
        self.subject_sp = Subject.objects.create(code="SP", name="Sport")
        self.subject_en = Subject.objects.create(code="E", name="English")

        self.student1 = Student.objects.create(
            student_id="ST001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            program="GS",
            primary_subject=self.subject_en,
            didactic_subject_1=self.subject_de,
            didactic_subject_2=self.subject_ma,
            didactic_subject_3=self.subject_sp,  # ZSP Target is Sport
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
        # Check that new subject name is in the list view
        self.assertIn("zsp_subject_name", response.data[0])
        self.assertEqual(response.data[0]["zsp_subject_name"], "Sport")

    def test_get_student_detail(self):
        response = self.client.get(f"/api/students/{self.student1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_id"], "ST001")
        self.assertIn("didactic_subject_1", response.data)  # Check for new fields
        self.assertEqual(response.data["didactic_subject_3_name"], "Sport")

    def test_create_student_with_subjects(self):
        data = {
            "student_id": "ST003",
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob@test.com",
            "program": "GS",
            "primary_subject": self.subject_de.id,
            "didactic_subject_3": self.subject_ma.id,
        }
        response = self.client.post("/api/students/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 3)
        new_student = Student.objects.get(student_id="ST003")
        self.assertEqual(new_student.didactic_subject_3.code, "MA")

    def test_update_student_completion_status(self):
        """Test that we can update a completion date via PATCH."""
        data = {"sfp_completed_date": "2025-09-15"}
        response = self.client.patch(
            f"/api/students/{self.student1.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student1.refresh_from_db()
        self.assertEqual(str(self.student1.sfp_completed_date), "2025-09-15")

    def test_excel_import(self):
        """Test importing students from Excel file."""
        from openpyxl import Workbook
        from io import BytesIO

        # Create a simple Excel file
        wb = Workbook()
        ws = wb.active
        ws.append([
            "student_id", "first_name", "last_name", "email", "program",
            "primary_subject_code", "didactic_subject_3_code"
        ])
        ws.append([
            "ST999", "Excel", "Test", "excel@test.com", "GS", "E", "SP"
        ])

        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        excel_file.name = "test_students.xlsx"

        response = self.client.post(
            "/api/students/import_excel/",
            {"file": excel_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("created", response.data)
        self.assertTrue(Student.objects.filter(student_id="ST999").exists())

    def test_excel_export(self):
        """Test exporting students to Excel file."""
        response = self.client.get("/api/students/export_excel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("students_export.xlsx", response["Content-Disposition"])

    def test_get_unassigned_students(self):
        """Test getting list of unassigned students."""
        response = self.client.get("/api/students/unassigned/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Both test students are UNPLACED by default
        self.assertEqual(len(response.data), 2)
