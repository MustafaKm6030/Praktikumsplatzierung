from django.test import TestCase
from subjects.models import Subject, PraktikumType
from schools.models import School
from .models import PraktikumsLehrkraft, PLSubjectAvailability


class PraktikumsLehrkraftModelTests(TestCase):
    """Test cases for PraktikumsLehrkraft model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a school
        self.school = School.objects.create(
            name='Grundschule Test',
            school_type='GS',
            address='Test Street 1',
            district='Passau',
            city='Passau',
            opnv_zone='ZONE_1',
            is_active=True
        )
        
        # Create subjects
        self.deutsch = Subject.objects.create(code='DE', name='Deutsch')
        self.math = Subject.objects.create(code='MA', name='Mathematik')
        
        # Create praktikum types
        self.pdp1 = PraktikumType.objects.create(
            code='PDP_I',
            name='PDP I',
            is_block_praktikum=True
        )
        
        # Create a PL
        self.pl = PraktikumsLehrkraft.objects.create(
            first_name='Maria',
            last_name='Schmidt',
            email='maria.schmidt@test.de',
            school=self.school,
            program='GS',
            main_subject=self.deutsch,
            is_available=True
        )
    
    def test_pl_creation(self):
        """Test that PL is created correctly."""
        self.assertEqual(self.pl.first_name, 'Maria')
        self.assertEqual(self.pl.last_name, 'Schmidt')
        self.assertEqual(self.pl.program, 'GS')
        self.assertTrue(self.pl.is_available)
    
    def test_pl_string_representation(self):
        """Test the string representation."""
        expected = 'Schmidt, Maria (Grundschule Test)'
        self.assertEqual(str(self.pl), expected)
    
    def test_pl_school_relationship(self):
        """Test that PL is correctly linked to school."""
        self.assertEqual(self.pl.school.name, 'Grundschule Test')
        self.assertEqual(self.school.praktikumslehrkraefte.count(), 1)
    
    def test_pl_must_supervise_two_praktikum(self):
        """Test the business rule that PL supervises 2 praktikum."""
        self.assertEqual(self.pl.max_simultaneous_praktikum, 2)
    
    def test_filter_available_pls(self):
        """Test filtering available PLs."""
        # Create an unavailable PL
        PraktikumsLehrkraft.objects.create(
            first_name='Hans',
            last_name='Müller',
            email='hans.mueller@test.de',
            school=self.school,
            program='GS',
            is_available=False
        )
        
        available_pls = PraktikumsLehrkraft.objects.filter(is_available=True)
        self.assertEqual(available_pls.count(), 1)


class PLSubjectAvailabilityTests(TestCase):
    """Test cases for PL Subject Availability matrix."""
    
    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name='Test School',
            school_type='GS',
            address='Test',
            district='Test',
            city='Test',
            opnv_zone='ZONE_1'
        )
        
        self.deutsch = Subject.objects.create(code='DE', name='Deutsch')
        self.math = Subject.objects.create(code='MA', name='Mathematik')
        
        self.pdp1 = PraktikumType.objects.create(
            code='PDP_I',
            name='PDP I',
            is_block_praktikum=True
        )
        self.sfp = PraktikumType.objects.create(
            code='SFP',
            name='SFP',
            is_block_praktikum=False
        )
        
        self.pl = PraktikumsLehrkraft.objects.create(
            first_name='Test',
            last_name='Teacher',
            email='test@test.de',
            school=self.school,
            program='GS'
        )
    
    def test_pl_can_teach_subject_for_praktikum(self):
        """Test that PL can be assigned to specific subject-praktikum combinations."""
        # PL can teach Deutsch for PDP I
        availability = PLSubjectAvailability.objects.create(
            pl=self.pl,
            subject=self.deutsch,
            praktikum_type=self.pdp1,
            is_available=True
        )
        
        self.assertTrue(availability.is_available)
        self.assertEqual(availability.pl, self.pl)
        self.assertEqual(availability.subject, self.deutsch)
    
    def test_pl_cannot_teach_all_combinations(self):
        """Test that PL might not be qualified for all combinations."""
        # PL can teach Deutsch for PDP I
        PLSubjectAvailability.objects.create(
            pl=self.pl,
            subject=self.deutsch,
            praktikum_type=self.pdp1,
            is_available=True
        )
        
        # But not Math for SFP
        PLSubjectAvailability.objects.create(
            pl=self.pl,
            subject=self.math,
            praktikum_type=self.sfp,
            is_available=False
        )
        
        available_combos = PLSubjectAvailability.objects.filter(
            pl=self.pl,
            is_available=True
        )
        self.assertEqual(available_combos.count(), 1)
