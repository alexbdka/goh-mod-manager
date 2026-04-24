import logging
import os

from src.application.queries import ApplicationQueryService
from src.application.state import (
    ActiveModsState,
    CatalogueState,
    LoadOrderActivationResult,
    LoadOrderMutationResult,
    ModState,
    PresetsState,
    SettingsState,
    SettingsUpdateResult,
    ShareCodeExportResult,
    ShareCodeImportResult,
)
from src.application.use_cases import (
    ApplicationDebugReportUseCase,
    ApplicationLoadOrderUseCase,
    ApplicationSettingsUseCase,
    ApplicationShareCodeUseCase,
)
from src.core import constants
from src.core.config import AppConfig
from src.core.events import EventBus, EventType
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
    High-level application facade used by the UI layer.

    The window, dialogs, controllers, and CLI interact with this class instead of
    reaching directly into services. Read-oriented calls return view-neutral state
    objects from ``src.application.state``. Mutating calls delegate to application
    use cases and emit coarse-grained events for the UI.
    """

    def __init__(self):
        self.events = EventBus()
        self._config_service = ConfigService()
        self._catalogue = ModsCatalogueService()
        self._active_mods = ActiveModsService(self._catalogue)
        self._preset_service = PresetService(
            self._config_service, self._catalogue, self._active_mods
        )
        self._share_code_service = ShareCodeService()
        self._mod_import_service = ModImportService()
        self.queries = ApplicationQueryService(
            self._config_service,
            self._catalogue,
            self._active_mods,
            self._preset_service,
        )
        self.settings = ApplicationSettingsUseCase(self._config_service)
        self.debug_reports = ApplicationDebugReportUseCase(self.queries)
        self.share_codes = ApplicationShareCodeUseCase(
            self._share_code_service,
            self._active_mods,
            self._catalogue,
            self._config_service,
        )
        self.load_order = ApplicationLoadOrderUseCase(
            self._active_mods,
            self._catalogue,
            self._config_service,
        )

    @property
    def config_service(self) -> ConfigService:
        return self._config_service

    @property
    def catalogue(self) -> ModsCatalogueService:
        return self._catalogue

    @property
    def active_mods(self) -> ActiveModsService:
        return self._active_mods

    @property
    def preset_service(self) -> PresetService:
        return self._preset_service

    @property
    def share_code_service(self) -> ShareCodeService:
        return self._share_code_service

    @property
    def mod_import_service(self) -> ModImportService:
        return self._mod_import_service

    def subscribe(self, event_type: str, callback) -> None:
        """Registers a callback on the internal event bus."""
        self.events.subscribe(event_type, callback)

    def unsubscribe(self, event_type: str, callback) -> None:
        """Removes a callback from the internal event bus."""
        self.events.unsubscribe(event_type, callback)

    def initialize(self) -> bool:
        """
        Load configuration-dependent state and attempt path auto-detection.

        Returns ``True`` when the minimum required paths were resolved and the
        catalogue/profile state could be loaded. Returns ``False`` when the UI
        should prompt the user for missing configuration.
        """
        config = self.config_service.get_config()
        paths_updated = False

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

        if paths_updated:
            self.config_service.save()

        if not config.game_path or not config.profile_path:
            logger.warning(
                "Could not auto-detect game or profile paths. "
                "Manual configuration needed."
            )
            return False

        local_mods_dir = os.path.join(config.game_path, constants.MODS_DIR)
        workshop_dir = config.workshop_path if config.workshop_path else ""
        self.catalogue.load_catalogue(local_mods_dir, workshop_dir)
        self.events.emit(EventType.CATALOGUE_CHANGED)

        self.active_mods.load_from_profile(config.profile_path)
        self.events.emit(EventType.ACTIVE_MODS_CHANGED)

        return True

    def reload(self) -> None:
        """
        Reload the catalogue and active profile from the currently configured
        paths.
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

    def get_settings_state(self) -> SettingsState:
        """Returns a view-neutral snapshot of the current settings."""
        return self.queries.get_settings_state()

    def apply_settings(self, settings_state: SettingsState) -> SettingsUpdateResult:
        """Applies settings and returns a neutral summary of what changed."""
        return self.settings.apply(settings_state)

    def has_seen_onboarding(self) -> bool:
        """Returns whether the first-run interface tour has been completed."""
        return self.config_service.get_config().onboarding_seen

    def mark_onboarding_seen(self) -> None:
        """Stores that the first-run interface tour has been completed."""
        self.config_service.set_onboarding_seen(True)

    def build_debug_report(self) -> str:
        """Builds a text debug report independently of the UI."""
        return self.debug_reports.build()

    # --- Data Access for UI ---

    def get_catalogue_state(self) -> CatalogueState:
        """Returns a view-neutral snapshot of the current catalogue."""
        return self.queries.get_catalogue_state()

    def get_active_mods_state(self) -> ActiveModsState:
        """Returns a view-neutral snapshot of the active load order."""
        return self.queries.get_active_mods_state()

    def get_mod_state(self, mod_id: str) -> ModState | None:
        """Returns a view-neutral snapshot for a specific mod."""
        return self.queries.get_mod_state(mod_id)

    def is_mod_active(self, mod_id: str) -> bool:
        """Checks if a specific mod is active."""
        return mod_id in self.active_mods.active_mods_ids

    # --- Mod Manipulation ---

    def activate_mods(self, mod_ids: list[str]) -> LoadOrderActivationResult:
        result = self.load_order.activate_mods(mod_ids)
        if result.changed:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    def deactivate_mod(self, mod_id: str) -> LoadOrderMutationResult:
        result = self.load_order.deactivate_mod(mod_id)
        if result.changed:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    def move_mod_up(self, mod_id: str) -> LoadOrderMutationResult:
        """Increases the load priority of a mod and saves."""
        result = self.load_order.move_up(mod_id)
        if result.changed:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    def move_mod_down(self, mod_id: str) -> LoadOrderMutationResult:
        """Decreases the load priority of a mod and saves."""
        result = self.load_order.move_down(mod_id)
        if result.changed:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    def set_active_mods_order(self, mod_ids: list[str]) -> LoadOrderMutationResult:
        """Sets the active mods list directly to the specified order and saves."""
        result = self.load_order.reorder(mod_ids)
        if result.changed:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    def clear_active_mods(self) -> LoadOrderMutationResult:
        """Clears all currently active mods and saves."""
        result = self.load_order.clear()
        if result.changed:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    def _persist_active_mods(self) -> None:
        """Persist the in-memory active load order to the configured profile file."""
        config = self.config_service.get_config()
        if config.profile_path:
            self.active_mods.save_to_profile(
                config.profile_path, catalogue_service=self.catalogue
            )
        else:
            logger.error("Cannot apply changes: Profile path is not configured.")

    # --- Preset Management ---

    def get_all_presets(self) -> dict[str, list[str]]:
        return self.preset_service.get_all_presets()

    def get_presets_state(
        self, selected_preset_name: str | None = None
    ) -> PresetsState:
        """Returns a view-neutral snapshot of presets and current preset match."""
        return self.queries.get_presets_state(selected_preset_name)

    def save_preset(self, name: str) -> None:
        self.preset_service.save_preset(name)
        self.events.emit(EventType.PRESETS_CHANGED)

    def delete_preset(self, name: str) -> bool:
        result = self.preset_service.delete_preset(name)
        if result:
            self.events.emit(EventType.PRESETS_CHANGED)
        return result

    def apply_preset(self, name: str) -> tuple[bool, list[str]]:
        success, missing = self.preset_service.apply_preset(name)
        if success:
            self._persist_active_mods()
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return success, missing

    # --- Share Codes ---

    def build_share_code_export(self) -> ShareCodeExportResult:
        """Builds a share code export result for the current load order."""
        return self.share_codes.export_active_mods()

    def apply_share_code(self, code: str) -> ShareCodeImportResult:
        """Applies a share code and returns a neutral result."""
        result = self.share_codes.import_share_code(code)
        if result.success:
            self.events.emit(EventType.ACTIVE_MODS_CHANGED)
        return result

    # --- Mod Importing ---

    def import_mod(
        self,
        path: str,
        progress_callback=None,
        conflict_callback=None,
        reload_on_success: bool = True,
    ) -> bool:
        """
        Import a mod from a directory or archive into the local mods folder.
        """
        config = self.config_service.get_config()
        if not config.game_path:
            logger.error("Cannot import mod: Game path is not configured.")
            return False

        local_mods_dir = os.path.join(config.game_path, constants.MODS_DIR)

        success = self.mod_import_service.import_mod(
            path, local_mods_dir, progress_callback, conflict_callback
        )
        if success and reload_on_success:
            self.reload()
        return success

    # --- Game Launching ---

    def launch_game(self) -> bool:
        """Launch the game through the Steam protocol handler."""
        launch_url = f"steam://rungameid/{constants.STEAM_APP_ID}"
        success = system_actions.open_url(launch_url)
        if success:
            logger.info("Launched game via Steam protocol.")
        else:
            logger.error("Failed to launch game via Steam protocol.")
        return success
