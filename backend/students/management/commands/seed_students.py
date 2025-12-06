import random
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from students.models import Student
from subjects.models import Subject


class Command(BaseCommand):
    help = "Seeds the database with 50 random students and necessary subjects"

    # --- 1. Static Data Definitions (Moved out of methods) ---
    SUBJECT_DEFINITIONS = [
        ("D", "Deutsch"),
        ("MA", "Mathematik"),
        ("E", "Englisch"),
        ("DaZ", "Deutsch als Zweitsprache"),
        ("KRel", "Kath. Religion"),
        ("ERel", "Evang. Religion"),
        ("SK", "Sozialkunde"),
        ("PO", "Politik"),
        ("GE", "Geschichte"),
        ("GEO", "Geographie"),
        ("KE", "Kunsterziehung"),
        ("MU", "Musik"),
        ("SP", "Sport"),
        ("BIO", "Biologie"),
        ("CHE", "Chemie"),
        ("PHY", "Physik"),
        ("AL", "Arbeitslehre"),
        ("WI", "Wirtschaft"),
        ("BK", "Berufskunde"),
        ("IT", "Informatik"),
        ("SSE", "Schriftspracherwerb"),
    ]

    FIRST_NAMES = [
        "Lukas",
        "Maria",
        "Maximilian",
        "Sophie",
        "Paul",
        "Anna",
        "Leon",
        "Laura",
        "Felix",
        "Lena",
        "Elias",
        "Mia",
        "Jonas",
        "Emma",
        "David",
        "Hannah",
        "Julian",
        "Sarah",
        "Tim",
        "Lisa",
    ]

    LAST_NAMES = [
        "Müller",
        "Schmidt",
        "Schneider",
        "Fischer",
        "Weber",
        "Meyer",
        "Wagner",
        "Becker",
        "Schulz",
        "Hoffmann",
        "Koch",
        "Richter",
        "Klein",
        "Wolf",
        "Schröder",
        "Neumann",
        "Schwarz",
        "Zimmermann",
        "Braun",
        "Krüger",
    ]

    REGIONS = ["Passau", "Regen", "Deggendorf", "Straubing", "Passau-Land"]
    ADDRESSES = [
        "Innstraße",
        "Donaupromenade",
        "Stadtplatz",
        "Bahnhofstraße",
        "Schulweg",
        "Hauptstraße",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing test students before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("--- Starting Student Seeding Process ---")

        # 1. Cleanup
        self._clear_existing_data(options)

        # 2. Setup Subjects
        db_subjects = self._ensure_subjects_exist()

        # 3. Generate Students
        self.stdout.write("Generating Student Data...")
        students = self._generate_student_batch(db_subjects)

        # 4. Save
        Student.objects.bulk_create(students, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(students)} students!")
        )

    def _clear_existing_data(self, options):
        """Handles the deletion of existing test data."""
        if options["clear"]:
            deleted_count, _ = Student.objects.filter(
                student_id__startswith="ST-2025-"
            ).delete()
            self.stdout.write(
                self.style.WARNING(f"Removed {deleted_count} existing test students.")
            )

    def _ensure_subjects_exist(self):
        """Creates subjects in the DB and returns a lookup dictionary."""
        self.stdout.write("Ensuring Subjects exist...")
        db_subjects = {}
        for code, name in self.SUBJECT_DEFINITIONS:
            sub, _ = Subject.objects.get_or_create(code=code, defaults={"name": name})
            db_subjects[name] = sub
        return db_subjects

    def _get_pools(self, program):
        """Returns the primary and didactic subject pools based on program type."""
        # Note: You could also move these lists to class attributes if they are static
        gs_primary = [
            "Sozialkunde",
            "Politik",
            "Deutsch als Zweitsprache",
            "Kath. Religion",
            "Evang. Religion",
            "Deutsch",
            "Englisch",
            "Geschichte",
            "Geographie",
            "Kunsterziehung",
            "Mathematik",
        ]
        gs_didactic = gs_primary + [
            "Biologie",
            "Chemie",
            "Physik",
            "Musik",
            "Sport",
            "Schriftspracherwerb",
        ]

        ms_primary = [
            "Arbeitslehre",
            "Wirtschaft",
            "Berufskunde",
            "Sozialkunde",
            "Politik",
            "Kath. Religion",
            "Evang. Religion",
            "Informatik",
            "Biologie",
            "Chemie",
            "Physik",
            "Deutsch als Zweitsprache",
            "Deutsch",
            "Englisch",
            "Geschichte",
            "Geographie",
            "Kunsterziehung",
            "Mathematik",
        ]
        ms_didactic = ms_primary + ["Musik", "Sport"]

        if program == "GS":
            return gs_primary, gs_didactic
        return ms_primary, ms_didactic

    def _generate_student_batch(self, db_subjects):
        """Generates the list of Student objects."""
        students_to_create = []
        for i in range(1, 51):
            student = self._create_single_student(i, db_subjects)
            if student:
                students_to_create.append(student)
        return students_to_create

    def _create_single_student(self, index, db_subjects):
        """Creates a single Student instance."""
        # 1. Basic Info
        s_id = f"ST-2025-{index:03d}"
        f_name = random.choice(self.FIRST_NAMES)
        l_name = random.choice(self.LAST_NAMES)
        email = f"{f_name.lower()}.{l_name.lower()}.{index}@stud.uni-passau.de"
        region = random.choice(self.REGIONS)
        program = "GS" if index <= 35 else "MS"

        # 2. Logic Helpers
        address = self._generate_address(region)
        subject_data = self._select_subjects(program, db_subjects)

        if not subject_data:
            self.stdout.write(self.style.WARNING(f"Not enough subjects for {s_id}"))
            return None

        pdp1, pdp2, sfp, zsp = self._calculate_dates(index)

        # 3. Create Object
        return Student(
            student_id=s_id,
            first_name=f_name,
            last_name=l_name,
            email=email,
            program=program,
            primary_subject=subject_data["primary"],
            didactic_subject_1=subject_data["d1"],
            didactic_subject_2=subject_data["d2"],
            didactic_subject_3=subject_data["d3"],
            home_address=address,
            semester_address="Innstraße 41, 94032 Passau",
            home_region=region,
            pdp1_completed_date=pdp1,
            pdp2_completed_date=pdp2,
            sfp_completed_date=sfp,
            zsp_completed_date=zsp,
            placement_status="UNPLACED",
        )

    def _generate_address(self, region):
        """Generates a random address based on region."""
        street = random.choice(self.ADDRESSES)
        number = random.randint(1, 100)

        if region == "Passau":
            return f"{street} {number}, 94032 Passau"
        return f"{street} {number}, 94XXX {region}"

    def _select_subjects(self, program, db_subjects):
        """Selects valid primary and didactic subjects."""
        prim_pool, didactic_pool = self._get_pools(program)

        # Pick Primary
        prim_name = random.choice(prim_pool)

        # Pick Didactics (excluding primary)
        available_didactics = [name for name in didactic_pool if name != prim_name]

        if len(available_didactics) < 3:
            return None

        selected = random.sample(available_didactics, 3)

        return {
            "primary": db_subjects[prim_name],
            "d1": db_subjects[selected[0]],
            "d2": db_subjects[selected[1]],
            "d3": db_subjects[selected[2]],
        }

    def _calculate_dates(self, index):
        """Determines the completed dates based on random logic."""
        pdp1 = pdp2 = sfp = zsp = None
        rand_val = index % 5

        if rand_val == 1:  # Type B
            pdp1 = date(2023, 3, 1)
        elif rand_val == 2:  # Type C
            pdp1 = date(2023, 3, 1)
            sfp = date(2024, 7, 15)
        elif rand_val == 3:  # Type D
            pdp1 = date(2023, 3, 1)
        elif rand_val == 4:  # Type E
            pdp1 = date(2023, 3, 1)

        return pdp1, pdp2, sfp, zsp
