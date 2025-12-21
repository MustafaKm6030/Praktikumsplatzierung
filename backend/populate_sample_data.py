import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from subjects.models import Subject, PraktikumType
from system_settings.models import SystemSettings


def create_sample_data():
    """
    Populates the database with the static reference data (Subjects, Types, Settings).
    Does NOT create Schools, Teachers, or Students.
    """
    print("--- Starting Reference Data Population ---")

    # --- 1. Create Subjects ---
    print("\n1. Creating Subjects...")
    subjects_data = [
        ("D", "Deutsch"),
        ("MA", "Mathematik"),
        ("E", "Englisch"),
        ("MU", "Musik"),
        ("SP", "Sport"),
        ("GE", "Geschichte"),
        ("HSU", "Heimat- und Sachunterricht"),
        ("SK/PuG", "Sozialkunde/Politik und Gesellschaft"),
        ("PCB", "Physik/Chemie/Biologie"),
        ("DaZ", "Deutsch als Zweitsprache"),
        ("KRel", "Kath. Religion"),
        ("GEO", "Geographie"),
        ("KE", "Kunsterziehung"),
        ("AL/WiB", "Arbeitslehre"),
        ("IT", "Informatik"),
        ("SSE", "Schriftspracherwerb"),
        ("GSE/GPG", "Geschichte/Sozialkunde/Erdkunde"),
        ("GU", "Grundlegender Unterricht"),
    ]

    for code, name in subjects_data:
        subject, created = Subject.objects.update_or_create(
            code=code, defaults={"name": name}
        )
        if created:
            print(f"   Created Subject: {name}")

    # --- 2. Create Praktikum Types ---
    print("\n2. Creating Praktikum Types...")
    praktikum_types_data = [
        ("PDP_I", "Pädagogisch-didaktisches Praktikum I", True),
        ("PDP_II", "Pädagogisch-didaktisches Praktikum II", True),
        ("SFP", "Studienbegleitendes Fachpraktikum", False),
        ("ZSP", "Zusätzliches studienbegleitendes Praktikum", False),
    ]

    for code, name, is_block in praktikum_types_data:
        pt, created = PraktikumType.objects.update_or_create(
            code=code, defaults={"name": name, "is_block_praktikum": is_block}
        )
        if created:
            print(f"   Created Type: {name}")

    # --- 3. Create System Settings ---
    print("\n3. Creating System Settings...")
    SystemSettings.objects.update_or_create(
        current_academic_year="2024/2025",
        defaults={"total_anrechnungsstunden_budget": 210.0, "is_active": True},
    )
    print("   System Settings updated.")

    print("\n✅ Reference data creation complete!")


if __name__ == "__main__":
    create_sample_data()
