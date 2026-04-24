import logging

from src.application.state import ShareCodeExportResult, ShareCodeImportResult
from src.core.exceptions import ProfileWriteError
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.share_code_service import ShareCodeService

logger = logging.getLogger(__name__)


class ApplicationShareCodeUseCase:
    """
    Handles share code import/export as an application use case.
    """

    def __init__(
        self,
        share_code_service: ShareCodeService,
        active_mods_service: ActiveModsService,
        catalogue_service: ModsCatalogueService,
        config_service: ConfigService,
    ):
        self._share_code_service = share_code_service
        self._active_mods_service = active_mods_service
        self._catalogue_service = catalogue_service
        self._config_service = config_service

    def export_active_mods(self) -> ShareCodeExportResult:
        active_mods = self._active_mods_service.get_active_mods()
        if not active_mods:
            return ShareCodeExportResult(has_active_mods=False, code="")

        return ShareCodeExportResult(
            has_active_mods=True,
            code=self._share_code_service.encode(active_mods),
        )

    def import_share_code(self, code: str) -> ShareCodeImportResult:
        decoded_data = self._share_code_service.decode(code)
        if not decoded_data:
            return ShareCodeImportResult(success=False, missing_mods=[])

        profile_path = self._require_profile_path()

        found_mods, missing_mods = self._share_code_service.resolve_mods(
            decoded_data, self._catalogue_service.all_mods
        )

        dependency_missing_ids = self._active_mods_service.replace_active_mods(
            [mod.id for mod in found_mods]
        )

        known_missing_ids = {str(item.get("id", "")) for item in missing_mods}
        for mod_id in dependency_missing_ids:
            if mod_id not in known_missing_ids:
                missing_mods.append({"id": mod_id, "name": mod_id})
                known_missing_ids.add(mod_id)

        self._active_mods_service.save_to_profile(
            profile_path, catalogue_service=self._catalogue_service
        )

        return ShareCodeImportResult(success=True, missing_mods=missing_mods)

    def _require_profile_path(self) -> str:
        config = self._config_service.get_config()
        if config.profile_path:
            return config.profile_path

        raise ProfileWriteError("", "Profile path is not configured.")
