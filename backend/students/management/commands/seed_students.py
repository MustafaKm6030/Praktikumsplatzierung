import random
from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction

# Adjust these imports based on your actual project structure
from students.models import Student
from subjects.models import Subject


class Command(BaseCommand):
    help = "Seeds the database with 50 random students and necessary subjects"

    def add_arguments(self, parser):
        # Optional: Add a flag to delete existing test students before seeding
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing test students (ST-2025-*) before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("--- Starting Student Seeding Process ---")

        # 0. Cleanup if requested
        if options["clear"]:
            deleted_count, _ = Student.objects.filter(
                student_id__startswith="ST-2025-"
            ).delete()
            self.stdout.write(
                self.style.WARNING(f"Removed {deleted_count} existing test students.")
            )

        # 1. Define the Universe of Subjects
        all_subject_definitions = [
            # Languages & Core
            ("D", "Deutsch"),
            ("MA", "Mathematik"),
            ("E", "Englisch"),
            ("DaZ", "Deutsch als Zweitsprache"),
            # Religion (Pooled)
            ("KRel", "Kath. Religion"),
            ("ERel", "Evang. Religion"),
            # Social Studies
            ("SK", "Sozialkunde"),
            ("PO", "Politik"),
            ("GE", "Geschichte"),
            ("GEO", "Geographie"),
            # Arts & Sport
            ("KE", "Kunsterziehung"),
            ("MU", "Musik"),
            ("SP", "Sport"),
            # Science (Maps to HSU in GS, PCB in MS)
            ("BIO", "Biologie"),
            ("CHE", "Chemie"),
            ("PHY", "Physik"),
            # MS Specific
            ("AL", "Arbeitslehre"),
            ("WI", "Wirtschaft"),
            ("BK", "Berufskunde"),
            ("IT", "Informatik"),
            # GS Specific
            ("SSE", "Schriftspracherwerb"),
        ]

        # Create/Get Subjects in DB and store in a lookup dict
        self.stdout.write("Ensuring Subjects exist...")
        db_subjects = {}
        for code, name in all_subject_definitions:
            sub, created = Subject.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            db_subjects[name] = sub

        # 2. Define Valid Pools based on Rules
        # --- Grundschule (GS) Pools ---
        gs_primary_pool_names = [
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

        gs_didactic_pool_names = gs_primary_pool_names + [
            "Biologie",
            "Chemie",
            "Physik",
            "Musik",
            "Sport",
            "Schriftspracherwerb",
        ]

        # --- Mittelschule (MS) Pools ---
        ms_primary_pool_names = [
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

        ms_didactic_pool_names = ms_primary_pool_names + ["Musik", "Sport"]

        # 3. Random Data Lists
        first_names = [
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
        last_names = [
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
        regions = ["Passau", "Regen", "Deggendorf", "Straubing", "Passau-Land"]
        addresses = [
            "Innstraße",
            "Donaupromenade",
            "Stadtplatz",
            "Bahnhofstraße",
            "Schulweg",
            "Hauptstraße",
        ]

        students_to_create = []

        self.stdout.write("Generating Student Data...")

        # 4. Generate 50 Students
        for i in range(1, 51):
            s_id = f"ST-2025-{i:03d}"
            f_name = random.choice(first_names)
            l_name = random.choice(last_names)
            email = f"{f_name.lower()}.{l_name.lower()}.{i}@stud.uni-passau.de"
            region = random.choice(regions)

            # 70% GS, 30% MS
            program = "GS" if i <= 35 else "MS"

            if region == "Passau":
                addr = (
                    f"{random.choice(addresses)} {random.randint(1, 100)}, 94032 Passau"
                )
            else:
                addr = f"{random.choice(addresses)} {random.randint(1, 100)}, 94XXX {region}"

            # --- SUBJECT SELECTION LOGIC ---
            if program == "GS":
                prim_pool = gs_primary_pool_names
                didactic_pool = gs_didactic_pool_names
            else:
                prim_pool = ms_primary_pool_names
                didactic_pool = ms_didactic_pool_names

            # 1. Pick Primary Subject (Target for SFP)
            prim_name = random.choice(prim_pool)
            primary_subject = db_subjects[prim_name]

            # 2. Pick 3 Distinct Didactic Subjects
            # Ensure we don't pick the primary again if not desired
            available_didactics = [name for name in didactic_pool if name != prim_name]

            # Safety check: ensure we have enough subjects to sample from
            if len(available_didactics) < 3:
                self.stdout.write(
                    self.style.WARNING(
                        f"Not enough didactic subjects for {program} pool. Skipping {s_id}."
                    )
                )
                continue

            selected_didactics_names = random.sample(available_didactics, 3)

            didactic_1 = db_subjects[selected_didactics_names[0]]
            didactic_2 = db_subjects[selected_didactics_names[1]]
            didactic_3 = db_subjects[selected_didactics_names[2]]  # Target for ZSP

            # --- DEMAND GENERATION ---
            pdp1_date = None
            pdp2_date = None
            sfp_date = None
            zsp_date = None
            placement_status = "UNPLACED"

            rand_val = i % 5

            if rand_val == 0:
                # Type A: Freshman (Needs PDP I)
                pass
            elif rand_val == 1:
                # Type B: Mid-Study (Needs SFP - Primary Subject)
                pdp1_date = date(2023, 3, 1)
            elif rand_val == 2:
                # Type C: Advanced (Needs ZSP - Didactic Subject 3)
                pdp1_date = date(2023, 3, 1)
                sfp_date = date(2024, 7, 15)
            elif rand_val == 3:
                # Type D: Needs PDP II
                pdp1_date = date(2023, 3, 1)
            else:
                # Type E: Needs SFP AND ZSP
                pdp1_date = date(2023, 3, 1)

            student = Student(
                student_id=s_id,
                first_name=f_name,
                last_name=l_name,
                email=email,
                program=program,
                primary_subject=primary_subject,
                didactic_subject_1=didactic_1,
                didactic_subject_2=didactic_2,
                didactic_subject_3=didactic_3,
                home_address=addr,
                semester_address="Innstraße 41, 94032 Passau",
                home_region=region,
                pdp1_completed_date=pdp1_date,
                pdp2_completed_date=pdp2_date,
                sfp_completed_date=sfp_date,
                zsp_completed_date=zsp_date,
                placement_status=placement_status,
            )
            students_to_create.append(student)

        # Bulk create
        Student.objects.bulk_create(students_to_create, ignore_conflicts=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(students_to_create)} students!"
            )
        )
