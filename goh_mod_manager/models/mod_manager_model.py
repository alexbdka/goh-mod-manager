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
    """
    Core model for the Gates of Hell mod manager application.

    Handles mod installation, activation, presets, and configuration management.
    Provides signal-based updates for UI components.
    """

    # Qt Signals for UI updates
    installed_mods_signal = Signal()
    presets_signal = Signal()
    mods_counter_signal = Signal(int)

    def __init__(self):
        """Initialize the mod manager with empty collections and configuration."""
        super().__init__()
        self._config = ConfigManager()
        self._installed_mods: List[Mod] = []
        self._active_mods: List[Mod] = []
        self._presets: Dict[str, List[Mod]] = {}

    # ================== PROPERTIES ==================

    def get_config(self) -> ConfigManager:
        """Get the configuration manager instance."""
        return self._config

    def get_installed_mods(self) -> List[Mod]:
        """Get a copy of all installed mods."""
        return self._installed_mods.copy()

    def get_active_mods(self) -> List[Mod]:
        """Get a copy of currently active mods in load order."""
        return self._active_mods.copy()

    def get_active_mods_count(self) -> int:
        """Get the number of currently active mods."""
        return len(self._active_mods)

    def get_presets_names(self) -> List[str]:
        """Get a list of all preset names."""
        return list(self._presets.keys())

    # ================== CONFIGURATION ==================

    def set_mods_directory(self, mods_directory: str) -> None:
        """
        Set the mods directory path and refresh installed mods.

        Args:
            mods_directory: Path to the directory containing mod files
        """
        self._config.set_mods_directory(mods_directory)
        self._load_installed_mods()

    def set_game_directory(self, game_directory: str) -> None:
        """
        Set the game directory path.

        Args:
            game_directory: Path to the game's installation directory
        """
        self._config.set_game_directory(game_directory)

    def set_options_file(self, options_file: str) -> None:
        """
        Set the options file path and refresh active mods.

        Args:
            options_file: Path to the game's options.set file
        """
        self._config.set_options_file(options_file)
        self._load_active_mods()

    # ================== PRESET MANAGEMENT ==================

    def get_preset_mods(self, preset_name: str) -> List[Mod]:
        """
        Get mods for a specific preset.

        Args:
            preset_name: Name of the preset

        Returns:
            List of mods in the preset, empty if preset doesn't exist
        """
        return self._presets.get(preset_name, [])

    def has_preset(self, preset_name: str) -> bool:
        """Check if a preset exists."""
        return preset_name in self._presets

    def set_presets(self, presets: Dict[str, List[str]]) -> None:
        """
        Load presets from configuration data.

        Args:
            presets: Dictionary mapping preset names to mod ID lists
        """
        self._presets = {}
        for preset_name, mod_ids in presets.items():
            resolved_mods = self._resolve_preset_mods(mod_ids)
            self._presets[preset_name] = resolved_mods
        self.presets_signal.emit()

    def save_preset(self, preset_name: str) -> bool:
        """
        Save current active mods as a new preset.

        Args:
            preset_name: Name for the new preset

        Returns:
            True if preset was saved successfully, False if no active mods
        """
        if not self._active_mods:
            logger.warning("Cannot save empty preset")
            return False

        self._presets[preset_name] = self._active_mods.copy()
        self._save_presets_to_config()
        self.presets_signal.emit()
        logger.info(f"Preset '{preset_name}' saved with {len(self._active_mods)} mods")
        return True

    def load_preset(self, preset_name: str) -> bool:
        """
        Load a preset and activate its mods.

        Args:
            preset_name: Name of the preset to load

        Returns:
            True if preset was loaded successfully, False if preset doesn't exist
        """
        if preset_name not in self._presets:
            logger.error(f"Preset '{preset_name}' not found")
            return False

        preset_mods = self._presets[preset_name]
        self.clear_active_mods()

        self.set_mods_order(preset_mods)
        logger.info(f"Preset '{preset_name}' loaded with {len(preset_mods)} mods")
        return True

    def delete_preset(self, preset_name: str) -> bool:
        """
        Delete a preset.

        Args:
            preset_name: Name of the preset to delete

        Returns:
            True if preset was deleted, False if preset doesn't exist
        """
        if preset_name not in self._presets:
            logger.error(f"Preset '{preset_name}' not found")
            return False

        del self._presets[preset_name]
        self._save_presets_to_config()
        self.presets_signal.emit()
        logger.info(f"Preset '{preset_name}' deleted")
        return True

    # ================== MOD MANAGEMENT ==================

    def enable_mod(self, mod: Mod) -> bool:
        """
        Enable a mod by adding it to the active mods list.

        Args:
            mod: The mod to enable

        Returns:
            True if mod was successfully enabled
        """
        if mod not in self._active_mods:
            self._active_mods.append(mod)
        return self._save_active_mods()

    def disable_mod(self, mod: Mod) -> bool:
        """
        Disable a mod by removing it from the active mods list.

        Args:
            mod: The mod to disable

        Returns:
            True if mod was successfully disabled
        """
        if mod in self._active_mods:
            self._active_mods.remove(mod)
        return self._save_active_mods()

    def delete_mod(self, mod: Mod) -> bool:
        """
        Permanently delete a mod from the system.

        Args:
            mod: The mod to delete

        Returns:
            True if mod was successfully deleted
        """
        if mod not in self._installed_mods:
            return False

        self._installed_mods.remove(mod)

        try:
            mod_path = os.path.join(self._get_game_mods_directory(), str(mod.id))
            if os.path.isdir(mod_path):
                shutil.rmtree(mod_path)
            return True
        except Exception as e:
            logger.error(f"Error while deleting mod folder: {e}")
            return False

    def set_mods_order(self, reordered_mods: List[Mod]) -> bool:
        """
        Set the load order of active mods.

        Args:
            reordered_mods: List of mods in desired order

        Returns:
            True if the order was successfully updated
        """
        self._active_mods = reordered_mods.copy()
        return self._save_active_mods()

    def clear_active_mods(self) -> bool:
        """
        Disable all active mods.

        Returns:
            True if mods were successfully cleared
        """
        try:
            parser = OptionsSetParser(self._config.get_options_file())
            parser.clear_mods_section()
            self._load_active_mods()
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while clearing mods: {e}")
            return False

    # ================== REFRESH OPERATIONS ==================

    def refresh_all(self) -> None:
        """Refresh both installed and active mods from their sources."""
        self.refresh_installed_mods()
        self.refresh_active_mods()

    def refresh_installed_mods(self) -> None:
        """Refresh the list of installed mods from the filesystem."""
        self._load_installed_mods()
        self.installed_mods_signal.emit()

    def refresh_active_mods(self) -> None:
        """Refresh the list of active mods from the options file."""
        self._load_active_mods()
        self._emit_updates()

    # ================== MOD IMPORT ==================

    def import_mod(self, path: str) -> bool:
        """
        Import a mod from a directory or archive file.

        Args:
            path: Path to the archive file

        Returns:
            True if mod was successfully imported
        """
        if not self._is_valid_game_mods_directory(self._get_game_mods_directory()):
            logger.error("Invalid game mods directory")
            return False

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

    # ================== PRIVATE METHODS - DATA LOADING ==================

    def _load_installed_mods(self) -> None:
        """
        Scan mod directories and load all installed mods.

        Scans both the configured mods directory and the game's mods directory.
        """
        self._installed_mods = []
        mods_directory = self._config.get_mods_directory()
        game_mods_directory = self._get_game_mods_directory()

        directories_to_scan = []

        # Add the main mods directory if it exists
        if mods_directory and os.path.exists(mods_directory):
            directories_to_scan.append(mods_directory)

        # Add the game mods directory if it exists and is valid
        if self._is_valid_game_mods_directory(game_mods_directory):
            directories_to_scan.append(game_mods_directory)

        # Scan each directory for mod folders
        for directory in directories_to_scan:
            for item in os.listdir(directory):
                mod_path = os.path.join(directory, item)
                if os.path.isdir(mod_path):
                    self._load_mod_from_directory(mod_path)

    def _load_mod_from_directory(self, mod_path: str) -> None:
        """
        Load a mod from its directory.

        Args:
            mod_path: Path to the mod directory containing mod.info
        """
        mod_info_file = os.path.join(mod_path, "mod.info")

        if not os.path.exists(mod_info_file):
            return

        try:
            parser = ModInfoParser(mod_info_file)
            mod = parser.parse()
            self._installed_mods.append(mod)
        except Exception as e:
            logger.error(f"Error while parsing {mod_info_file}: {e}")

    def _load_active_mods(self) -> None:
        """
        Load active mods from the game's options file.

        Parses the options file to get active mod IDs and resolves them
        to mod objects from the installed mods list.
        """
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
        """
        Resolve mod IDs to mod objects and populate the active mods list.

        Args:
            active_mod_ids: List of mod IDs from the options file
        """
        for mod_id in active_mod_ids:
            mod = self._find_installed_mod_by_id(mod_id)
            if mod:
                self._active_mods.append(mod)
            else:
                logger.warning(
                    f"Active mod with ID '{mod_id}' not found in installed mods"
                )

    def _find_installed_mod_by_id(self, mod_id: str) -> Optional[Mod]:
        """
        Find an installed mod by its ID.

        Args:
            mod_id: The mod ID to search for

        Returns:
            The mod object if found, None otherwise
        """
        for mod in self._installed_mods:
            if mod.id == mod_id:
                return mod
        return None

    # ================== PRIVATE METHODS - DATA SAVING ==================

    def _save_active_mods(self) -> bool:
        """
        Save the current active mods list to the options file.

        Returns:
            True if mods were successfully saved
        """
        try:
            parser = OptionsSetParser(self._config.get_options_file())
            parser.set_mods(self._active_mods)
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while setting mods: {e}")
            return False

    def _save_presets_to_config(self) -> None:
        """Save current presets to the configuration manager."""
        if not self._config:
            return

        # Convert mod objects to mod IDs for serialization
        config_presets = {
            name: [mod.id for mod in mods] for name, mods in self._presets.items()
        }
        self._config.set_presets(config_presets)

    # ================== PRIVATE METHODS - UTILITIES ==================

    def _emit_updates(self) -> None:
        """Emit Qt signals to update UI components."""
        self.installed_mods_signal.emit()
        self.mods_counter_signal.emit(len(self._active_mods))

    def _resolve_preset_mods(self, mod_ids: List[str]) -> List[Mod]:
        """
        Resolve a list of mod IDs to mod objects for presets.

        Args:
            mod_ids: List of mod IDs from preset configuration

        Returns:
            List of resolved mod objects
        """
        resolved_mods = []
        for mod_id in mod_ids:
            mod = self._find_installed_mod_by_id(mod_id)
            if mod:
                resolved_mods.append(mod)
            else:
                logger.warning(f"Mod with ID '{mod_id}' not found in installed mods")
        return resolved_mods

    def _get_game_mods_directory(self) -> str:
        """
        Derive the game's mods directory from the configured mods directory.

        Assumes Steam installation structure and navigates to the game's
        actual mods directory from the Steam library path.

        Returns:
            Path to the game's mods directory, empty string if not found
        """
        mods_directory = Path(self._config.get_mods_directory())
        parts = mods_directory.parts

        if "steamapps" not in parts:
            return ""

        # Navigate from steamapps to the game's mods directory
        idx = parts.index("steamapps")
        steam_root = Path(*parts[: idx + 1])
        game_mods_dir = steam_root / "common" / "Call to Arms - Gates of Hell" / "mods"
        return str(game_mods_dir)

    # ================== PRIVATE METHODS - MOD IMPORT ==================

    def _import_from_directory(self, dir_path: str) -> bool:
        """
        Import a mod from a directory structure.

        Recursively searches for mod.info files in the directory tree.

        Args:
            dir_path: Path to the directory to import from

        Returns:
            True if mod was successfully imported
        """
        for root, dirs, files in os.walk(dir_path):
            if "mod.info" in files:
                return self._copy_mod_directory(root)

        logger.warning("No mod.info found in directory or subdirectories")
        return False

    def _copy_mod_directory(self, mod_dir: str) -> bool:
        """
        Copy a mod directory to the game's mods directory.

        Args:
            mod_dir: Source directory containing the mod

        Returns:
            True if mod was successfully copied
        """
        mod_name = os.path.basename(mod_dir)
        dest_dir = self._get_game_mods_directory()
        dest = os.path.join(dest_dir, mod_name)

        # Check if mod already exists
        if os.path.exists(dest):
            logger.warning(f"Mod already exists: {mod_name}")
            return False

        try:
            shutil.copytree(mod_dir, dest)
            self._mark_as_imported(dest)
            logger.info(f"Mod imported in directory: {dest}")
            self.refresh_installed_mods()
            return True
        except Exception as e:
            logger.error(f"Error copying mod directory: {e}")
            return False

    def _import_from_archive(self, archive_path: str) -> bool:
        """
        Import a mod from an archive file.

        Extracts the archive to a temporary directory and imports from there.

        Args:
            archive_path: Path to the archive file

        Returns:
            True if mod was successfully imported
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                self._extract_archive(archive_path, temp_dir)
                self._mark_as_imported(temp_dir)
                return self._import_from_directory(temp_dir)
            except Exception as e:
                logger.error(f"Error importing from archive: {e}")
                return False

    @staticmethod
    def _extract_archive(archive_path: str, extract_to: str) -> None:
        """
        Extract various archive formats to a directory.

        Supports ZIP, 7Z, RAR, and TAR archives.

        Args:
            archive_path: Path to the archive file
            extract_to: Directory to extract files to

        Raises:
            ValueError: If the archive format is not supported
            RuntimeError: If extraction fails
        """
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
            # Clean up on failure
            shutil.rmtree(extract_to, ignore_errors=True)
            raise RuntimeError(f"Failed to extract archive: {e}")

    @staticmethod
    def _mark_as_imported(path: str) -> None:
        """
        Create a marker file to indicate the mod was imported by this manager.

        Args:
            path: Directory path to mark as imported
        """
        marker_path = os.path.join(path, ".imported_by_mod_manager")
        try:
            with open(marker_path, "w") as f:
                f.write("Imported by Mod Manager")
        except Exception as e:
            logger.warning(f"Could not create import marker: {e}")

    @staticmethod
    def _is_valid_game_mods_directory(path: str | None) -> bool:
        """
        Validate that the game mods directory path exists and is accessible.

        Args:
            path: Path to validate

        Returns:
            True if the path is valid and exists
        """
        return bool(path) and os.path.exists(path)
