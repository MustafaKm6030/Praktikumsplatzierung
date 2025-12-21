import pandas as pd
from django.db import transaction
from django.db.models import Q
from .models import PraktikumsLehrkraft
from schools.models import School
from subjects.models import Subject, PraktikumType


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
    Business Logic: Imports PLs from an Excel file (.xlsx) using pandas.
    Includes robust 'End of Data' detection based on row structure.
    """
    import pandas as pd
    from django.db import transaction
    from schools.models import School
    from subjects.models import Subject, PraktikumType

    print("--- STARTING EXCEL IMPORT ---")

    created_count = 0
    updated_count = 0
    errors = []
    consecutive_empty_rows = 0

    try:
        # 1. Read Excel
        df = pd.read_excel(file_obj, engine="openpyxl")

        # Clean headers
        df.columns = (
            df.columns.astype(str).str.replace("\n", "", regex=False).str.strip()
        )
        print(f"Found Columns: {df.columns.tolist()}")

        # 2. Cache DB objects
        schools_cache = {school.name: school for school in School.objects.all()}
        subjects_cache = {subject.code: subject for subject in Subject.objects.all()}
        ptypes_cache = {pt.code: pt for pt in PraktikumType.objects.all()}

        SUBJECT_COLUMNS = [col for col in df.columns if col in subjects_cache]

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # --- ROBUST END-OF-DATA CHECK ---
                    raw_last_name = row.get("Nachname")
                    raw_first_name = row.get(
                        "Vor-name"
                    )  # Check exact header name from your logs!

                    last_name = str(raw_last_name).strip()
                    first_name = str(raw_first_name).strip()

                    # Handle "nan" string conversion from pandas
                    if last_name.lower() == "nan":
                        last_name = ""
                    if first_name.lower() == "nan":
                        first_name = ""

                    # 1. Check for Empty Row
                    if not last_name:
                        consecutive_empty_rows += 1
                        if consecutive_empty_rows >= 5:
                            print(
                                f"Row {index + 2}: 5 consecutive empty rows. Stopping."
                            )
                            break
                        continue  # Skip this empty row

                    # 2. Reset empty counter since we found a non-empty Last Name
                    consecutive_empty_rows = 0

                    # 3. CRITICAL STOP CONDITION: Text in Last Name, but NO First Name
                    # This catches "Legende:", "Schuljahr...", notes, etc.
                    # A valid teacher MUST have a first name.
                    if last_name and not first_name:
                        print(
                            f"Row {index + 2}: Found text '{last_name}' but no First Name. Assuming End of Data."
                        )
                        break
                    # --------------------------------

                    # --- School Logic ---
                    school_name_raw = str(row.get("Schulart", "")).strip()
                    school_ort_raw = str(row.get("Schulort", "")).strip()

                    if school_name_raw and school_ort_raw:
                        school_unique_name = f"{school_name_raw} {school_ort_raw}"
                    elif school_name_raw:
                        school_unique_name = school_name_raw
                    else:
                        print(f"Row {index + 2}: No school data. Skipping.")
                        continue

                    # --- NEW: Extract Real Geo-Data ---
                    # 1. Zone (Handle floats like 1.0)
                    try:
                        raw_zone = row.get("Zone 1")
                        zone_val = int(float(raw_zone)) if pd.notna(raw_zone) else 1
                    except (ValueError, TypeError):
                        zone_val = 1  # Fallback

                    # 2. Distance (Handle floats/ints)
                    try:
                        raw_dist = row.get("Entfern-ungs km")
                        dist_val = int(float(raw_dist)) if pd.notna(raw_dist) else None
                    except (ValueError, TypeError):
                        dist_val = None

                    # 3. ÖPNV Code (String)
                    raw_opnv = str(row.get("ÖPNV", "")).strip()
                    # Only accept valid codes, otherwise blank
                    opnv_val = raw_opnv if raw_opnv in ["4a", "4b"] else ""

                    # --- CREATE OR UPDATE SCHOOL ---
                    school_type_guess = (
                        "GS" if "grund" in school_name_raw.lower() else "MS"
                    )

                    # We use update_or_create to fix existing schools with bad defaults
                    school, _ = School.objects.update_or_create(
                        name=school_unique_name,
                        defaults={
                            "school_type": school_type_guess,
                            "city": school_ort_raw,
                            "district": str(
                                row.get("Schul-amt", "")
                            ).strip(),  # Ensure district is set
                            "zone": zone_val,
                            "opnv_code": opnv_val,
                            "distance_km": dist_val,
                            "is_active": True,
                        },
                    )
                    schools_cache[school_unique_name] = school

                    # --- Data Extraction ---
                    # Use index to ensure email uniqueness even for duplicate names
                    email = f"{first_name.lower()}.{last_name.lower()}.{index}@placeholder.local"
                    schulamt_val = str(row.get("Schul-amt", "")).strip()
                    program_raw = str(row.get("LA", "GS")).strip()
                    program = program_raw[:2] if len(program_raw) >= 2 else "GS"
                    raw_anre = row.get("Anre-Std.SJ 25_26")
                    if pd.isna(raw_anre):
                        raw_anre = row.get("Anre-Std. SJ 25_26")
                    try:
                        anre_std = float(raw_anre) if pd.notna(raw_anre) else 1.0
                    except (ValueError, TypeError):
                        anre_std = 1.0

                    pl_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "school": school,
                        "program": program,
                        "anrechnungsstunden": anre_std,
                        "preferred_praktika_raw": str(
                            row.get("bevorzugte Praktika der PL", "")
                        ),
                        "schulamt": schulamt_val,
                        "current_year_notes": str(
                            row.get("Besonderheiten SJ 25_26", "")
                        ),
                        "is_active": str(row.get("Status", "ok")).lower() == "ok",
                    }

                    pl, created = PraktikumsLehrkraft.objects.update_or_create(
                        email=email, defaults=pl_data
                    )

                    # --- M2M Relations ---
                    # Subjects
                    pl_subjects = []
                    for sub_code in SUBJECT_COLUMNS:
                        val = str(row.get(sub_code, "")).strip().lower()
                        if val == "x":
                            pl_subjects.append(subjects_cache[sub_code])
                    pl.available_subjects.set(pl_subjects)

                    # Praktikum Types
                    pl_ptypes = []
                    pref_text = pl.preferred_praktika_raw.upper()
                    for ptype_code, ptype_obj in ptypes_cache.items():
                        search_term = ptype_code.replace("_", " ")
                        if search_term in pref_text:
                            pl_ptypes.append(ptype_obj)
                    pl.available_praktikum_types.set(pl_ptypes)

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

    except Exception as e:
        import traceback

        traceback.print_exc()
        errors.append(f"Critical Error Reading Excel File: {str(e)}")

    return {"created": created_count, "updated": updated_count, "errors": errors}


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

    pls = (
        PraktikumsLehrkraft.objects.all()
        .select_related("school", "main_subject")
        .prefetch_related("available_praktikum_types", "available_subjects")
        .order_by("last_name", "first_name")
    )
    for pl in pls:
        writer.writerow(_get_pl_row(pl))

    return output.getvalue()


def _get_pl_csv_headers():
    """Helper: Returns CSV header row for PLs."""
    return [
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "school_name",
        "program",
        "main_subject_code",
        "schulamt",
        "anrechnungsstunden",
        "capacity",
        "praktikum_types",
        "available_subjects",
        "preferred_praktika_raw",
        "current_year_notes",
        "is_active",
        "notes",
        "created_at",
        "updated_at",
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
