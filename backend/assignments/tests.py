from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from students.models import Student, StudentPraktikumPreference
from subjects.models import Subject, PraktikumType


class DemandAPITests(APITestCase):
    def setUp(self):
        """Set up test data reflecting the actual model relationships."""
        # Create Subjects
        self.sub_bio = Subject.objects.create(name="Biologie", code="BIO")
        self.sub_gesch = Subject.objects.create(name="Geschichte", code="GE")
        self.sub_soz = Subject.objects.create(name="Sozialkunde", code="SOZ")
        self.sub_de = Subject.objects.create(name="Deutsch", code="DE")
        self.sub_ma = Subject.objects.create(name="Mathematik", code="MA")

        # Create Praktikum Types
        self.pt_pdp1 = PraktikumType.objects.create(
            code="PDP I", is_block_praktikum=True
        )
        self.pt_zsp = PraktikumType.objects.create(code="ZSP", is_block_praktikum=False)
        self.pt_sfp = PraktikumType.objects.create(code="SFP", is_block_praktikum=False)

        # Create Students
        self.student_gs_1 = Student.objects.create(
            student_id="111",
            first_name="GS",
            last_name="S1",
            program="GS",
            primary_subject=self.sub_bio,
            email="s1@test.com",  # ADDED unique email
        )
        self.student_gs_2 = Student.objects.create(
            student_id="222",
            first_name="GS",
            last_name="S2",
            program="GS",
            primary_subject=self.sub_gesch,
            email="s2@test.com",  # ADDED unique email
        )
        self.student_ms_1 = Student.objects.create(
            student_id="333",
            first_name="MS",
            last_name="S3",
            program="MS",
            primary_subject=self.sub_soz,
            email="s3@test.com",  # ADDED unique email
        )
        self.student_gs_3 = Student.objects.create(
            student_id="444",
            first_name="GS",
            last_name="S4",
            program="GS",
            primary_subject=self.sub_de,
            email="s4@test.com",  # ADDED unique email
        )

        # --- Create the actual source of demand: The Preferences ---
        # Scenario 1: Two GS students need ZSP -> should become one HSU group of 2
        StudentPraktikumPreference.objects.create(
            student=self.student_gs_1, praktikum_type=self.pt_zsp, status="UNPLACED"
        )
        StudentPraktikumPreference.objects.create(
            student=self.student_gs_2, praktikum_type=self.pt_zsp, status="UNPLACED"
        )

        # Scenario 2: One MS student needs SFP -> should become one PUG group of 1
        StudentPraktikumPreference.objects.create(
            student=self.student_ms_1, praktikum_type=self.pt_sfp, status="UNPLACED"
        )

        # Scenario 3: Three GS students need PDP I -> should become one PDP I group of 3 (subjects are ignored)
        StudentPraktikumPreference.objects.create(
            student=self.student_gs_1, praktikum_type=self.pt_pdp1, status="UNPLACED"
        )
        StudentPraktikumPreference.objects.create(
            student=self.student_gs_2, praktikum_type=self.pt_pdp1, status="UNPLACED"
        )
        StudentPraktikumPreference.objects.create(
            student=self.student_gs_3, praktikum_type=self.pt_pdp1, status="UNPLACED"
        )

        # Scenario 4 (Ignored): A student with a 'PLACED' preference
        StudentPraktikumPreference.objects.create(
            student=self.student_gs_3, praktikum_type=self.pt_zsp, status="PLACED"
        )

    def test_get_demand_api_aggregates_correctly(self):
        """
        Ensure the demand API aggregates preferences correctly based on status and rules.
        """
        url = reverse("demand-api")  # Assumes the URL is named 'demand-api'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # We expect 3 distinct demand groups from the 'UNPLACED' preferences
        self.assertEqual(len(response.data), 3)

        # Convert response to a more easily searchable format by sorting
        response_data = sorted(response.data, key=lambda x: x["practicum_type"])

        # Assert PDP I demand (bulk, no subject)
        pdp_demand = response_data[0]
        self.assertEqual(pdp_demand["practicum_type"], "PDP I")
        self.assertEqual(pdp_demand["program_type"], "GS")
        self.assertEqual(pdp_demand["subject"], "N/A")
        self.assertEqual(pdp_demand["required_slots"], 3)

        # Assert SFP demand (grouped subject)
        sfp_demand = response_data[1]
        self.assertEqual(sfp_demand["practicum_type"], "SFP")
        self.assertEqual(sfp_demand["program_type"], "MS")
        self.assertEqual(sfp_demand["subject"], "SK/PuG")
        self.assertEqual(sfp_demand["required_slots"], 1)

        # Assert ZSP demand (grouped subject)
        zsp_demand = response_data[2]
        self.assertEqual(zsp_demand["practicum_type"], "ZSP")
        self.assertEqual(zsp_demand["program_type"], "GS")
        self.assertEqual(zsp_demand["subject"], "HSU")
        self.assertEqual(zsp_demand["required_slots"], 2)
