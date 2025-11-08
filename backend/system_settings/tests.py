from django.test import TestCase
from datetime import date
from .models import SystemSettings


class SystemSettingsTests(TestCase):
    """Test cases for SystemSettings model."""
    
    def test_system_settings_creation(self):
        """Test creating system settings for an academic year."""
        settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            total_anrechnungsstunden_budget=210.0,
            gs_budget_percentage=80.48,
            ms_budget_percentage=19.52,
            is_active=True
        )
        
        self.assertEqual(settings.current_academic_year, '2024/2025')
        self.assertEqual(settings.total_anrechnungsstunden_budget, 210.0)
        self.assertTrue(settings.is_active)
    
    def test_budget_percentages(self):
        """Test that budget percentages are set correctly."""
        settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            gs_budget_percentage=80.48,
            ms_budget_percentage=19.52
        )
        
        # Check that percentages add up to 100 (approximately)
        total = settings.gs_budget_percentage + settings.ms_budget_percentage
        self.assertAlmostEqual(float(total), 100.0, places=2)
    
    def test_calculate_gs_budget(self):
        """Test calculating GS budget from total."""
        settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            total_anrechnungsstunden_budget=210.0,
            gs_budget_percentage=80.48
        )
        
        gs_budget = (settings.total_anrechnungsstunden_budget * 
                    settings.gs_budget_percentage / 100)
        self.assertAlmostEqual(float(gs_budget), 169.0, places=0)
    
    def test_system_settings_deadlines(self):
        """Test that deadlines can be set."""
        settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            pdp_i_demand_deadline=date(2024, 5, 1),
            pl_assignment_deadline=date(2024, 6, 15),
            winter_semester_adjustment_date=date(2025, 1, 15)
        )
        
        self.assertEqual(settings.pdp_i_demand_deadline, date(2024, 5, 1))
        self.assertEqual(settings.pl_assignment_deadline, date(2024, 6, 15))
    
    def test_only_one_active_settings(self):
        """Test getting the currently active system settings."""
        # Create settings for multiple years
        old_settings = SystemSettings.objects.create(
            current_academic_year='2023/2024',
            is_active=False
        )
        
        current_settings = SystemSettings.objects.create(
            current_academic_year='2024/2025',
            is_active=True
        )
        
        active = SystemSettings.objects.filter(is_active=True)
        self.assertEqual(active.count(), 1)
        self.assertEqual(active.first().current_academic_year, '2024/2025')
