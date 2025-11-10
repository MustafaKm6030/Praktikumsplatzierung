from django.db import models
from django.core.validators import MaxValueValidator
from subjects.models import TimeStampedModel, Subject, PraktikumType
from schools.models import School


class PraktikumsLehrkraft(TimeStampedModel):
    """
    Represents a Praktikum teacher/mentor (PL).
    Business Logic: Each PL has specific subject availability matrix,
    Praktikum type preferences, and Anrechnungsstunden allocation.
    """
    PROGRAM_CHOICES = [
        ('GS', 'Grundschule'),
        ('MS', 'Mittelschule'),
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
        related_name='praktikumslehrkraefte',
        help_text="Current school assignment (cannot change mid-year)"
    )
    program = models.CharField(
        max_length=2,
        choices=PROGRAM_CHOICES,
        help_text="GS or MS program - must match student program"
    )
    
    # Main Teaching Subject
    main_subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        related_name='main_pls',
        help_text="Primary teaching subject (Hauptfach)"
    )
    
    # Praktikum Availability
    available_praktikum_types = models.ManyToManyField(
        PraktikumType,
        related_name='available_pls',
        help_text="Praktikum types this PL can supervise"
    )
    
    # Subject-Praktikum Matrix (stores which subjects for which Praktikum types)
    # This will be managed through a separate through table
    available_subjects = models.ManyToManyField(
        Subject,
        through='PLSubjectAvailability',
        related_name='qualified_pls',
        help_text="Subjects this PL can supervise"
    )
    
    # Administrative Assignment
    schulamt = models.CharField(
        max_length=100,
        blank=True,
        help_text="Associated Schulamt (e.g., Passau-Land, Regen)"
    )
    
    # Capacity Constraints
    max_students_per_praktikum = models.PositiveIntegerField(
        default=3,
        help_text="Max students per Praktikum session (same time slot)"
    )
    max_simultaneous_praktikum = models.PositiveIntegerField(
        default=2,
        validators=[MaxValueValidator(2)],
        help_text="Must supervise exactly 2 internships per year"
    )
    
    # Special Notes
    besonderheiten = models.TextField(
        blank=True,
        help_text="Special conditions (e.g., '2 Mittwochs-Praktika')"
    )
    
    # Status
    is_available = models.BooleanField(
        default=True,
        help_text="Available for assignment (false if ill/absent)"
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Praktikumslehrkraft"
        verbose_name_plural = "Praktikumslehrkräfte"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['school', 'program']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name} ({self.school.name})"


class PLSubjectAvailability(TimeStampedModel):
    """
    Through table for PL-Subject-Praktikum matrix.
    Business Logic: Captures which subjects a PL can teach 
    for which specific Praktikum types (from Excel matrix).
    """
    pl = models.ForeignKey(
        PraktikumsLehrkraft,
        on_delete=models.CASCADE,
        related_name='subject_availabilities'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='pl_availabilities'
    )
    praktikum_type = models.ForeignKey(
        PraktikumType,
        on_delete=models.CASCADE,
        related_name='subject_availabilities'
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Can this PL teach this subject for this Praktikum?"
    )
    
    class Meta:
        verbose_name = "PL Subject Availability"
        verbose_name_plural = "PL Subject Availabilities"
        unique_together = ['pl', 'subject', 'praktikum_type']
        indexes = [
            models.Index(fields=['pl', 'praktikum_type', 'is_available']),
        ]
    
    def __str__(self):
        return f"{self.pl} - {self.subject} - {self.praktikum_type}"
