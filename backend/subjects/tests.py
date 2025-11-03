from django.test import TestCase
from .models import Subject, PraktikumType


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
