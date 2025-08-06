import os
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

import rarfile
from PySide6.QtCore import QObject, Signal
from py7zr import py7zr

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.utils.config_manager import ConfigManager
from goh_mod_manager.utils.mod_info_parser import ModInfoParser
from goh_mod_manager.utils.mod_manager_logger import logger
from goh_mod_manager.utils.options_set_parser import OptionsSetParser


class ModManagerModel(QObject):
    """Model for the mod manager application"""

    # Signals
    mods_updated = Signal()
    presets_updated = Signal()
    active_mods_count_updated = Signal(int)

    def __init__(self):
        super().__init__()
        self._config = ConfigManager()
        self._installed_mods: List[Mod] = []
        self._active_mods: List[Mod] = []
        self._presets: Dict[str, List[Mod]] = {}

    # Properties
    @property
    def config(self) -> ConfigManager:
        return self._config

    @property
    def installed_mods(self) -> List[Mod]:
        return self._installed_mods.copy()

    @property
    def active_mods(self) -> List[Mod]:
        return self._active_mods.copy()

    @property
    def active_mods_count(self) -> int:
        return len(self._active_mods)

    @property
    def preset_names(self) -> List[str]:
        return list(self._presets.keys())

    # Configuration methods
    def set_config(self, config: ConfigManager) -> None:
        """Set the configuration manager."""
        self._config = config

    def set_mods_directory(self, mods_directory: str) -> None:
        """Set the mods directory and refresh installed mods."""
        self._config.set_mods_directory(mods_directory)
        self._load_installed_mods()

    def set_options_file(self, options_file: str) -> None:
        """Set the options file and refresh active mods."""
        self._config.set_options_file(options_file)
        self._load_active_mods()

    # Preset methods
    def get_preset_mods(self, preset_name: str) -> List[Mod]:
        """Get mods for a specific preset."""
        return self._presets.get(preset_name, [])

    def has_preset(self, name: str) -> bool:
        """Check if a preset exists."""
        return name in self._presets

    def set_presets(self, presets: Dict[str, List[str]]) -> None:
        """Set presets from configuration data."""
        self._presets = {}
        for preset_name, mod_ids in presets.items():
            resolved_mods = self._resolve_preset_mods(mod_ids)
            self._presets[preset_name] = resolved_mods
        self.presets_updated.emit()

    def save_preset(self, preset_name: str) -> bool:
        """Save current active mods as a preset."""
        if not self._active_mods:
            logger.warning("Cannot save empty preset")
            return False

        self._presets[preset_name] = self._active_mods.copy()
        self._save_presets_to_config()
        self.presets_updated.emit()
        logger.info(f"Preset '{preset_name}' saved with {len(self._active_mods)} mods")
        return True

    def load_preset(self, preset_name: str) -> bool:
        """Load a preset and set it as active mods."""
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
        """Delete a preset."""
        if preset_name not in self._presets:
            logger.warning(f"Preset '{preset_name}' not found for deletion")
            return False

        del self._presets[preset_name]
        self._save_presets_to_config()
        self.presets_updated.emit()
        logger.info(f"Preset '{preset_name}' deleted")
        return True

    # Mod management methods
    def enable_mod(self, mod: Mod) -> bool:
        """Enable a mod by adding it to active mods."""
        if mod not in self._active_mods:
            self._active_mods.append(mod)
        return self._save_active_mods()

    def disable_mod(self, mod: Mod) -> bool:
        """Disable a mod by removing it from active mods."""
        if mod in self._active_mods:
            self._active_mods.remove(mod)
        return self._save_active_mods()

    def delete_mod(self, mod: Mod) -> bool:
        """Delete a mod"""
        if mod in self._installed_mods:
            self._installed_mods.remove(mod)
            try:
                mod_path = os.path.join(self._get_game_mods_directory(), str(mod.id))
                if os.path.isdir(mod_path):
                    shutil.rmtree(mod_path)
                return True
            except Exception as e:
                logger.error(f"Error while deleting mod folder: {e}")
                return False
        return False

    def set_mods_order(self, reordered_mods: List[Mod]) -> bool:
        """Set the order of active mods."""
        self._active_mods = reordered_mods.copy()
        return self._save_active_mods()

    def clear_active_mods(self) -> bool:
        """Clear all active mods."""
        try:
            parser = OptionsSetParser(self._config.get_options_file())
            parser.clear_mods_section()
            self._load_active_mods()
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while clearing mods: {e}")
            return False

    # Refresh methods
    def refresh_all(self) -> None:
        """Refresh both installed and active mods."""
        self.refresh_installed_mods()
        self.refresh_active_mods()

    def refresh_installed_mods(self) -> None:
        """Refresh the list of installed mods."""
        self._load_installed_mods()
        self.mods_updated.emit()

    def refresh_active_mods(self) -> None:
        """Refresh the list of active mods."""
        self._load_active_mods()
        self._emit_updates()

    # Import methods
    def import_mod(self, path: str) -> bool:
        """Import a mod from a directory or archive file."""
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

    # Private methods - Data loading
    def _load_installed_mods(self) -> None:
        """Load installed mods from mods directories."""
        self._installed_mods = []
        mods_directory = self._config.get_mods_directory()
        game_mods_directory = self._get_game_mods_directory()

        if not os.path.exists(mods_directory) or not os.path.exists(
            game_mods_directory
        ):
            return

        # Load from both directories
        for directory in [mods_directory, game_mods_directory]:
            for item in os.listdir(directory):
                mod_path = os.path.join(directory, item)
                if os.path.isdir(mod_path):
                    self._load_mod_from_directory(mod_path)

    def _load_mod_from_directory(self, mod_path: str) -> None:
        """Load a mod from a directory containing mod.info."""
        mod_info_file = os.path.join(mod_path, "mod.info")
        if os.path.exists(mod_info_file):
            try:
                parser = ModInfoParser(mod_info_file)
                mod = parser.parse()
                self._installed_mods.append(mod)
            except Exception as e:
                logger.error(f"Error while parsing {mod_info_file}: {e}")

    def _load_active_mods(self) -> None:
        """Load active mods from options file."""
        self._active_mods = []
        options_file = self._config.get_options_file()

        if not os.path.exists(options_file):
            return

        try:
            parser = OptionsSetParser(options_file)
            active_mod_ids = parser.get_mods()
            self._resolve_active_mods(active_mod_ids)
        except Exception as e:
            logger.error(f"Error while parsing {options_file}: {e}")

    def _resolve_active_mods(self, active_mod_ids: List[str]) -> None:
        """Resolve active mod IDs to mod objects."""
        for mod_id in active_mod_ids:
            mod = self._find_installed_mod_by_id(mod_id)
            if mod:
                self._active_mods.append(mod)
            else:
                logger.warning(
                    f"Active mod with ID '{mod_id}' not found in installed mods"
                )

    def _find_installed_mod_by_id(self, mod_id: str) -> Optional[Mod]:
        """Find an installed mod by its ID."""
        for mod in self._installed_mods:
            if mod.id == mod_id:
                return mod
        return None

    # Private methods - Data saving
    def _save_active_mods(self) -> bool:
        """Save active mods to options file."""
        try:
            parser = OptionsSetParser(self._config.get_options_file())
            parser.set_mods(self._active_mods)
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while setting mods: {e}")
            return False

    def _save_presets_to_config(self) -> None:
        """Save presets to configuration."""
        if self._config:
            config_presets = {
                name: [mod.id for mod in mods] for name, mods in self._presets.items()
            }
            self._config.set_presets(config_presets)

    # Private methods - Utilities
    def _emit_updates(self) -> None:
        """Emit update signals."""
        self.mods_updated.emit()
        self.active_mods_count_updated.emit(len(self._active_mods))

    def _resolve_preset_mods(self, mod_ids: List[str]) -> List[Mod]:
        """Resolve preset mod IDs to mod objects."""
        resolved_mods = []
        for mod_id in mod_ids:
            mod = self._find_installed_mod_by_id(mod_id)
            if mod:
                resolved_mods.append(mod)
            else:
                logger.warning(f"Mod with ID '{mod_id}' not found in installed mods")
        return resolved_mods

    def _get_game_mods_directory(self) -> str:
        """Get the game's mods directory path."""
        mods_directory = Path(self._config.get_mods_directory())
        parts = mods_directory.parts

        if "steamapps" not in parts:
            raise ValueError("No 'steamapps' directory found in mods directory path")

        idx = parts.index("steamapps")
        steam_root = Path(*parts[: idx + 1])
        game_mods_dir = steam_root / "common" / "Call to Arms - Gates of Hell" / "mods"
        return str(game_mods_dir)

    # Private methods - Import functionality
    def _import_from_directory(self, dir_path: str) -> bool:
        """Import a mod from a directory."""
        for root, dirs, files in os.walk(dir_path):
            if "mod.info" in files:
                return self._copy_mod_directory(root)

        logger.warning("No mod.info found in directory or subdirectories")
        return False

    def _copy_mod_directory(self, mod_dir: str) -> bool:
        """Copy a mod directory to the game mods directory."""
        mod_name = os.path.basename(mod_dir)
        dest_dir = self._get_game_mods_directory()
        dest = os.path.join(dest_dir, mod_name)

        if os.path.exists(dest):
            logger.warning(f"Mod already exists: {mod_name}")
            return False

        shutil.copytree(mod_dir, dest)
        self._mark_as_imported(dest)
        logger.info(f"Mod imported in directory: {dest}")
        self.refresh_installed_mods()
        return True

    def _import_from_archive(self, archive_path: str) -> bool:
        """Import a mod from an archive file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self._extract_archive(archive_path, temp_dir)
            self._mark_as_imported(temp_dir)
            return self._import_from_directory(temp_dir)

    @staticmethod
    def _extract_archive(archive_path: str, extract_to: str) -> None:
        """Extract an archive to a directory."""
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
        """Mark a directory as imported by the mod manager."""
        marker = os.path.join(path, ".imported_by_mod_manager")
        with open(marker, "w") as f:
            f.write("Imported by Mod Manager")
