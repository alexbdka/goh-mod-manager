import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path

import rarfile
from py7zr import py7zr

from goh_mod_manager.infrastructure.mod_manager_logger import logger


class ModImportService:
    def import_mod(self, path: str, game_mods_directory: str | None) -> bool:
        if not self._is_valid_game_mods_directory(game_mods_directory):
            logger.error("Invalid game mods directory")
            return False

        try:
            if os.path.isdir(path):
                return self._import_from_directory(path, game_mods_directory)
            if os.path.isfile(path):
                return self._import_from_archive(path, game_mods_directory)

            logger.warning(f"Invalid path: {path}")
            return False
        except Exception as e:
            logger.error(f"Error while importing mod: {e}")
            return False

    def _import_from_directory(self, dir_path: str, game_mods_directory: str) -> bool:
        for root, _, files in os.walk(dir_path):
            if "mod.info" in files:
                return self._copy_mod_directory(root, game_mods_directory)

        logger.warning("No mod.info found in directory or subdirectories")
        return False

    def _copy_mod_directory(self, mod_dir: str, game_mods_directory: str) -> bool:
        mod_name = os.path.basename(mod_dir)
        dest = os.path.join(game_mods_directory, mod_name)

        if os.path.exists(dest):
            logger.warning(f"Mod already exists: {mod_name}")
            return False

        try:
            shutil.copytree(mod_dir, dest)
            self._mark_as_imported(dest)
            logger.info(f"Mod imported in directory: {dest}")
            return True
        except Exception as e:
            logger.error(f"Error copying mod directory: {e}")
            return False

    def _import_from_archive(self, archive_path: str, game_mods_directory: str) -> bool:
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                self._extract_archive(archive_path, temp_dir)
                return self._import_from_directory(temp_dir, game_mods_directory)
            except Exception as e:
                logger.error(f"Error importing from archive: {e}")
                return False

    @staticmethod
    def _extract_archive(archive_path: str, extract_to: str) -> None:
        ext = Path(archive_path).suffix.lower()
        os.makedirs(extract_to, exist_ok=True)

        try:
            if ext == ".zip":
                with zipfile.ZipFile(archive_path, "r") as archive:
                    archive.extractall(extract_to)
            elif ext == ".7z":
                with py7zr.SevenZipFile(archive_path, mode="r") as archive:
                    archive.extractall(path=extract_to)
            elif ext == ".rar":
                with rarfile.RarFile(archive_path) as archive:
                    archive.extractall(path=extract_to)
            elif ext in [".tar", ".gz", ".tgz", ".xz"]:
                with tarfile.open(archive_path, "r:*") as tar:
                    tar.extractall(path=extract_to)
            else:
                raise ValueError(f"Unsupported archive format: {ext}")
        except Exception as e:
            shutil.rmtree(extract_to, ignore_errors=True)
            raise RuntimeError(f"Failed to extract archive: {e}")

    @staticmethod
    def _mark_as_imported(path: str) -> None:
        marker_path = os.path.join(path, ".imported_by_mod_manager")
        try:
            with open(marker_path, "w", encoding="utf-8") as f:
                f.write("Imported by Mod Manager")
        except Exception as e:
            logger.warning(f"Could not create import marker: {e}")

    @staticmethod
    def _is_valid_game_mods_directory(path: str | None) -> bool:
        return bool(path) and os.path.exists(path)
