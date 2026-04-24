import logging

from src.application.state import LoadOrderActivationResult, LoadOrderMutationResult
from src.core.exceptions import ProfileWriteError
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService

logger = logging.getLogger(__name__)


class ApplicationLoadOrderUseCase:
    """
    Application use case for load order mutations.
    """

    def __init__(
        self,
        active_mods_service: ActiveModsService,
        catalogue_service: ModsCatalogueService,
        config_service: ConfigService,
    ):
        self._active_mods_service = active_mods_service
        self._catalogue_service = catalogue_service
        self._config_service = config_service

    def activate_mods(self, mod_ids: list[str]) -> LoadOrderActivationResult:
        activated_mod_ids: list[str] = []
        missing_dependencies: list[str] = []
        mod_ids_to_activate = [
            mod_id
            for mod_id in mod_ids
            if mod_id not in self._active_mods_service.active_mods_ids
        ]

        if not mod_ids_to_activate:
            return LoadOrderActivationResult(
                changed=False,
                activated_mod_ids=[],
                missing_dependencies=[],
            )

        profile_path = self._require_profile_path()

        for mod_id in mod_ids_to_activate:
            activated_mod_ids.append(mod_id)
            missing_dependencies.extend(self._active_mods_service.activate_mod(mod_id))

        self._persist_changes(profile_path)
        unique_missing = list(dict.fromkeys(missing_dependencies))
        return LoadOrderActivationResult(
            changed=True,
            activated_mod_ids=activated_mod_ids,
            missing_dependencies=unique_missing,
        )

    def deactivate_mod(self, mod_id: str) -> LoadOrderMutationResult:
        if mod_id not in self._active_mods_service.active_mods_ids:
            return LoadOrderMutationResult(
                changed=False,
                active_mod_ids=list(self._active_mods_service.active_mods_ids),
            )

        profile_path = self._require_profile_path()
        self._active_mods_service.deactivate_mod(mod_id)
        self._persist_changes(profile_path)
        return LoadOrderMutationResult(
            changed=True,
            active_mod_ids=list(self._active_mods_service.active_mods_ids),
        )

    def clear(self) -> LoadOrderMutationResult:
        if not self._active_mods_service.active_mods_ids:
            return LoadOrderMutationResult(changed=False, active_mod_ids=[])

        profile_path = self._require_profile_path()
        self._active_mods_service.active_mods_ids.clear()
        self._persist_changes(profile_path)
        return LoadOrderMutationResult(changed=True, active_mod_ids=[])

    def move_up(self, mod_id: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mods_ids)
        if mod_id not in before or before.index(mod_id) == 0:
            return LoadOrderMutationResult(changed=False, active_mod_ids=before)

        profile_path = self._require_profile_path()
        self._active_mods_service.move_mod_up(mod_id)
        return self._persist_if_changed(before, profile_path)

    def move_down(self, mod_id: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mods_ids)
        if mod_id not in before or before.index(mod_id) == len(before) - 1:
            return LoadOrderMutationResult(changed=False, active_mod_ids=before)

        profile_path = self._require_profile_path()
        self._active_mods_service.move_mod_down(mod_id)
        return self._persist_if_changed(before, profile_path)

    def reorder(self, mod_ids: list[str]) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mods_ids)
        if list(mod_ids) == before:
            return LoadOrderMutationResult(changed=False, active_mod_ids=before)

        profile_path = self._require_profile_path()
        self._active_mods_service.active_mods_ids = list(mod_ids)
        return self._persist_if_changed(before, profile_path)

    def _persist_if_changed(
        self, before: list[str], profile_path: str
    ) -> LoadOrderMutationResult:
        current = list(self._active_mods_service.active_mods_ids)
        if current == before:
            return LoadOrderMutationResult(changed=False, active_mod_ids=current)

        self._persist_changes(profile_path)
        return LoadOrderMutationResult(changed=True, active_mod_ids=current)

    def _require_profile_path(self) -> str:
        config = self._config_service.get_config()
        if config.profile_path:
            return config.profile_path

        raise ProfileWriteError("", "Profile path is not configured.")

    def _persist_changes(self, profile_path: str) -> None:
        self._active_mods_service.save_to_profile(
            profile_path, catalogue_service=self._catalogue_service
        )
