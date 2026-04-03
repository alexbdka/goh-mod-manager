import logging
import os
from typing import Dict, List, Optional, Tuple

from src.core import constants
from src.core.config import AppConfig
from src.core.events import EventBus, EventType
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mod_import_service import ModImportService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.preset_service import PresetService
from src.services.share_code_service import ShareCodeService
from src.utils import steam_utils, system_actions

logger = logging.getLogger(__name__)


class ModManager:
    """
    Facade class that acts as the central orchestrator for the Mod Manager.
    The UI should only interact with this class to keep the view decoupled
    from the underlying services and business logic.
    """

    def __init__(self):
        self.events = EventBus()
        self.config_service = ConfigService()
        self.catalogue = ModsCatalogueService()
        self.active_mods = ActiveModsService(self.catalogue)
        self.preset_service = PresetService(
            self.config_service, self.catalogue, self.active_mods
        )
        self.share_code_service = ShareCodeService()
        self.mod_import_service = ModImportService()

    def subscribe(self, event_type: str, callback) -> None:
        """Registers a callback on the internal event bus."""
        self.events.subscribe(event_type, callback)

    def unsubscribe(self, event_type: str, callback) -> None:
        """Removes a callback from the internal event bus."""
        self.events.unsubscribe(event_type, callback)

    def initialize(self) -> bool:
        """
        Initializes the application state:
        1. Loads the configuration.
        2. Auto-detects missing paths via SteamUtils.
        3. Loads the mod catalogue from disk.
        4. Loads the active mods profile.

        Returns True if initialization was successful and minimum paths are valid.
        """
        config = self.config_service.get_config()
        paths_updated = False

        # 1. Auto-detect paths if missing
        if not config.game_path:
            game_path = steam_utils.get_goh_game_path()
            if game_path:
                config.game_path = str(game_path)
                paths_updated = True

        if not config.workshop_path:
            workshop_path = steam_utils.get_goh_workshop_path()
            if workshop_path:
                config.workshop_path = str(workshop_path)
                paths_updated = True

        if not config.profile_path:
            profile_path = steam_utils.get_goh_profile_path()
            if profile_path:
                config.profile_path = str(profile_path)
                paths_updated = True

        # Save auto-detected paths
        if paths_updated:
            self.config_service.save()

        # 2. Validate paths
        if not config.game_path or not config.profile_path:
            logger.warning(
                "Could not auto-detect game or profile paths. Manual configuration needed."
            )
            # We don't necessarily fail here, as the UI might prompt the user to locate them.
            return False

        # 3. Load Catalogue
        local_mods_dir = os.path.join(config.game_path, constants.MODS_DIR)
        workshop_dir = config.workshop_path if config.workshop_path else ""
        self.catalogue.load_catalogue(local_mods_dir, workshop_dir)
        self.events.emit(EventType.CATALOGUE_CHANGED)

        # 4. Load Active Mods Profile
        self.active_mods.load_from_profile(config.profile_path)
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

        return True

    def reload(self) -> None:
        """
        Reloads the mod catalogue and active mods profile from disk.
        """
        config = self.config_service.get_config()
        if config.game_path:
            local_mods_dir = os.path.join(config.game_path, constants.MODS_DIR)
            workshop_dir = config.workshop_path if config.workshop_path else ""
            self.catalogue.load_catalogue(local_mods_dir, workshop_dir)
            self.events.emit(EventType.CATALOGUE_CHANGED)

        if config.profile_path:
            self.active_mods.load_from_profile(config.profile_path)
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)

    # --- Configuration ---

    def get_config(self) -> AppConfig:
        """Returns the current application configuration."""
        return self.config_service.get_config()

    def update_paths(
        self,
        game_path: Optional[str] = None,
        workshop_path: Optional[str] = None,
        profile_path: Optional[str] = None,
        language: Optional[str] = None,
        theme: Optional[str] = None,
        font: Optional[str] = None,
    ) -> None:
        """Updates the configured paths and saves them."""
        self.config_service.update_paths(
            game_path=game_path,
            workshop_path=workshop_path,
            profile_path=profile_path,
            language=language,
            theme=theme,
            font=font,
        )

    # --- Data Access for UI ---

    def get_all_mods(self) -> List[ModInfo]:
        """Returns the full catalogue of local and workshop mods."""
        return self.catalogue.all_mods

    def get_local_mods(self) -> List[ModInfo]:
        """Returns only locally installed mods."""
        return self.catalogue.local_mods

    def get_workshop_mods(self) -> List[ModInfo]:
        """Returns only Steam Workshop mods."""
        return self.catalogue.workshop_mods

    def get_active_mods(self) -> List[ModInfo]:
        """Returns the list of currently active mods in their load order."""
        return self.active_mods.get_active_mods()

    def is_mod_active(self, mod_id: str) -> bool:
        """Checks if a specific mod is active."""
        return mod_id in self.active_mods.active_mods_ids

    # --- Mod Manipulation ---

    def toggle_mod(self, mod_id: str) -> List[str]:
        """Activates the mod if it's inactive, deactivates it if active and saves.
        Returns a list of missing dependency IDs if any."""
        missing_deps = []
        if self.is_mod_active(mod_id):
            self.active_mods.deactivate_mod(mod_id)
        else:
            missing_deps = self.active_mods.activate_mod(mod_id)
        self.apply_changes()
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return missing_deps

    def move_mod_up(self, mod_id: str) -> None:
        """Increases the load priority of a mod and saves."""
        self.active_mods.move_mod_up(mod_id)
        self.apply_changes()
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

    def move_mod_down(self, mod_id: str) -> None:
        """Decreases the load priority of a mod and saves."""
        self.active_mods.move_mod_down(mod_id)
        self.apply_changes()
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

    def set_active_mods_order(self, mod_ids: List[str]) -> None:
        """Sets the active mods list directly to the specified order and saves."""
        self.active_mods.active_mods_ids = mod_ids
        self.apply_changes()
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

    def clear_active_mods(self) -> None:
        """Clears all currently active mods and saves."""
        self.active_mods.active_mods_ids.clear()
        self.apply_changes()
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

    # --- State Persistence ---

    def apply_changes(self) -> None:
        """Saves the current active mods order to the options.set profile."""
        config = self.config_service.get_config()
        if config.profile_path:
            self.active_mods.save_to_profile(
                config.profile_path, catalogue_service=self.catalogue
            )
        else:
            logger.error("Cannot apply changes: Profile path is not configured.")

    # --- Preset Management ---

    def get_all_presets(self) -> Dict[str, List[str]]:
        return self.preset_service.get_all_presets()

    def save_preset(self, name: str) -> None:
        self.preset_service.save_preset(name)
        self.apply_changes()
        self.events.emit(EventType.PRESETS_CHANGED)

    def delete_preset(self, name: str) -> bool:
        result = self.preset_service.delete_preset(name)
        if result:
            self.events.emit(EventType.PRESETS_CHANGED)
        return result

    def apply_preset(self, name: str) -> Tuple[bool, List[str]]:
        success, missing = self.preset_service.apply_preset(name)
        if success:
            self.apply_changes()
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return success, missing

    # --- Share Codes ---

    def export_share_code(self) -> str:
        """Encodes the currently active mods into a share code."""
        active_mods = self.get_active_mods()
        return self.share_code_service.encode(active_mods)

    def import_share_code(self, code: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Decodes a share code and applies it.
        Returns a tuple: (Success bool, List of missing mods data: {'id': ..., 'name': ...}).
        Raises InvalidShareCodeError if the code is invalid.
        """
        decoded_data = self.share_code_service.decode(code)
        if not decoded_data:
            return False, []

        found_mods, missing_mods = self.share_code_service.resolve_mods(
            decoded_data, self.get_all_mods()
        )

        # Apply the found mods using the same dependency resolution as manual activation.
        dependency_missing_ids = self.active_mods.replace_active_mods(
            [mod.id for mod in found_mods]
        )

        known_missing_ids = {str(item.get("id", "")) for item in missing_mods}
        for mod_id in dependency_missing_ids:
            if mod_id not in known_missing_ids:
                missing_mods.append({"id": mod_id, "name": mod_id})
                known_missing_ids.add(mod_id)

        self.apply_changes()
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

        return True, missing_mods

    # --- Mod Importing ---

    def import_mod(
        self,
        path: str,
        progress_callback=None,
        conflict_callback=None,
        reload_on_success: bool = True,
    ) -> bool:
        """
        Imports a mod from a directory or archive.
        Raises ModImportError (or a subclass) if the import fails.
        """
        config = self.config_service.get_config()
        if not config.game_path:
            logger.error("Cannot import mod: Game path is not configured.")
            return False

        local_mods_dir = os.path.join(config.game_path, constants.MODS_DIR)

        # The service returns True or raises an exception
        success = self.mod_import_service.import_mod(
            path, local_mods_dir, progress_callback, conflict_callback
        )
        if success and reload_on_success:
            self.reload()
        return success

    # --- Game Launching ---

    def launch_game(self) -> bool:
        """
        Launches the game via Steam protocol.
        """
        launch_url = f"steam://rungameid/{constants.STEAM_APP_ID}"
        success = system_actions.open_url(launch_url)
        if success:
            logger.info("Launched game via Steam protocol.")
        else:
            logger.error("Failed to launch game via Steam protocol.")
        return success
