import argparse
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> int:
    """Update Qt translation sources and compile them into runtime ``.qm`` files."""
    args = parse_args()
    root_dir = ROOT_DIR
    src_dir = root_dir / "src"
    i18n_dir = src_dir / "ui" / "i18n"

    i18n_dir.mkdir(parents=True, exist_ok=True)

    ts_files = [str(path) for path in sorted(i18n_dir.glob("*.ts"))]
    if not ts_files:
        print(
            f"Error: no translation source files found in {i18n_dir}.",
            file=sys.stderr,
        )
        return 1

    py_files = [str(p) for p in src_dir.rglob("*.py")]

    if args.update_sources:
        print("--- Updating translation files (.ts) ---")
        lupdate_cmd = (
            ["pyside6-lupdate"] + py_files + ["-no-obsolete", "-ts"] + ts_files
        )

        try:
            subprocess.run(lupdate_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running pyside6-lupdate: {e}", file=sys.stderr)
            return 1
        except FileNotFoundError:
            print("Error: 'pyside6-lupdate' not found.", file=sys.stderr)
            print(
                "Make sure the current environment has PySide6 installed.",
                file=sys.stderr,
            )
            return 1

    validation_errors = _validate_translation_tree(i18n_dir)
    if validation_errors:
        print("Translation validation failed:", file=sys.stderr)
        for error in validation_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.compile_binaries:
        print("\n--- Compiling translation files (.qm) ---")
        lrelease_cmd = ["pyside6-lrelease"] + ts_files

        try:
            subprocess.run(lrelease_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running pyside6-lrelease: {e}", file=sys.stderr)
            return 1
        except FileNotFoundError:
            print("Error: 'pyside6-lrelease' not found.", file=sys.stderr)
            return 1

    print("\nTranslations built successfully!")
    print(f"Check the {i18n_dir.relative_to(root_dir)} directory for the .qm files.")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the translation build workflow."""
    parser = argparse.ArgumentParser(
        description="Update Qt translation sources and compile runtime binaries."
    )
    parser.add_argument(
        "--no-update",
        dest="update_sources",
        action="store_false",
        default=True,
        help="Skip pyside6-lupdate and only compile existing .ts files.",
    )
    parser.add_argument(
        "--no-compile",
        dest="compile_binaries",
        action="store_false",
        default=True,
        help="Skip pyside6-lrelease.",
    )
    return parser.parse_args()


def _validate_translation_tree(i18n_dir: Path) -> list[str]:
    from src.ui.i18n_registry import validate_translation_tree

    return validate_translation_tree(i18n_dir)


if __name__ == "__main__":
    raise SystemExit(main())
