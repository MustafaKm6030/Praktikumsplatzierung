from django.db import models
from subjects.models import TimeStampedModel, Subject, PraktikumType
from schools.models import School


class Student(TimeStampedModel):
    """
    Represents a student requiring Praktikum placement.
    Business Logic: Students have program type, subject preferences,
    and geographical constraints for placement.
    """
    PROGRAM_CHOICES = [
        ('GS', 'Grundschule'),
        ('MS', 'Mittelschule'),
    ]
    
    PLACEMENT_STATUS_CHOICES = [
        ('UNPLACED', 'Unplaced'),
        ('IN_REVIEW', 'In Review'),
        ('PLACED', 'Placed'),
        ('COMPLETED', 'Completed'),
    ]
    
    # Basic Information
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Program
    program = models.CharField(
        max_length=2,
        choices=PROGRAM_CHOICES,
        help_text="GS or MS program"
    )
    major = models.CharField(max_length=100, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
    
    # Primary Subject
    primary_subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        related_name='primary_students',
        help_text="Student's primary teaching subject"
    )
    
    # Additional Subjects
    additional_subjects = models.ManyToManyField(
        Subject,
        related_name='students',
        blank=True,
        help_text="Additional subjects the student is qualified to teach"
    )
    
    # Geographical Information
    home_address = models.TextField(blank=True)
    home_region = models.CharField(
        max_length=100,
        blank=True,
        help_text="Region for Heimatnah matching"
    )
    preferred_zone = models.CharField(
        max_length=10,
        blank=True,
        help_text="Preferred distance zone"
    )
    
    # Status
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['program']),
        ]
    
    def __str__(self):
        return f"{self.student_id} - {self.last_name}, {self.first_name}"


class StudentPraktikumPreference(TimeStampedModel):
    """
    Tracks which Praktikum types a student needs/prefers.
    Business Logic: Students declare which Praktika they want to complete.
    """
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='praktikum_preferences'
    )
    praktikum_type = models.ForeignKey(
        PraktikumType,
        on_delete=models.CASCADE,
        related_name='student_preferences'
    )
    
    # Preferred subjects for this Praktikum
    preferred_subjects = models.ManyToManyField(
        Subject,
        related_name='preferred_by_students',
        blank=True
    )
    
    # Preferred schools/regions
    preferred_schools = models.ManyToManyField(
        School,
        related_name='preferred_by_students',
        blank=True
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Student.PLACEMENT_STATUS_CHOICES,
        default='UNPLACED'
    )
    
    # Timing preference
    availability_note = models.TextField(
        blank=True,
        help_text="e.g., 'I.d.R. im Herbst' for PDP I"
    )
    
    class Meta:
        verbose_name = "Student Praktikum Preference"
        verbose_name_plural = "Student Praktikum Preferences"
        unique_together = ['student', 'praktikum_type']
    
    def __str__(self):
        return f"{self.student} - {self.praktikum_type}"
