import argparse
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

APP_NAME = "GoH Mod Manager"


def main() -> int:
    """Run local validation steps and build the packaged app with PyInstaller."""
    args = parse_args()
    root_dir = Path(__file__).resolve().parent.parent

    if args.translations:
        run([sys.executable, "scripts/build_translations.py"], root_dir)

    if args.tests:
        run(
            [sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts"],
            root_dir,
        )
        run([sys.executable, "-m", "pytest", "-q"], root_dir)

    pyinstaller_args = build_pyinstaller_args(root_dir, args)
    run([sys.executable, "-m", "PyInstaller", *pyinstaller_args], root_dir)

    if args.package:
        package_build(root_dir, args.name, args.onefile)

    print_build_summary(root_dir, args.name, args.onefile, args.package)
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the local PyInstaller wrapper."""
    parser = argparse.ArgumentParser(
        description="Build GoH Mod Manager locally with PyInstaller."
    )
    build_mode = parser.add_mutually_exclusive_group()
    build_mode.add_argument(
        "--onefile",
        action="store_true",
        default=True,
        help="Build a single executable. This matches CI and is the default.",
    )
    build_mode.add_argument(
        "--onedir",
        dest="onefile",
        action="store_false",
        help="Build a directory-based app bundle. This matches the README examples.",
    )
    parser.add_argument(
        "--name",
        default=APP_NAME,
        help=f"Executable name to pass to PyInstaller. Default: {APP_NAME}.",
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Create a zip archive in out/ after a successful onefile build.",
    )
    parser.add_argument(
        "--skip-tests",
        dest="tests",
        action="store_false",
        default=True,
        help="Skip compileall and pytest before building.",
    )
    parser.add_argument(
        "--skip-translations",
        dest="translations",
        action="store_false",
        default=True,
        help="Skip rebuilding Qt translation files before building.",
    )
    return parser.parse_args()


def build_pyinstaller_args(root_dir: Path, args: argparse.Namespace) -> list[str]:
    """Build the PyInstaller argument list for the current platform."""
    add_data_separator = ";" if is_windows() else ":"
    icon_path = (
        root_dir / "assets" / "icons" / "logo.ico"
        if is_windows()
        else root_dir / "assets" / "icons" / "logo.png"
    )

    pyinstaller_args = [
        "--onefile" if args.onefile else "--onedir",
        "--clean",
        "--windowed",
        "--paths",
        ".",
        "--name",
        args.name,
        "--icon",
        str(icon_path),
        "--add-data",
        add_data("assets/icons", "assets/icons", add_data_separator),
        "--add-data",
        add_data("assets/fonts", "assets/fonts", add_data_separator),
        "--add-data",
        add_data(".app-version", ".", add_data_separator),
    ]

    if list((root_dir / "src" / "ui" / "i18n").glob("*.qm")):
        pyinstaller_args.extend(
            [
                "--add-data",
                add_data("src/ui/i18n/*.qm", "src/ui/i18n", add_data_separator),
            ]
        )

    pyinstaller_args.append("src/main.py")
    return pyinstaller_args


def add_data(source: str, destination: str, separator: str) -> str:
    """Format a PyInstaller ``--add-data`` argument."""
    return f"{source}{separator}{destination}"


def package_build(root_dir: Path, app_name: str, onefile: bool) -> None:
    """Package a onefile build into a zip archive under ``out/``."""
    if not onefile:
        raise SystemExit("--package is only supported with --onefile builds.")

    executable = root_dir / "dist" / executable_name(app_name)
    if not executable.exists():
        raise SystemExit(f"Missing build output: {executable}")

    out_dir = root_dir / "out"
    out_dir.mkdir(exist_ok=True)
    archive_path = out_dir / archive_name(app_name)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(executable, executable.name)


def print_build_summary(
    root_dir: Path, app_name: str, onefile: bool, packaged: bool
) -> None:
    """Print the generated build and package paths for local use."""
    output_path = (
        root_dir / "dist" / executable_name(app_name)
        if onefile
        else root_dir / "dist" / app_name
    )
    print(f"Build output: {output_path}")
    if packaged:
        print(f"Package output: {root_dir / 'out' / archive_name(app_name)}")


def run(command: list[str], cwd: Path) -> None:
    """Run a subprocess in the repository root and echo the command."""
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def executable_name(app_name: str) -> str:
    """Return the platform-specific executable file name."""
    return f"{app_name}.exe" if is_windows() else app_name


def archive_name(app_name: str) -> str:
    """Return the packaged zip file name for the current platform."""
    os_id = "windows" if is_windows() else "linux"
    return f"{app_name}-{os_id}-x64.zip"


def is_windows() -> bool:
    """Return ``True`` when running on Windows."""
    return platform.system() == "Windows"


if __name__ == "__main__":
    raise SystemExit(main())
