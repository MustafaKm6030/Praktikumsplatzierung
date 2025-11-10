from django.db import models


# ==================== BASE MODEL ====================

class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating 
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ==================== PRAKTIKUM TYPE MODEL ====================

class PraktikumType(TimeStampedModel):
    """
    Represents types of internships: PDP I, PDP II, SFP, ZSP.
    Business Logic: Each type has different rules for matching
    (e.g., Block vs Wednesday, distance requirements).
    """
    PRAKTIKUM_CHOICES = [
        ('PDP_I', 'PDP I (Pädagogisch-didaktisches Praktikum I)'),
        ('PDP_II', 'PDP II (Pädagogisch-didaktisches Praktikum II)'),
        ('SFP', 'SFP (Studienbegleitendes Fachpraktikum)'),
        ('ZSP', 'ZSP (Zusätzliches studienbegleitendes Praktikum)'),
    ]
    
    code = models.CharField(
        max_length=10, 
        choices=PRAKTIKUM_CHOICES, 
        unique=True
    )
    name = models.CharField(max_length=100)
    is_block_praktikum = models.BooleanField(
        default=False,
        help_text="True for PDP I/II (allow Zone 3), False for SFP/ZSP (Zone 1/2 only)"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Praktikum Type"
        verbose_name_plural = "Praktikum Types"
        ordering = ['code']
    
    def __str__(self):
        return self.get_code_display()


# ==================== SUBJECT MODEL ====================

class Subject(TimeStampedModel):
    """
    Represents teaching subjects (Deutsch, Mathematik, etc.).
    Used for matching PLs to students based on subject requirements.
    """
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    subject_group = models.CharField(
        max_length=50,
        blank=True,
        help_text="Subject grouping for GS/MS matching rules"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
