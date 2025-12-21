from django.core.management.base import BaseCommand
from django.db.models import Count
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

        # Standard order for display
        type_order = ["PDP_I", "PDP_II", "SFP", "ZSP"]

        self._print_breakdown_by_type(type_order)
        self._print_detailed_breakdown(type_order)

        self.stdout.write("\n=======================================\n")

    def _print_breakdown_by_type(self, type_order):
        """Prints high-level stats: Type count and GS/MS split."""
        self.stdout.write("--- 📌 Breakdown by Type ---")

        for type_code in type_order:
            # Get total count for this type
            qs = Assignment.objects.filter(practicum_type__code=type_code)
            total_count = qs.count()

            if total_count == 0:
                continue

            gs_count = qs.filter(mentor__program="GS").count()
            ms_count = qs.filter(mentor__program="MS").count()

            # Format: - PDP_I: 50 [GS: 40 | MS: 10]
            self.stdout.write(
                f"- {type_code}: {self.style.WARNING(str(total_count))} "
                f"[{self.style.MIGRATE_HEADING('GS: ' + str(gs_count))} | "
                f"{self.style.MIGRATE_HEADING('MS: ' + str(ms_count))}]"
            )

    def _print_detailed_breakdown(self, type_order):
        """Prints granular stats: Grouped by Type -> Subject -> Program."""
        self.stdout.write("\n--- 🔬 Detailed Breakdown (Type + Subject + Program) ---")

        for type_code in type_order:
            assignments_for_type = Assignment.objects.filter(
                practicum_type__code=type_code
            )

            if not assignments_for_type.exists():
                continue

            self.stdout.write(f"\n[{type_code}]")
            self._print_subject_groups(assignments_for_type)

    def _print_subject_groups(self, assignments_qs):
        """Helper to aggregate and print subject lines for a specific queryset."""
        subject_counts = (
            assignments_qs.values("subject__name", "subject__code")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        if not subject_counts:
            self.stdout.write("  (No assignments)")
            return

        for entry in subject_counts:
            subj_name = entry["subject__name"]
            subj_code = entry["subject__code"]
            count = entry["total"]

            # Calculate GS/MS split for this specific subject line
            filters = (
                {"subject__code": subj_code} if subj_code else {"subject__isnull": True}
            )

            gs_count = assignments_qs.filter(mentor__program="GS", **filters).count()
            ms_count = assignments_qs.filter(mentor__program="MS", **filters).count()

            split_info = f"[GS: {gs_count} | MS: {ms_count}]"

            if subj_name is None:
                display_name = "General / No Subject"
            else:
                display_name = f"{subj_name} ({subj_code})"

            self.stdout.write(
                f"  • {display_name}: {self.style.SUCCESS(str(count))} {split_info}"
            )
