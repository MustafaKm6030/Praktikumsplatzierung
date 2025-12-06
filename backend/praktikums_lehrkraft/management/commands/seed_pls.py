import random
from django.core.management.base import BaseCommand
from django.db import transaction
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from subjects.models import Subject, PraktikumType


class Command(BaseCommand):
    help = "Seeds the database with 3 PLs per school (Optimized for Solver Feasibility)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing PLs before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("--- Starting PL Seeding Process ---")

        # 0. Cleanup if requested
        if options["clear"]:
            count, _ = PraktikumsLehrkraft.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removed {count} existing PLs."))

        # 1. Get Dependencies
        schools = School.objects.all()
        if not schools.exists():
            self.stdout.write(
                self.style.ERROR("No schools found! Please run seed_schools first.")
            )
            return

        all_subjects = list(Subject.objects.all())
        if not all_subjects:
            self.stdout.write(self.style.ERROR("No subjects found!"))
            return

        # Define "High Demand" subjects to ensure mentors are assignable
        # (This prevents the "Capacity mismatch" error where a mentor has subjects nobody needs)
        high_demand_codes = ["D", "MA", "E"]
        high_demand_subjects = [s for s in all_subjects if s.code in high_demand_codes]

        # Map types for easy access
        pt_pdp1 = PraktikumType.objects.get(code="PDP_I")
        pt_pdp2 = PraktikumType.objects.get(code="PDP_II")
        pt_sfp = PraktikumType.objects.get(code="SFP")
        pt_zsp = PraktikumType.objects.get(code="ZSP")

        # Names for generation
        first_names = [
            "Julia",
            "Thomas",
            "Sarah",
            "Michael",
            "Anna",
            "Peter",
            "Sandra",
            "Markus",
            "Lisa",
            "Stefan",
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
        ]

        created_count = 0

        # 2. Loop through EACH school and create 3 PLs
        for school in schools:
            self.stdout.write(f"Seeding 3 PLs for {school.name}...")

            # REDUCED TO 3 PER SCHOOL to ensure Demand > Supply
            for i in range(1, 4):
                # -- A. Basic Info --
                f_name = random.choice(first_names)
                l_name = random.choice(last_names)
                email = f"pl.{f_name.lower()}.{l_name.lower()}.{school.id}.{i}@test.de"

                program = school.school_type

                # -- B. SMART SUBJECT LOGIC (Crucial for Solver) --
                # To prevent solver crashes, every mentor gets at least 1 High Demand subject.
                # 1. Pick one Major Subject (D, MA, or E)
                sub1 = random.choice(high_demand_subjects)

                # 2. Pick any second subject (excluding the first one)
                remaining_subjects = [s for s in all_subjects if s != sub1]
                sub2 = random.choice(remaining_subjects)

                my_subjects = [sub1, sub2]
                main_subject = sub1

                # -- C. Capacity Logic --
                # Keep it simple: Mostly capacity 2 (Standard).
                # Very rare chance of 4 (only 10%) to reduce complexity.
                is_high_cap = random.random() < 0.1
                anre_std = 2.0 if is_high_cap else 1.0

                # -- D. Preference Logic --
                # Default: Standard Pair
                pref_types = [pt_pdp1, pt_sfp]
                pref_text = "PDP I, SFP"

                if is_high_cap:
                    pref_types = [pt_pdp1, pt_pdp2, pt_sfp, pt_zsp]
                    pref_text = "PDP I, PDP II, SFP, ZSP"
                elif program == "MS" and i % 2 == 0:
                    pref_types = [pt_sfp, pt_zsp]
                    pref_text = "SFP, ZSP"

                # -- E. Create the PL --
                pl = PraktikumsLehrkraft.objects.create(
                    first_name=f_name,
                    last_name=l_name,
                    email=email,
                    phone=f"+49 123 456 {school.id}{i}",
                    school=school,
                    program=program,
                    main_subject=main_subject,
                    schulamt=school.district,
                    anrechnungsstunden=anre_std,
                    preferred_praktika_raw=pref_text,
                    is_active=True,
                    current_year_notes="4 für 2" if is_high_cap else "",
                )

                # -- F. Set M2M Relations --
                pl.available_praktikum_types.set(pref_types)
                pl.available_subjects.set(my_subjects)

                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully seeded {created_count} PLs across {schools.count()} schools!"
            )
        )
