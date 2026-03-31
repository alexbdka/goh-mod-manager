import subprocess
import sys
from pathlib import Path


def main():
    """
    Build script for Qt translations.
    1. Scans the `src` directory for translatable strings using pyside6-lupdate.
    2. Generates/updates .ts files in `src/ui/i18n`.
    3. Compiles .ts files into .qm files using pyside6-lrelease.
    """
    root_dir = Path(__file__).parent.parent
    src_dir = root_dir / "src"
    i18n_dir = src_dir / "ui" / "i18n"

    # Ensure the i18n directory exists
    i18n_dir.mkdir(parents=True, exist_ok=True)

    # Define supported languages
    languages = ["en_US", "fr_FR"]
    ts_files = [str(i18n_dir / f"{lang}.ts") for lang in languages]

    # Collect all Python files
    py_files = [str(p) for p in src_dir.rglob("*.py")]

    print("--- Updating translation files (.ts) ---")
    lupdate_cmd = ["pyside6-lupdate"] + py_files + ["-ts"] + ts_files

    try:
        subprocess.run(lupdate_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running pyside6-lupdate: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'pyside6-lupdate' not found.", file=sys.stderr)
        print(
            "Make sure you are in your virtual environment and PySide6 is installed.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\n--- Compiling translation files (.qm) ---")
    lrelease_cmd = ["pyside6-lrelease"] + ts_files

    try:
        subprocess.run(lrelease_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running pyside6-lrelease: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'pyside6-lrelease' not found.", file=sys.stderr)
        sys.exit(1)

    print("\nTranslations built successfully!")
    print(f"Check the {i18n_dir.relative_to(root_dir)} directory for the .qm files.")


if __name__ == "__main__":
    main()
