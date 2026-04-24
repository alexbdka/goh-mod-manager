import logging
import os
import shutil
import tarfile
import tempfile
import zipfile
from collections.abc import Iterable
from pathlib import Path

import rarfile
from py7zr import py7zr

from src.core import constants
from src.core.exceptions import (
    ArchiveExtractionError,
    InvalidModPathError,
    ModAlreadyExistsError,
    ModInfoNotFoundError,
)

logger = logging.getLogger(__name__)


class ModImportService:
    """
    Import mods from directories or archives into the local mods directory.

    The service locates the imported mod root by finding ``mod.info`` and then
    copies that root directory into the game's local ``mods`` folder.
    """

    def import_mod(
        self,
        path: str,
        game_mods_directory: str,
        progress_callback=None,
        conflict_callback=None,
    ) -> bool:
        """
        Import a mod from a directory or archive path.

        Returns ``True`` on success and raises a ``ModImportError`` subclass on
        failure.
        """
        if not game_mods_directory or not os.path.exists(game_mods_directory):
            raise InvalidModPathError(
                f"Invalid game mods directory: {game_mods_directory}"
            )

        if os.path.isdir(path):
            return self._import_from_directory(
                path, game_mods_directory, progress_callback, conflict_callback
            )
        if os.path.isfile(path):
            return self._import_from_archive(
                path, game_mods_directory, progress_callback, conflict_callback
            )

        raise InvalidModPathError(
            f"Invalid path, neither a file nor a directory: {path}"
        )

    def _import_from_directory(
        self,
        dir_path: str,
        game_mods_directory: str,
        progress_callback=None,
        conflict_callback=None,
    ) -> bool:
        """Search recursively for ``mod.info`` and copy the containing mod root."""
        if progress_callback:
            progress_callback(0, "Searching for mod.info...")

        for root, _, files in os.walk(dir_path):
            if constants.MOD_INFO_FILE in files:
                return self._copy_mod_directory(
                    root, game_mods_directory, progress_callback, conflict_callback
                )

        raise ModInfoNotFoundError(
            f"No '{constants.MOD_INFO_FILE}' found in directory "
            f"or subdirectories of {dir_path}"
        )

    def _copy_mod_directory(
        self,
        mod_dir: str,
        game_mods_directory: str,
        progress_callback=None,
        conflict_callback=None,
    ) -> bool:
        """Copy a resolved mod directory into the destination mods folder."""
        mod_name = os.path.basename(mod_dir)
        dest = os.path.join(game_mods_directory, mod_name)
        overwrite_existing = False

        if os.path.exists(dest):
            if conflict_callback:
                action = conflict_callback(mod_name)
                if action == "overwrite":
                    overwrite_existing = True
                elif action == "skip":
                    return True
                else:
                    raise ModAlreadyExistsError(
                        f"Mod already exists in destination: {mod_name}"
                    )
            else:
                raise ModAlreadyExistsError(
                    f"Mod already exists in destination: {mod_name}"
                )

        total_files = 0
        if progress_callback:
            progress_callback(50, "Counting files...")
            for _, _, files in os.walk(mod_dir):
                total_files += len(files)

        copied_files = 0

        def copy_function(src, dst):
            shutil.copy2(src, dst)
            nonlocal copied_files
            copied_files += 1
            if progress_callback and total_files > 0:
                percent = 50 + int((copied_files / total_files) * 49)
                progress_callback(
                    percent, f"Copying files... ({copied_files}/{total_files})"
                )

        temp_root = tempfile.mkdtemp(
            dir=game_mods_directory, prefix=f".{mod_name}.import-"
        )
        temp_dest = os.path.join(temp_root, mod_name)
        backup_dest = None

        try:
            shutil.copytree(mod_dir, temp_dest, copy_function=copy_function)
            if overwrite_existing:
                backup_dest = tempfile.mkdtemp(
                    dir=game_mods_directory, prefix=f".{mod_name}.backup-"
                )
                shutil.rmtree(backup_dest)
                # Swap the existing install out of the way only after the
                # replacement was copied successfully to a temporary location.
                os.replace(dest, backup_dest)

            os.replace(temp_dest, dest)

            if backup_dest and os.path.exists(backup_dest):
                shutil.rmtree(backup_dest, ignore_errors=True)

            if progress_callback:
                progress_callback(100, "Done")
            logger.info(f"Mod imported successfully to: {dest}")
            return True
        except Exception as e:
            logger.error(f"Error copying mod directory: {e}")
            if backup_dest and os.path.exists(backup_dest) and not os.path.exists(dest):
                os.replace(backup_dest, dest)
            raise
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)
            if backup_dest and os.path.exists(backup_dest):
                shutil.rmtree(backup_dest, ignore_errors=True)

    def _import_from_archive(
        self,
        archive_path: str,
        game_mods_directory: str,
        progress_callback=None,
        conflict_callback=None,
    ) -> bool:
        """Extract an archive to a temporary directory, then import from there."""
        if progress_callback:
            progress_callback(0, "Extracting archive...")

        with tempfile.TemporaryDirectory() as temp_dir:
            self._extract_archive(archive_path, temp_dir)
            return self._import_from_directory(
                temp_dir, game_mods_directory, progress_callback, conflict_callback
            )

    @staticmethod
    def _extract_archive(archive_path: str, extract_to: str) -> None:
        """Extract an archive after validating that all members stay in bounds."""
        ext = Path(archive_path).suffix.lower()
        os.makedirs(extract_to, exist_ok=True)

        try:
            if ext == ".zip":
                with zipfile.ZipFile(archive_path, "r") as archive:
                    ModImportService._validate_archive_members(
                        extract_to, (info.filename for info in archive.infolist())
                    )
                    archive.extractall(extract_to)
            elif ext == ".7z":
                with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                    ModImportService._validate_archive_members(
                        extract_to, archive.getnames()
                    )
                    archive.extractall(path=extract_to)
            elif ext == ".rar":
                with rarfile.RarFile(archive_path) as archive:
                    ModImportService._validate_archive_members(
                        extract_to, archive.namelist()
                    )
                    archive.extractall(path=extract_to)
            elif ext in [".tar", ".gz", ".tgz", ".xz"]:
                with tarfile.open(archive_path, "r:*") as tar:
                    members = tar.getmembers()
                    ModImportService._validate_archive_members(
                        extract_to, (member.name for member in members)
                    )
                    for member in members:
                        if member.issym() or member.islnk():
                            raise ArchiveExtractionError(
                                "Archive contains unsupported link entry: "
                                f"{member.name}"
                            )
                    tar.extractall(path=extract_to)
            else:
                raise ValueError(f"Unsupported archive format: {ext}")
        except Exception as e:
            raise ArchiveExtractionError(f"Failed to extract archive: {e}") from e

    @staticmethod
    def _validate_archive_members(extract_to: str, member_names: Iterable[str]) -> None:
        """Reject archive members that would escape the extraction directory."""
        base_path = Path(extract_to).resolve()

        for raw_name in member_names:
            member_name = str(raw_name).replace("\\", "/").strip()
            if not member_name:
                continue

            member_path = Path(member_name)
            if member_path.is_absolute():
                raise ArchiveExtractionError(
                    f"Archive contains an absolute path entry: {member_name}"
                )

            destination = (base_path / member_path).resolve()
            try:
                destination.relative_to(base_path)
            except ValueError as exc:
                raise ArchiveExtractionError(
                    f"Archive contains an unsafe path entry: {member_name}"
                ) from exc
