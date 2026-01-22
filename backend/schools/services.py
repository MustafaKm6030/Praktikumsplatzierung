import time
import csv
import io
import openpyxl 
from io import BytesIO  
from django.db import transaction
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from .models import School
from praktikums_lehrkraft.models import PraktikumsLehrkraft


class GeocodingConnectionError(Exception):
    pass


def get_schools_by_zone(zone):
    return School.objects.filter(zone=zone, is_active=True)


def get_schools_by_type(school_type):
    return School.objects.filter(school_type=school_type, is_active=True)


def get_school_capacity(school_id: int) -> dict:
    """
    Calculates the dynamic capacity of a school by summing the capacities
    of all active mentors assigned to it.
    """
    active_pls = PraktikumsLehrkraft.objects.filter(school_id=school_id, is_active=True)

    total_capacity = 0
    for pl in active_pls:
        total_capacity += pl.capacity

    return {
        "school_id": school_id,
        "active_mentors": active_pls.count(),
        "total_available_slots": total_capacity,
    }


def get_schools_for_wednesday_praktika():
    """
    Returns all schools that are logistically feasible for Wednesday internships (SFP/ZSP).
    """
    return School.objects.filter(
        zone__in=[1, 2], opnv_code__in=["4a", "4b"], is_active=True
    )


def get_reachable_schools(praktikum_type_code: str):
    """
    Returns a queryset of schools that are logistically reachable for a given
    internship type, based on Zone and ÖPNV rules.
    """
    # Rule for Block Internships (PDP I, PDP II)
    if praktikum_type_code in ["PDP_I", "PDP_II"]:
        return School.objects.filter(is_active=True)

    # Rule for Wednesday Internships (SFP, ZSP)
    if praktikum_type_code in ["SFP", "ZSP"]:
        return School.objects.filter(
            is_active=True,
            zone__in=[1, 2],
        )

    # For any other or unknown type, return an empty queryset
    return School.objects.none()


def import_schools_from_csv(file_obj):
    """
    Business Logic: Imports schools from CSV file.
    Creates or updates schools based on name as unique identifier.
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
                name = row.get("name", "").strip()
                if not name:
                    errors.append(f"Row {row_num}: name is required")
                    continue

                school_data = _build_school_data(row)
                school, created = School.objects.update_or_create(
                    name=name, defaults=school_data
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

    return {"created": created_count, "updated": updated_count, "errors": errors}


def _build_school_data(row):
    """Helper: Builds school data dictionary from CSV row."""
    return {
        "school_type": row.get("school_type", "GS"),
        "city": row.get("city", ""),
        "district": row.get("district", ""),
        "zone": int(row.get("zone", 1)) if row.get("zone") else 1,
        "opnv_code": row.get("opnv_code", ""),
        "distance_km": float(row.get("distance_km", 0))
        if row.get("distance_km")
        else 0,
        "is_active": row.get("is_active", "true").lower() == "true",
        "notes": row.get("notes", ""),
        "latitude": float(row.get("latitude", 0)) if row.get("latitude") else None,
        "longitude": float(row.get("longitude", 0)) if row.get("longitude") else None,
    }

# ---------------------------------------------------------
# EXCEL EXPORT LOGIC
# ---------------------------------------------------------

def export_schools_to_excel():
    """
    Generates an Excel file containing all schools.
    Returns: BytesIO buffer containing the .xlsx file
    """
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Schools'

    # Define headers
    headers = [
        'ID', 'Name', 'Type', 'City', 'District', 'Zone', 
        'Opnv Code', 'Distance (km)', 'Active', 'Notes', 
        'Latitude', 'Longitude'
    ]
    worksheet.append(headers)

    # Fetch data
    schools = School.objects.all().order_by('name')

    for school in schools:
        row = [
            school.id,
            school.name,
            school.school_type,
            school.city,
            school.district,
            school.zone,
            school.opnv_code,
            school.distance_km,
            'Yes' if school.is_active else 'No',
            school.notes,
            school.latitude,
            school.longitude
        ]
        worksheet.append(row)

    # Save to buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------
# GEOCODING LOGIC
# ---------------------------------------------------------

def geocode_school(school):
    """
    Attempts to find lat/lon for a single school object using geopy.
    """
    should_stop, result = _check_geocoding_prerequisites(school)
    if should_stop:
        return result

    try:
        geolocator = Nominatim(user_agent="uni-passau-praktikumsamt-app/1.0")
        query = f"{school.name}, {school.city}, Germany"
        print(f"[GEOCODE] Querying address: {query}")

        location = geolocator.geocode(query, timeout=10)
        return _process_geocoding_result(school, location)

    except Exception as e:
        return _handle_geocoding_exception(school, e)


def _check_geocoding_prerequisites(school):
    """Returns (Should_Stop_Bool, Return_Value_Bool)"""
    if not school or not school.name or not school.city:
        print(f"[GEOCODE] Missing required fields: {school.name}, {school.city}")
        return True, False

    if school.geocoding_status == "success":
        return True, True

    if school.latitude and school.longitude:
        _update_school_status(school, "not_needed")
        return True, True

    return False, None


def _process_geocoding_result(school, location):
    if location:
        school.latitude = location.latitude
        school.longitude = location.longitude
        _update_school_status(school, "success", fields=["latitude", "longitude"])
        return True

    print("[GEOCODE] FAILED - No location found")
    _update_school_status(school, "failed")
    return False


def _handle_geocoding_exception(school, e):
    error_str = str(e).lower()
    is_conn_keyword = any(k in error_str for k in ["connection", "network", "timeout"])

    if isinstance(e, (GeocoderTimedOut, GeocoderServiceError)):
        _update_school_status(school, "failed")
        raise GeocodingConnectionError(f"Service error: {e}")

    if isinstance(e, OSError) or is_conn_keyword:
        _update_school_status(school, "pending")
        raise GeocodingConnectionError(f"Connection error: {e}")

    print(f"[GEOCODE] ERROR - Unexpected: {e}")
    _update_school_status(school, "failed")
    return False


def _update_school_status(school, status, fields=None):
    """Helper to update status and save specific fields."""
    school.geocoding_status = status
    update_fields = ["geocoding_status"] + (fields or [])
    school.save(update_fields=update_fields)


def geocode_schools_batch(schools_queryset=None, delay_between_requests=1):
    """
    Geocodes multiple schools in batch with rate limiting.
    """
    if schools_queryset is None:
        schools_queryset = School.objects.filter(
            geocoding_status="pending", latitude__isnull=True, longitude__isnull=True
        )

    stats = {
        "total": schools_queryset.count(),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "connection_error": None,
    }

    for school in schools_queryset:
        try:
            result = geocode_school(school)
            if result:
                stats["success"] += 1
            else:
                stats["failed"] += 1
        except GeocodingConnectionError as e:
            stats["connection_error"] = str(e)
            print(f"[GEOCODE] Batch stopped due to connection error: {e}")
            break

        time.sleep(delay_between_requests)

    return stats