from django.test import TestCase
from subjects.models import Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from assignments.services import calculate_eligibility_for_pl, get_mentor_capacity


class PLEligibilityCalculationTests(TestCase):
    """
    Test suite for the PL Eligibility Calculation Service.
    Verifies that `calculate_eligibility_for_pl` correctly applies all hard constraints.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up data once for all tests in this class."""
        cls.sub_math = Subject.objects.create(code="MA", name="Mathematik")
        cls.sub_german = Subject.objects.create(code="D", name="Deutsch")
        cls.sub_pcb = Subject.objects.create(code="PCB", name="Physik/Chemie/Biologie")
        cls.sub_hsu = Subject.objects.create(
            code="HSU", name="Heimat- und Sachunterricht"
        )

        cls.pdp1 = PraktikumType.objects.create(code="PDP_I", is_block_praktikum=True)
        cls.pdp2 = PraktikumType.objects.create(code="PDP_II", is_block_praktikum=True)
        cls.sfp = PraktikumType.objects.create(code="SFP", is_block_praktikum=False)
        cls.zsp = PraktikumType.objects.create(code="ZSP", is_block_praktikum=False)

        cls.school_gs = School.objects.create(
            name="Test Grundschule",
            school_type="GS",
            city="Passau",
            district="Passau-Land",
            zone=1,
            opnv_code="4a",
        )

    def test_standard_gs_mentor_eligibility(self):
        """Test a standard GS mentor with multiple subjects and types."""
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Anna",
            last_name="Standard",
            email="anna@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
        )
        mentor.available_praktikum_types.add(self.pdp1, self.sfp, self.zsp)
        mentor.available_subjects.add(self.sub_math, self.sub_german)

        eligibility = calculate_eligibility_for_pl(mentor)
        expected = {
            ("PDP_I", "N/A"),
            ("SFP", "MA"),
            ("SFP", "D"),
            ("ZSP", "MA"),
            ("ZSP", "D"),
        }
        self.assertEqual(set(eligibility), expected)

    def test_mentor_with_nur_blockpraktika_note(self):
        """Test that 'nur Blockpraktika' in notes restricts eligibility to PDPs."""
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Ben",
            last_name="Block",
            email="ben@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            current_year_notes="Kann nur Blockpraktika machen.",
        )
        mentor.available_praktikum_types.add(self.pdp1, self.pdp2, self.sfp, self.zsp)
        mentor.available_subjects.add(self.sub_math)

        eligibility = calculate_eligibility_for_pl(mentor)
        expected = {("PDP_I", "N/A"), ("PDP_II", "N/A")}
        self.assertEqual(set(eligibility), expected)

    def test_mentor_with_ruhend_note(self):
        """Test that a mentor marked as 'ruhend' has no eligibility."""
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="Carla",
            last_name="Resting",
            email="carla@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            current_year_notes="Status: ruhend bis 2026",
        )
        mentor.available_praktikum_types.add(self.pdp1, self.sfp)

        eligibility = calculate_eligibility_for_pl(mentor)
        self.assertEqual(eligibility, [])

    def test_inactive_mentor(self):
        """Test that a mentor with is_active=False has no eligibility."""
        mentor = PraktikumsLehrkraft.objects.create(
            first_name="David",
            last_name="Inactive",
            email="david@test.de",
            school=self.school_gs,
            program="GS",
            is_active=False,
        )
        mentor.available_praktikum_types.add(self.pdp1, self.sfp)

        eligibility = calculate_eligibility_for_pl(mentor)
        self.assertEqual(eligibility, [])

    def test_get_mentor_capacity_default_and_override(self):
        """Test default capacity and override from notes."""
        mentor_default = PraktikumsLehrkraft.objects.create(
            first_name="Heidi",
            last_name="Default",
            email="heidi@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=2.0,  # "4 for 2"
        )
        self.assertEqual(get_mentor_capacity(mentor_default), 4)

        mentor_override = PraktikumsLehrkraft.objects.create(
            first_name="Ingo",
            last_name="Override",
            email="ingo@test.de",
            school=self.school_gs,
            program="GS",
            is_active=True,
            anrechnungsstunden=2.0,
            current_year_notes="kann dieses Jahr nur 1 Prak. übernehmen",
        )
        self.assertEqual(get_mentor_capacity(mentor_override), 1)
