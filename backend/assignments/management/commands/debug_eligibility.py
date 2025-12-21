from collections import defaultdict
from django.core.management.base import BaseCommand
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from subjects.models import Subject
from assignments.services import calculate_eligibility_for_pl


class Command(BaseCommand):
    help = "Debugs PL eligibility counts to find discrepancies between DB and Solver logic."

    def handle(self, *args, **options):
        self.stdout.write("\n=== 🕵️ ELIGIBILITY DEBUGGER (FULL SCAN) ===\n")

        # 1. RAW DATABASE CHECK
        self._print_database_raw_counts()

        # 2. SOLVER ELIGIBILITY CHECK
        self._print_solver_calculated_counts()

        self.stdout.write("\n=======================================")

    def _print_database_raw_counts(self):
        """Checks source of truth: Active PLs linked to subjects."""
        self.stdout.write("--- 1. Raw Database Counts (Source of Truth) ---")
        self.stdout.write(
            "(Counts all Active PLs who have this subject in 'available_subjects')"
        )

        all_subjects = Subject.objects.all().order_by("code")
        for sub in all_subjects:
            count = PraktikumsLehrkraft.objects.filter(
                is_active=True, available_subjects=sub
            ).count()

            status_style = self.style.SUCCESS if count > 0 else self.style.WARNING
            self.stdout.write(
                f"- {sub.code.ljust(6)} ({sub.name}): {status_style(str(count))}"
            )

    def _print_solver_calculated_counts(self):
        """Checks logic: Active + Reachable + Eligible for SFP/ZSP."""
        self.stdout.write("\n--- 2. Solver Eligibility Counts (Calculated) ---")
        self.stdout.write(
            "(Counts PLs who are Active + Reachable + Eligible for SFP/ZSP)"
        )

        # Structure: { 'PTYPE': { 'PROGRAM': { 'SUBJECT': count } } }
        counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        mentors = PraktikumsLehrkraft.objects.filter(is_active=True).prefetch_related(
            "available_praktikum_types", "available_subjects", "school"
        )

        for pl in mentors:
            eligibilities = calculate_eligibility_for_pl(pl)
            for ptype_code, subject_code in eligibilities:
                if subject_code != "N/A":
                    counts[ptype_code][pl.program][subject_code] += 1

        for ptype in ["SFP", "ZSP"]:
            self.stdout.write(f"\n[{ptype}]")
            for program in ["GS", "MS"]:
                self._print_program_line(program, counts[ptype][program])

    def _print_program_line(self, program_code, subjects_dict):
        """Helper to format a single line of subject counts for a program."""
        if not subjects_dict:
            return

        # Sort by count descending
        sorted_items = sorted(subjects_dict.items(), key=lambda x: x[1], reverse=True)
        count_str = ", ".join([f"{code}: {val}" for code, val in sorted_items])

        self.stdout.write(f"  {program_code}: {count_str}")
