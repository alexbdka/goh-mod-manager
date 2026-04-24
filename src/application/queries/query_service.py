from src.application.state import (
    ActiveModsState,
    CatalogueState,
    ModState,
    PresetsState,
    SettingsState,
)
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.preset_service import PresetService


class ApplicationQueryService:
    """Build immutable UI-facing read models from domain and service state."""

    def __init__(
        self,
        config_service: ConfigService,
        catalogue_service: ModsCatalogueService,
        active_mods_service: ActiveModsService,
        preset_service: PresetService,
    ):
        self._config_service = config_service
        self._catalogue_service = catalogue_service
        self._active_mods_service = active_mods_service
        self._preset_service = preset_service

    def get_settings_state(self) -> SettingsState:
        """Return the current settings as a view-neutral state object."""
        config = self._config_service.get_config()
        return SettingsState(
            game_path=config.game_path,
            workshop_path=config.workshop_path,
            profile_path=config.profile_path,
            language=config.language,
            theme=config.theme,
            font=config.font,
        )

    def get_catalogue_state(self) -> CatalogueState:
        """Return catalogue items annotated with active-state and dependency status."""
        active_mod_ids = set(self._active_mods_service.active_mods_ids)
        known_mod_ids = {mod.id for mod in self._catalogue_service.all_mods}

        items = [
            self._to_mod_state(
                mod,
                is_active=mod.id in active_mod_ids,
                missing_dependencies=[
                    dep_id for dep_id in mod.dependencies if dep_id not in known_mod_ids
                ],
            )
            for mod in self._catalogue_service.all_mods
        ]
        return CatalogueState(items=items)

    def get_active_mods_state(self) -> ActiveModsState:
        """Return active mods in the same order used by the game profile."""
        items = [
            self._to_mod_state(mod, is_active=True, load_order=index + 1)
            for index, mod in enumerate(self._active_mods_service.get_active_mods())
        ]
        return ActiveModsState(items=items)

    def get_mod_state(self, mod_id: str) -> ModState | None:
        """Return a single mod snapshot enriched with active/load-order metadata."""
        mod = self._catalogue_service.get_mod(mod_id)
        if not mod:
            return None

        active_mod_ids = set(self._active_mods_service.active_mods_ids)
        known_mod_ids = {item.id for item in self._catalogue_service.all_mods}
        load_order = None
        if mod_id in self._active_mods_service.active_mods_ids:
            load_order = self._active_mods_service.active_mods_ids.index(mod_id) + 1

        return self._to_mod_state(
            mod,
            is_active=mod_id in active_mod_ids,
            load_order=load_order,
            missing_dependencies=[
                dep_id for dep_id in mod.dependencies if dep_id not in known_mod_ids
            ],
        )

    def get_presets_state(
        self, selected_preset_name: str | None = None
    ) -> PresetsState:
        """
        Return preset names plus the currently selected or matching preset state.

        ``selected_preset_name`` lets the UI preserve the user's current preset
        selection even when the active load order no longer matches it exactly.
        """
        config = self._config_service.get_config()
        active_mod_ids = list(self._active_mods_service.active_mods_ids)
        preset_names = list(config.presets.keys())

        if selected_preset_name and selected_preset_name in config.presets:
            current_preset_name = selected_preset_name
            is_unsaved = config.presets[selected_preset_name] != active_mod_ids
        else:
            current_preset_name = next(
                (
                    preset_name
                    for preset_name, preset_mod_ids in config.presets.items()
                    if preset_mod_ids == active_mod_ids
                ),
                None,
            )
            is_unsaved = False

        return PresetsState(
            preset_names=preset_names,
            current_preset_name=current_preset_name,
            is_unsaved=is_unsaved,
        )

    @staticmethod
    def _to_mod_state(
        mod: ModInfo,
        *,
        is_active: bool = False,
        load_order: int | None = None,
        missing_dependencies: list[str] | None = None,
    ) -> ModState:
        """Convert a domain ``ModInfo`` object into a view-neutral ``ModState``."""
        return ModState(
            id=mod.id,
            name=mod.name,
            description=mod.desc,
            tags=list(mod.tags),
            min_game_version=mod.minGameVersion,
            max_game_version=mod.maxGameVersion,
            dependencies=list(mod.dependencies),
            missing_dependencies=list(missing_dependencies or []),
            is_local=mod.isLocal,
            has_shaders=mod.hasShaders,
            path=mod.path,
            image_path=mod.image_path,
            is_active=is_active,
            load_order=load_order,
        )
