import random
from django.core.management.base import BaseCommand
from django.db import transaction
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from schools.models import School
from subjects.models import Subject, PraktikumType


class Command(BaseCommand):
    help = "Seeds the database with 3 PLs per school (Optimized for Solver Feasibility)"

    # --- Static Constants ---
    FIRST_NAMES = [
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
    ]
    HIGH_DEMAND_CODES = ["D", "MA", "E"]

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing PLs before seeding",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("--- Starting PL Seeding Process ---")

        # 1. Cleanup
        if options["clear"]:
            count, _ = PraktikumsLehrkraft.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removed {count} existing PLs."))

        # 2. Dependencies
        schools = School.objects.all()
        all_subjects = list(Subject.objects.all())

        if not self._validate_dependencies(schools, all_subjects):
            return

        # 3. Setup Lookups
        high_demand_subjects = [
            s for s in all_subjects if s.code in self.HIGH_DEMAND_CODES
        ]
        ptypes_map = {
            "PDP_I": PraktikumType.objects.get(code="PDP_I"),
            "PDP_II": PraktikumType.objects.get(code="PDP_II"),
            "SFP": PraktikumType.objects.get(code="SFP"),
            "ZSP": PraktikumType.objects.get(code="ZSP"),
        }

        # 4. Generate PLs
        created_count = self._seed_mentors(
            schools, all_subjects, high_demand_subjects, ptypes_map
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Successfully seeded {created_count} PLs across {schools.count()} schools!"
            )
        )

    def _validate_dependencies(self, schools, subjects):
        if not schools.exists():
            self.stdout.write(
                self.style.ERROR("No schools found! Please run seed_schools first.")
            )
            return False
        if not subjects:
            self.stdout.write(self.style.ERROR("No subjects found!"))
            return False
        return True

    def _seed_mentors(self, schools, all_subjects, high_demand_subjects, ptypes_map):
        count = 0
        for school in schools:
            self.stdout.write(f"Seeding 3 PLs for {school.name}...")
            for i in range(1, 4):
                self._create_single_mentor(
                    i, school, all_subjects, high_demand_subjects, ptypes_map
                )
                count += 1
        return count

    def _create_single_mentor(
        self, index, school, all_subjects, high_demand_subjects, ptypes_map
    ):
        # A. Basic Info
        f_name = random.choice(self.FIRST_NAMES)
        l_name = random.choice(self.LAST_NAMES)
        email = f"pl.{f_name.lower()}.{l_name.lower()}.{school.id}.{index}@test.de"

        # B. Subject Logic
        sub1 = random.choice(high_demand_subjects)
        remaining = [s for s in all_subjects if s != sub1]
        sub2 = random.choice(remaining)
        my_subjects = [sub1, sub2]

        # C. Capacity & Preferences
        is_high_cap = random.random() < 0.1
        anre_std = 2.0 if is_high_cap else 1.0
        pref_types, pref_text = self._get_preferences(
            is_high_cap, school.school_type, index, ptypes_map
        )

        # D. Creation
        pl = PraktikumsLehrkraft.objects.create(
            first_name=f_name,
            last_name=l_name,
            email=email,
            phone=f"+49 123 456 {school.id}{index}",
            school=school,
            program=school.school_type,
            main_subject=sub1,
            schulamt=school.district,
            anrechnungsstunden=anre_std,
            preferred_praktika_raw=pref_text,
            is_active=True,
            current_year_notes="4 für 2" if is_high_cap else "",
        )
        pl.available_praktikum_types.set(pref_types)
        pl.available_subjects.set(my_subjects)

    def _get_preferences(self, is_high_cap, program, index, pt_map):
        """Determines the preference types and text string."""
        if is_high_cap:
            return [
                pt_map["PDP_I"],
                pt_map["PDP_II"],
                pt_map["SFP"],
                pt_map["ZSP"],
            ], "PDP I, PDP II, SFP, ZSP"

        if program == "MS" and index % 2 == 0:
            return [pt_map["SFP"], pt_map["ZSP"]], "SFP, ZSP"

        return [pt_map["PDP_I"], pt_map["SFP"]], "PDP I, SFP"
