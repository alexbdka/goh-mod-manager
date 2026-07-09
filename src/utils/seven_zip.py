"""Thin wrapper around the bundled 7-Zip binary for archive extraction."""

import logging
import os
import subprocess
import sys
from pathlib import Path

from src.core.exceptions import ArchiveExtractionError
from src.utils.app_paths import get_resource_path

logger = logging.getLogger(__name__)


class SevenZipNotFoundError(ArchiveExtractionError):
    """Raised when the bundled 7-Zip binary cannot be located."""


class UnsupportedArchiveError(ArchiveExtractionError):
    """Raised when 7-Zip cannot identify or open the archive."""


def get_seven_zip_path() -> Path:
    """Return the platform-specific bundled 7-Zip executable path."""
    if sys.platform == "win32":
        binary = get_resource_path("res", "7zip", "windows", "7z.exe")
    else:
        binary = get_resource_path("res", "7zip", "linux", "7zz")

    if not binary.exists():
        raise SevenZipNotFoundError(f"Bundled 7-Zip binary not found: {binary}")
    return binary


def _run_seven_zip(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run the bundled 7-Zip binary with the provided arguments."""
    binary = get_seven_zip_path()
    cmd = [str(binary)] + args
    logger.debug("Running 7-Zip command: %s", " ".join(cmd))
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_list_output(output: str) -> list[str]:
    """Parse ``7z l -ba`` output and return member paths."""
    members: list[str] = []
    for line in output.splitlines():
        line = line.rstrip()
        if not line:
            continue
        # The path is the last column. ``7z l -ba`` prints:
        # Date Time Attr Size Compressed Name
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        members.append(parts[1].replace("\\", "/"))
    return members


def _validate_members(extract_to: str, members: list[str]) -> None:
    """Reject archive members that would escape the extraction directory."""
    base_path = Path(extract_to).resolve()

    for member_name in members:
        member_name = member_name.strip()
        if not member_name:
            continue

        if member_name.startswith("/") or Path(member_name).is_absolute():
            raise ArchiveExtractionError(
                f"Archive contains an absolute path entry: {member_name}"
            )

        if ".." in Path(member_name).parts:
            raise ArchiveExtractionError(
                f"Archive contains an unsafe path entry: {member_name}"
            )

        destination = (base_path / member_name).resolve()
        try:
            destination.relative_to(base_path)
        except ValueError as exc:
            raise ArchiveExtractionError(
                f"Archive contains an unsafe path entry: {member_name}"
            ) from exc


def list_archive_members(archive_path: str) -> list[str]:
    """Return the list of member paths contained in ``archive_path``."""
    result = _run_seven_zip(["l", "-ba", archive_path])
    if result.returncode != 0:
        raise UnsupportedArchiveError(
            f"Failed to list archive contents: {result.stderr or result.stdout}"
        )
    return _parse_list_output(result.stdout)


def extract_archive(archive_path: str, extract_to: str) -> None:
    """Extract ``archive_path`` into ``extract_to`` using the bundled 7-Zip.

    The extraction is performed with full paths preserved (``x`` command) and
    all prompts answered with "yes" (``-y``). Output is silenced to avoid
    polluting logs. Before extraction, member paths are validated to reject
    absolute paths and directory traversal attempts.
    """
    os.makedirs(extract_to, exist_ok=True)

    members = list_archive_members(archive_path)
    _validate_members(extract_to, members)

    result = _run_seven_zip(
        [
            "x",  # extract with full paths
            "-y",  # assume yes
            "-bso0",  # disable standard output
            "-bse0",  # disable error output
            "-bsp0",  # disable progress output
            f"-o{extract_to}",
            archive_path,
        ]
    )

    if result.returncode != 0:
        raise ArchiveExtractionError(
            f"Failed to extract archive: {result.stderr or result.stdout}"
        )
