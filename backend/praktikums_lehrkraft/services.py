from django.db.models import Q, Count
from .models import PraktikumsLehrkraft


def get_pls_by_school(school_id):
    """
    Returns all PLs for a specific school.
    Business Logic: Filter active PLs by school for assignment.
    """
    return PraktikumsLehrkraft.objects.filter(
        school_id=school_id, is_active=True
    ).select_related("school", "main_subject")


def get_pls_by_program(program):
    """
    Returns all PLs for a specific program (GS or MS).
    Business Logic: Filter PLs by program for student matching.
    """
    return PraktikumsLehrkraft.objects.filter(
        program=program, is_active=True
    ).select_related("school", "main_subject")


def search_pls(search_term):
    """Search PLs by name, school name, or PL ID."""
    query = (
        Q(first_name__icontains=search_term)
        | Q(last_name__icontains=search_term)
        | Q(email__icontains=search_term)
        | Q(school__name__icontains=search_term)
    )

    if search_term.isdigit():
        query |= Q(id=int(search_term))

    return (
        PraktikumsLehrkraft.objects.filter(query)
        .select_related("school", "main_subject")
        .distinct()
    )


def get_available_pls_for_praktikum(praktikum_type_id, subject_id=None):
    """
    Returns PLs available for a specific praktikum type and optionally subject.
    """
    queryset = PraktikumsLehrkraft.objects.filter(
        is_active=True, available_praktikum_types__id=praktikum_type_id
    )

    # Optional subject filter: PL must have this subject in their 'x' list
    if subject_id:
        queryset = queryset.filter(available_subjects__id=subject_id)

    return queryset.select_related("school", "main_subject").distinct()


def get_pl_capacity_info(pl_id):
    """
    Returns capacity information for a PL based on Anrechnungsstunden.
    """
    pl = PraktikumsLehrkraft.objects.get(id=pl_id)
    return {
        "anrechnungsstunden": float(pl.anrechnungsstunden),
        "total_capacity": pl.capacity,
        "current_assignments": 0,  # Placeholder for future assignment count
        "remaining_capacity": pl.capacity,  # Placeholder
    }


def get_pls_by_subject(subject_id, praktikum_type_id=None):
    """
    Returns PLs who can teach a specific subject (have 'x' in that column).
    """
    return (
        PraktikumsLehrkraft.objects.filter(
            available_subjects__id=subject_id, is_active=True
        )
        .select_related("school", "main_subject")
        .distinct()
    )


def import_pls_from_csv(file_obj):
    """
    Business Logic: Imports PLs from CSV file.
    Creates or updates PLs based on email as unique identifier.
    """
    import csv
    import io
    from django.db import transaction
    from schools.models import School
    from subjects.models import Subject, PraktikumType

    decoded_file = file_obj.read().decode("utf-8")
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)

    created_count = 0
    updated_count = 0
    errors = []

    # Cache for lookups
    schools_cache = {school.name: school for school in School.objects.all()}
    subjects_cache = {subject.code: subject for subject in Subject.objects.all()}

    with transaction.atomic():
        for row_num, row in enumerate(reader, start=2):
            try:
                email = row.get("email", "").strip()
                if not email:
                    errors.append(f"Row {row_num}: email is required")
                    continue

                pl_data = _build_pl_data(row, schools_cache, subjects_cache)
                if "error" in pl_data:
                    errors.append(f"Row {row_num}: {pl_data['error']}")
                    continue

                # Extract many-to-many fields
                praktikum_types = pl_data.pop("praktikum_types", [])
                available_subjects = pl_data.pop("available_subjects", [])

                pl, created = PraktikumsLehrkraft.objects.update_or_create(
                    email=email, defaults=pl_data
                )

                # Update many-to-many relationships
                if praktikum_types:
                    pl.available_praktikum_types.set(praktikum_types)
                if available_subjects:
                    pl.available_subjects.set(available_subjects)

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

    return {"created": created_count, "updated": updated_count, "errors": errors}


def _build_pl_data(row, schools_cache, subjects_cache):
    """Helper: Builds PL data dictionary from CSV row."""
    from subjects.models import PraktikumType

    school_name = row.get("school_name", "").strip()
    school = schools_cache.get(school_name)
    if not school and school_name:
        return {"error": f"School '{school_name}' not found"}

    main_subject_code = row.get("main_subject_code", "").strip()
    main_subject = subjects_cache.get(main_subject_code) if main_subject_code else None

    # Parse praktikum types
    praktikum_types = _parse_praktikum_types(row.get("praktikum_types", ""))

    # Parse available subjects
    available_subjects = _parse_subjects(row.get("available_subjects", ""), subjects_cache)

    return {
        "first_name": row.get("first_name", ""),
        "last_name": row.get("last_name", ""),
        "phone": row.get("phone", ""),
        "school": school,
        "program": row.get("program", "GS"),
        "main_subject": main_subject,
        "schulamt": row.get("schulamt", ""),
        "anrechnungsstunden": float(row.get("anrechnungsstunden", 0)) if row.get("anrechnungsstunden") else 0,
        "preferred_praktika_raw": row.get("preferred_praktika_raw", ""),
        "current_year_notes": row.get("current_year_notes", ""),
        "is_active": row.get("is_active", "true").lower() == "true",
        "notes": row.get("notes", ""),
        "praktikum_types": praktikum_types,
        "available_subjects": available_subjects,
    }


def _parse_praktikum_types(types_str):
    """Helper: Parses praktikum types from comma-separated string."""
    from subjects.models import PraktikumType

    if not types_str:
        return []

    codes = [code.strip() for code in types_str.split(",")]
    return list(PraktikumType.objects.filter(code__in=codes))


def _parse_subjects(subjects_str, subjects_cache):
    """Helper: Parses subjects from comma-separated string."""
    if not subjects_str:
        return []

    codes = [code.strip() for code in subjects_str.split(",")]
    return [subjects_cache[code] for code in codes if code in subjects_cache]


def export_pls_to_csv():
    """
    Business Logic: Exports all PLs to CSV format.
    Returns CSV string content ready for download.
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(_get_pl_csv_headers())

    pls = PraktikumsLehrkraft.objects.all().select_related("school", "main_subject").prefetch_related("available_praktikum_types", "available_subjects").order_by("last_name", "first_name")
    for pl in pls:
        writer.writerow(_get_pl_row(pl))

    return output.getvalue()


def _get_pl_csv_headers():
    """Helper: Returns CSV header row for PLs."""
    return [
        "id", "first_name", "last_name", "email", "phone",
        "school_name", "program", "main_subject_code",
        "schulamt", "anrechnungsstunden", "capacity",
        "praktikum_types", "available_subjects",
        "preferred_praktika_raw", "current_year_notes",
        "is_active", "notes", "created_at", "updated_at",
    ]


def _get_pl_row(pl):
    """Helper: Formats a PL instance as CSV row."""
    praktikum_types = ",".join([pt.code for pt in pl.available_praktikum_types.all()])
    available_subjects = ",".join([s.code for s in pl.available_subjects.all()])

    return [
        pl.id,
        pl.first_name,
        pl.last_name,
        pl.email,
        pl.phone or "",
        pl.school.name if pl.school else "",
        pl.program,
        pl.main_subject.code if pl.main_subject else "",
        pl.schulamt or "",
        pl.anrechnungsstunden,
        pl.capacity,
        praktikum_types,
        available_subjects,
        pl.preferred_praktika_raw or "",
        pl.current_year_notes or "",
        pl.is_active,
        pl.notes or "",
        pl.created_at.isoformat() if pl.created_at else "",
        pl.updated_at.isoformat() if pl.updated_at else "",
    ]
