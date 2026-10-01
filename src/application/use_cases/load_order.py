import logging

from src.application.state import LoadOrderActivationResult, LoadOrderMutationResult
from src.core.exceptions import CircularDependencyError, ProfileWriteError
from src.core.mod import ModInfo
from src.core.mod_reference import parse_reference_key, to_reference_key
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.utils.game_version import get_game_version, is_mod_version_compatible

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
        self._cached_game_version: tuple[int, ...] | None = None
        self._cached_game_path: str | None = None

    def activate_mods(self, mod_identifiers: list[str]) -> LoadOrderActivationResult:
        activated_mod_ids: list[str] = []
        missing_dependencies: list[str] = []
        circular_dependency_refs: list[str] = []
        active_refs = set(self._active_mods_service.active_mod_refs)
        mod_ids_to_activate: list[str] = []
        for mod_identifier in mod_identifiers:
            normalized_refs = self._active_mods_service.normalize_mod_refs(
                [mod_identifier]
            )
            if normalized_refs and normalized_refs[0] in active_refs:
                continue
            mod_ids_to_activate.append(mod_identifier)

        if not mod_ids_to_activate:
            return LoadOrderActivationResult(
                changed=False,
                activated_mod_ids=[],
                missing_dependencies=[],
            )

        profile_path = self._require_profile_path()

        # Resolve game version once for the whole batch when enforcement is on.
        config = self._config_service.get_config()
        game_version: tuple[int, ...] | None = None
        if config.enforce_game_version and config.game_path:
            game_version = self._get_game_version(config.game_path)

        version_incompatible_mods: list[str] = []

        for mod_identifier in mod_ids_to_activate:
            # Version compatibility check (skipped when version is unavailable).
            if config.enforce_game_version and game_version is not None:
                mod_info = self._resolve_mod_info(mod_identifier)
                if mod_info is not None and not is_mod_version_compatible(
                    game_version,
                    mod_info.minGameVersion,
                    mod_info.maxGameVersion,
                ):
                    version_incompatible_mods.append(
                        to_reference_key(mod_info.id, mod_info.isLocal)
                    )
                    logger.info(
                        "Blocked activation of '%s': game version incompatible "
                        "(game=%s, min=%s, max=%s).",
                        mod_identifier,
                        game_version,
                        mod_info.minGameVersion,
                        mod_info.maxGameVersion,
                    )
                    continue

            before_refs = list(self._active_mods_service.active_mod_refs)
            try:
                missing = self._active_mods_service.activate_mod(mod_identifier)
            except CircularDependencyError as error:
                circular_dependency_refs.extend(error.mod_refs)
                continue
            if missing:
                missing_dependencies.extend(missing)
                continue
            if self._active_mods_service.active_mod_refs == before_refs:
                continue
            parsed = parse_reference_key(mod_identifier)
            activated_mod_ids.append(parsed.id if parsed else mod_identifier)

        changed = bool(activated_mod_ids)
        if changed:
            self._persist_changes(profile_path)

        unique_missing = list(dict.fromkeys(missing_dependencies))
        unique_cycle_refs = list(dict.fromkeys(circular_dependency_refs))
        unique_incompatible = list(dict.fromkeys(version_incompatible_mods))
        return LoadOrderActivationResult(
            changed=changed,
            activated_mod_ids=activated_mod_ids,
            missing_dependencies=unique_missing,
            version_incompatible_mods=unique_incompatible,
            blocked_reason="circular_dependency" if unique_cycle_refs else None,
            blocking_mod_refs=unique_cycle_refs,
        )

    def deactivate_mod(self, mod_identifier: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        config = self._config_service.get_config()
        if config.enforce_dependency_order:
            dependents = self._active_mods_service.get_dependents_for_active_mod(
                mod_identifier
            )
            if dependents:
                return LoadOrderMutationResult(
                    changed=False,
                    active_mod_ids=list(self._active_mods_service.active_mods_ids),
                    blocked_reason="required_by_active_mods",
                    blocking_mod_refs=dependents,
                )

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
        blocked = self._rollback_if_dependency_order_invalid(before)
        if blocked:
            return blocked
        return self._persist_if_changed(before, profile_path)

    def move_down(self, mod_identifier: str) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        profile_path = self._require_profile_path()
        self._active_mods_service.move_mod_down(mod_identifier)
        blocked = self._rollback_if_dependency_order_invalid(before)
        if blocked:
            return blocked
        return self._persist_if_changed(before, profile_path)

    def reorder(self, mod_identifiers: list[str]) -> LoadOrderMutationResult:
        before = list(self._active_mods_service.active_mod_refs)
        normalized_refs = self._active_mods_service.normalize_mod_refs(
            list(mod_identifiers)
        )
        if len(normalized_refs) != len(mod_identifiers) or set(normalized_refs) != set(
            before
        ):
            return LoadOrderMutationResult(
                changed=False,
                active_mod_ids=list(self._active_mods_service.active_mods_ids),
                blocked_reason="invalid_order_payload",
            )

        if normalized_refs == before:
            return LoadOrderMutationResult(
                changed=False,
                active_mod_ids=list(self._active_mods_service.active_mods_ids),
            )

        config = self._config_service.get_config()
        if config.enforce_dependency_order:
            violations = self._active_mods_service.find_order_dependency_violations(
                normalized_refs
            )
            if violations:
                return LoadOrderMutationResult(
                    changed=False,
                    active_mod_ids=list(self._active_mods_service.active_mods_ids),
                    blocked_reason="invalid_dependency_order",
                    blocking_mod_refs=violations,
                )

        profile_path = self._require_profile_path()
        self._active_mods_service.active_mod_refs = normalized_refs
        return self._persist_if_changed(before, profile_path)

    def _rollback_if_dependency_order_invalid(
        self, before: list[str]
    ) -> LoadOrderMutationResult | None:
        config = self._config_service.get_config()
        if not config.enforce_dependency_order:
            return None

        violations = self._active_mods_service.find_order_dependency_violations(
            self._active_mods_service.active_mod_refs
        )
        if not violations:
            return None

        self._active_mods_service.active_mod_refs = before
        return LoadOrderMutationResult(
            changed=False,
            active_mod_ids=list(self._active_mods_service.active_mods_ids),
            blocked_reason="invalid_dependency_order",
            blocking_mod_refs=violations,
        )

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

    def _get_game_version(self, game_path: str) -> tuple[int, ...] | None:
        """Return the cached game version, re-reading when the path changes."""
        if self._cached_game_path != game_path:
            self._cached_game_path = game_path
            self._cached_game_version = get_game_version(game_path)
        return self._cached_game_version

    def _resolve_mod_info(self, mod_identifier: str) -> ModInfo | None:
        """Look up a ``ModInfo`` from a ref-key or plain mod ID."""
        ref = parse_reference_key(mod_identifier)
        if ref is not None:
            return self._catalogue_service.get_mod_by_source(
                ref.id, is_local=ref.is_local
            )
        return self._catalogue_service.get_mod(mod_identifier)

    def _require_profile_path(self) -> str:
        config = self._config_service.get_config()
        if config.profile_path:
            return config.profile_path

        raise ProfileWriteError("", "Profile path is not configured.")

    def _persist_changes(self, profile_path: str) -> None:
        self._active_mods_service.save_to_profile(
            profile_path, catalogue_service=self._catalogue_service
        )
