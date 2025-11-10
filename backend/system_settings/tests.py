from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date
from .models import SystemSettings


class SystemSettingsModelTests(TestCase):
    """
    Tests for SystemSettings model.
    Business Logic: Validate model creation and field constraints.
    """
    
    def setUp(self):
        """Set up test data."""
        self.settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            total_anrechnungsstunden_budget=210.0,
            gs_budget_percentage=80.48,
            ms_budget_percentage=19.52,
            university_name='Universität Passau',
            contact_email='test@uni-passau.de',
            contact_phone='+49851509',
            is_active=True
        )
    
    def test_settings_creation(self):
        """Test settings are created correctly."""
        self.assertEqual(self.settings.current_academic_year, '2024/2025')
        self.assertAlmostEqual(float(self.settings.total_anrechnungsstunden_budget), 210.0, places=2)
        self.assertAlmostEqual(float(self.settings.gs_budget_percentage), 80.48, places=2)
        self.assertAlmostEqual(float(self.settings.ms_budget_percentage), 19.52, places=2)
        self.assertTrue(self.settings.is_active)
    
    def test_settings_string_representation(self):
        """Test settings string representation."""
        expected = 'Settings for 2024/2025'
        self.assertEqual(str(self.settings), expected)
    
    def test_budget_percentages_sum_to_100(self):
        """Test that GS and MS percentages sum to 100."""
        total = self.settings.gs_budget_percentage + self.settings.ms_budget_percentage
        self.assertAlmostEqual(float(total), 100.0, places=2)
    
    def test_unique_academic_year(self):
        """Test academic year uniqueness constraint."""
        with self.assertRaises(Exception):
            SystemSettings.objects.create(
                current_academic_year='2024/2025',  # Duplicate
                total_anrechnungsstunden_budget=200.0,
                gs_budget_percentage=80.0,
                ms_budget_percentage=20.0,
                is_active=False
            )
    
    def test_university_default_name(self):
        """Test default university name."""
        self.assertEqual(self.settings.university_name, 'Universität Passau')


class SystemSettingsAPITests(APITestCase):
    """
    Tests for System Settings API endpoints.
    Business Logic: Test all CRUD operations and custom endpoints.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        self.settings1 = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            total_anrechnungsstunden_budget=210.0,
            gs_budget_percentage=80.48,
            ms_budget_percentage=19.52,
            university_name='Universität Passau',
            pdp_i_demand_deadline=date(2024, 12, 15),
            pl_assignment_deadline=date(2025, 1, 31),
            is_active=True
        )
        
        self.settings2 = SystemSettings.objects.create(
            current_academic_year='2023/2024',
            total_anrechnungsstunden_budget=200.0,
            gs_budget_percentage=80.0,
            ms_budget_percentage=20.0,
            university_name='Universität Passau',
            is_active=False
        )
    
    def test_get_active_settings(self):
        """Test GET /api/settings/ - Returns active settings."""
        response = self.client.get('/api/settings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_academic_year'], '2024/2025')
        self.assertTrue(response.data['is_active'])
    
    def test_get_specific_settings(self):
        """Test GET /api/settings/{id}/ - Retrieve specific settings."""
        response = self.client.get(f'/api/settings/{self.settings1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_academic_year'], '2024/2025')
    
    def test_create_settings(self):
        """Test POST /api/settings/ - Create new settings."""
        data = {
            'current_academic_year': '2025/2026',
            'total_anrechnungsstunden_budget': 220.0,
            'gs_budget_percentage': 81.0,
            'ms_budget_percentage': 19.0,
            'university_name': 'Universität Passau',
            'is_active': False
        }
        response = self.client.post('/api/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SystemSettings.objects.count(), 3)
        self.assertEqual(response.data['current_academic_year'], '2025/2026')
    
    def test_update_settings(self):
        """Test PUT /api/settings/{id}/ - Update settings."""
        data = {
            'current_academic_year': '2024/2025',
            'total_anrechnungsstunden_budget': 215.0,
            'gs_budget_percentage': 82.0,
            'ms_budget_percentage': 18.0,
            'university_name': 'Universität Passau',
            'contact_email': 'updated@uni-passau.de',
            'is_active': True
        }
        response = self.client.put(f'/api/settings/{self.settings1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.settings1.refresh_from_db()
        self.assertEqual(self.settings1.total_anrechnungsstunden_budget, Decimal('215.0'))
        self.assertEqual(self.settings1.contact_email, 'updated@uni-passau.de')
    
    def test_partial_update_settings(self):
        """Test PATCH /api/settings/{id}/ - Partial update."""
        data = {
            'contact_email': 'newemail@uni-passau.de',
            'contact_phone': '+49851509999'
        }
        response = self.client.patch(f'/api/settings/{self.settings1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.settings1.refresh_from_db()
        self.assertEqual(self.settings1.contact_email, 'newemail@uni-passau.de')
        self.assertEqual(self.settings1.contact_phone, '+49851509999')
        # Other fields should remain unchanged
        self.assertEqual(self.settings1.current_academic_year, '2024/2025')
    
    def test_delete_inactive_settings(self):
        """Test DELETE /api/settings/{id}/ - Delete inactive settings."""
        settings_id = self.settings2.id
        initial_count = SystemSettings.objects.count()
        
        response = self.client.delete(f'/api/settings/{settings_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify settings is deleted
        self.assertEqual(SystemSettings.objects.count(), initial_count - 1)
        self.assertFalse(SystemSettings.objects.filter(id=settings_id).exists())
    
    def test_cannot_delete_active_settings(self):
        """Test cannot delete active settings."""
        response = self.client.delete(f'/api/settings/{self.settings1.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        # Verify settings still exists
        self.assertTrue(SystemSettings.objects.filter(id=self.settings1.id).exists())
    
    def test_budget_allocation_endpoint(self):
        """Test GET /api/settings/{id}/budget_allocation/."""
        response = self.client.get(f'/api/settings/{self.settings1.id}/budget_allocation/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_budget', response.data)
        self.assertIn('gs_hours', response.data)
        self.assertIn('ms_hours', response.data)
        
        # Verify calculations
        expected_gs = 210.0 * 80.48 / 100
        expected_ms = 210.0 * 19.52 / 100
        self.assertAlmostEqual(response.data['gs_hours'], expected_gs, places=2)
        self.assertAlmostEqual(response.data['ms_hours'], expected_ms, places=2)
    
    def test_get_all_settings_endpoint(self):
        """Test GET /api/settings/all/ - Get all settings."""
        response = self.client.get('/api/settings/all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Should be ordered by academic year descending
        self.assertEqual(response.data[0]['current_academic_year'], '2024/2025')
    
    def test_activate_academic_year(self):
        """Test POST /api/settings/activate/ - Activate specific year."""
        data = {'academic_year': '2023/2024'}
        response = self.client.post('/api/settings/activate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify activation
        self.settings2.refresh_from_db()
        self.settings1.refresh_from_db()
        self.assertTrue(self.settings2.is_active)
        self.assertFalse(self.settings1.is_active)
    
    def test_activate_nonexistent_year(self):
        """Test activating non-existent academic year returns 404."""
        data = {'academic_year': '2099/2100'}
        response = self.client.post('/api/settings/activate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_activate_without_year(self):
        """Test activate endpoint without academic_year returns error."""
        response = self.client.post('/api/settings/activate/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_budget_percentages_validation(self):
        """Test budget percentages must sum to 100%."""
        data = {
            'current_academic_year': '2026/2027',
            'total_anrechnungsstunden_budget': 210.0,
            'gs_budget_percentage': 70.0,
            'ms_budget_percentage': 25.0,  # Sum = 95%, should fail
            'university_name': 'Universität Passau',
            'is_active': False
        }
        response = self.client.post('/api/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_academic_year_format_validation(self):
        """Test academic year format validation."""
        # Invalid format - no slash
        data = {
            'current_academic_year': '2024-2025',
            'total_anrechnungsstunden_budget': 210.0,
            'gs_budget_percentage': 80.0,
            'ms_budget_percentage': 20.0,
            'university_name': 'Universität Passau',
            'is_active': False
        }
        response = self.client.post('/api/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_academic_year_consecutive_years_validation(self):
        """Test second year must be one year after first."""
        data = {
            'current_academic_year': '2024/2026',  # Not consecutive
            'total_anrechnungsstunden_budget': 210.0,
            'gs_budget_percentage': 80.0,
            'ms_budget_percentage': 20.0,
            'university_name': 'Universität Passau',
            'is_active': False
        }
        response = self.client.post('/api/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_computed_budget_fields(self):
        """Test computed gs_budget_hours and ms_budget_hours fields."""
        response = self.client.get(f'/api/settings/{self.settings1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('gs_budget_hours', response.data)
        self.assertIn('ms_budget_hours', response.data)
    
    def test_activating_new_settings_deactivates_others(self):
        """Test activating new settings deactivates all others."""
        data = {
            'current_academic_year': '2025/2026',
            'total_anrechnungsstunden_budget': 220.0,
            'gs_budget_percentage': 80.0,
            'ms_budget_percentage': 20.0,
            'university_name': 'Universität Passau',
            'is_active': True  # Set to active
        }
        response = self.client.post('/api/settings/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify old settings are deactivated
        self.settings1.refresh_from_db()
        self.settings2.refresh_from_db()
        self.assertFalse(self.settings1.is_active)
        self.assertFalse(self.settings2.is_active)
        
        # Verify new settings is active
        new_settings = SystemSettings.objects.get(current_academic_year='2025/2026')
        self.assertTrue(new_settings.is_active)
    
    def test_get_nonexistent_settings(self):
        """Test getting non-existent settings returns 404."""
        response = self.client.get('/api/settings/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_nonexistent_settings(self):
        """Test updating non-existent settings returns 404."""
        data = {
            'current_academic_year': '2024/2025',
            'total_anrechnungsstunden_budget': 210.0,
            'gs_budget_percentage': 80.0,
            'ms_budget_percentage': 20.0,
            'university_name': 'Test',
            'is_active': False
        }
        response = self.client.put('/api/settings/99999/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
