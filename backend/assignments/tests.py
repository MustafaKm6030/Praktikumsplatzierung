from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import date
from students.models import Student
from subjects.models import Subject


class DemandAPITests(APITestCase):
    def setUp(self):
        """
        Set up test data.
        CRITICAL: We must explicitly set 'completed_date' to a value for
        internships we DO NOT want to test, otherwise they will generate
        accidental demand (since the aggregator counts all missing dates).
        """
        self.sub_bio = Subject.objects.create(name="Biologie", code="BIO")
        self.sub_gesch = Subject.objects.create(name="Geschichte", code="GE")
        self.sub_soz = Subject.objects.create(name="Sozialkunde", code="SOZ")
        self.sub_de = Subject.objects.create(name="Deutsch", code="DE")

        # --- Scenario 1: Two GS students need ONLY ZSP (HSU Grouping) ---
        # They have done PDP I, PDP II, and SFP. Only ZSP is None.
        # Student 1: Biologie -> HSU
        self.student_gs_1 = Student.objects.create(
            student_id="111",
            first_name="GS",
            last_name="S1",
            program="GS",
            primary_subject=self.sub_bio,
            email="s1@test.com",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,  # <--- Generating Demand
            placement_status="UNPLACED",
        )
        # Student 2: Geschichte -> HSU
        self.student_gs_2 = Student.objects.create(
            student_id="222",
            first_name="GS",
            last_name="S2",
            program="GS",
            primary_subject=self.sub_gesch,
            email="s2@test.com",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=None,  # <--- Generating Demand
            placement_status="UNPLACED",
        )

        # --- Scenario 2: One MS student needs ONLY SFP (SK/PuG Grouping) ---
        # Has done PDP I, PDP II, ZSP. Needs SFP.
        self.student_ms_1 = Student.objects.create(
            student_id="333",
            first_name="MS",
            last_name="S3",
            program="MS",
            primary_subject=self.sub_soz,
            email="s3@test.com",
            pdp1_completed_date=date(2023, 1, 1),
            pdp2_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            sfp_completed_date=None,  # <--- Generating Demand
            placement_status="UNPLACED",
        )

        # --- Scenario 3: Three GS students need ONLY PDP I ---
        # To isolate PDP I count for this test, we mark other internships
        # as completed (even if academically unusual) to prevent them from
        # appearing in the SFP/ZSP demand buckets during this specific test run.
        self.student_pdp_1 = Student.objects.create(
            student_id="901",
            program="GS",
            email="p1@t.com",
            pdp1_completed_date=None,  # <--- Generating Demand
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )
        self.student_pdp_2 = Student.objects.create(
            student_id="902",
            program="GS",
            email="p2@t.com",
            pdp1_completed_date=None,  # <--- Generating Demand
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )
        self.student_pdp_3 = Student.objects.create(
            student_id="903",
            program="GS",
            email="p3@t.com",
            pdp1_completed_date=None,  # <--- Generating Demand
            pdp2_completed_date=date(2023, 1, 1),
            sfp_completed_date=date(2023, 1, 1),
            zsp_completed_date=date(2023, 1, 1),
            placement_status="UNPLACED",
        )

        # Scenario 4 (Ignored): A student who is fully PLACED
        Student.objects.create(
            student_id="444",
            program="GS",
            primary_subject=self.sub_de,
            email="s4@test.com",
            zsp_completed_date=None,
            placement_status="PLACED",
        )

    def test_get_demand_api_aggregates_correctly(self):
        """
        Ensure the demand API aggregates based on missing completion dates.
        """
        url = reverse("demand-api")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We expect exactly 3 distinct demand groups because we silenced the others:
        # 1. GS PDP I (3 slots)
        # 2. MS SFP (1 slot)
        # 3. GS ZSP (2 slots)
        self.assertEqual(len(response.data), 3)

        data_map = {}
        for item in response.data:
            key = f"{item['practicum_type']}_{item['program_type']}_{item['subject_code']}"
            data_map[key] = item

        # Assert PDP I demand
        pdp_key = "PDP_I_GS_N/A"
        self.assertIn(pdp_key, data_map)
        self.assertEqual(data_map[pdp_key]["required_slots"], 3)

        # Assert SFP demand (MS - Sozialkunde -> SK/PuG)
        sfp_key = "SFP_MS_SK/PuG"
        self.assertIn(sfp_key, data_map)
        self.assertEqual(data_map[sfp_key]["required_slots"], 1)
        self.assertEqual(
            data_map[sfp_key]["subject_display_name"],
            "Sozialkunde/Politik und Gesellschaft (SK/PuG)",
        )

        # Assert ZSP demand (GS - Bio & Geschichte -> HSU)
        zsp_key = "ZSP_GS_HSU"
        self.assertIn(zsp_key, data_map)
        self.assertEqual(data_map[zsp_key]["required_slots"], 2)
        self.assertEqual(
            data_map[zsp_key]["subject_display_name"],
            "Heimat- und Sachunterricht (HSU)",
        )
