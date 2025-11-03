from django.test import TestCase
from .models import School


class SchoolModelTests(TestCase):
    """Test cases for School model."""
    
    def setUp(self):
        """Create test schools."""
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
        """Test that schools are created with correct attributes."""
        self.assertEqual(self.gs_school.name, 'Grundschule Passau')
        self.assertEqual(self.gs_school.school_type, 'GS')
        self.assertEqual(self.gs_school.opnv_zone, 'ZONE_1')
    
    def test_school_string_representation(self):
        """Test the string representation."""
        expected = 'Grundschule Passau (Grundschule (Primary School))'
        self.assertEqual(str(self.gs_school), expected)
    
    def test_filter_schools_by_type(self):
        """Test filtering schools by type."""
        gs_schools = School.objects.filter(school_type='GS')
        self.assertEqual(gs_schools.count(), 1)
        self.assertEqual(gs_schools.first().name, 'Grundschule Passau')
    
    def test_filter_schools_by_zone(self):
        """Test filtering schools by OPNV zone."""
        zone1_schools = School.objects.filter(opnv_zone='ZONE_1')
        self.assertEqual(zone1_schools.count(), 1)
        
        zone3_schools = School.objects.filter(opnv_zone='ZONE_3')
        self.assertEqual(zone3_schools.count(), 1)
    
    def test_school_capacity(self):
        """Test that school capacity fields work correctly."""
        self.assertEqual(self.gs_school.max_block_praktikum_slots, 20)
        self.assertEqual(self.gs_school.max_wednesday_praktikum_slots, 15)
    
    def test_travel_time_filtering(self):
        """Test filtering schools by travel time."""
        # Schools within 30 minutes
        nearby_schools = School.objects.filter(travel_time_minutes__lte=30)
        self.assertEqual(nearby_schools.count(), 1)
        self.assertEqual(nearby_schools.first().name, 'Grundschule Passau')
