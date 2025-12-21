import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from praktikums_lehrkraft.services import import_pls_from_csv


def main():
    """
    Main function to run the debug script.
    """
    csv_file_name = "Example_Data.xlsx"  # Changed to .xlsx
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, csv_file_name)

    print(f"--- Attempting to open file: {csv_file_path} ---")

    if not os.path.exists(csv_file_path):
        print(f"❌ ERROR: '{csv_file_name}' not found in the backend directory.")
        return

    try:
        # Open the file in binary read mode ('rb')
        with open(csv_file_path, "rb") as file_obj:
            results = import_pls_from_csv(file_obj)

        print("\n--- SCRIPT FINISHED ---")
        print("Results:")
        print(results)

    except Exception as e:
        print("\n--- A CRITICAL ERROR OCCURRED OUTSIDE THE SCRIPT ---")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
