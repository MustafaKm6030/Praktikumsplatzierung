from django.db import models
from subjects.models import TimeStampedModel, Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from students.models import Student


class Assignment(TimeStampedModel):
    """
    Represents a finalized assignment slot for a mentor.
    This is the OUTPUT of the solver.
    """

    mentor = models.ForeignKey(
        PraktikumsLehrkraft, on_delete=models.CASCADE, related_name="assignments"
    )
    practicum_type = models.ForeignKey(PraktikumType, on_delete=models.PROTECT)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        null=True,  # Can be null for PDP I / II (generic)
        blank=True,
    )
    school = models.ForeignKey(School, on_delete=models.PROTECT)

    # Stores the academic year (e.g., "2025/26")
    academic_year = models.CharField(max_length=20, default="2025/26")

    class Meta:
        unique_together = ["mentor", "practicum_type", "subject", "academic_year"]

    def __str__(self):
        sbj = self.subject.code if self.subject else "N/A"
        return f"{self.mentor.last_name} - {self.practicum_type.code} ({sbj})"


class StudentAssignment(TimeStampedModel):
    """
    Represents a student's assignment to a mentor for a specific practicum.
    Tracks the relationship between students and their praktikum placements.
    """
    
    ASSIGNMENT_STATUS_CHOICES = [
        ("ASSIGNED", "Assigned"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="praktikum_assignments"
    )
    mentor = models.ForeignKey(
        PraktikumsLehrkraft,
        on_delete=models.CASCADE,
        related_name="student_assignments"
    )
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    practicum_type = models.ForeignKey(PraktikumType, on_delete=models.PROTECT)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Subject for this practicum (required for SFP/ZSP)"
    )
    
    assignment_status = models.CharField(
        max_length=20,
        choices=ASSIGNMENT_STATUS_CHOICES,
        default="ASSIGNED"
    )
    assignment_date = models.DateField(auto_now_add=True)
    academic_year = models.CharField(max_length=20, default="2025/26")
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Student Assignment"
        verbose_name_plural = "Student Assignments"
        unique_together = ["student", "practicum_type", "academic_year"]
        indexes = [
            models.Index(fields=["student", "practicum_type"]),
            models.Index(fields=["mentor", "practicum_type"]),
            models.Index(fields=["assignment_status"]),
        ]
    
    def __str__(self):
        return f"{self.student.student_id} → {self.mentor.last_name} ({self.practicum_type.code})"
