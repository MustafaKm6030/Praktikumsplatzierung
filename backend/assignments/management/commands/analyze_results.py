from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from assignments.models import Assignment


class Command(BaseCommand):
    help = "Analyzes the results of the assignment solver with GS/MS breakdown."

    def handle(self, *args, **options):
        self.stdout.write("\n=== 📊 ASSIGNMENT RESULT ANALYSIS ===\n")

        total_assignments = Assignment.objects.count()
        if total_assignments == 0:
            self.stdout.write(
                self.style.ERROR(
                    "No assignments found in the database. Run the solver first!"
                )
            )
            return

        self.stdout.write(
            f"Total Assignments Created: {self.style.SUCCESS(str(total_assignments))}\n"
        )

        # --- 1. Breakdown by Praktikum Type ---
        self.stdout.write("--- 📌 Breakdown by Type ---")

        # We assume standard order for display
        type_order = ["PDP_I", "PDP_II", "SFP", "ZSP"]

        for type_code in type_order:
            # Get total count for this type
            total_count = Assignment.objects.filter(
                practicum_type__code=type_code
            ).count()

            if total_count == 0:
                continue

            # Get breakdown GS vs MS
            gs_count = Assignment.objects.filter(
                practicum_type__code=type_code, mentor__program="GS"
            ).count()

            ms_count = Assignment.objects.filter(
                practicum_type__code=type_code, mentor__program="MS"
            ).count()

            # Format: - PDP_I: 50 [GS: 40 | MS: 10]
            self.stdout.write(
                f"- {type_code}: {self.style.WARNING(str(total_count))} "
                f"[{self.style.MIGRATE_HEADING('GS: ' + str(gs_count))} | "
                f"{self.style.MIGRATE_HEADING('MS: ' + str(ms_count))}]"
            )

        # --- 2. Detailed Breakdown (Type + Subject) ---
        self.stdout.write("\n--- 🔬 Detailed Breakdown (Type + Subject + Program) ---")

        for type_code in type_order:
            # Check if we have assignments for this type
            assignments_for_type = Assignment.objects.filter(
                practicum_type__code=type_code
            )
            if not assignments_for_type.exists():
                continue

            self.stdout.write(f"\n[{type_code}]")

            # Group by Subject
            subject_counts = (
                assignments_for_type.values("subject__name", "subject__code")
                .annotate(total=Count("id"))
                .order_by("-total")
            )

            has_subjects = False
            for entry in subject_counts:
                subj_name = entry["subject__name"]
                subj_code = entry["subject__code"]
                count = entry["total"]

                # Calculate GS/MS split for this specific subject line
                if subj_code:
                    gs_sub_count = assignments_for_type.filter(
                        subject__code=subj_code, mentor__program="GS"
                    ).count()
                    ms_sub_count = assignments_for_type.filter(
                        subject__code=subj_code, mentor__program="MS"
                    ).count()
                else:
                    # Handle 'No Subject' / General cases
                    gs_sub_count = assignments_for_type.filter(
                        subject__isnull=True, mentor__program="GS"
                    ).count()
                    ms_sub_count = assignments_for_type.filter(
                        subject__isnull=True, mentor__program="MS"
                    ).count()

                # Formatting string for the split
                split_info = f"[GS: {gs_sub_count} | MS: {ms_sub_count}]"

                if subj_name is None:
                    # PDPs often have no subject
                    self.stdout.write(
                        f"  • General / No Subject: {self.style.SUCCESS(str(count))} {split_info}"
                    )
                else:
                    has_subjects = True
                    self.stdout.write(
                        f"  • {subj_name} ({subj_code}): {self.style.SUCCESS(str(count))} {split_info}"
                    )

            if (
                not has_subjects
                and not assignments_for_type.filter(subject__isnull=True).exists()
            ):
                self.stdout.write("  (No assignments)")

        self.stdout.write("\n=======================================\n")
