import csv
import io
from django.db import transaction
from .models import School


def get_schools_by_zone(zone):
    return School.objects.filter(opnv_zone=zone, is_active=True)


def get_schools_by_type(school_type):
    return School.objects.filter(school_type=school_type, is_active=True)


def calculate_school_capacity(school):
    return {
        'block_available': school.max_block_praktikum_slots,
        'wednesday_available': school.max_wednesday_praktikum_slots,
    }


def get_schools_within_travel_time(max_minutes):
    return School.objects.filter(
        travel_time_minutes__lte=max_minutes,
        is_active=True
    )


def import_schools_from_csv(file_obj):
    decoded_file = file_obj.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.DictReader(io_string)
    
    created_count = 0
    updated_count = 0
    errors = []
    
    with transaction.atomic():
        for row_num, row in enumerate(reader, start=2):
            try:
                name = row.get('name', '').strip()
                if not name:
                    errors.append(f"Row {row_num}: Name is required")
                    continue
                
                school_data = {
                    'name': name,
                    'school_type': row.get('school_type', 'GS'),
                    'address': row.get('address', ''),
                    'district': row.get('district', ''),
                    'city': row.get('city', ''),
                    'opnv_zone': row.get('opnv_zone', 'ZONE_1'),
                    'travel_time_minutes': int(row.get('travel_time_minutes', 0)) if row.get('travel_time_minutes') else None,
                    'max_block_praktikum_slots': int(row.get('max_block_praktikum_slots', 0)),
                    'max_wednesday_praktikum_slots': int(row.get('max_wednesday_praktikum_slots', 0)),
                    'contact_person': row.get('contact_person', ''),
                    'phone': row.get('phone', ''),
                    'email': row.get('email', ''),
                    'is_active': row.get('is_active', 'true').lower() in ['true', '1', 'yes'],
                    'notes': row.get('notes', ''),
                }
                
                if row.get('latitude'):
                    school_data['latitude'] = float(row['latitude'])
                if row.get('longitude'):
                    school_data['longitude'] = float(row['longitude'])
                
                school, created = School.objects.update_or_create(
                    name=name,
                    defaults=school_data
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        'created': created_count,
        'updated': updated_count,
        'errors': errors
    }


def export_schools_to_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'id', 'name', 'school_type', 'address', 'district', 'city',
        'latitude', 'longitude', 'opnv_zone', 'travel_time_minutes',
        'max_block_praktikum_slots', 'max_wednesday_praktikum_slots',
        'contact_person', 'phone', 'email', 'is_active', 'notes',
        'created_at', 'updated_at'
    ])
    
    schools = School.objects.all().order_by('name')
    for school in schools:
        writer.writerow([
            school.id,
            school.name,
            school.school_type,
            school.address,
            school.district,
            school.city,
            school.latitude or '',
            school.longitude or '',
            school.opnv_zone,
            school.travel_time_minutes or '',
            school.max_block_praktikum_slots,
            school.max_wednesday_praktikum_slots,
            school.contact_person,
            school.phone,
            school.email,
            school.is_active,
            school.notes,
            school.created_at.isoformat() if school.created_at else '',
            school.updated_at.isoformat() if school.updated_at else '',
        ])
    
    return output.getvalue()

