from django.core.management.base import BaseCommand
from assignments.solver import run_solver


class Command(BaseCommand):
    help = "Runs the optimization solver to assign mentors to students."

    def handle(self, *args, **options):
        self.stdout.write("Starting Allocation Algorithm...")

        # Run the solver
        results = run_solver()

        if results["status"] == "SUCCESS":
            # 1. Get the lists using the NEW keys
            assignments = results.get("assignments", [])
            unassigned = results.get("unassigned", [])

            # 2. Print Success Message
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Optimization Complete! Saved {len(assignments)} assignments."
                )
            )

            # 3. Print Assignment Details (Optional summary)
            # for a in assignments:
            #     self.stdout.write(f"  - {a['mentor_name']} -> {a['practicum_type']}")

            # 4. Print Unassigned Warning (The new feature)
            if unassigned:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️  {len(unassigned)} Mentors were NOT assigned:"
                    )
                )
                for u in unassigned:
                    self.stdout.write(f"  - {u['name']} ({u['reason']})")

                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "\nCheck the Admin Panel or Dashboard to fix data errors."
                    )
                )

        else:
            self.stdout.write(self.style.ERROR("\n❌ Optimization Failed."))
            self.stdout.write("Check the console logs above for infeasibility reasons.")
