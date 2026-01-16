from typing import List

from PySide6.QtCore import QObject, Signal, Qt

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.core.mod_manager_model import ModManagerModel
from goh_mod_manager.infrastructure.async_worker import Worker, run_in_thread
from goh_mod_manager.services.dependencies_service import DependenciesService
from goh_mod_manager.services.mods_catalog_service import ModsCatalogService


class ModActionsViewModel(QObject):
    refresh_installed_started = Signal()
    refresh_installed_finished = Signal()
    refresh_installed_error = Signal(str)

    def __init__(self, model: ModManagerModel):
        super().__init__()
        self._model = model
        self._dependencies = DependenciesService()
        self._mods_catalog = ModsCatalogService()
        self._workers: list[Worker] = []

    def get_active_mods(self) -> List[Mod]:
        return self._model.get_active_mods()

    def get_installed_mods(self) -> List[Mod]:
        return self._model.get_installed_mods()

    def get_missing_dependencies(self, mod: Mod) -> List[Mod]:
        return self._dependencies.get_missing_dependencies(
            mod, self._model.get_active_mods(), self._model.get_installed_mods()
        )

    def enable_mod(self, mod: Mod) -> bool:
        return self._model.enable_mod(mod)

    def disable_mod(self, mod: Mod) -> bool:
        return self._model.disable_mod(mod)

    def disable_mods(self, mods: List[Mod]) -> None:
        for mod in mods:
            self._model.disable_mod(mod)

    def set_mods_order(self, reordered_mods: List[Mod]) -> bool:
        return self._model.set_mods_order(reordered_mods)

    def clear_active_mods(self) -> bool:
        return self._model.clear_active_mods()

    def refresh_all(self) -> None:
        self._model.refresh_all()

    def refresh_installed_mods(self) -> None:
        self._model.refresh_installed_mods()

    def refresh_active_mods(self) -> None:
        self._model.refresh_active_mods()

    def refresh_installed_mods_async(self) -> None:
        self.refresh_installed_started.emit()
        mods_directory = self._model.get_config().get_mods_directory()
        game_mods_directory = self._model.get_game_mods_directory()
        worker = Worker(
            self._mods_catalog.scan_installed_mods,
            mods_directory,
            game_mods_directory,
        )
        worker.signals.result.connect(self._on_refresh_installed_result)
        worker.signals.error.connect(self.refresh_installed_error.emit)
        worker.signals.finished.connect(self.refresh_installed_finished.emit)
        worker.signals.finished.connect(
            lambda w=worker: self._workers.remove(w), Qt.QueuedConnection
        )
        self._workers.append(worker)
        run_in_thread(worker)

    def _on_refresh_installed_result(self, mods: List[Mod]) -> None:
        self._model.replace_installed_mods(mods)

    def refresh_all_async(self) -> None:
        self.refresh_active_mods()
        self.refresh_installed_mods_async()
