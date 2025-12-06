from django.core.management.base import BaseCommand
from schools.models import School


class Command(BaseCommand):
    help = "Seeds the database with 6 sample schools"

    # --- Static Data Definition ---
    SCHOOLS_DATA = [
        {
            "name": "Grundschule Passau-Innstadt",
            "school_type": "GS",
            "district": "Passau",
            "city": "Passau",
            "zone": 1,
            "opnv_code": "4a",
            "distance_km": 2,
            "latitude": 48.5714,
            "longitude": 13.4632,
            "is_active": True,
        },
        {
            "name": "Mittelschule Vilshofen",
            "school_type": "MS",
            "district": "Passau-Land",
            "city": "Vilshofen",
            "zone": 1,
            "opnv_code": "4a",
            "distance_km": 25,
            "latitude": 48.6335,
            "longitude": 13.1866,
            "is_active": True,
        },
        {
            "name": "Grundschule Deggendorf-Theodor Eckert",
            "school_type": "GS",
            "district": "Deggendorf",
            "city": "Deggendorf",
            "zone": 2,
            "opnv_code": "4b",
            "distance_km": 55,
            "latitude": 48.8350,
            "longitude": 12.9600,
            "is_active": True,
        },
        {
            "name": "Grundschule Pocking",
            "school_type": "GS",
            "district": "Passau-Land",
            "city": "Pocking",
            "zone": 2,
            "opnv_code": "4b",
            "distance_km": 30,
            "latitude": 48.4000,
            "longitude": 13.3100,
            "is_active": True,
        },
        {
            "name": "Mittelschule Hengersberg",
            "school_type": "MS",
            "district": "Deggendorf",
            "city": "Hengersberg",
            "zone": 2,
            "opnv_code": "4b",
            "distance_km": 42,
            "latitude": 48.7700,
            "longitude": 13.0500,
            "is_active": True,
        },
        {
            "name": "Grundschule Regen",
            "school_type": "GS",
            "district": "Regen",
            "city": "Regen",
            "zone": 3,
            "opnv_code": "",
            "distance_km": 70,
            "latitude": 48.9700,
            "longitude": 13.1200,
            "is_active": True,
        },
        {
            "name": "Mittelschule Straubing-Ittling",
            "school_type": "MS",
            "district": "Straubing",
            "city": "Straubing",
            "zone": 3,
            "opnv_code": "",
            "distance_km": 85,
            "latitude": 48.8800,
            "longitude": 12.5700,
            "is_active": True,
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write("Seeding schools...")

        created_count, updated_count = self._seed_schools()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully seeded schools! Created: {created_count}, Updated: {updated_count}"
            )
        )

    def _seed_schools(self):
        """Iterates through SCHOOLS_DATA and updates/creates records."""
        created_count = 0
        updated_count = 0

        for data in self.SCHOOLS_DATA:
            school, created = School.objects.update_or_create(
                name=data["name"], defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {data['name']}"))
            else:
                updated_count += 1
                self.stdout.write(f"Updated: {data['name']}")

        return created_count, updated_count
