from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from .models import School


class SchoolModelTests(TestCase):
    
    def setUp(self):
        self.gs_school = School.objects.create(
            name='Grundschule Passau',
            school_type='GS',
            address='Hauptstraße 1, 94032 Passau',
            district='Passau',
            city='Passau',
            opnv_zone='ZONE_1',
            travel_time_minutes=15,
            max_block_praktikum_slots=20,
            max_wednesday_praktikum_slots=15,
            is_active=True
        )
        
        self.ms_school = School.objects.create(
            name='Mittelschule Regen',
            school_type='MS',
            address='Schulweg 5, 94209 Regen',
            district='Regen',
            city='Regen',
            opnv_zone='ZONE_3',
            travel_time_minutes=90,
            max_block_praktikum_slots=15,
            max_wednesday_praktikum_slots=5,
            is_active=True
        )
    
    def test_school_creation(self):
        self.assertEqual(self.gs_school.name, 'Grundschule Passau')
        self.assertEqual(self.gs_school.school_type, 'GS')
        self.assertEqual(self.gs_school.opnv_zone, 'ZONE_1')
    
    def test_school_string_representation(self):
        expected = 'Grundschule Passau (Grundschule (Primary School))'
        self.assertEqual(str(self.gs_school), expected)
    
    def test_filter_schools_by_type(self):
        gs_schools = School.objects.filter(school_type='GS')
        self.assertEqual(gs_schools.count(), 1)
        self.assertEqual(gs_schools.first().name, 'Grundschule Passau')
    
    def test_filter_schools_by_zone(self):
        zone1_schools = School.objects.filter(opnv_zone='ZONE_1')
        self.assertEqual(zone1_schools.count(), 1)
        
        zone3_schools = School.objects.filter(opnv_zone='ZONE_3')
        self.assertEqual(zone3_schools.count(), 1)
    
    def test_school_capacity(self):
        self.assertEqual(self.gs_school.max_block_praktikum_slots, 20)
        self.assertEqual(self.gs_school.max_wednesday_praktikum_slots, 15)
    
    def test_travel_time_filtering(self):
        nearby_schools = School.objects.filter(travel_time_minutes__lte=30)
        self.assertEqual(nearby_schools.count(), 1)
        self.assertEqual(nearby_schools.first().name, 'Grundschule Passau')


class SchoolAPITests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.school1 = School.objects.create(
            name='Test Grundschule',
            school_type='GS',
            address='Test Street 1',
            district='Passau',
            city='Passau',
            opnv_zone='ZONE_1',
            travel_time_minutes=20,
            max_block_praktikum_slots=10,
            max_wednesday_praktikum_slots=5,
            is_active=True
        )
        self.school2 = School.objects.create(
            name='Test Mittelschule',
            school_type='MS',
            address='Test Street 2',
            district='Regen',
            city='Regen',
            opnv_zone='ZONE_2',
            travel_time_minutes=45,
            max_block_praktikum_slots=8,
            max_wednesday_praktikum_slots=3,
            is_active=True
        )
    
    def test_get_schools_list(self):
        response = self.client.get('/api/schools/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_school_detail(self):
        response = self.client.get(f'/api/schools/{self.school1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Grundschule')
    
    def test_create_school(self):
        data = {
            'name': 'New School',
            'school_type': 'GS',
            'address': 'New Address',
            'district': 'Passau',
            'city': 'Passau',
            'opnv_zone': 'ZONE_1',
            'max_block_praktikum_slots': 15,
            'max_wednesday_praktikum_slots': 10
        }
        response = self.client.post('/api/schools/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 3)
    
    def test_update_school(self):
        data = {
            'name': 'Updated School',
            'school_type': 'GS',
            'address': 'Updated Address',
            'district': 'Passau',
            'city': 'Passau',
            'opnv_zone': 'ZONE_2',
            'max_block_praktikum_slots': 20,
            'max_wednesday_praktikum_slots': 12
        }
        response = self.client.put(f'/api/schools/{self.school1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.school1.refresh_from_db()
        self.assertEqual(self.school1.name, 'Updated School')
    
    def test_delete_school(self):
        response = self.client.delete(f'/api/schools/{self.school1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(School.objects.count(), 1)
    
    def test_filter_by_school_type(self):
        response = self.client.get('/api/schools/?school_type=GS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['school_type'], 'GS')
    
    def test_filter_by_zone(self):
        response = self.client.get('/api/schools/?opnv_zone=ZONE_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_search_schools(self):
        response = self.client.get('/api/schools/?search=Grundschule')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Grundschule')
    
    def test_by_zone_endpoint(self):
        response = self.client.get('/api/schools/by_zone/?zone=ZONE_1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_by_type_endpoint(self):
        response = self.client.get('/api/schools/by_type/?type=MS')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_export_csv(self):
        response = self.client.get('/api/schools/export/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_import_csv(self):
        csv_content = """name,school_type,address,district,city,opnv_zone,travel_time_minutes,max_block_praktikum_slots,max_wednesday_praktikum_slots
Imported School,GS,Import Street,Passau,Passau,ZONE_1,25,12,8"""
        
        csv_file = SimpleUploadedFile(
            "schools.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            '/api/schools/import_csv/',
            {'file': csv_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(School.objects.count(), 3)
