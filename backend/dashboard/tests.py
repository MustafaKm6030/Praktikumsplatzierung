# in dashboard/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from students.models import Student
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from subjects.models import Subject

from .services import (
    get_dashboard_summary_data,
    get_assignment_status,
    get_budget_summary,
    get_entity_counts,
    build_assignment_status_list,
)
from .serializers import (
    AssignmentStatusSerializer,
    BudgetSummarySerializer,
    EntityCountsSerializer,
    DashboardSummarySerializer,
)


class DashboardServicesTestCase(TestCase):
    """
    Unit tests for dashboard service layer functions.
    Tests data aggregation logic for assignment status, budget, and entity counts.
    """

    def setUp(self):
        """
        Creates test data for students, schools, and PLs.
        """
        # Create test school
        self.school = School.objects.create(
            name="Test School",
            school_type="GS",
            district="Test District",
            city="Test City",
            zone=1,
        )

        # Create second test school
        self.school2 = School.objects.create(
            name="Test School 2",
            school_type="MS",
            district="Test District 2",
            city="Test City 2",
            zone=2,
        )

        # Create test subject
        self.subject = Subject.objects.create(
            name="Mathematics",
            code="MATH",
        )

        # Create test students
        self.create_test_students()

        # Create test PLs
        self.create_test_pls()

    def create_test_students(self):
        """Creates various test students with different completion statuses."""
        # Student needing PDP I
        Student.objects.create(
            student_id="S001",
            first_name="Test",
            last_name="Student1",
            email="s1@test.com",
            program="GS",
            placement_status="UNPLACED",
            pdp1_completed_date=None,
        )

        # Student needing PDP II
        Student.objects.create(
            student_id="S002",
            first_name="Test",
            last_name="Student2",
            email="s2@test.com",
            program="MS",
            placement_status="UNPLACED",
            pdp1_completed_date="2024-01-01",
            pdp2_completed_date=None,
        )

        # Placed student
        Student.objects.create(
            student_id="S003",
            first_name="Test",
            last_name="Student3",
            email="s3@test.com",
            program="GS",
            placement_status="PLACED",
        )

    def create_test_pls(self):
        """Creates test PLs with different programs and budget allocations."""
        # GS PL
        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="GS1",
            email="tgs1@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=1.0,
            is_active=True,
        )

        # MS PL
        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="MS1",
            email="tms1@test.com",
            school=self.school,
            program="MS",
            anrechnungsstunden=2.0,
            is_active=True,
        )

        # Inactive PL (should not be counted)
        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="Inactive",
            email="tinactive@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=1.0,
            is_active=False,
        )

    def test_get_entity_counts(self):
        """
        Tests entity counts calculation.
        Verifies correct counting of students and active PLs by program.
        """
        counts = get_entity_counts()

        self.assertEqual(counts["total_students"], 3)
        self.assertEqual(counts["unplaced_students"], 2)
        self.assertEqual(counts["active_pls_total"], 2)
        self.assertEqual(counts["active_pls_gs"], 1)
        self.assertEqual(counts["active_pls_ms"], 1)

    def test_get_budget_summary(self):
        """
        Tests budget summary calculation.
        Verifies correct aggregation of anrechnungsstunden by program.
        """
        budget = get_budget_summary()

        self.assertEqual(budget["total_budget"], 210)
        self.assertEqual(budget["distributed_gs"], 1.0)
        self.assertEqual(budget["distributed_ms"], 2.0)
        self.assertEqual(budget["remaining_budget"], 207.0)

    def test_get_assignment_status(self):
        """
        Tests assignment status generation.
        Verifies structure and data types of assignment status list.
        """
        assignment_status = get_assignment_status()

        # Should return list of 4 practicum types
        self.assertEqual(len(assignment_status), 4)

        # Verify structure of first item
        first_item = assignment_status[0]
        self.assertIn("practicum_type", first_item)
        self.assertIn("demand_slots", first_item)
        self.assertIn("assigned_slots", first_item)
        self.assertIn("unassigned_slots", first_item)

        # Verify data types
        self.assertIsInstance(first_item["demand_slots"], int)
        self.assertIsInstance(first_item["assigned_slots"], int)
        self.assertIsInstance(first_item["unassigned_slots"], int)

    def test_get_dashboard_summary_data(self):
        """
        Tests complete dashboard summary data aggregation.
        Verifies all three main sections are present and structured correctly.
        """
        summary = get_dashboard_summary_data()

        # Verify all main keys are present
        self.assertIn("assignment_status", summary)
        self.assertIn("budget_summary", summary)
        self.assertIn("entity_counts", summary)

        # Verify assignment_status is a list
        self.assertIsInstance(summary["assignment_status"], list)

        # Verify budget_summary is a dict with required keys
        budget = summary["budget_summary"]
        self.assertIn("total_budget", budget)
        self.assertIn("distributed_gs", budget)
        self.assertIn("distributed_ms", budget)
        self.assertIn("remaining_budget", budget)

        # Verify entity_counts is a dict with required keys
        counts = summary["entity_counts"]
        self.assertIn("total_students", counts)
        self.assertIn("unplaced_students", counts)
        self.assertIn("active_pls_total", counts)


class DashboardServicesEdgeCasesTestCase(TestCase):
    """
    Tests edge cases and various scenarios for dashboard services.
    Ensures robustness with empty data, varied combinations, and boundary conditions.
    """

    def setUp(self):
        """Creates minimal test data."""
        self.school = School.objects.create(
            name="Test School",
            school_type="GS",
            district="Test District",
            city="Test City",
            zone=1,
        )
        self.subject_de = Subject.objects.create(code="DE", name="Deutsch")
        self.subject_ma = Subject.objects.create(code="MA", name="Mathematik")

    def test_get_entity_counts_with_no_data(self):
        """
        Tests entity counts when database is empty.
        Should return zero counts without errors.
        """
        counts = get_entity_counts()

        self.assertEqual(counts["total_students"], 0)
        self.assertEqual(counts["unplaced_students"], 0)
        self.assertEqual(counts["active_pls_total"], 0)
        self.assertEqual(counts["active_pls_gs"], 0)
        self.assertEqual(counts["active_pls_ms"], 0)

    def test_get_budget_summary_with_no_pls(self):
        """
        Tests budget summary when no PLs exist.
        Should return zero distributed budget.
        """
        budget = get_budget_summary()

        self.assertEqual(budget["total_budget"], 210)
        self.assertEqual(budget["distributed_gs"], 0)
        self.assertEqual(budget["distributed_ms"], 0)
        self.assertEqual(budget["remaining_budget"], 210)

    def test_get_budget_summary_with_only_gs_pls(self):
        """
        Tests budget calculation with only GS program PLs.
        """
        # Create only GS PLs
        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="GS1",
            email="tgs1@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=3.5,
            is_active=True,
        )

        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="GS2",
            email="tgs2@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=2.0,
            is_active=True,
        )

        budget = get_budget_summary()

        self.assertEqual(budget["distributed_gs"], 5.5)
        self.assertEqual(budget["distributed_ms"], 0)
        self.assertEqual(budget["remaining_budget"], 204.5)

    def test_get_budget_summary_with_only_ms_pls(self):
        """
        Tests budget calculation with only MS program PLs.
        """
        # Create only MS PLs
        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="MS1",
            email="tms1@test.com",
            school=self.school,
            program="MS",
            anrechnungsstunden=4.0,
            is_active=True,
        )

        budget = get_budget_summary()

        self.assertEqual(budget["distributed_gs"], 0)
        self.assertEqual(budget["distributed_ms"], 4.0)
        self.assertEqual(budget["remaining_budget"], 206)

    def test_get_budget_summary_ignores_inactive_pls(self):
        """
        Tests that inactive PLs are not counted in budget.
        """
        # Create active PL
        PraktikumsLehrkraft.objects.create(
            first_name="Active",
            last_name="Teacher",
            email="active@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=2.0,
            is_active=True,
        )

        # Create inactive PLs
        PraktikumsLehrkraft.objects.create(
            first_name="Inactive",
            last_name="Teacher1",
            email="inactive1@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=5.0,
            is_active=False,
        )

        PraktikumsLehrkraft.objects.create(
            first_name="Inactive",
            last_name="Teacher2",
            email="inactive2@test.com",
            school=self.school,
            program="MS",
            anrechnungsstunden=3.0,
            is_active=False,
        )

        budget = get_budget_summary()

        self.assertEqual(budget["distributed_gs"], 2.0)
        self.assertEqual(budget["distributed_ms"], 0)
        self.assertEqual(budget["remaining_budget"], 208)

    def test_entity_counts_with_all_placed_students(self):
        """
        Tests entity counts when all students are placed.
        """
        # Create placed students only
        Student.objects.create(
            student_id="S001",
            first_name="Placed",
            last_name="Student1",
            email="placed1@test.com",
            program="GS",
            placement_status="PLACED",
        )

        Student.objects.create(
            student_id="S002",
            first_name="Placed",
            last_name="Student2",
            email="placed2@test.com",
            program="MS",
            placement_status="PLACED",
        )

        counts = get_entity_counts()

        self.assertEqual(counts["total_students"], 2)
        self.assertEqual(counts["unplaced_students"], 0)

    def test_entity_counts_with_all_unplaced_students(self):
        """
        Tests entity counts when all students are unplaced.
        """
        # Create unplaced students only
        Student.objects.create(
            student_id="S001",
            first_name="Unplaced",
            last_name="Student1",
            email="unplaced1@test.com",
            program="GS",
            placement_status="UNPLACED",
        )

        Student.objects.create(
            student_id="S002",
            first_name="Unplaced",
            last_name="Student2",
            email="unplaced2@test.com",
            program="MS",
            placement_status="UNPLACED",
        )

        counts = get_entity_counts()

        self.assertEqual(counts["total_students"], 2)
        self.assertEqual(counts["unplaced_students"], 2)

    def test_entity_counts_pl_by_program_distribution(self):
        """
        Tests correct counting of PLs by program.
        """
        # Create multiple PLs for each program
        for i in range(3):
            PraktikumsLehrkraft.objects.create(
                first_name=f"GS_Teacher",
                last_name=f"Test{i}",
                email=f"gs{i}@test.com",
                school=self.school,
                program="GS",
                anrechnungsstunden=1.0,
                is_active=True,
            )

        for i in range(5):
            PraktikumsLehrkraft.objects.create(
                first_name=f"MS_Teacher",
                last_name=f"Test{i}",
                email=f"ms{i}@test.com",
                school=self.school,
                program="MS",
                anrechnungsstunden=1.0,
                is_active=True,
            )

        counts = get_entity_counts()

        self.assertEqual(counts["active_pls_total"], 8)
        self.assertEqual(counts["active_pls_gs"], 3)
        self.assertEqual(counts["active_pls_ms"], 5)

    def test_assignment_status_structure(self):
        """
        Tests that assignment status always returns 4 practicum types.
        Verifies correct structure even with no demand.
        """
        assignment_status = get_assignment_status()

        # Should always return 4 practicum types
        self.assertEqual(len(assignment_status), 4)

        # Verify all expected practicum types are present
        practicum_types = [item["practicum_type"] for item in assignment_status]
        self.assertIn("PDP I", practicum_types)
        self.assertIn("PDP II", practicum_types)
        self.assertIn("SFP", practicum_types)
        self.assertIn("ZSP", practicum_types)

        # Verify all have correct structure
        for item in assignment_status:
            self.assertIn("practicum_type", item)
            self.assertIn("demand_slots", item)
            self.assertIn("assigned_slots", item)
            self.assertIn("unassigned_slots", item)

            # Verify data types
            self.assertIsInstance(item["demand_slots"], int)
            self.assertIsInstance(item["assigned_slots"], int)
            self.assertIsInstance(item["unassigned_slots"], int)

            # Verify non-negative values
            self.assertGreaterEqual(item["demand_slots"], 0)
            self.assertGreaterEqual(item["assigned_slots"], 0)
            self.assertGreaterEqual(item["unassigned_slots"], 0)

    def test_assignment_status_with_students_needing_all_practicums(self):
        """
        Tests assignment status calculation with students needing all types.
        """
        # Student needing all practicums (none completed)
        Student.objects.create(
            student_id="S_ALL_NEEDS",
            first_name="Needs",
            last_name="All",
            email="needsall@test.com",
            program="GS",
            placement_status="UNPLACED",
            pdp1_completed_date=None,
            pdp2_completed_date=None,
            sfp_completed_date=None,
            zsp_completed_date=None,
        )

        assignment_status = get_assignment_status()

        # Helper to extract demand by type
        def get_demand_slots(ptype):
            return next(
                (
                    item["demand_slots"]
                    for item in assignment_status
                    if item["practicum_type"] == ptype
                ),
                0,
            )

        # Logic: A student with nothing completed only generates demand
        # for the first step (PDP I).
        self.assertEqual(get_demand_slots("PDP I"), 1)
        self.assertEqual(get_demand_slots("PDP II"), 0)
        self.assertEqual(get_demand_slots("SFP"), 0)
        self.assertEqual(get_demand_slots("ZSP"), 0)

    def test_assignment_status_with_partially_completed_student(self):
        """
        Tests assignment status with student who completed some practicums.
        """
        # Student who completed PDP I but needs others
        Student.objects.create(
            student_id="S_PARTIAL",
            first_name="Partial",
            last_name="Complete",
            email="partial@test.com",
            program="GS",
            placement_status="UNPLACED",
            primary_subject=self.subject_de,
            didactic_subject_3=self.subject_ma,
            pdp1_completed_date="2024-01-15",
            pdp2_completed_date=None,
            sfp_completed_date=None,
            zsp_completed_date=None,
        )

        assignment_status = get_assignment_status()

        # Helper to extract demand by type (reduces code repetition)
        def get_demand(ptype):
            return next(
                (
                    item["demand_slots"]
                    for item in assignment_status
                    if item["practicum_type"] == ptype
                ),
                0,
            )

        # Should have demand for PDP II, SFP, ZSP but NOT PDP I (because it is completed)
        self.assertEqual(get_demand("PDP I"), 0)
        self.assertEqual(get_demand("PDP II"), 1)
        self.assertEqual(get_demand("SFP"), 1)
        self.assertEqual(get_demand("ZSP"), 1)

    def test_budget_summary_with_decimal_anrechnungsstunden(self):
        """
        Tests budget calculation with various decimal values.
        """
        # Create PLs with decimal anrechnungsstunden
        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="Decimal1",
            email="decimal1@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=1.5,
            is_active=True,
        )

        PraktikumsLehrkraft.objects.create(
            first_name="Teacher",
            last_name="Decimal2",
            email="decimal2@test.com",
            school=self.school,
            program="MS",
            anrechnungsstunden=2.5,
            is_active=True,
        )

        budget = get_budget_summary()

        self.assertEqual(budget["distributed_gs"], 1.5)
        self.assertEqual(budget["distributed_ms"], 2.5)
        self.assertEqual(budget["remaining_budget"], 206.0)

    def test_get_dashboard_summary_data_integration(self):
        """
        Tests full integration of all dashboard data components.
        """
        # Create comprehensive test data
        Student.objects.create(
            student_id="S001",
            first_name="Test",
            last_name="Student",
            email="test@test.com",
            program="GS",
            placement_status="UNPLACED",
        )

        PraktikumsLehrkraft.objects.create(
            first_name="Test",
            last_name="Teacher",
            email="teacher@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=1.0,
            is_active=True,
        )

        summary = get_dashboard_summary_data()

        # Verify structure
        self.assertIsInstance(summary, dict)
        self.assertEqual(len(summary.keys()), 3)

        # Verify all sections have data
        self.assertIsInstance(summary["assignment_status"], list)
        self.assertIsInstance(summary["budget_summary"], dict)
        self.assertIsInstance(summary["entity_counts"], dict)

        # Verify data consistency
        self.assertEqual(summary["entity_counts"]["total_students"], 1)
        self.assertEqual(summary["entity_counts"]["active_pls_total"], 1)


class DashboardAPITestCase(APITestCase):
    """
    Integration tests for dashboard API endpoint.
    Tests API response structure and status codes.
    """

    def setUp(self):
        """Creates minimal test data."""
        self.url = reverse("dashboard-summary")

        # Create minimal test data
        self.school = School.objects.create(
            name="Test School",
            school_type="GS",
            district="Test District",
            city="Test City",
            zone=1,
        )

    def test_dashboard_summary_endpoint_success(self):
        """
        Tests successful GET request to dashboard summary endpoint.
        Verifies 200 status and correct response structure.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify response structure
        data = response.json()
        self.assertIn("assignment_status", data)
        self.assertIn("budget_summary", data)
        self.assertIn("entity_counts", data)

    def test_dashboard_summary_response_format(self):
        """
        Tests response format matches API contract.
        Verifies all required fields are present in correct format.
        """
        response = self.client.get(self.url)
        data = response.json()

        # Verify assignment_status format
        assignment_status = data["assignment_status"]
        self.assertIsInstance(assignment_status, list)
        if len(assignment_status) > 0:
            item = assignment_status[0]
            self.assertIn("practicum_type", item)
            self.assertIn("demand_slots", item)
            self.assertIn("assigned_slots", item)
            self.assertIn("unassigned_slots", item)

        # Verify budget_summary format
        budget = data["budget_summary"]
        self.assertIn("total_budget", budget)
        self.assertIn("distributed_gs", budget)
        self.assertIn("distributed_ms", budget)
        self.assertIn("remaining_budget", budget)

        # Verify entity_counts format
        counts = data["entity_counts"]
        self.assertIn("total_students", counts)
        self.assertIn("unplaced_students", counts)
        self.assertIn("active_pls_total", counts)
        self.assertIn("active_pls_gs", counts)
        self.assertIn("active_pls_ms", counts)

    def test_dashboard_summary_returns_json_content_type(self):
        """
        Tests that the endpoint returns JSON content type.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["content-type"], "application/json")

    def test_dashboard_summary_with_real_data(self):
        """
        Tests dashboard with realistic data scenario.
        """
        # Create students with different statuses
        Student.objects.create(
            student_id="S001",
            first_name="Unplaced",
            last_name="Student",
            email="unplaced@test.com",
            program="GS",
            placement_status="UNPLACED",
            pdp1_completed_date=None,
        )

        Student.objects.create(
            student_id="S002",
            first_name="Placed",
            last_name="Student",
            email="placed@test.com",
            program="MS",
            placement_status="PLACED",
        )

        # Create PLs
        PraktikumsLehrkraft.objects.create(
            first_name="Active",
            last_name="Teacher",
            email="active@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=2.0,
            is_active=True,
        )

        response = self.client.get(self.url)
        data = response.json()

        # Verify correct counts
        self.assertEqual(data["entity_counts"]["total_students"], 2)
        self.assertEqual(data["entity_counts"]["unplaced_students"], 1)
        self.assertEqual(data["entity_counts"]["active_pls_total"], 1)
        self.assertEqual(data["entity_counts"]["active_pls_gs"], 1)
        self.assertEqual(data["entity_counts"]["active_pls_ms"], 0)

        # Verify budget
        self.assertEqual(data["budget_summary"]["distributed_gs"], 2.0)

    def test_dashboard_summary_assignment_status_has_four_types(self):
        """
        Tests that assignment status always returns exactly 4 practicum types.
        """
        response = self.client.get(self.url)
        data = response.json()

        assignment_status = data["assignment_status"]
        self.assertEqual(len(assignment_status), 4)

        practicum_types = [item["practicum_type"] for item in assignment_status]
        self.assertEqual(
            sorted(practicum_types), sorted(["PDP I", "PDP II", "SFP", "ZSP"])
        )

    def test_dashboard_summary_budget_calculation_accuracy(self):
        """
        Tests accuracy of budget calculations.
        """
        # Create PLs with known values
        PraktikumsLehrkraft.objects.create(
            first_name="GS",
            last_name="Teacher1",
            email="gs1@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=3.0,
            is_active=True,
        )

        PraktikumsLehrkraft.objects.create(
            first_name="MS",
            last_name="Teacher1",
            email="ms1@test.com",
            school=self.school,
            program="MS",
            anrechnungsstunden=4.5,
            is_active=True,
        )

        response = self.client.get(self.url)
        data = response.json()

        budget = data["budget_summary"]

        self.assertEqual(budget["total_budget"], 210)
        self.assertEqual(budget["distributed_gs"], 3.0)
        self.assertEqual(budget["distributed_ms"], 4.5)
        self.assertEqual(budget["remaining_budget"], 202.5)

    def test_dashboard_summary_empty_database(self):
        """
        Tests dashboard endpoint with empty database.
        Should not error and return valid structure with zeros.
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Should have valid structure even with no data
        self.assertIn("assignment_status", data)
        self.assertIn("budget_summary", data)
        self.assertIn("entity_counts", data)

        # Entity counts should be zero
        counts = data["entity_counts"]
        self.assertEqual(counts["total_students"], 0)
        self.assertEqual(counts["unplaced_students"], 0)
        self.assertEqual(counts["active_pls_total"], 0)

    def test_dashboard_summary_multiple_requests_consistency(self):
        """
        Tests that multiple requests return consistent data.
        """
        # Make multiple requests
        response1 = self.client.get(self.url)
        response2 = self.client.get(self.url)
        response3 = self.client.get(self.url)

        # All should succeed
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)

        # All should return the same data
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()

        self.assertEqual(data1, data2)
        self.assertEqual(data2, data3)

    def test_dashboard_summary_only_allows_get(self):
        """
        Tests that only GET method is allowed on the endpoint.
        """
        # GET should work
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)

        # POST should not be allowed
        post_response = self.client.post(self.url, {})
        self.assertEqual(post_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PUT should not be allowed
        put_response = self.client.put(self.url, {})
        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # DELETE should not be allowed
        delete_response = self.client.delete(self.url)
        self.assertEqual(
            delete_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_dashboard_summary_data_types(self):
        """
        Tests that all numeric values are proper numbers, not strings.
        """
        # Create some test data
        PraktikumsLehrkraft.objects.create(
            first_name="Test",
            last_name="Teacher",
            email="test@test.com",
            school=self.school,
            program="GS",
            anrechnungsstunden=1.5,
            is_active=True,
        )

        response = self.client.get(self.url)
        data = response.json()

        # Check budget_summary data types
        budget = data["budget_summary"]
        self.assertIsInstance(budget["total_budget"], (int, float))
        self.assertIsInstance(budget["distributed_gs"], (int, float))
        self.assertIsInstance(budget["distributed_ms"], (int, float))
        self.assertIsInstance(budget["remaining_budget"], (int, float))

        # Check entity_counts data types
        counts = data["entity_counts"]
        self.assertIsInstance(counts["total_students"], int)
        self.assertIsInstance(counts["unplaced_students"], int)
        self.assertIsInstance(counts["active_pls_total"], int)
        self.assertIsInstance(counts["active_pls_gs"], int)
        self.assertIsInstance(counts["active_pls_ms"], int)

        # Check assignment_status data types
        for item in data["assignment_status"]:
            self.assertIsInstance(item["demand_slots"], int)
            self.assertIsInstance(item["assigned_slots"], int)
            self.assertIsInstance(item["unassigned_slots"], int)


class BuildAssignmentStatusListTestCase(TestCase):
    """
    Unit tests for the build_assignment_status_list helper function.
    Tests mock data generation and list building logic.
    """

    def test_build_with_empty_practicum_totals(self):
        """
        Tests building assignment status list with no demand.
        """
        practicum_totals = {}
        result = build_assignment_status_list(practicum_totals)

        # Should return 4 practicum types
        self.assertEqual(len(result), 4)

        # All should have zero demand
        for item in result:
            self.assertEqual(item["demand_slots"], 0)

    def test_build_with_all_practicum_types(self):
        """
        Tests building with demand for all practicum types.
        """
        practicum_totals = {
            "PDP_I": 10,
            "PDP_II": 15,
            "SFP": 20,
            "ZSP": 12,
        }

        result = build_assignment_status_list(practicum_totals)

        self.assertEqual(len(result), 4)

        # Verify demand slots match
        pdp1 = next(item for item in result if item["practicum_type"] == "PDP I")
        pdp2 = next(item for item in result if item["practicum_type"] == "PDP II")
        sfp = next(item for item in result if item["practicum_type"] == "SFP")
        zsp = next(item for item in result if item["practicum_type"] == "ZSP")

        self.assertEqual(pdp1["demand_slots"], 10)
        self.assertEqual(pdp2["demand_slots"], 15)
        self.assertEqual(sfp["demand_slots"], 20)
        self.assertEqual(zsp["demand_slots"], 12)

    def test_build_with_partial_practicum_types(self):
        """
        Tests building with demand for only some practicum types.
        """
        practicum_totals = {
            "PDP_I": 5,
            "SFP": 8,
        }

        result = build_assignment_status_list(practicum_totals)

        self.assertEqual(len(result), 4)

        # Types with demand
        pdp1 = next(item for item in result if item["practicum_type"] == "PDP I")
        sfp = next(item for item in result if item["practicum_type"] == "SFP")

        self.assertEqual(pdp1["demand_slots"], 5)
        self.assertEqual(sfp["demand_slots"], 8)

        # Types without demand should be zero
        pdp2 = next(item for item in result if item["practicum_type"] == "PDP II")
        zsp = next(item for item in result if item["practicum_type"] == "ZSP")

        self.assertEqual(pdp2["demand_slots"], 0)
        self.assertEqual(zsp["demand_slots"], 0)

    def test_build_applies_real_assignment_data_correctly(self):
        """
        Tests that real assignment data is applied correctly.
        When no assignments exist, unassigned equals demand.
        """
        practicum_totals = {
            "PDP_I": 50,
            "PDP_II": 45,
            "SFP": 60,
            "ZSP": 55,
        }

        result = build_assignment_status_list(practicum_totals)

        # With no assignments in database, all should have 0 assigned and unassigned equals demand
        sfp = next(item for item in result if item["practicum_type"] == "SFP")
        self.assertEqual(sfp["unassigned_slots"], 60)
        self.assertEqual(sfp["assigned_slots"], 0)

        # Others should also have 0 assigned
        pdp1 = next(item for item in result if item["practicum_type"] == "PDP I")
        self.assertEqual(pdp1["unassigned_slots"], 50)
        self.assertEqual(pdp1["assigned_slots"], 0)

    def test_build_returns_correct_structure(self):
        """
        Tests that returned items have correct structure.
        """
        practicum_totals = {"PDP_I": 1}
        result = build_assignment_status_list(practicum_totals)

        for item in result:
            self.assertIn("practicum_type", item)
            self.assertIn("demand_slots", item)
            self.assertIn("assigned_slots", item)
            self.assertIn("unassigned_slots", item)
            self.assertEqual(len(item.keys()), 4)


class SerializerTestCase(TestCase):
    """
    Unit tests for dashboard serializers.
    Tests serialization and validation logic.
    """

    def test_assignment_status_serializer(self):
        """
        Tests AssignmentStatusSerializer with valid data.
        """
        data = {
            "practicum_type": "PDP I",
            "demand_slots": 50,
            "assigned_slots": 48,
            "unassigned_slots": 2,
        }

        serializer = AssignmentStatusSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["practicum_type"], "PDP I")
        self.assertEqual(serializer.validated_data["demand_slots"], 50)

    def test_budget_summary_serializer(self):
        """
        Tests BudgetSummarySerializer with valid data.
        """
        data = {
            "total_budget": 210,
            "distributed_gs": 100.5,
            "distributed_ms": 50.5,
            "remaining_budget": 59.0,
        }

        serializer = BudgetSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["total_budget"], 210)
        self.assertEqual(serializer.validated_data["distributed_gs"], 100.5)

    def test_entity_counts_serializer(self):
        """
        Tests EntityCountsSerializer with valid data.
        """
        data = {
            "total_students": 1000,
            "unplaced_students": 50,
            "placed_students": 950,
            "unplaced_students_gs": 30,
            "unplaced_students_ms": 20,
            "placed_students_gs": 570,
            "placed_students_ms": 380,
            "active_pls_total": 200,
            "active_pls_gs": 120,
            "active_pls_ms": 80,
        }

        serializer = EntityCountsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["total_students"], 1000)
        self.assertEqual(serializer.validated_data["active_pls_gs"], 120)

    def test_dashboard_summary_serializer_complete(self):
        """
        Tests DashboardSummarySerializer with complete valid data.
        """
        # 1. Get Data from helper
        data = self._get_complete_dashboard_data()

        # 2. Validate
        serializer = DashboardSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # 3. Verify nested data types
        validated = serializer.validated_data
        self.assertIsInstance(validated["assignment_status"], list)
        self.assertIsInstance(validated["budget_summary"], dict)
        self.assertIsInstance(validated["entity_counts"], dict)

    def _get_complete_dashboard_data(self):
        """Helper to return a full payload for testing."""
        return {
            "assignment_status": [
                {
                    "practicum_type": "PDP I",
                    "demand_slots": 50,
                    "assigned_slots": 50,
                    "unassigned_slots": 0,
                }
            ],
            "budget_summary": {
                "total_budget": 210,
                "distributed_gs": 100,
                "distributed_ms": 50,
                "remaining_budget": 60,
            },
            "entity_counts": {
                "total_students": 1000,
                "unplaced_students": 50,
                "placed_students": 950,
                "unplaced_students_gs": 30,
                "unplaced_students_ms": 20,
                "placed_students_gs": 570,
                "placed_students_ms": 380,
                "active_pls_total": 200,
                "active_pls_gs": 120,
                "active_pls_ms": 80,
            },
        }

    def test_dashboard_summary_serializer_multiple_assignment_statuses(self):
        """
        Tests serializer with multiple assignment status items.
        """
        data = {
            "assignment_status": [
                {
                    "practicum_type": "PDP I",
                    "demand_slots": 50,
                    "assigned_slots": 50,
                    "unassigned_slots": 0,
                },
                {
                    "practicum_type": "SFP",
                    "demand_slots": 60,
                    "assigned_slots": 58,
                    "unassigned_slots": 2,
                },
            ],
            "budget_summary": {
                "total_budget": 210,
                "distributed_gs": 100,
                "distributed_ms": 50,
                "remaining_budget": 60,
            },
            "entity_counts": {
                "total_students": 1000,
                "unplaced_students": 50,
                "placed_students": 950,
                "unplaced_students_gs": 30,
                "unplaced_students_ms": 20,
                "placed_students_gs": 570,
                "placed_students_ms": 380,
                "active_pls_total": 200,
                "active_pls_gs": 120,
                "active_pls_ms": 80,
            },
        }

        serializer = DashboardSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["assignment_status"]), 2)

    def test_serializer_with_zero_values(self):
        """
        Tests serializers handle zero values correctly.
        """
        data = {
            "assignment_status": [],
            "budget_summary": {
                "total_budget": 210,
                "distributed_gs": 0,
                "distributed_ms": 0,
                "remaining_budget": 210,
            },
            "entity_counts": {
                "total_students": 0,
                "unplaced_students": 0,
                "placed_students": 0,
                "unplaced_students_gs": 0,
                "unplaced_students_ms": 0,
                "placed_students_gs": 0,
                "placed_students_ms": 0,
                "active_pls_total": 0,
                "active_pls_gs": 0,
                "active_pls_ms": 0,
            },
        }

        serializer = DashboardSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_decimal_budget_values(self):
        """
        Tests serializers handle decimal values in budget.
        """
        data = {
            "total_budget": 210.0,
            "distributed_gs": 123.5,
            "distributed_ms": 45.8,
            "remaining_budget": 40.7,
        }

        serializer = BudgetSummarySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["distributed_gs"], 123.5)
