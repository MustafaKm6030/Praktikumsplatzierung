from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import PraktikumsLehrkraft, PLSubjectAvailability
from schools.models import School
from subjects.models import Subject, PraktikumType


class PraktikumsLehrkraftModelTests(TestCase):
    """
    Tests for PraktikumsLehrkraft model.
    Business Logic: Validate model creation and relationships.
    """
    
    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name='Test Grundschule',
            school_type='GS',
            address='Test Address',
            district='Passau',
            city='Passau',
            opnv_zone='ZONE_1',
            max_block_praktikum_slots=20,
            max_wednesday_praktikum_slots=15
        )
        
        self.subject = Subject.objects.create(
            code='MATH',
            name='Mathematik',
            is_active=True
        )
        
        self.praktikum_type = PraktikumType.objects.create(
            code='PDP_I',
            name='PDP I',
            is_block_praktikum=True,
            is_active=True
        )
        
        self.pl = PraktikumsLehrkraft.objects.create(
            first_name='Max',
            last_name='Mustermann',
            email='max.mustermann@test.de',
            phone='+49123456789',
            school=self.school,
            program='GS',
            main_subject=self.subject,
            max_students_per_praktikum=3,
            max_simultaneous_praktikum=2,
            is_available=True
        )
        
        self.pl.available_praktikum_types.add(self.praktikum_type)
        # Create the through table entry with praktikum_type
        PLSubjectAvailability.objects.create(
            pl=self.pl,
            subject=self.subject,
            praktikum_type=self.praktikum_type,
            is_available=True
        )
    
    def test_pl_creation(self):
        """Test PL is created correctly."""
        self.assertEqual(self.pl.first_name, 'Max')
        self.assertEqual(self.pl.last_name, 'Mustermann')
        self.assertEqual(self.pl.email, 'max.mustermann@test.de')
        self.assertEqual(self.pl.school.name, 'Test Grundschule')
        self.assertEqual(self.pl.program, 'GS')
    
    def test_pl_string_representation(self):
        """Test PL string representation."""
        expected = 'Mustermann, Max (Test Grundschule)'
        self.assertEqual(str(self.pl), expected)
    
    def test_pl_school_relationship(self):
        """Test PL to School relationship."""
        self.assertEqual(self.pl.school, self.school)
        self.assertIn(self.pl, self.school.praktikumslehrkraefte.all())
    
    def test_pl_main_subject_relationship(self):
        """Test PL main subject relationship."""
        self.assertEqual(self.pl.main_subject, self.subject)
    
    def test_pl_available_praktikum_types(self):
        """Test PL available praktikum types."""
        self.assertEqual(self.pl.available_praktikum_types.count(), 1)
        self.assertIn(self.praktikum_type, self.pl.available_praktikum_types.all())
    
    def test_pl_capacity_constraints(self):
        """Test PL capacity constraints."""
        self.assertEqual(self.pl.max_students_per_praktikum, 3)
        self.assertEqual(self.pl.max_simultaneous_praktikum, 2)
    
    def test_pl_availability_status(self):
        """Test PL availability status."""
        self.assertTrue(self.pl.is_available)
        self.pl.is_available = False
        self.pl.save()
        self.assertFalse(self.pl.is_available)


class PLSubjectAvailabilityTests(TestCase):
    """
    Tests for PLSubjectAvailability model.
    Business Logic: Test PL-Subject-Praktikum matrix.
    """
    
    def setUp(self):
        """Set up test data."""
        self.school = School.objects.create(
            name='Test School',
            school_type='GS',
            address='Address',
            district='Passau',
            city='Passau',
            opnv_zone='ZONE_1',
            max_block_praktikum_slots=10,
            max_wednesday_praktikum_slots=5
        )
        
        self.subject = Subject.objects.create(
            code='MATH',
            name='Mathematik'
        )
        
        self.praktikum_type = PraktikumType.objects.create(
            code='PDP_I',
            name='PDP I',
            is_block_praktikum=True
        )
        
        self.pl = PraktikumsLehrkraft.objects.create(
            first_name='Test',
            last_name='PL',
            email='test@test.de',
            school=self.school,
            program='GS',
            main_subject=self.subject
        )
        
        self.availability = PLSubjectAvailability.objects.create(
            pl=self.pl,
            subject=self.subject,
            praktikum_type=self.praktikum_type,
            is_available=True
        )
        
    def test_availability_creation(self):
        """Test subject availability is created correctly."""
        self.assertEqual(self.availability.pl, self.pl)
        self.assertEqual(self.availability.subject, self.subject)
        self.assertEqual(self.availability.praktikum_type, self.praktikum_type)
        self.assertTrue(self.availability.is_available)
    
    def test_availability_unique_constraint(self):
        """Test unique constraint on PL-Subject-Praktikum combination."""
        with self.assertRaises(Exception):
            PLSubjectAvailability.objects.create(
                pl=self.pl,
                subject=self.subject,
                praktikum_type=self.praktikum_type,
                is_available=False
            )


class PLAPITests(APITestCase):
    """
    Tests for PL API endpoints.
    Business Logic: Test all CRUD operations and filtering.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.school1 = School.objects.create(
            name='Grundschule Test',
            school_type='GS',
            address='Street 1',
            district='Passau',
            city='Passau',
            opnv_zone='ZONE_1',
            max_block_praktikum_slots=20,
            max_wednesday_praktikum_slots=15
        )
        
        self.school2 = School.objects.create(
            name='Mittelschule Test',
            school_type='MS',
            address='Street 2',
            district='Regen',
            city='Regen',
            opnv_zone='ZONE_2',
            max_block_praktikum_slots=15,
            max_wednesday_praktikum_slots=10
        )
        
        self.subject = Subject.objects.create(
            code='MATH',
            name='Mathematik'
        )
        
        self.praktikum_type = PraktikumType.objects.create(
            code='PDP_I',
            name='PDP I',
            is_block_praktikum=True
        )
        
        self.pl1 = PraktikumsLehrkraft.objects.create(
            first_name='Max',
            last_name='Mustermann',
            email='max@test.de',
            phone='+49123456789',
            school=self.school1,
            program='GS',
            main_subject=self.subject,
            is_available=True
        )
        
        self.pl2 = PraktikumsLehrkraft.objects.create(
            first_name='Anna',
            last_name='Schmidt',
            email='anna@test.de',
            phone='+49987654321',
            school=self.school2,
            program='MS',
            main_subject=self.subject,
            is_available=True
        )
        
        self.pl1.available_praktikum_types.add(self.praktikum_type)
        # Create the through table entry with praktikum_type
        PLSubjectAvailability.objects.create(
            pl=self.pl1,
            subject=self.subject,
            praktikum_type=self.praktikum_type,
            is_available=True
        )
    
    def test_get_pls_list(self):
        """Test GET /api/pls/ - List all PLs."""
        response = self.client.get('/api/pls/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_pl_detail(self):
        """Test GET /api/pls/{id}/ - Retrieve single PL."""
        response = self.client.get(f'/api/pls/{self.pl1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['last_name'], 'Mustermann')
        self.assertEqual(response.data['email'], 'max@test.de')
    
    def test_create_pl(self):
        """Test POST /api/pls/ - Create new PL."""
        data = {
            'first_name': 'Test',
            'last_name': 'Teacher',
            'email': 'test.teacher@test.de',
            'phone': '+491234567890',
            'school': self.school1.id,
            'program': 'GS',
            'main_subject': self.subject.id,
            'max_students_per_praktikum': 3,
            'max_simultaneous_praktikum': 2,
            'is_available': True
        }
        response = self.client.post('/api/pls/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PraktikumsLehrkraft.objects.count(), 3)
    
    def test_update_pl(self):
        """Test PUT /api/pls/{id}/ - Update PL."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'max@test.de',
            'phone': '+49999999999',
            'school': self.school1.id,
            'program': 'GS',
            'main_subject': self.subject.id,
            'max_students_per_praktikum': 4,
            'max_simultaneous_praktikum': 2,
            'is_available': False
        }
        response = self.client.put(f'/api/pls/{self.pl1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pl1.refresh_from_db()
        self.assertEqual(self.pl1.first_name, 'Updated')
        self.assertEqual(self.pl1.last_name, 'Name')
        self.assertFalse(self.pl1.is_available)
    
    def test_partial_update_pl(self):
        """Test PATCH /api/pls/{id}/ - Partial update PL."""
        data = {
            'is_available': False,
            'phone': '+49111111111'
        }
        response = self.client.patch(f'/api/pls/{self.pl1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pl1.refresh_from_db()
        self.assertFalse(self.pl1.is_available)
        self.assertEqual(self.pl1.phone, '+49111111111')
        # Other fields should remain unchanged
        self.assertEqual(self.pl1.first_name, 'Max')
        self.assertEqual(self.pl1.last_name, 'Mustermann')
    
    def test_delete_pl(self):
        """Test DELETE /api/pls/{id}/ - Delete PL from database."""
        pl_id = self.pl1.id
        initial_count = PraktikumsLehrkraft.objects.count()
        
        response = self.client.delete(f'/api/pls/{pl_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify PL is deleted from database
        self.assertEqual(PraktikumsLehrkraft.objects.count(), initial_count - 1)
        self.assertFalse(PraktikumsLehrkraft.objects.filter(id=pl_id).exists())
        
        # Verify trying to get deleted PL returns 404
        response = self.client.get(f'/api/pls/{pl_id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_filter_by_school(self):
        """Test filtering PLs by school."""
        response = self.client.get(f'/api/pls/?school={self.school1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['school'], self.school1.id)
    
    def test_filter_by_program(self):
        """Test filtering PLs by program."""
        response = self.client.get('/api/pls/?program=GS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['program'], 'GS')
    
    def test_filter_by_school_type(self):
        """Test filtering PLs by school type."""
        response = self.client.get('/api/pls/?school__school_type=MS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_search_pls_by_name(self):
        """Test searching PLs by name."""
        response = self.client.get('/api/pls/?search=Max')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'Max')
    
    def test_search_pls_by_school_name(self):
        """Test searching PLs by school name."""
        response = self.client.get('/api/pls/?search=Grundschule')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_by_school_endpoint(self):
        """Test /api/pls/by_school/ custom endpoint."""
        response = self.client.get(f'/api/pls/by_school/?school_id={self.school1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_by_program_endpoint(self):
        """Test /api/pls/by_program/ custom endpoint."""
        response = self.client.get('/api/pls/by_program/?program=MS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['program'], 'MS')
    
    def test_search_endpoint(self):
        """Test /api/pls/search/ custom endpoint."""
        response = self.client.get('/api/pls/search/?q=Anna')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'Anna')
    
    def test_search_by_pl_id(self):
        """Test searching PL by ID."""
        response = self.client.get(f'/api/pls/search/?q={self.pl1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_available_for_praktikum_endpoint(self):
        """Test /api/pls/available_for_praktikum/ endpoint."""
        response = self.client.get(
            f'/api/pls/available_for_praktikum/?praktikum_type_id={self.praktikum_type.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_capacity_info_endpoint(self):
        """Test /api/pls/{id}/capacity_info/ endpoint."""
        response = self.client.get(f'/api/pls/{self.pl1.id}/capacity_info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('max_students_per_praktikum', response.data)
        self.assertIn('max_simultaneous_praktikum', response.data)
    
    def test_by_subject_endpoint(self):
        """Test /api/pls/by_subject/ endpoint."""
        response = self.client.get(f'/api/pls/by_subject/?subject_id={self.subject.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_pl_with_duplicate_email(self):
        """Test creating PL with duplicate email fails."""
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Email',
            'email': 'max@test.de',  # Duplicate email
            'school': self.school1.id,
            'program': 'GS',
            'main_subject': self.subject.id
        }
        response = self.client.post('/api/pls/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_pl_with_invalid_max_simultaneous(self):
        """Test creating PL with max_simultaneous_praktikum > 2 fails."""
        data = {
            'first_name': 'Test',
            'last_name': 'Invalid',
            'email': 'invalid@test.de',
            'school': self.school1.id,
            'program': 'GS',
            'main_subject': self.subject.id,
            'max_simultaneous_praktikum': 3  # Should fail
        }
        response = self.client.post('/api/pls/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_ordering_pls(self):
        """Test ordering PLs by last_name."""
        response = self.client.get('/api/pls/?ordering=last_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['last_name'], 'Mustermann')
        self.assertEqual(response.data[1]['last_name'], 'Schmidt')
    
    def test_get_nonexistent_pl(self):
        """Test getting non-existent PL returns 404."""
        response = self.client.get('/api/pls/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_nonexistent_pl(self):
        """Test updating non-existent PL returns 404."""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@test.de',
            'school': self.school1.id,
            'program': 'GS',
            'main_subject': self.subject.id
        }
        response = self.client.put('/api/pls/99999/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_nonexistent_pl(self):
        """Test deleting non-existent PL returns 404."""
        response = self.client.delete('/api/pls/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_pl_missing_required_fields(self):
        """Test creating PL without required fields fails."""
        data = {
            'first_name': 'Test'
            # Missing required fields
        }
        response = self.client.post('/api/pls/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_filter_by_availability(self):
        """Test filtering PLs by availability."""
        self.pl1.is_available = False
        self.pl1.save()
        
        response = self.client.get('/api/pls/?is_available=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.pl2.id)
    
    def test_by_school_without_parameter(self):
        """Test by_school endpoint without school_id parameter returns error."""
        response = self.client.get('/api/pls/by_school/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_by_program_without_parameter(self):
        """Test by_program endpoint without program parameter returns error."""
        response = self.client.get('/api/pls/by_program/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_search_without_parameter(self):
        """Test search endpoint without q parameter returns error."""
        response = self.client.get('/api/pls/search/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_available_for_praktikum_without_parameter(self):
        """Test available_for_praktikum without praktikum_type_id returns error."""
        response = self.client.get('/api/pls/available_for_praktikum/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_by_subject_without_parameter(self):
        """Test by_subject endpoint without subject_id parameter returns error."""
        response = self.client.get('/api/pls/by_subject/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_pl_with_all_fields(self):
        """Test creating PL with all optional fields."""
        data = {
            'first_name': 'Complete',
            'last_name': 'Test',
            'email': 'complete@test.de',
            'phone': '+491234567890',
            'school': self.school1.id,
            'program': 'GS',
            'main_subject': self.subject.id,
            'available_praktikum_types': [self.praktikum_type.id],
            'schulamt': 'Passau-Land',
            'max_students_per_praktikum': 4,
            'max_simultaneous_praktikum': 2,
            'besonderheiten': 'Special notes here',
            'is_available': True,
            'notes': 'Additional notes'
        }
        response = self.client.post('/api/pls/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all fields were saved
        pl = PraktikumsLehrkraft.objects.get(email='complete@test.de')
        self.assertEqual(pl.schulamt, 'Passau-Land')
        self.assertEqual(pl.besonderheiten, 'Special notes here')
        self.assertEqual(pl.notes, 'Additional notes')
        self.assertEqual(pl.max_students_per_praktikum, 4)
    
    def test_ordering_descending(self):
        """Test descending ordering by first name."""
        response = self.client.get('/api/pls/?ordering=-first_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['first_name'], 'Max')
        self.assertEqual(response.data[1]['first_name'], 'Anna')
    
    def test_combined_filters(self):
        """Test combining multiple filters."""
        response = self.client.get(f'/api/pls/?school={self.school1.id}&program=GS&is_available=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.pl1.id)
