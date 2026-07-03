import logging
from dataclasses import dataclass, field

from src.services.active_mods_service import ActiveModsReplaceResult, ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PresetApplyResult:
    success: bool = False
    missing_mods: list[str] = field(default_factory=list)
    blocked_reason: str | None = None
    blocking_mod_refs: list[str] = field(default_factory=list)

    def __iter__(self):
        yield self.success
        yield self.missing_mods


class PresetService:
    """
    Manages local mod presets (saving, loading, and applying lists of mods).
    """

    def __init__(
        self,
        config_service: ConfigService,
        catalogue_service: ModsCatalogueService,
        active_mods_service: ActiveModsService,
    ):
        self.config_service = config_service
        self.catalogue = catalogue_service
        self.active_mods = active_mods_service

    def get_all_presets(self) -> dict[str, list[str]]:
        """Returns a dictionary of all saved presets."""
        config = self.config_service.get_config()
        return config.presets

    def get_preset(self, name: str) -> list[str] | None:
        """Returns the mod IDs for a specific preset, or None if not found."""
        return self.get_all_presets().get(name)

    def save_preset(self, name: str, mod_ids: list[str] | None = None) -> None:
        """
        Saves a list of mod references as a preset.
        If mod_ids is not provided, saves the currently active source-aware refs.
        """
        if mod_ids is None:
            # Create a copy of the list so it's not by reference
            mod_ids = list(self.active_mods.active_mod_refs)
        else:
            mod_ids = self.normalize_preset_mods(mod_ids)

        config = self.config_service.get_config()
        config.presets[name] = mod_ids
        self.config_service.save()

        logger.info(f"Saved preset '{name}' with {len(mod_ids)} mods.")

    def delete_preset(self, name: str) -> bool:
        """Deletes a preset by name. Returns True if successful."""
        config = self.config_service.get_config()
        if name in config.presets:
            del config.presets[name]
            self.config_service.save()
            logger.info(f"Deleted preset '{name}'.")
            return True

        logger.warning(f"Failed to delete preset '{name}': Not found.")
        return False

    def apply_preset(self, name: str) -> PresetApplyResult:
        """
        Applies a preset, completely replacing the currently active mods.
        The result remains tuple-unpackable as ``(success, missing_mods)`` for
        compatibility with the pre-refactor call sites.
        """
        preset_mod_ids = self.get_preset(name)
        if preset_mod_ids is None:
            logger.error(f"Attempted to apply unknown preset: '{name}'")
            return PresetApplyResult(success=False)

        replace_result: ActiveModsReplaceResult = self.active_mods.replace_active_mods(
            preset_mod_ids
        )

        if replace_result.missing_mods:
            logger.warning(
                f"Applied preset '{name}' but {len(replace_result.missing_mods)} mods "
                "are missing from the catalogue."
            )
        elif replace_result.blocked_reason:
            logger.warning(
                "Applied preset '%s' with blocked entries: %s",
                name,
                replace_result.blocked_reason,
            )
        else:
            logger.info(f"Successfully applied preset '{name}'.")

        return PresetApplyResult(
            success=True,
            missing_mods=replace_result.missing_mods,
            blocked_reason=replace_result.blocked_reason,
            blocking_mod_refs=replace_result.blocking_mod_refs,
        )

    def normalize_preset_mods(self, mod_ids: list[str]) -> list[str]:
        """
        Convert installed preset entries to source-aware refs.

        Unknown entries are preserved verbatim so legacy presets can still report
        missing mods by the original ID instead of inventing a source prefix.
        """
        normalized: list[str] = []
        for mod_id in mod_ids:
            refs = self.active_mods.normalize_mod_refs([mod_id])
            if refs and self._is_installed_ref(refs[0]):
                normalized.append(refs[0])
            else:
                normalized.append(mod_id)
        return normalized

    def _is_installed_ref(self, mod_ref: str) -> bool:
        reference = self.active_mods.reference_from_identifier(mod_ref)
        if reference is None:
            return False
        return bool(
            self.catalogue.get_mod_by_source(reference.id, is_local=reference.is_local)
        )
