import logging

from src.application.state import LoadOrderActivationResult, LoadOrderMutationResult
from src.core.exceptions import ProfileWriteError
from src.core.mod_reference import parse_reference_key
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

    def activate_mods(self, mod_identifiers: list[str]) -> LoadOrderActivationResult:
        activated_mod_ids: list[str] = []
        missing_dependencies: list[str] = []
        active_refs = set(self._active_mods_service.active_mod_refs)
        mod_ids_to_activate = [
            mod_identifier
            for mod_identifier in mod_identifiers
            if mod_identifier not in active_refs
        ]

        if not mod_ids_to_activate:
            return LoadOrderActivationResult(
                changed=False,
                activated_mod_ids=[],
                missing_dependencies=[],
            )

        profile_path = self._require_profile_path()

        for mod_identifier in mod_ids_to_activate:
            missing = self._active_mods_service.activate_mod(mod_identifier)
            if missing:
                missing_dependencies.extend(missing)
                continue
            parsed = parse_reference_key(mod_identifier)
            activated_mod_ids.append(parsed.id if parsed else mod_identifier)

        changed = bool(activated_mod_ids)
        if changed:
            self._persist_changes(profile_path)

        unique_missing = list(dict.fromkeys(missing_dependencies))
        return LoadOrderActivationResult(
            changed=changed,
            activated_mod_ids=activated_mod_ids,
            missing_dependencies=unique_missing,
        )

    def deactivate_mod(self, mod_identifier: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        profile_path = self._require_profile_path()
        self._active_mods_service.deactivate_mod(mod_identifier)
        return self._persist_if_changed(before, profile_path)

    def clear(self) -> LoadOrderMutationResult:
        if not self._active_mods_service.active_mod_refs:
            return LoadOrderMutationResult(changed=False, active_mod_ids=[])

        profile_path = self._require_profile_path()
        self._active_mods_service.active_mod_refs = []
        self._persist_changes(profile_path)
        return LoadOrderMutationResult(changed=True, active_mod_ids=[])

    def move_up(self, mod_identifier: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        profile_path = self._require_profile_path()
        self._active_mods_service.move_mod_up(mod_identifier)
        return self._persist_if_changed(before, profile_path)

    def move_down(self, mod_identifier: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        profile_path = self._require_profile_path()
        self._active_mods_service.move_mod_down(mod_identifier)
        return self._persist_if_changed(before, profile_path)

    def reorder(self, mod_identifiers: list[str]) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        if list(mod_identifiers) == before:
            return LoadOrderMutationResult(
                changed=False,
                active_mod_ids=list(self._active_mods_service.active_mods_ids),
            )

        profile_path = self._require_profile_path()
        self._active_mods_service.active_mod_refs = list(mod_identifiers)
        return self._persist_if_changed(before, profile_path)

    def _persist_if_changed(
        self, before: list[str], profile_path: str
    ) -> LoadOrderMutationResult:
        current_refs = list(self._active_mods_service.active_mod_refs)
        if current_refs == before:
            return LoadOrderMutationResult(
                changed=False,
                active_mod_ids=list(self._active_mods_service.active_mods_ids),
            )

        self._persist_changes(profile_path)
        return LoadOrderMutationResult(
            changed=True, active_mod_ids=list(self._active_mods_service.active_mods_ids)
        )

    def _require_profile_path(self) -> str:
        config = self._config_service.get_config()
        if config.profile_path:
            return config.profile_path

        raise ProfileWriteError("", "Profile path is not configured.")

    def _persist_changes(self, profile_path: str) -> None:
        self._active_mods_service.save_to_profile(
            profile_path, catalogue_service=self._catalogue_service
        )
