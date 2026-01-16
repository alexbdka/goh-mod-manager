from typing import List

from PySide6.QtCore import QObject, Signal

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.core.mod_manager_model import ModManagerModel


class PresetsViewModel(QObject):
    presets_changed = Signal(list)

    def __init__(self, model: ModManagerModel):
        super().__init__()
        self._model = model
        self._model.presets_signal.connect(self._emit_presets)

    def get_presets_names(self) -> List[str]:
        return self._model.get_presets_names()

    def get_preset_mods(self, preset_name: str) -> List[Mod]:
        return self._model.get_preset_mods(preset_name)

    def has_preset(self, preset_name: str) -> bool:
        return self._model.has_preset(preset_name)

    def get_active_mods_count(self) -> int:
        return self._model.get_active_mods_count()

    def save_preset(self, preset_name: str) -> bool:
        return self._model.save_preset(preset_name)

    def load_preset(self, preset_name: str) -> bool:
        return self._model.load_preset(preset_name)

    def delete_preset(self, preset_name: str) -> bool:
        return self._model.delete_preset(preset_name)

    def _emit_presets(self) -> None:
        self.presets_changed.emit(self._model.get_presets_names())
