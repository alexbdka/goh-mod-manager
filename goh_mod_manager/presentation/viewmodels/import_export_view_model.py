from typing import Dict, List, Tuple

from PySide6.QtCore import QObject

from goh_mod_manager.core.mod_manager_model import ModManagerModel
from goh_mod_manager.services.share_code_service import ShareCodeService


class ImportExportViewModel(QObject):
    def __init__(self, model: ModManagerModel):
        super().__init__()
        self._model = model
        self._share_code_service = ShareCodeService()

    def get_export_code(self) -> Tuple[str, int]:
        active_mods = self._model.get_active_mods()
        code = self._share_code_service.encode_mods_list(active_mods)
        return code, len(active_mods)

    def get_share_code(self) -> Tuple[str, int]:
        active_mods = self._model.get_active_mods()
        code = self._share_code_service.encode_versioned(active_mods)
        return code, len(active_mods)

    def import_code(self, code: str) -> Tuple[List[Dict], List[Dict], int]:
        mod_data = self._share_code_service.decode(code)
        found_mods, missing_mods = self._share_code_service.resolve_mods(
            mod_data, self._model.get_installed_mods()
        )
        self._model.clear_active_mods()
        for mod in found_mods:
            self._model.enable_mod(mod)

        found_payload = [{"id": mod.id, "name": mod.name} for mod in found_mods]
        return found_payload, missing_mods, len(mod_data)
