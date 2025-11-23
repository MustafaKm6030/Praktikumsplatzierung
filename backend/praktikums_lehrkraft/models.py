from django.db import models
from subjects.models import TimeStampedModel, Subject, PraktikumType
from schools.models import School


class PraktikumsLehrkraft(TimeStampedModel):
    """
    Represents a Praktikum teacher/mentor (PL).
    Refactored to match the Excel Source of Truth.
    """

    PROGRAM_CHOICES = [
        ("GS", "Grundschule"),
        ("MS", "Mittelschule"),
    ]

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)

    # School Assignment
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="praktikumslehrkraefte",
        help_text="Current school assignment",
    )
    program = models.CharField(
        max_length=2, choices=PROGRAM_CHOICES, help_text="GS or MS program"
    )

    # Main Teaching Subject
    main_subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="main_pls",
        help_text="Primary teaching subject (Hauptfach) - Informational only",
    )

    # Praktikum Availability
    available_praktikum_types = models.ManyToManyField(
        PraktikumType,
        related_name="available_pls",
        blank=True,
        help_text="Praktikum types this PL can supervise (Parsed from 'bevorzugte Praktika')",
    )

    preferred_praktika_raw = models.CharField(
        max_length=255,
        blank=True,
        help_text="Raw text from 'bevorzugte Praktika' column",
    )

    # Subject Availability - Direct M2M (replacing the through table)
    available_subjects = models.ManyToManyField(
        Subject,
        related_name="qualified_pls",
        blank=True,
        help_text="Subjects this PL can supervise this year (from the 'x' columns)",
    )

    # Administrative Assignment
    schulamt = models.CharField(
        max_length=100,
        blank=True,
        help_text="Associated Schulamt (e.g., Passau-Land, Regen)",
    )

    # Capacity Constraints (The Budget)
    anrechnungsstunden = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1.0,
        help_text="Credited hours (Anre-Std.). Standard is 1.0. '4 for 2' is 2.0.",
    )

    # Special Notes
    current_year_notes = models.TextField(
        blank=True, help_text="Year-specific notes (e.g., 'Besonderheiten SJ 25_26')"
    )

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Master availability switch"
    )

    notes = models.TextField(blank=True, help_text="Internal system notes")

    # Data Lineage
    csv_id = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Praktikumslehrkraft"
        verbose_name_plural = "Praktikumslehrkräfte"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["school", "program"]),
            models.Index(fields=["is_active"]),
        ]

    @property
    def capacity(self):
        """
        Calculates the number of internships this PL must supervise.
        Rule: 1 Anrechnungsstunde = 2 Internships.
        """
        return int(self.anrechnungsstunden * 2)

    @property
    def is_available(self):
        """
        Checks logical availability based on active status and notes.
        This is a helper, the algo will do deeper parsing.
        """
        return self.is_active

    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.school.name})"
