import os
import shutil
from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import QObject, Signal

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.infrastructure.config_manager import ConfigManager
from goh_mod_manager.infrastructure.mod_manager_logger import logger
from goh_mod_manager.services.active_mods_service import ActiveModsService
from goh_mod_manager.services.mod_import_service import ModImportService
from goh_mod_manager.services.mods_catalog_service import ModsCatalogService
from goh_mod_manager.services.presets_service import PresetsService


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
        self._installed_mods: List[Mod] = []
        self._active_mods: List[Mod] = []
        self._presets: Dict[str, List[Mod]] = {}
        self._config = ConfigManager()
        self._mods_catalog = ModsCatalogService()
        self._active_mods_service = ActiveModsService()
        self._presets_service = PresetsService()
        self._mod_import_service = ModImportService()

    # Getters
    def get_config(self) -> ConfigManager:
        """Get the configuration manager instance."""
        return self._config

    def get_installed_mods(self) -> List[Mod]:
        return self._installed_mods.copy()

    def get_active_mods(self) -> List[Mod]:
        return self._active_mods.copy()

    def get_active_mods_count(self) -> int:
        return len(self._active_mods)

    def get_presets_names(self) -> List[str]:
        return list(self._presets.keys())

    # Setters
    def set_game_directory(self, game_directory: str) -> None:
        self._config.set_game_directory(game_directory)

    def set_mods_directory(self, mods_directory: str) -> None:
        self._config.set_mods_directory(mods_directory)
        self._load_installed_mods()

    def set_options_file(self, options_file: str) -> None:
        self._config.set_options_file(options_file)
        self._load_active_mods()

    # Preset Management
    def get_preset_mods(self, preset_name: str) -> List[Mod]:
        return self._presets.get(preset_name, [])

    def set_presets(self, presets: Dict[str, List[str]]) -> None:
        self._presets = self._presets_service.resolve_presets(
            presets, self._installed_mods
        )
        self.presets_signal.emit()

    def has_preset(self, preset_name: str) -> bool:
        return preset_name in self._presets

    def save_preset(self, preset_name: str) -> bool:
        if not self._active_mods:
            logger.warning("Cannot save empty preset")
            return False

        self._presets[preset_name] = self._active_mods.copy()
        self._save_presets_to_config()
        self.presets_signal.emit()
        logger.info(f"Preset '{preset_name}' saved with {len(self._active_mods)} mods")
        return True

    def load_preset(self, preset_name: str) -> bool:
        if preset_name not in self._presets:
            logger.error(f"Preset '{preset_name}' not found")
            return False

        preset_mods = self._presets[preset_name]
        self.clear_active_mods()

        self.set_mods_order(preset_mods)
        logger.info(f"Preset '{preset_name}' loaded with {len(preset_mods)} mods")
        return True

    def delete_preset(self, preset_name: str) -> bool:
        if preset_name not in self._presets:
            logger.error(f"Preset '{preset_name}' not found")
            return False

        del self._presets[preset_name]
        self._save_presets_to_config()
        self.presets_signal.emit()
        logger.info(f"Preset '{preset_name}' deleted")
        return True

    # Mod Management
    def enable_mod(self, mod: Mod) -> bool:
        if mod not in self._active_mods:
            self._active_mods.append(mod)
        return self._save_active_mods()

    def disable_mod(self, mod: Mod) -> bool:
        if mod in self._active_mods:
            self._active_mods.remove(mod)
        return self._save_active_mods()

    def delete_mod(self, mod: Mod) -> bool:
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
        self._active_mods = reordered_mods.copy()
        return self._save_active_mods()

    def clear_active_mods(self) -> bool:
        try:
            if not self._active_mods_service.clear_active_mods(
                self._config.get_options_file()
            ):
                return False
            self._load_active_mods()
            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while clearing mods: {e}")
            return False

    # Refresh
    def refresh_all(self) -> None:
        """Refresh both installed and active mods from their sources."""
        self.refresh_installed_mods()
        self.refresh_active_mods()

    def refresh_installed_mods(self) -> None:
        """Refresh the list of installed mods from the filesystem."""
        self._load_installed_mods()
        self.installed_mods_signal.emit()

    def replace_installed_mods(self, mods: List[Mod]) -> None:
        self._installed_mods = mods
        self.installed_mods_signal.emit()

    def refresh_active_mods(self) -> None:
        """Refresh the list of active mods from the options file."""
        self._load_active_mods()
        self._emit_updates()

    # Import Mod
    def import_mod(self, path: str) -> bool:
        """
        Import a mod from a directory or archive file.

        Args:
            path: Path to the archive file

        Returns:
            True if mod was successfully imported
        """
        success = self._mod_import_service.import_mod(
            path, self._get_game_mods_directory()
        )
        if success:
            self.refresh_installed_mods()
        return success

    # Data Loading
    def _load_installed_mods(self) -> None:
        """
        Scan mod directories and load all installed mods.

        Scans both the configured mods directory and the game's mods directory.
        """
        mods_directory = self._config.get_mods_directory()
        game_mods_directory = self._get_game_mods_directory()
        self._installed_mods = self._mods_catalog.scan_installed_mods(
            mods_directory, game_mods_directory
        )

    def _load_active_mods(self) -> None:
        """
        Load active mods from the game's options file.

        Parses the options file to get active mod IDs and resolves them
        to mod objects from the installed mods list.
        """
        self._active_mods = []
        options_file = self._config.get_options_file()

        try:
            active_mod_ids = self._active_mods_service.load_active_mod_ids(options_file)
            self._active_mods = self._mods_catalog.resolve_active_mods(
                active_mod_ids, self._installed_mods
            )
        except Exception as e:
            logger.error(f"Error while parsing {options_file}: {e}")

    # Data Saving

    def _save_active_mods(self) -> bool:
        """
        Save the current active mods list to the options file.

        Returns:
            True if mods were successfully saved
        """
        try:
            if not self._active_mods_service.save_active_mods(
                self._config.get_options_file(), self._active_mods
            ):
                return False

            self._emit_updates()
            return True
        except Exception as e:
            logger.error(f"Error while setting mods: {e}")
            return False

    def _save_presets_to_config(self) -> None:
        """Save current presets to the configuration manager."""
        if not self._config:
            return

        self._config.set_presets(self._presets_service.to_config_payload(self._presets))

    # Utilities
    def _emit_updates(self) -> None:
        """Emit Qt signals to update UI components."""
        self.installed_mods_signal.emit()
        self.mods_counter_signal.emit(len(self._active_mods))

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

    def get_game_mods_directory(self) -> str:
        return self._get_game_mods_directory()
