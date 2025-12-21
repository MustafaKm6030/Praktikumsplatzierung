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


def _extract_school_data(row):
    """Parses school-related fields from a row."""
    name_raw = str(row.get("Schulart", "")).strip()
    ort_raw = str(row.get("Schulort", "")).strip()

    # Zone, Distance, and ÖPNV parsing
    try:
        raw_z, raw_d = row.get("Zone 1"), row.get("Entfern-ungs km")
        zone = int(float(raw_z)) if pd.notna(raw_z) else 1
        dist = int(float(raw_d)) if pd.notna(raw_d) else None
    except (ValueError, TypeError):
        zone, dist = 1, None

    opnv = str(row.get("ÖPNV", "")).strip()
    return {
        "unique_name": f"{name_raw} {ort_raw}".strip() or name_raw,
        "city": ort_raw,
        "zone": zone,
        "dist": dist,
        "opnv": opnv if opnv in ["4a", "4b"] else "",
        "type": "GS" if "grund" in name_raw.lower() else "MS",
    }


def _save_pl_data(index, row, school, first_name, last_name):
    """Prepares the dictionary for PraktikumsLehrkraft."""
    # 1. Flatten numeric parsing using pd.to_numeric to avoid try/except blocks
    raw_anre = row.get("Anre-Std.SJ 25_26") or row.get("Anre-Std. SJ 25_26")
    anre_std = pd.to_numeric(raw_anre, errors="coerce")
    if pd.isna(anre_std):
        anre_std = 1.0

    # 2. Clean strings and handle slicing in-place
    prog = str(row.get("LA", "GS")).strip()
    email = f"{first_name.lower()}.{last_name.lower()}.{index}@placeholder.local"

    # 3. Return the flat structure
    return {
        "email": email,
        "defaults": {
            "first_name": first_name,
            "last_name": last_name,
            "school": school,
            "program": prog[:2] if len(prog) >= 2 else "GS",
            "anrechnungsstunden": float(anre_std),
            "preferred_praktika_raw": str(row.get("bevorzugte Praktika der PL", "")),
            "schulamt": str(row.get("Schul-amt", "")).strip(),
            "current_year_notes": str(row.get("Besonderheiten SJ 25_26", "")),
            "is_active": str(row.get("Status", "ok")).lower() == "ok",
        },
    }


# --- MAIN FUNCTION (Now ~50 lines) ---


def import_pls_from_csv(file_obj):
    print("--- STARTING EXCEL IMPORT ---")
    created_count, updated_count, errors, consecutive_empty_rows = 0, 0, [], 0

    try:
        df = pd.read_excel(file_obj, engine="openpyxl")
        df.columns = (
            df.columns.astype(str).str.replace("\n", "", regex=False).str.strip()
        )

        subjects_cache = {s.code: s for s in Subject.objects.all()}
        ptypes_cache = {pt.code: pt for pt in PraktikumType.objects.all()}
        SUB_COLS = [col for col in df.columns if col in subjects_cache]

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    f_name = str(row.get("Vor-name", "")).strip().replace("nan", "")
                    l_name = str(row.get("Nachname", "")).strip().replace("nan", "")

                    if not l_name:
                        consecutive_empty_rows += 1
                        if consecutive_empty_rows >= 5:
                            break
                        continue

                    if l_name and not f_name:
                        break  # End of data check
                    consecutive_empty_rows = 0

                    # Process School
                    s_data = _extract_school_data(row)
                    if not s_data["unique_name"]:
                        continue

                    school, _ = School.objects.update_or_create(
                        name=s_data["unique_name"],
                        defaults={
                            "school_type": s_data["type"],
                            "city": s_data["city"],
                            "district": str(row.get("Schul-amt", "")).strip(),
                            "zone": s_data["zone"],
                            "opnv_code": s_data["opnv"],
                            "distance_km": s_data["dist"],
                            "is_active": True,
                        },
                    )

                    # Process Teacher
                    pl_info = _save_pl_data(index, row, school, f_name, l_name)
                    pl, created = PraktikumsLehrkraft.objects.update_or_create(
                        email=pl_info["email"], defaults=pl_info["defaults"]
                    )

                    # M2M Relations
                    subs = [
                        subjects_cache[c]
                        for c in SUB_COLS
                        if str(row.get(c, "")).strip().lower() == "x"
                    ]
                    pl.available_subjects.set(subs)

                    pref = pl.preferred_praktika_raw.upper()
                    ptypes = [
                        obj
                        for c, obj in ptypes_cache.items()
                        if c.replace("_", " ") in pref
                    ]
                    pl.available_praktikum_types.set(ptypes)

                    created_count += 1 if created else 0
                    updated_count += 1 if not created else 0

                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

    except Exception as e:
        errors.append(f"Critical Error: {str(e)}")

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
