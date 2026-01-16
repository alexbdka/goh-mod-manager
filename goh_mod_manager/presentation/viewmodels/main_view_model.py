from typing import List

from PySide6.QtCore import QObject, Signal

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.core.mod_manager_model import ModManagerModel


class MainViewModel(QObject):
    mods_lists_changed = Signal(list, list)
    presets_changed = Signal(list)
    active_mods_count_changed = Signal(int)

    def __init__(self, model: ModManagerModel):
        super().__init__()
        self._model = model
        self._connect_model_signals()

    def load_from_config(
        self, mods_directory: str, options_file: str, presets: dict
    ) -> None:
        self._model.set_mods_directory(mods_directory)
        self._model.set_options_file(options_file)
        self._model.set_presets(presets)
        self.emit_all()

    def emit_all(self) -> None:
        self._emit_mods_snapshot()
        self._emit_presets_snapshot()
        self.active_mods_count_changed.emit(self._model.get_active_mods_count())

    def get_installed_mods(self) -> List[Mod]:
        return self._model.get_installed_mods()

    def get_active_mods(self) -> List[Mod]:
        return self._model.get_active_mods()

    def get_presets_names(self) -> List[str]:
        return self._model.get_presets_names()

    def _connect_model_signals(self) -> None:
        self._model.installed_mods_signal.connect(self._emit_mods_snapshot)
        self._model.presets_signal.connect(self._emit_presets_snapshot)
        self._model.mods_counter_signal.connect(self.active_mods_count_changed.emit)

    def _emit_mods_snapshot(self) -> None:
        self.mods_lists_changed.emit(
            self._model.get_installed_mods(), self._model.get_active_mods()
        )

    def _emit_presets_snapshot(self) -> None:
        self.presets_changed.emit(self._model.get_presets_names())
