# backend/assignments/management/commands/run_allocation.py

from django.core.management.base import BaseCommand
from assignments.solver import run_solver
from assignments.models import Assignment


class Command(BaseCommand):
    help = "Runs the assignment solver algorithm against current DB data."

    def handle(self, *args, **options):
        self.stdout.write("Starting Allocation Algorithm...")

        # Execute the solver
        # (The solver function handles the logic of deleting old assignments
        # and saving new ones to the database automatically)
        results = run_solver()

        if results["status"] == "SUCCESS":
            count = len(results["solution"])
            db_count = Assignment.objects.count()

            self.stdout.write(self.style.SUCCESS("\n✅ Solver completed successfully!"))
            self.stdout.write(f"   - Solution Size: {count} assignments calculated.")
            self.stdout.write(
                f"   - Database Count: {db_count} Assignment objects created."
            )
        else:
            self.stdout.write(
                self.style.ERROR("\n❌ Solver failed to find a valid solution.")
            )
            self.stdout.write(
                "   Check your constraints, capacity, or data consistency."
            )
