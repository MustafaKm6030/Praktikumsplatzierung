"""
Shared factory helpers for creating test data in assignment tests.
"""
from datetime import date
from students.models import Student
from subjects.models import Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School


def create_test_subjects():
    """Create standard test subjects."""
    return {
        "math": Subject.objects.create(name="Mathematik", code="MA", is_active=True),
        "german": Subject.objects.create(name="Deutsch", code="D", is_active=True),
        "hsu": Subject.objects.create(
            name="Heimat- und Sachunterricht", code="HSU", is_active=True
        ),
    }


def create_test_praktikum_types():
    """Create standard test praktikum types."""
    return {
        "pdp1": PraktikumType.objects.create(
            code="PDP_I", name="PDP I", is_block_praktikum=True, is_active=True
        ),
        "pdp2": PraktikumType.objects.create(
            code="PDP_II", name="PDP II", is_block_praktikum=True, is_active=True
        ),
        "sfp": PraktikumType.objects.create(
            code="SFP", name="SFP", is_block_praktikum=False, is_active=True
        ),
        "zsp": PraktikumType.objects.create(
            code="ZSP", name="ZSP", is_block_praktikum=False, is_active=True
        ),
    }


def create_test_school(name, school_type, zone=1, opnv_code="4a"):
    """Create a test school with specified parameters."""
    return School.objects.create(
        name=name,
        school_type=school_type,
        city="Passau",
        district="Passau-Land",
        zone=zone,
        opnv_code=opnv_code,
        is_active=True,
    )


def create_test_pl(first_name, email, school, program, anrechnungsstunden=1.0):
    """Create a test PraktikumsLehrkraft."""
    return PraktikumsLehrkraft.objects.create(
        first_name=first_name,
        last_name="Test",
        email=email,
        school=school,
        program=program,
        is_active=True,
        anrechnungsstunden=anrechnungsstunden,
    )


def create_test_student(student_id, email, program, **kwargs):
    """Create a test student with specified completion dates."""
    defaults = {
        "first_name": f"S{student_id}",
        "last_name": "Test",
        "placement_status": "UNPLACED",
    }
    defaults.update(kwargs)
    return Student.objects.create(
        student_id=student_id, email=email, program=program, **defaults
    )

