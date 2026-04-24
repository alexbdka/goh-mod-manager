import sys
from pathlib import Path


def main() -> int:
    """Validate translation file naming and Qt TS metadata conventions."""
    root_dir = Path(__file__).resolve().parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    from src.ui.i18n_registry import get_i18n_dir, validate_translation_tree

    errors = validate_translation_tree(get_i18n_dir())
    if errors:
        print("Translation validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Translation validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
