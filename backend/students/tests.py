from django.test import TestCase
from datetime import date
from subjects.models import Subject, PraktikumType
from schools.models import School
from .models import Student, StudentPraktikumPreference


class StudentModelTests(TestCase):
    """Test cases for Student model."""
    
    def setUp(self):
        """Set up test data."""
        self.deutsch = Subject.objects.create(code='DE', name='Deutsch')
        self.math = Subject.objects.create(code='MA', name='Mathematik')
        
        self.student = Student.objects.create(
            student_id='12345',
            first_name='Max',
            last_name='Mustermann',
            email='max.mustermann@uni-passau.de',
            program='GS',
            major='Grundschullehramt',
            primary_subject=self.deutsch,
            home_region='Passau',
            enrollment_date=date(2023, 10, 1)
        )
    
    def test_student_creation(self):
        """Test that student is created correctly."""
        self.assertEqual(self.student.student_id, '12345')
        self.assertEqual(self.student.first_name, 'Max')
        self.assertEqual(self.student.program, 'GS')
    
    def test_student_string_representation(self):
        """Test the string representation."""
        expected = '12345 - Mustermann, Max'
        self.assertEqual(str(self.student), expected)
    
    def test_student_primary_subject(self):
        """Test that student has a primary subject."""
        self.assertEqual(self.student.primary_subject.name, 'Deutsch')
    
    def test_student_additional_subjects(self):
        """Test that student can have additional subjects."""
        self.student.additional_subjects.add(self.math)
        self.assertEqual(self.student.additional_subjects.count(), 1)
    
    def test_filter_students_by_program(self):
        """Test filtering students by program."""
        # Create MS student
        Student.objects.create(
            student_id='67890',
            first_name='Anna',
            last_name='Weber',
            email='anna.weber@uni-passau.de',
            program='MS',
            primary_subject=self.deutsch
        )
        
        gs_students = Student.objects.filter(program='GS')
        ms_students = Student.objects.filter(program='MS')
        
        self.assertEqual(gs_students.count(), 1)
        self.assertEqual(ms_students.count(), 1)


class StudentPraktikumPreferenceTests(TestCase):
    """Test cases for Student Praktikum Preferences."""
    
    def setUp(self):
        """Set up test data."""
        self.deutsch = Subject.objects.create(code='DE', name='Deutsch')
        
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
        
        self.student = Student.objects.create(
            student_id='12345',
            first_name='Max',
            last_name='Test',
            email='max@test.de',
            program='GS',
            primary_subject=self.deutsch
        )
        
        self.school = School.objects.create(
            name='Test School',
            school_type='GS',
            address='Test',
            district='Test',
            city='Test',
            opnv_zone='ZONE_1'
        )
    
    def test_student_can_have_praktikum_preferences(self):
        """Test that students can declare which praktikum they want."""
        preference = StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='UNPLACED'
        )
        
        self.assertEqual(preference.student, self.student)
        self.assertEqual(preference.praktikum_type, self.pdp1)
        self.assertEqual(preference.status, 'UNPLACED')
    
    def test_student_can_prefer_specific_schools(self):
        """Test that students can prefer specific schools."""
        preference = StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='UNPLACED'
        )
        preference.preferred_schools.add(self.school)
        
        self.assertEqual(preference.preferred_schools.count(), 1)
    
    def test_student_can_have_multiple_preferences(self):
        """Test that students can have preferences for different praktikum types."""
        StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='COMPLETED'
        )
        
        StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.sfp,
            status='UNPLACED'
        )
        
        preferences = self.student.praktikum_preferences.all()
        self.assertEqual(preferences.count(), 2)
    
    def test_filter_unplaced_preferences(self):
        """Test filtering preferences by status."""
        StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='UNPLACED'
        )
        
        unplaced = StudentPraktikumPreference.objects.filter(status='UNPLACED')
        self.assertEqual(unplaced.count(), 1)
