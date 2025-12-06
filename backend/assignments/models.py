from django.db import models
from subjects.models import TimeStampedModel, Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School


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
