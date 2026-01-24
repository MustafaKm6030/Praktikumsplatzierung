from django.core.management.base import BaseCommand
from assignments.models import Assignment
from praktikums_lehrkraft.models import PraktikumsLehrkraft
from subjects.models import Subject
import re

# --- Re-use the parsing logic from your objectives file ---
# It's good practice to move these to a shared utils file later.
SUBJECT_NAME_TO_CODE_MAP = {}


def _build_subject_name_map():
    if SUBJECT_NAME_TO_CODE_MAP:
        return
    for subject in Subject.objects.all():
        SUBJECT_NAME_TO_CODE_MAP[subject.name.lower()] = subject.code


def _get_historical_subject_code(history_text: str) -> str:
    text = history_text.lower()
    for name, code in SUBJECT_NAME_TO_CODE_MAP.items():
        if re.search(r"\b" + re.escape(name) + r"\b", text):
            return code
    return ""


# ----------------------------------------------------


class Command(BaseCommand):
    help = "Analyzes the solver's results to calculate the Continuity Score."

    def handle(self, *args, **options):
        self.stdout.write("\n=== 📈 CONTINUITY ANALYSIS ===\n")

        # Build the subject map for parsing
        _build_subject_name_map()

        assignments = Assignment.objects.all().select_related(
            "mentor", "practicum_type", "subject"
        )
        total_assignments = assignments.count()

        if total_assignments == 0:
            self.stdout.write(self.style.ERROR("No assignments found in the database."))
            return

        match_count = 0

        for assignment in assignments:
            mentor = assignment.mentor
            ptype = assignment.practicum_type.code
            subject_code = assignment.subject.code if assignment.subject else "N/A"

            # 1. Get the raw history value
            history_value = ""
            if ptype == "PDP_I":
                history_value = mentor.history_pdp1
            elif ptype == "PDP_II":
                history_value = mentor.history_pdp2
            elif ptype == "SFP":
                history_value = mentor.history_sfp
            elif ptype == "ZSP":
                history_value = mentor.history_zsp

            if not history_value:
                continue

            # 2. Check for negatives
            negative_keywords = ["nicht", "nein", "keine"]
            if any(keyword in history_value.lower() for keyword in negative_keywords):
                continue

            # 3. Check for a match
            is_match = False
            if ptype in ["PDP_I", "PDP_II"]:
                if subject_code == "N/A" and history_value.lower().strip() in [
                    "ja",
                    "hier",
                    "x",
                ]:
                    is_match = True
            else:  # SFP/ZSP
                historical_code = _get_historical_subject_code(history_value)
                if historical_code and historical_code == subject_code:
                    is_match = True

            if is_match:
                match_count += 1
                self.stdout.write(
                    f"  ✅ Match found: Mentor {mentor.id} -> {ptype}-{subject_code}"
                )

        # 4. Calculate and display the final score
        if total_assignments > 0:
            percentage = (match_count / total_assignments) * 100
            self.stdout.write("\n--- FINAL SCORE ---")
            self.stdout.write(f"Total Assignments: {total_assignments}")
            self.stdout.write(
                f"Continuity Matches: {self.style.SUCCESS(str(match_count))}"
            )
            self.stdout.write(
                f"Continuity Score: {self.style.SUCCESS(f'{percentage:.2f}%')}"
            )

        self.stdout.write("\n=====================\n")
