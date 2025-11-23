import csv
import io
from datetime import datetime
from django.db import transaction
from .models import Student


def get_students_by_program(program):
    return Student.objects.filter(program=program)


def get_students_by_region(region):
    return Student.objects.filter(home_region=region)


def _parse_date(date_str):
    """Helper to parse YYYY-MM-DD string to date object, handling empty strings."""
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def import_students_from_csv(file_obj):
    """
    Imports students from a CSV file.
    Updated to handle the new Student model fields.
    """
    decoded_file = file_obj.read().decode("utf-8")
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)

    created_count = 0
    updated_count = 0
    errors = []

    with transaction.atomic():
        for row_num, row in enumerate(reader, start=2):
            try:
                student_id = row.get("student_id", "").strip()
                if not student_id:
                    errors.append(f"Row {row_num}: student_id is required")
                    continue

                email = row.get("email", "").strip()
                if not email:
                    errors.append(f"Row {row_num}: email is required")
                    continue

                # Map CSV columns to New Model Fields
                student_data = {
                    "student_id": student_id,
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "email": email,
                    "phone": row.get("phone", ""),
                    "program": row.get("program", "GS"),
                    "major": row.get("major", ""),
                    # Location Fields
                    "home_address": row.get("home_address", ""),
                    "semester_address": row.get("semester_address", ""),  # NEW
                    "home_region": row.get("home_region", ""),
                    "preferred_zone": row.get("preferred_zone", ""),
                    # Completion Checklist (Parsing Dates)
                    "pdp1_completed_date": _parse_date(row.get("pdp1_completed_date")),
                    "pdp2_completed_date": _parse_date(row.get("pdp2_completed_date")),
                    "sfp_completed_date": _parse_date(row.get("sfp_completed_date")),
                    "zsp_completed_date": _parse_date(row.get("zsp_completed_date")),
                    "placement_status": row.get("placement_status", "UNPLACED"),
                    "notes": row.get("notes", ""),
                }

                # Handle Enrollment Date
                student_data["enrollment_date"] = _parse_date(
                    row.get("enrollment_date")
                )

                # Update or Create logic
                student, created = Student.objects.update_or_create(
                    student_id=student_id, defaults=student_data
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

    return {"created": created_count, "updated": updated_count, "errors": errors}


def export_students_to_csv():
    """
    Exports students to CSV.
    Updated to include new Student model fields.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Updated Header Row
    writer.writerow(
        [
            "id",
            "student_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "program",
            "major",
            "enrollment_date",
            "primary_subject_id",
            "home_address",
            "semester_address",
            "home_region",
            "preferred_zone",  # Location
            "pdp1_completed_date",
            "pdp2_completed_date",
            "sfp_completed_date",
            "zsp_completed_date",  # Checklist
            "placement_status",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    students = Student.objects.all().order_by("last_name", "first_name")
    for student in students:
        writer.writerow(
            [
                student.id,
                student.student_id,
                student.first_name,
                student.last_name,
                student.email,
                student.phone,
                student.program,
                student.major,
                student.enrollment_date.isoformat() if student.enrollment_date else "",
                student.primary_subject_id or "",
                student.home_address,
                student.semester_address,  # NEW
                student.home_region,
                student.preferred_zone,
                # Completion Dates
                student.pdp1_completed_date.isoformat()
                if student.pdp1_completed_date
                else "",
                student.pdp2_completed_date.isoformat()
                if student.pdp2_completed_date
                else "",
                student.sfp_completed_date.isoformat()
                if student.sfp_completed_date
                else "",
                student.zsp_completed_date.isoformat()
                if student.zsp_completed_date
                else "",
                student.placement_status,
                student.notes,
                student.created_at.isoformat() if student.created_at else "",
                student.updated_at.isoformat() if student.updated_at else "",
            ]
        )

    return output.getvalue()
