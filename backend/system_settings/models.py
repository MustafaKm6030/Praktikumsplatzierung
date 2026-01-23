from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from subjects.models import TimeStampedModel


def default_core_subjects():
    return ["D", "MA"]


class SystemSettings(TimeStampedModel):
    """
    System-wide configuration and settings.
    Business Logic: Stores current academic year, budget, deadlines.
    """
    # Academic Year
    current_academic_year = models.CharField(
        max_length=20,
        unique=True,
        help_text="e.g., '2024/2025'"
    )
    
    # Budget
    total_anrechnungsstunden_budget = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=210.0,
        help_text="Total credit hours budget (210 = 210 mentors × 2 Praktika each)"
    )
    gs_budget_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.48,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage allocated to GS (e.g., 80.48%)"
    )
    ms_budget_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19.52,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage allocated to MS (e.g., 19.52%)"
    )
    
    # Deadlines
    pdp_i_demand_deadline = models.DateField(null=True, blank=True)
    pl_assignment_deadline = models.DateField(null=True, blank=True)
    winter_semester_adjustment_date = models.DateField(null=True, blank=True)
    
    # University Info
    university_name = models.CharField(
        max_length=200,
        default="Universität Passau"
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    
    # Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Is this the active academic year?"
    )
    core_subjects = models.JSONField(
        default=default_core_subjects,
        help_text="List of core subject codes (e.g., ['D', 'MA'])"
    )
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
        ordering = ['-current_academic_year']
    
    def __str__(self):
        return f"Settings for {self.current_academic_year}"
