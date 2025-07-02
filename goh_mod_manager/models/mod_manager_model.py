import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import List, Dict

import rarfile
from PySide6.QtCore import QObject, Signal
from py7zr import py7zr

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.utils.config_manager import ConfigManager
from goh_mod_manager.utils.mod_info_parser import ModInfoParser
from goh_mod_manager.utils.mod_manager_logger import logger
from goh_mod_manager.utils.options_set_parser import OptionsSetParser


class ModManagerModel(QObject):
    # Signals
    mods_updated = Signal()
    presets_updated = Signal()
    active_mods_count_updated = Signal(int)

    def __init__(self):
        super().__init__()
        self._mods_directory = ""
        self._options_file = ""
        self._installed_mods = []
        self._active_mods = []
        self._presets = {}
        self._config = None

    # Properties and getters
    def get_mods_directory(self) -> str:
        return self._mods_directory

    def get_options_file(self) -> str:
        return self._options_file

    def get_installed_mods(self) -> List[Mod]:
        return self._installed_mods.copy()

    def get_active_mods(self) -> List[Mod]:
        return self._active_mods.copy()

    def get_active_mods_count(self) -> int:
        return len(self._active_mods)

    def get_presets(self) -> Dict[str, List[str]]:
        return {name: [mod.id for mod in mods] for name, mods in self._presets.items()}

    def get_preset_names(self) -> List[str]:
        return list(self._presets.keys())

    def get_preset_mods(self, preset_name: str) -> list:
        if preset_name in self._presets:
            return self._presets[preset_name]
        return []

    def has_preset(self, name: str) -> bool:
        return name in self._presets

    def set_config(self, config: ConfigManager):
        self._config = config

    # Configuration methods
    def set_mods_directory(self, mods_directory: str):
        self._mods_directory = mods_directory
        self._load_installed_mods()

    def set_options_file(self, options_file: str):
        self._options_file = options_file
        self._load_active_mods()

    def set_presets(self, presets: Dict[str, List[str]]):
        self._presets = {}
        for preset_name, mod_ids in presets.items():
            resolved_mods = self._resolve_preset_mods(mod_ids)
            self._presets[preset_name] = resolved_mods
        self.presets_updated.emit()

    # Core mod management
    def refresh_all(self):
        self._load_installed_mods()
        self._load_active_mods()
        self._emit_updates()

    def refresh_installed_mods(self):
        self._load_installed_mods()
        self.mods_updated.emit()

    def refresh_active_mods(self):
        self._load_active_mods()
        self._emit_updates()

    def enable_mod(self, mod: Mod) -> bool:
        if mod not in self._active_mods:
            self._active_mods.append(mod)
        return self._save_active_mods()

    def disable_mod(self, mod: Mod) -> bool:
        if mod in self._active_mods:
            self._active_mods.remove(mod)
        return self._save_active_mods()

    def set_mods_order(self, reordered_mods: List[Mod]) -> bool:
        self._active_mods = reordered_mods.copy()
        return self._save_active_mods()

    def clear_active_mods(self) -> bool:
        try:
            parser = OptionsSetParser(self._options_file)
            parser.clear_mods_section()
            self._load_active_mods()
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while clearing mods: {e}")
            return False

    # Preset management
    def save_preset(self, preset_name: str) -> bool:
        if not self._active_mods:
            logger.warning("Cannot save empty preset")
            return False

        self._presets[preset_name] = self._active_mods.copy()
        self._save_presets_to_config()
        self.presets_updated.emit()
        logger.info(f"Preset '{preset_name}' saved with {len(self._active_mods)} mods")
        return True

    def load_preset(self, preset_name: str) -> bool:
        if preset_name not in self._presets:
            logger.error(f"Preset '{preset_name}' not found")
            return False

        preset_mods = self._presets[preset_name]
        self.clear_active_mods()
        if preset_mods:
            self.set_mods_order(preset_mods)
            logger.info(f"Preset '{preset_name}' loaded with {len(preset_mods)} mods")
        return True

    def delete_preset(self, preset_name: str) -> bool:
        if preset_name not in self._presets:
            logger.warning(f"Preset '{preset_name}' not found for deletion")
            return False

        del self._presets[preset_name]
        self._save_presets_to_config()
        self.presets_updated.emit()
        logger.info(f"Preset '{preset_name}' deleted")
        return True

    # Import functionality
    def import_mod(self, path: str) -> bool:
        try:
            if os.path.isdir(path):
                return self._import_from_directory(path)
            elif os.path.isfile(path):
                return self._import_from_archive(path)
            else:
                logger.warning(f"Invalid path: {path}")
                return False
        except Exception as e:
            logger.error(f"Error while importing mod: {e}")
            return False

    # Private methods
    def _load_installed_mods(self):
        self._installed_mods = []

        if not os.path.exists(self._mods_directory):
            return

        for item in os.listdir(self._mods_directory):
            mod_path = os.path.join(self._mods_directory, item)
            if os.path.isdir(mod_path):
                mod_info_file = os.path.join(mod_path, "mod.info")
                if os.path.exists(mod_info_file):
                    try:
                        parser = ModInfoParser(mod_info_file)
                        mod = parser.parse()
                        self._installed_mods.append(mod)
                    except Exception as e:
                        logger.error(f"Error while parsing {mod_info_file}: {e}")

    def _load_active_mods(self):
        self._active_mods = []

        if not os.path.exists(self._options_file):
            return

        try:
            parser = OptionsSetParser(self._options_file)
            active_mod_ids = parser.get_mods()

            for mod_id in active_mod_ids:
                for mod in self._installed_mods:
                    if mod.id == mod_id:
                        self._active_mods.append(mod)
                        break
                else:
                    logger.warning(
                        f"Active mod with ID '{mod_id}' not found in installed mods"
                    )

        except Exception as e:
            logger.error(f"Error while parsing {self._options_file}: {e}")

    def _save_active_mods(self) -> bool:
        try:
            parser = OptionsSetParser(self._options_file)
            parser.set_mods(self._active_mods)
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while setting mods: {e}")
            return False

    def _emit_updates(self):
        self.mods_updated.emit()
        self.active_mods_count_updated.emit(len(self._active_mods))

    def _resolve_preset_mods(self, mod_ids: List[str]) -> List[Mod]:
        resolved_mods = []
        for mod_id in mod_ids:
            for installed_mod in self._installed_mods:
                if installed_mod.id == mod_id:
                    resolved_mods.append(installed_mod)
                    break
            else:
                logger.warning(f"Mod with ID '{mod_id}' not found in installed mods")
        return resolved_mods

    def _save_presets_to_config(self):
        if self._config:
            config_presets = {
                name: [mod.id for mod in mods] for name, mods in self._presets.items()
            }
            self._config.set_presets(config_presets)

    def _import_from_directory(self, dir_path: str) -> bool:
        for root, dirs, files in os.walk(dir_path):
            if "mod.info" in files:
                mod_dir = root
                mod_name = os.path.basename(mod_dir)
                dest = os.path.join(self._mods_directory, mod_name)

                if os.path.exists(dest):
                    logger.warning(f"Mod already exists: {mod_name}")
                    return False

                shutil.copytree(mod_dir, dest)
                self._mark_as_imported(dest)
                logger.info(f"Mod imported in directory: {dest}")
                self.refresh_installed_mods()
                return True

        logger.warning("No mod.info found in directory or subdirectories")
        return False

    def _import_from_archive(self, archive_path: str) -> bool:
        with tempfile.TemporaryDirectory() as temp_dir:
            self._extract_archive(archive_path, temp_dir)
            self._mark_as_imported(temp_dir)
            return self._import_from_directory(temp_dir)

    @staticmethod
    def _extract_archive(archive_path: str, extract_to: str):
        ext = Path(archive_path).suffix.lower()
        os.makedirs(extract_to, exist_ok=True)

        try:
            if ext == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(extract_to)
            elif ext in [".tar", ".gz", ".tgz", ".xz"]:
                with tarfile.open(archive_path, "r:*") as tar:
                    tar.extractall(path=extract_to)
            elif ext == ".7z":
                with py7zr.SevenZipFile(archive_path, mode="r") as sevenzip:
                    sevenzip.extractall(path=extract_to)
            elif ext == ".rar":
                with rarfile.RarFile(archive_path) as rf:
                    rf.extractall(path=extract_to)
            else:
                raise ValueError(f"Unsupported archive format: {ext}")
        except Exception as e:
            shutil.rmtree(extract_to, ignore_errors=True)
            raise RuntimeError(f"Failed to extract archive: {e}")

    @staticmethod
    def _mark_as_imported(path: str):
        marker = os.path.join(path, ".imported_by_mod_manager")
        with open(marker, "w") as f:
            f.write("Imported by Mod Manager")
