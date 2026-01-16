from .models import School
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time


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

    Business Logic (from slides):
    - Must be in Zone 1 or Zone 2.
    - Must have a valid ÖPNV code ('4a' or '4b').
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
    # All active schools in any zone are considered reachable.
    # The 'heimatnah' (close to home) logic is a soft constraint handled later by the solver.
    if praktikum_type_code in ["PDP_I", "PDP_II"]:
        return School.objects.filter(is_active=True)

    # Rule for Wednesday Internships (SFP, ZSP)
    # These have strict constraints based on the project briefing.
    if praktikum_type_code in ["SFP", "ZSP"]:
        return School.objects.filter(
            is_active=True,
            zone__in=[1, 2],
            # opnv_code__in=["4a", "4b"]
        )

    # For any other or unknown type, return an empty queryset
    return School.objects.none()


def import_schools_from_csv(file_obj):
    """
    Business Logic: Imports schools from CSV file.
    Creates or updates schools based on name as unique identifier.
    """
    import csv
    import io
    from django.db import transaction

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


def export_schools_to_csv():
    """
    Business Logic: Exports all schools to CSV format.
    Returns CSV string content ready for download.
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(_get_school_csv_headers())

    schools = School.objects.all().order_by("name")
    for school in schools:
        writer.writerow(_get_school_row(school))

    return output.getvalue()


def _get_school_csv_headers():
    """Helper: Returns CSV header row for schools."""
    return [
        "id",
        "name",
        "school_type",
        "city",
        "district",
        "zone",
        "opnv_code",
        "distance_km",
        "is_active",
        "notes",
        "latitude",
        "longitude",
        "created_at",
        "updated_at",
    ]


def _get_school_row(school):
    """Helper: Formats a School instance as CSV row."""
    return [
        school.id,
        school.name,
        school.school_type,
        school.city,
        school.district,
        school.zone,
        school.opnv_code,
        school.distance_km,
        school.is_active,
        school.notes or "",
        school.latitude or "",
        school.longitude or "",
        school.created_at.isoformat() if school.created_at else "",
        school.updated_at.isoformat() if school.updated_at else "",
    ]


def geocode_school(school):
    """
    Attempts to find lat/lon for a single school object using geopy.
    Updates the object and saves it. Returns True on success.
    """
    print(f"[GEOCODE] Starting geocoding for school: {school.name}")
    print(f"[GEOCODE] Current status: {school.geocoding_status}")
    print(f"[GEOCODE] Current lat/lng: {school.latitude}, {school.longitude}")
    
    if not school or not school.name or not school.city:
        print(f"[GEOCODE] Missing required fields - name: {school.name}, city: {school.city}")
        return False

    if school.geocoding_status == "success":
        print(f"[GEOCODE] Already successfully geocoded, skipping")
        return True

    if school.latitude and school.longitude:
        print(f"[GEOCODE] Already has coordinates, updating status to not_needed")
        school.geocoding_status = "not_needed"
        school.save(update_fields=["geocoding_status"])
        return True

    address_query = f"{school.name}, {school.city}, Germany"
    print(f"[GEOCODE] Querying address: {address_query}")
    
    geolocator = Nominatim(user_agent="uni-passau-praktikumsamt-app/1.0")

    try:
        location = geolocator.geocode(address_query, timeout=10)

        if location:
            print(f"[GEOCODE] SUCCESS - Found coordinates: {location.latitude}, {location.longitude}")
            school.latitude = location.latitude
            school.longitude = location.longitude
            school.geocoding_status = "success"
            school.save(update_fields=["latitude", "longitude", "geocoding_status"])
            return True
        else:
            print(f"[GEOCODE] FAILED - No location found for address")
            school.geocoding_status = "failed"
            school.save(update_fields=["geocoding_status"])
            return False

    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"[GEOCODE] ERROR - Geocoding service error: {e}")
        school.geocoding_status = "failed"
        school.save(update_fields=["geocoding_status"])
        raise GeocodingConnectionError(f"Connection lost during geocoding: {str(e)}")
    except (ConnectionError, OSError) as e:
        print(f"[GEOCODE] ERROR - Network connection error: {e}")
        school.geocoding_status = "pending"
        school.save(update_fields=["geocoding_status"])
        raise GeocodingConnectionError(f"Network connection lost: {str(e)}")
    except Exception as e:
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ['connection', 'network', 'timeout', 'unreachable', 'refused']):
            print(f"[GEOCODE] ERROR - Connection-related error: {e}")
            school.geocoding_status = "pending"
            school.save(update_fields=["geocoding_status"])
            raise GeocodingConnectionError(f"Connection error: {str(e)}")
        print(f"[GEOCODE] ERROR - Unexpected error: {e}")
        school.geocoding_status = "failed"
        school.save(update_fields=["geocoding_status"])
        return False


def geocode_schools_batch(schools_queryset=None, delay_between_requests=1):
    """
    Geocodes multiple schools in batch with rate limiting.
    Stops processing if connection is lost.

    Args:
        schools_queryset: QuerySet of schools to geocode. If None, geocodes all pending schools.
        delay_between_requests: Delay in seconds between geocoding requests

    Returns:
        dict: Statistics about the geocoding operation, including connection_error if applicable
    """
    if schools_queryset is None:
        schools_queryset = School.objects.filter(
            geocoding_status="pending", latitude__isnull=True, longitude__isnull=True
        )

    stats = {"total": schools_queryset.count(), "success": 0, "failed": 0, "skipped": 0, "connection_error": None}

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
