import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from schools.models import School
from subjects.models import Subject, PraktikumType
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from students.models import Student
from system_settings.models import SystemSettings
from datetime import date


def create_sample_data():
    print("Creating sample data...")

    print("\n1. Creating Subjects...")
    subjects_data = [
        ("DEU", "Deutsch"),
        ("MAT", "Mathematik"),
        ("ENG", "Englisch"),
        ("MUS", "Musik"),
        ("SPO", "Sport"),
        ("GES", "Geschichte"),
        ("BIO", "Biologie"),
    ]
    subjects = {}
    for code, name in subjects_data:
        subject, created = Subject.objects.get_or_create(
            code=code, defaults={"name": name}
        )
        subjects[code] = subject
        print(f"  {'Created' if created else 'Found'}: {name}")

    print("\n2. Creating Praktikum Types...")
    praktikum_types_data = [
        ("PDP_I", "Pädagogisch-didaktisches Praktikum I"),
        ("PDP_II", "Pädagogisch-didaktisches Praktikum II"),
        ("SFP", "Studienbegleitendes Fachpraktikum"),
        ("ZSP", "Zusätzliches studienbegleitendes Praktikum"),
    ]
    praktikum_types = {}
    for code, name in praktikum_types_data:
        pt, created = PraktikumType.objects.get_or_create(
            code=code, defaults={"name": name}
        )
        praktikum_types[code] = pt
        print(f"  {'Created' if created else 'Found'}: {name}")

    print("\n3. Creating Schools...")
    schools_data = [
        # (name, school_type, district, city, zone, opnv_code, distance_km, latitude, longitude, is_active)
        (
            "Grundschule Passau-Innstadt",
            "GS",
            "Passau",
            "Passau",
            1,
            "4a",
            5,
            48.57,
            13.46,
            True,
        ),
        (
            "Mittelschule Vilshofen",
            "MS",
            "Passau-Land",
            "Vilshofen",
            1,
            "4a",
            23,
            48.62,
            13.38,
            True,
        ),
        ("Grundschule Regen", "GS", "Regen", "Regen", 3, "", 71, 48.97, 13.12, False),
        (
            "Grundschule Deggendorf",
            "GS",
            "Deggendorf",
            "Deggendorf",
            2,
            "4b",
            53,
            48.83,
            12.96,
            True,
        ),
        (
            "Mittelschule Straubing",
            "MS",
            "Straubing",
            "Straubing",
            3,
            "",
            85,
            48.87,
            12.57,
            True,
        ),
    ]
    schools = {}
    for (
        name,
        school_type,
        district,
        city,
        zone,
        opnv_code,
        distance_km,
        latitude,
        longitude,
        is_active,
    ) in schools_data:
        school, created = School.objects.get_or_create(
            name=name,
            defaults={
                "school_type": school_type,
                "district": district,
                "city": city,
                "zone": zone,
                "opnv_code": opnv_code,
                "distance_km": distance_km,
                "latitude": latitude,
                "longitude": longitude,
                "is_active": is_active,
            },
        )
        schools[name] = school
        print(f"  {'Created' if created else 'Found'}: {name}")

    print("\n4. Creating Praktikumslehrkräfte (Teachers)...")
    pls_data = [
        {
            "first_name": "Anna",
            "last_name": "Schmidt",
            "email": "anna.schmidt@schule.de",
            "school": schools["Grundschule Regen"],
            "program": "GS",
            "main_subject": subjects["DEU"],
            "schulamt": "Regen",
            "anrechnungsstunden": 1.0,  # Standard capacity
            "is_active": False,  # This school is inactive
            "preferred_praktika_raw": "PDP I, SFP",
            "praktikum_types": ["PDP_I", "SFP"],
            "available_subjects": ["DEU", "MAT"],  # Can teach German and Math
        },
        {
            "first_name": "Michael",
            "last_name": "Müller",
            "email": "michael.mueller@schule.de",
            "school": schools["Mittelschule Vilshofen"],
            "program": "MS",
            "main_subject": subjects["MAT"],
            "schulamt": "Passau-Land",
            "anrechnungsstunden": 2.0,  # "4 for 2" mentor
            "is_active": True,
            "preferred_praktika_raw": "PDP I, PDP II, ZSP",
            "besonderheiten": "4 für 2, übernimmt gerne ZSP",
            "praktikum_types": ["PDP_I", "PDP_II", "ZSP"],
            "available_subjects": ["MAT", "SPO"],
        },
        {
            "first_name": "Sarah",
            "last_name": "Weber",
            "email": "sarah.weber@schule.de",
            "school": schools["Grundschule Deggendorf"],
            "program": "GS",
            "main_subject": subjects["MUS"],
            "schulamt": "Deggendorf",
            "anrechnungsstunden": 1.0,
            "is_active": False,  # This school is inactive
            "preferred_praktika_raw": "SFP, ZSP",
            "besonderheiten": "nur Mi-Prak.",  # Only Wednesday internships
            "praktikum_types": ["SFP", "ZSP"],
            "available_subjects": ["MUS", "DEU"],
        },
        {
            "first_name": "Thomas",
            "last_name": "Bauer",
            "email": "thomas.bauer@schule.de",
            "school": schools["Mittelschule Straubing"],
            "program": "MS",
            "main_subject": subjects["SPO"],
            "schulamt": "Straubing",
            "anrechnungsstunden": 0.0,  # Unavailable this year
            "is_active": False,  # Also unavailable
            "besonderheiten": "Sabbatjahr",
            "preferred_praktika_raw": "PDP I, PDP II",
            "praktikum_types": [],
            "available_subjects": [],
        },
        {
            "first_name": "Julia",
            "last_name": "Fischer",
            "email": "julia.fischer@schule.de",
            "school": schools["Grundschule Passau-Innstadt"],
            "program": "GS",
            "main_subject": subjects["GES"],
            "schulamt": "Passau",
            "anrechnungsstunden": 1.0,
            "is_active": True,
            "preferred_praktika_raw": "PDP I, SFP",
            "praktikum_types": ["PDP_I", "SFP"],
            "available_subjects": ["GES", "DEU", "MAT"],
        },
    ]

    for pl_data in pls_data:
        praktikum_type_codes = pl_data.pop("praktikum_types")
        subject_codes = pl_data.pop("available_subjects")

        pl, created = PraktikumsLehrkraft.objects.update_or_create(
            email=pl_data["email"], defaults=pl_data
        )

        pl.available_praktikum_types.clear()
        for pt_code in praktikum_type_codes:
            pl.available_praktikum_types.add(praktikum_types[pt_code])

        pl.available_subjects.clear()
        for sub_code in subject_codes:
            pl.available_subjects.add(subjects[sub_code])

        print(f"  {'Created/Updated'}: {pl.first_name} {pl.last_name}")

    print("\n5. Creating Students...")
    students_data = [
        {
            "student_id": "ST-2024-001",
            "first_name": "Anna",
            "last_name": "Hofmann",
            "email": "anna.hofmann@stud.uni-passau.de",
            "program": "GS",
            "primary_subject": subjects["DEU"],
            "home_region": "Passau",
        },
        {
            "student_id": "ST-2024-002",
            "first_name": "Max",
            "last_name": "Schneider",
            "email": "max.schneider@stud.uni-passau.de",
            "program": "MS",
            "primary_subject": subjects["ENG"],
            "home_region": "Deggendorf",
        },
        {
            "student_id": "ST-2024-003",
            "first_name": "Sophie",
            "last_name": "Wagner",
            "email": "sophie.wagner@stud.uni-passau.de",
            "program": "GS",
            "primary_subject": subjects["MAT"],
            "home_region": "Regen",
        },
        {
            "student_id": "ST-2024-004",
            "first_name": "Lukas",
            "last_name": "Becker",
            "email": "lukas.becker@stud.uni-passau.de",
            "program": "GS",
            "primary_subject": subjects["DEU"],
            "home_region": "Passau",
        },
        {
            "student_id": "ST-2024-005",
            "first_name": "Emma",
            "last_name": "Meyer",
            "email": "emma.meyer@stud.uni-passau.de",
            "program": "MS",
            "primary_subject": subjects["BIO"],
            "home_region": "Straubing",
        },
        {
            "student_id": "ST-2024-006",
            "first_name": "Jonas",
            "last_name": "Zimmermann",
            "email": "jonas.zimmermann@stud.uni-passau.de",
            "program": "GS",
            "primary_subject": subjects["MAT"],
            "home_region": "Passau",
        },
        {
            "student_id": "ST-2024-007",
            "first_name": "Lena",
            "last_name": "Koch",
            "email": "lena.koch@stud.uni-passau.de",
            "program": "MS",
            "primary_subject": subjects["DEU"],
            "home_region": "Deggendorf",
        },
        {
            "student_id": "ST-2024-008",
            "first_name": "Tim",
            "last_name": "Richter",
            "email": "tim.richter@stud.uni-passau.de",
            "program": "GS",
            "primary_subject": subjects["SPO"],
            "home_region": "Regen",
        },
    ]

    for student_data in students_data:
        student, created = Student.objects.get_or_create(
            student_id=student_data["student_id"], defaults=student_data
        )
        print(
            f"  {'Created' if created else 'Found'}: {student.first_name} {student.last_name} ({student.student_id})"
        )

    print("\n6. Creating System Settings...")
    settings, created = SystemSettings.objects.get_or_create(
        current_academic_year="2024/2025",
        defaults={
            "total_anrechnungsstunden_budget": 210.00,
            "gs_budget_percentage": 80.48,
            "ms_budget_percentage": 19.52,
            "pdp_i_demand_deadline": date(2025, 5, 1),
            "pl_assignment_deadline": date(2025, 6, 15),
            "university_name": "Universität Passau",
            "contact_email": "praktikumsamt@uni-passau.de",
            "contact_phone": "+49 851 509-0",
            "is_active": True,
        },
    )
    print(f"  {'Created' if created else 'Found'}: System Settings for 2024/2025")

    print("\n✅ Sample data creation complete!")
    print(f"\nSummary:")
    print(f"  - Schools: {School.objects.count()}")
    print(f"  - Subjects: {Subject.objects.count()}")
    print(f"  - Praktikum Types: {PraktikumType.objects.count()}")
    print(f"  - Praktikumslehrkräfte: {PraktikumsLehrkraft.objects.count()}")
    print(f"  - Students: {Student.objects.count()}")
    print(f"  - System Settings: {SystemSettings.objects.count()}")


if __name__ == "__main__":
    create_sample_data()
