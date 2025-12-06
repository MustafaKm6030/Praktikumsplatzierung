from django.db import models
from subjects.models import TimeStampedModel, Subject, PraktikumType
from schools.models import School


class Student(TimeStampedModel):
    """
    Represents a student requiring Praktikum placement.
    Refactored: Now acts as the single source of truth for internship completion.
    """

    PROGRAM_CHOICES = [
        ("GS", "Grundschule"),
        ("MS", "Mittelschule"),
    ]

    PLACEMENT_STATUS_CHOICES = [
        ("UNPLACED", "Unplaced"),
        ("PLACED", "Placed"),
    ]

    # Basic Information
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)

    # Program
    program = models.CharField(
        max_length=2, choices=PROGRAM_CHOICES, help_text="GS or MS program"
    )
    major = models.CharField(max_length=100, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)

    # Primary Subject
    primary_subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_students",
        help_text="Student's primary teaching subject",
    )

    didactic_subject_1 = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="didactic_1_students",
        help_text="Didaktikfach 1",
    )

    didactic_subject_2 = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="didactic_2_students",
        help_text="Didaktikfach 2",
    )

    didactic_subject_3 = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="didactic_3_students",
        help_text="Didaktikfach 3. (Target for ZSP in this MVP)",
    )

    # Geographical Information
    home_address = models.TextField(
        blank=True, help_text="For 'heimatnah' PDP matching"
    )
    semester_address = models.TextField(
        blank=True, help_text="For SFP/ZSP travel time calculation"
    )

    # Derived/Legacy fields kept for compatibility if needed, or can be removed
    home_region = models.CharField(max_length=100, blank=True)
    preferred_zone = models.CharField(max_length=10, blank=True)

    # --- Internship Checklist (The New Logic) ---
    pdp1_completed_date = models.DateField(
        null=True, blank=True, help_text="Date PDP I was completed"
    )
    pdp2_completed_date = models.DateField(
        null=True, blank=True, help_text="Date PDP II was completed"
    )
    sfp_completed_date = models.DateField(
        null=True, blank=True, help_text="Date SFP was completed"
    )
    zsp_completed_date = models.DateField(
        null=True, blank=True, help_text="Date ZSP was completed"
    )

    # Status for the current planning cycle
    placement_status = models.CharField(
        max_length=20, choices=PLACEMENT_STATUS_CHOICES, default="UNPLACED"
    )

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["student_id"]),
            models.Index(fields=["program"]),
            models.Index(fields=["placement_status"]),
        ]

    def __str__(self):
        return f"{self.student_id} - {self.last_name}, {self.first_name}"
