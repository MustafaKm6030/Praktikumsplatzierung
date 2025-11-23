from django.test import TestCase
from .models import Subject, PraktikumType

# Import the new, specific functions to be tested
from .services import get_subject_code, get_subject_display_name


class SubjectModelTests(TestCase):
    """Test cases for Subject model."""

    def setUp(self):
        """Create test subjects."""
        self.deutsch = Subject.objects.create(
            code="DE", name="Deutsch", subject_group="Language", is_active=True
        )
        self.math = Subject.objects.create(
            code="MA", name="Mathematik", subject_group="STEM", is_active=True
        )

    def test_subject_creation(self):
        """Test that subjects are created correctly."""
        self.assertEqual(self.deutsch.code, "DE")
        self.assertEqual(self.deutsch.name, "Deutsch")
        self.assertTrue(self.deutsch.is_active)

    def test_subject_string_representation(self):
        """Test the string representation of subject."""
        self.assertEqual(str(self.deutsch), "DE - Deutsch")

    def test_get_active_subjects(self):
        """Test filtering active subjects."""
        # Create an inactive subject
        Subject.objects.create(code="EN", name="English", is_active=False)
        active_subjects = Subject.objects.filter(is_active=True)
        self.assertEqual(active_subjects.count(), 2)


class PraktikumTypeModelTests(TestCase):
    """Test cases for PraktikumType model."""

    def setUp(self):
        """Create test praktikum types."""
        self.pdp1 = PraktikumType.objects.create(
            code="PDP_I", name="PDP I", is_block_praktikum=True, is_active=True
        )
        self.sfp = PraktikumType.objects.create(
            code="SFP", name="SFP", is_block_praktikum=False, is_active=True
        )

    def test_praktikum_type_creation(self):
        """Test that praktikum types are created properly."""
        self.assertEqual(self.pdp1.code, "PDP_I")
        self.assertTrue(self.pdp1.is_block_praktikum)

    def test_block_praktikum_filtering(self):
        """Test filtering block praktikum types."""
        block_types = PraktikumType.objects.filter(is_block_praktikum=True)
        self.assertEqual(block_types.count(), 1)
        self.assertEqual(block_types.first().code, "PDP_I")

    def test_wednesday_praktikum_filtering(self):
        """Test filtering wednesday praktikum types."""
        wednesday_types = PraktikumType.objects.filter(is_block_praktikum=False)
        self.assertEqual(wednesday_types.count(), 1)
        self.assertEqual(wednesday_types.first().code, "SFP")


class SubjectServicesTests(TestCase):
    """
    Test cases for business logic in services.py.
    These tests verify that the JSON rules are correctly applied to produce
    both the machine-readable 'code' and the human-readable 'display_name'.
    """

    def test_gs_zsp_grouping_for_hsu(self):
        """Verify grouping to HSU for GS ZSP for both code and display name."""
        # Test a subject that gets grouped
        self.assertEqual(get_subject_code("GS", "ZSP", "Biologie"), "HSU")
        self.assertEqual(
            get_subject_display_name("GS", "ZSP", "Biologie"),
            "Heimat- und Sachunterricht (HSU)",
        )

        # Test another subject that gets grouped to the same category
        self.assertEqual(get_subject_code("GS", "ZSP", "Geschichte"), "HSU")
        self.assertEqual(
            get_subject_display_name("GS", "ZSP", "Geschichte"),
            "Heimat- und Sachunterricht (HSU)",
        )

    def test_ms_sfp_grouping_for_pug(self):
        """Verify grouping to SK/PuG for MS SFP."""
        self.assertEqual(get_subject_code("MS", "SFP", "Sozialkunde"), "SK/PuG")
        self.assertEqual(
            get_subject_display_name("MS", "SFP", "Sozialkunde"),
            "Sozialkunde/Politik und Gesellschaft (SK/PuG)",
        )

        self.assertEqual(get_subject_code("MS", "SFP", "Politik"), "SK/PuG")
        self.assertEqual(
            get_subject_display_name("MS", "SFP", "Politik"),
            "Sozialkunde/Politik und Gesellschaft (SK/PuG)",
        )

    def test_ms_zsp_grouping_for_wib(self):
        """Verify grouping to AL/WiB for MS ZSP."""
        self.assertEqual(get_subject_code("MS", "ZSP", "Arbeitslehre"), "AL/WiB")
        self.assertEqual(
            get_subject_display_name("MS", "ZSP", "Arbeitslehre"),
            "Arbeitslehre/Wirtschaft und Beruf (AL/WiB)",
        )

    def test_no_grouping_applied_when_rule_is_direct(self):
        """Verify subjects with direct (non-grouped) rules are returned correctly."""
        # Test a subject that has a direct mapping in the rules file
        self.assertEqual(get_subject_code("GS", "ZSP", "Mathematik"), "MA")
        self.assertEqual(
            get_subject_display_name("GS", "ZSP", "Mathematik"), "Mathematik (MA)"
        )

        # Test a subject that is NOT grouped in this context (GS SFP) but IS grouped in another (GS ZSP)
        self.assertEqual(get_subject_code("GS", "SFP", "Geschichte"), "GE")
        self.assertEqual(
            get_subject_display_name("GS", "SFP", "Geschichte"), "Geschichte (GE)"
        )

    def test_fallback_when_no_rule_exists_at_all(self):
        """Verify that subjects with no rule in the JSON return the original name."""
        # Test a hypothetical subject not in our rules file
        self.assertEqual(get_subject_code("GS", "SFP", "Philosophy"), "Philosophy")
        self.assertEqual(
            get_subject_display_name("GS", "SFP", "Philosophy"), "Philosophy"
        )

    def test_graceful_failure_on_invalid_keys(self):
        """Verify that invalid program or practicum types return the original subject."""
        # Test with a program type not present in the rules JSON
        self.assertEqual(
            get_subject_code("UNKNOWN_PROGRAM", "SFP", "Deutsch"), "Deutsch"
        )
        self.assertEqual(
            get_subject_display_name("UNKNOWN_PROGRAM", "SFP", "Deutsch"), "Deutsch"
        )

        # Test with a practicum type not present in the rules JSON
        self.assertEqual(
            get_subject_code("GS", "UNKNOWN_PRAKTIKUM", "Deutsch"), "Deutsch"
        )
        self.assertEqual(
            get_subject_display_name("GS", "UNKNOWN_PRAKTIKUM", "Deutsch"), "Deutsch"
        )
