import os
import django

# --- SETUP DJANGO ---
# This allows us to use Django models in a standalone script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
# --------------------

from praktikums_lehrkraft.services import import_pls_from_csv


def main():
    """
    Main function to run the excel import script.
    """
    # Name of your file in the backend directory
    excel_file_name = "Example_Data.xlsx"

    # Locate file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, excel_file_name)

    print(f"--- Attempting to open file: {file_path} ---")

    if not os.path.exists(file_path):
        print(f"❌ ERROR: '{excel_file_name}' not found in the backend directory.")
        return

    try:
        # Open the file in binary read mode ('rb') for pandas/openpyxl
        with open(file_path, "rb") as file_obj:
            results = import_pls_from_csv(file_obj)

        print("\n--- SCRIPT FINISHED ---")
        print("Results:")
        print(results)

    except Exception as e:
        print("\n--- A CRITICAL ERROR OCCURRED ---")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
