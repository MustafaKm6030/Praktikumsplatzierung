from django.db import models
from subjects.models import TimeStampedModel


class School(TimeStampedModel):
    """
    Represents a participating school. Refactored to match the master CSV.
    Capacity is calculated dynamically from assigned mentors, not stored here.
    """

    SCHOOL_TYPE_CHOICES = [
        ("GS", "Grundschule (Primary School)"),
        ("MS", "Mittelschule (Secondary School)"),
        ("GMS", "Grund- und Mittelschule"),
    ]

    name = models.CharField(max_length=200, unique=True)
    school_type = models.CharField(max_length=3, choices=SCHOOL_TYPE_CHOICES)

    district = models.CharField(
        max_length=100, help_text="Landkreis/District (e.g., Passau-Land, Regen)"
    )

    city = models.CharField(max_length=100)

    zone = models.IntegerField(
        choices=[(1, "Zone 1"), (2, "Zone 2"), (3, "Zone 3")],
        help_text="Official travel zone from university (1=closest, 3=farthest)",
    )

    opnv_code = models.CharField(
        max_length=2,
        blank=True,
        choices=[("4a", "Up to 30 min"), ("4b", "Up to 60 min")],
        help_text="Public transport code ('4a' or '4b') from the CSV",
    )

    distance_km = models.IntegerField(null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude for map display",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude for map display",
    )

    GEOCODING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("not_needed", "Not Needed"),
    ]

    geocoding_status = models.CharField(
        max_length=20,
        choices=GEOCODING_STATUS_CHOICES,
        default="pending",
        help_text="Status of geocoding attempt",
    )

    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "School"
        verbose_name_plural = "Schools"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["school_type", "zone"]),
            models.Index(fields=["district"]),
        ]

    def __str__(self):
        return f"{self.name}"
