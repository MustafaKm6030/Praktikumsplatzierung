from django.test import TestCase
from .models import Subject, PraktikumType
from .services import apply_subject_grouping

class SubjectModelTests(TestCase):
    """Test cases for Subject model."""
    
    def setUp(self):
        """Create test subjects."""
        self.deutsch = Subject.objects.create(
            code='DE',
            name='Deutsch',
            subject_group='Language',
            is_active=True
        )
        self.math = Subject.objects.create(
            code='MA',
            name='Mathematik',
            subject_group='STEM',
            is_active=True
        )
    
    def test_subject_creation(self):
        """Test that subjects are created correctly."""
        self.assertEqual(self.deutsch.code, 'DE')
        self.assertEqual(self.deutsch.name, 'Deutsch')
        self.assertTrue(self.deutsch.is_active)
    
    def test_subject_string_representation(self):
        """Test the string representation of subject."""
        self.assertEqual(str(self.deutsch), 'DE - Deutsch')
    
    def test_get_active_subjects(self):
        """Test filtering active subjects."""
        # Create an inactive subject
        Subject.objects.create(
            code='EN',
            name='English',
            is_active=False
        )
        active_subjects = Subject.objects.filter(is_active=True)
        self.assertEqual(active_subjects.count(), 2)


class PraktikumTypeModelTests(TestCase):
    """Test cases for PraktikumType model."""
    
    def setUp(self):
        """Create test praktikum types."""
        self.pdp1 = PraktikumType.objects.create(
            code='PDP_I',
            name='PDP I',
            is_block_praktikum=True,
            is_active=True
        )
        self.sfp = PraktikumType.objects.create(
            code='SFP',
            name='SFP',
            is_block_praktikum=False,
            is_active=True
        )
    
    def test_praktikum_type_creation(self):
        """Test that praktikum types are created properly."""
        self.assertEqual(self.pdp1.code, 'PDP_I')
        self.assertTrue(self.pdp1.is_block_praktikum)
    
    def test_block_praktikum_filtering(self):
        """Test filtering block praktikum types."""
        block_types = PraktikumType.objects.filter(is_block_praktikum=True)
        self.assertEqual(block_types.count(), 1)
        self.assertEqual(block_types.first().code, 'PDP_I')
    
    def test_wednesday_praktikum_filtering(self):
        """Test filtering wednesday praktikum types."""
        wednesday_types = PraktikumType.objects.filter(is_block_praktikum=False)
        self.assertEqual(wednesday_types.count(), 1)
        self.assertEqual(wednesday_types.first().code, 'SFP')

        
class SubjectServicesTests(TestCase):
    """Test cases for business logic in services.py."""

    def test_gs_zsp_grouping_for_hsu(self):
        """Verify that various science/social studies subjects group to HSU for GS ZSP."""
        self.assertEqual(apply_subject_grouping("GS", "ZSP", "Biologie"), "Heimat- und Sachunterricht (HSU)")
        self.assertEqual(apply_subject_grouping("GS", "ZSP", "Geschichte"), "Heimat- und Sachunterricht (HSU)")
        self.assertEqual(apply_subject_grouping("GS", "ZSP", "Geographie"), "Heimat- und Sachunterricht (HSU)")

    def test_ms_sfp_grouping_for_pug(self):
        """Verify that social studies subjects group to PUG for MS SFP."""
        self.assertEqual(apply_subject_grouping("MS", "SFP", "Sozialkunde"), "Sozialkunde (SK), Politik und Gesellschaft (PUG)")
        self.assertEqual(apply_subject_grouping("MS", "SFP", "Politik"), "Sozialkunde (SK), Politik und Gesellschaft (PUG)")

    def test_ms_zsp_grouping_for_wib(self):
        """Verify that work-related subjects group to WIB for MS ZSP."""
        self.assertEqual(apply_subject_grouping("MS", "ZSP", "Arbeitslehre"), "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)")
        self.assertEqual(apply_subject_grouping("MS", "ZSP", "Wirtschaft"), "Arbeitslehre (AL), Wirtschaft und Beruf (WIB)")

    def test_no_grouping_applied_when_no_rule_exists(self):
        """Verify that subjects without a specific rule are returned unchanged."""
        # Test a subject that is never grouped
        self.assertEqual(apply_subject_grouping("GS", "ZSP", "Mathematik"), "Mathematik")
        # Test a subject that is only grouped in some contexts (Geschichte is not grouped in GS SFP)
        self.assertEqual(apply_subject_grouping("GS", "SFP", "Geschichte"), "Geschichte")

    def test_returns_original_subject_on_invalid_input(self):
        """Verify that the function handles invalid keys gracefully and returns the original subject."""
        # Test with a program type not present in the rules JSON
        self.assertEqual(apply_subject_grouping("UNKNOWN_PROGRAM", "SFP", "Deutsch"), "Deutsch")
        # Test with a practicum type not present in the rules JSON
        self.assertEqual(apply_subject_grouping("GS", "UNKNOWN_PRAKTIKUM", "Deutsch"), "Deutsch")