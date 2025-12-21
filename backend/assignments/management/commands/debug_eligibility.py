from collections import defaultdict
from django.core.management.base import BaseCommand
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from subjects.models import Subject
from assignments.services import calculate_eligibility_for_pl


class Command(BaseCommand):
    help = "Debugs PL eligibility counts to find discrepancies between DB and Solver logic."

    def handle(self, *args, **options):
        self.stdout.write("\n=== 🕵️ ELIGIBILITY DEBUGGER (FULL SCAN) ===\n")

        # 1. RAW DATABASE CHECK (The Truth)
        self.stdout.write("--- 1. Raw Database Counts (Source of Truth) ---")
        self.stdout.write(
            "(Counts all Active PLs who have this subject in 'available_subjects')"
        )

        # Get all subjects ordered by code
        all_subjects = Subject.objects.all().order_by("code")

        for sub in all_subjects:
            count = PraktikumsLehrkraft.objects.filter(
                is_active=True, available_subjects=sub
            ).count()

            # Print row
            if count > 0:
                self.stdout.write(
                    f"- {sub.code.ljust(6)} ({sub.name}): {self.style.SUCCESS(str(count))}"
                )
            else:
                self.stdout.write(
                    f"- {sub.code.ljust(6)} ({sub.name}): {self.style.WARNING('0')}"
                )

        # 2. SOLVER ELIGIBILITY CHECK (What the Solver Sees)
        self.stdout.write("\n--- 2. Solver Eligibility Counts (Calculated) ---")
        self.stdout.write(
            "(Counts PLs who are Active + Reachable + Eligible for SFP/ZSP)"
        )

        # Structure: { 'SFP': { 'GS': { 'MU': count } } }
        solver_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        all_mentors = PraktikumsLehrkraft.objects.filter(
            is_active=True
        ).prefetch_related("available_praktikum_types", "available_subjects", "school")

        for pl in all_mentors:
            eligibilities = calculate_eligibility_for_pl(pl)

            for ptype_code, subject_code in eligibilities:
                if subject_code != "N/A":
                    solver_counts[ptype_code][pl.program][subject_code] += 1

        for ptype in ["SFP", "ZSP"]:
            self.stdout.write(f"\n[{ptype}]")
            for program in ["GS", "MS"]:
                subjects = solver_counts[ptype][program]
                if not subjects:
                    continue

                sorted_subjects = sorted(
                    subjects.items(), key=lambda x: x[1], reverse=True
                )
                top_str = ", ".join([f"{k}: {v}" for k, v in sorted_subjects])
                self.stdout.write(f"  {program}: {top_str}")

        self.stdout.write("\n=======================================")
