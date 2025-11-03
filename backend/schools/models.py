from django.db import models
from subjects.models import TimeStampedModel


class School(TimeStampedModel):
    """
    Represents a participating school where internships take place.
    Business Logic: Schools have zones, capacity limits, and OPNV accessibility.
    """
    SCHOOL_TYPE_CHOICES = [
        ('GS', 'Grundschule (Primary School)'),
        ('MS', 'Mittelschule (Secondary School)'),
    ]
    
    OPNV_ZONE_CHOICES = [
        ('ZONE_1', 'Zone 1 (Close to University)'),
        ('ZONE_2', 'Zone 2 (Medium Distance)'),
        ('ZONE_3', 'Zone 3 (Far from University)'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    school_type = models.CharField(max_length=2, choices=SCHOOL_TYPE_CHOICES)
    
    # Address and Location
    address = models.TextField()
    district = models.CharField(
        max_length=100,
        help_text="Landkreis/District (e.g., Passau-Land, Regen)"
    )
    city = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    
    # OPNV Zone
    opnv_zone = models.CharField(
        max_length=10,
        choices=OPNV_ZONE_CHOICES,
        help_text="Public transport accessibility zone"
    )
    travel_time_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Travel time from university in minutes"
    )
    
    # Capacity
    max_block_praktikum_slots = models.PositiveIntegerField(
        default=0,
        help_text="Maximum slots for PDP I/II"
    )
    max_wednesday_praktikum_slots = models.PositiveIntegerField(
        default=0,
        help_text="Maximum slots for SFP/ZSP"
    )
    
    # Contact
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ['name']
        indexes = [
            models.Index(fields=['school_type', 'opnv_zone']),
            models.Index(fields=['district']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_school_type_display()})"
