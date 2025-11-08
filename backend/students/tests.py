from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
from subjects.models import Subject, PraktikumType
from schools.models import School
from .models import Student, StudentPraktikumPreference


class StudentModelTests(TestCase):
    
    def setUp(self):
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
        self.assertEqual(self.student.student_id, '12345')
        self.assertEqual(self.student.first_name, 'Max')
        self.assertEqual(self.student.program, 'GS')
    
    def test_student_string_representation(self):
        expected = '12345 - Mustermann, Max'
        self.assertEqual(str(self.student), expected)
    
    def test_student_primary_subject(self):
        self.assertEqual(self.student.primary_subject.name, 'Deutsch')
    
    def test_student_additional_subjects(self):
        self.student.additional_subjects.add(self.math)
        self.assertEqual(self.student.additional_subjects.count(), 1)
    
    def test_filter_students_by_program(self):
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


class StudentAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        self.subject = Subject.objects.create(
            code='MA',
            name='Mathematik'
        )
        
        self.student1 = Student.objects.create(
            student_id='ST001',
            first_name='John',
            last_name='Doe',
            email='john@test.com',
            program='GS',
            primary_subject=self.subject,
            home_region='Passau'
        )
        
        self.student2 = Student.objects.create(
            student_id='ST002',
            first_name='Jane',
            last_name='Smith',
            email='jane@test.com',
            program='MS',
            home_region='Regen'
        )
    
    def test_get_students_list(self):
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_student_detail(self):
        response = self.client.get(f'/api/students/{self.student1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['student_id'], 'ST001')
    
    def test_create_student(self):
        data = {
            'student_id': 'ST003',
            'first_name': 'Bob',
            'last_name': 'Johnson',
            'email': 'bob@test.com',
            'program': 'GS'
        }
        response = self.client.post('/api/students/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 3)
    
    def test_update_student(self):
        data = {
            'student_id': 'ST001',
            'first_name': 'John',
            'last_name': 'Doe Updated',
            'email': 'john@test.com',
            'program': 'GS',
            'home_region': 'Passau-Land'
        }
        response = self.client.put(f'/api/students/{self.student1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.last_name, 'Doe Updated')
    
    def test_delete_student(self):
        response = self.client.delete(f'/api/students/{self.student1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Student.objects.count(), 1)
    
    def test_filter_by_program(self):
        response = self.client.get('/api/students/?program=GS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['program'], 'GS')
    
    def test_filter_by_region(self):
        response = self.client.get('/api/students/?home_region=Passau')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_search_students(self):
        response = self.client.get('/api/students/?search=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'John')
    
    def test_by_program_endpoint(self):
        response = self.client.get('/api/students/by_program/?program=MS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_by_region_endpoint(self):
        response = self.client.get('/api/students/by_region/?region=Regen')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_export_csv(self):
        response = self.client.get('/api/students/export/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_import_csv(self):
        csv_content = """student_id,first_name,last_name,email,program,home_region
ST003,Alice,Brown,alice@test.com,GS,Passau"""
        
        csv_file = SimpleUploadedFile(
            "students.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            '/api/students/import_csv/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(Student.objects.count(), 3)
    
    def test_import_csv_no_file(self):
        response = self.client.post('/api/students/import_csv/', {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_import_csv_invalid_file_type(self):
        txt_file = SimpleUploadedFile(
            "students.txt",
            b"not a csv",
            content_type="text/plain"
        )
        
        response = self.client.post(
            '/api/students/import_csv/',
            {'file': txt_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class StudentPraktikumPreferenceTests(TestCase):
    
    def setUp(self):
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
        preference = StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='UNPLACED'
        )
        
        self.assertEqual(preference.student, self.student)
        self.assertEqual(preference.praktikum_type, self.pdp1)
        self.assertEqual(preference.status, 'UNPLACED')
    
    def test_student_can_prefer_specific_schools(self):
        preference = StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='UNPLACED'
        )
        preference.preferred_schools.add(self.school)
        
        self.assertEqual(preference.preferred_schools.count(), 1)
    
    def test_student_can_have_multiple_preferences(self):
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
        StudentPraktikumPreference.objects.create(
            student=self.student,
            praktikum_type=self.pdp1,
            status='UNPLACED'
        )
        
        unplaced = StudentPraktikumPreference.objects.filter(status='UNPLACED')
        self.assertEqual(unplaced.count(), 1)
