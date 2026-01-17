from pathlib import Path
from typing import Tuple

from PySide6.QtCore import QObject, Qt, Signal, Slot

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.core.mod_manager_model import ModManagerModel
from goh_mod_manager.infrastructure.async_worker import Worker, run_in_thread
from goh_mod_manager.infrastructure.config_manager import ConfigManager
from goh_mod_manager.infrastructure.mod_manager_logger import get_app_dir
from goh_mod_manager.services.mod_files_service import ModFilesService
from goh_mod_manager.services.mod_import_service import ModImportService
from goh_mod_manager.services.system_actions_service import SystemActionsService


class FileActionsViewModel(QObject):
    import_started = Signal()
    import_finished = Signal()
    import_succeeded = Signal()
    import_error = Signal(str)

    def __init__(self, model: ModManagerModel, config: ConfigManager):
        super().__init__()
        self._model = model
        self._config = config
        self._system_actions = SystemActionsService()
        self._mod_files = ModFilesService()
        self._mod_import_service = ModImportService()
        self._workers: list[Worker] = []

    def open_game_folder(self) -> Tuple[bool, str]:
        return self._system_actions.open_path(self._config.get_game_directory())

    def launch_game(self) -> Tuple[bool, str]:
        game_directory_value = self._config.get_game_directory()
        if not game_directory_value:
            return False, "Game directory is not set. Check Preferences."

        game_directory = Path(game_directory_value)
        if not game_directory.exists():
            return False, "Game directory is not set. Check Preferences."

        exe_path = game_directory / "binaries" / "x64" / "call_to_arms.exe"
        if not exe_path.exists():
            return False, f"Game executable not found: {exe_path}"

        return self._system_actions.launch_executable(
            exe_path, working_dir=exe_path.parent
        )

    def open_mods_folder(self) -> Tuple[bool, str]:
        return self._system_actions.open_path(self._config.get_mods_directory())

    def open_options_file(self) -> Tuple[bool, str]:
        return self._system_actions.open_path(self._config.get_options_file())

    def open_logs(self) -> Tuple[bool, str]:
        log_file = get_app_dir() / "logs" / "goh_mod_manager.log"
        return self._system_actions.open_path(log_file)

    def open_mod_folder(self, folder_path: str) -> Tuple[bool, str]:
        return self._system_actions.open_path(folder_path)

    def open_steam_page(self, mod_id: str) -> Tuple[bool, str]:
        return self._system_actions.open_url(f"steam://url/CommunityFilePage/{mod_id}")

    def generate_help_file(self, output_dir: str = ".") -> Tuple[bool, str]:
        return self._mod_files.generate_help_file(
            self._config.get_options_file(),
            self._config.get_game_directory(),
            self._config.get_mods_directory(),
            self._model.get_active_mods(),
            output_dir=output_dir,
        )

    def open_path(self, path: str) -> Tuple[bool, str]:
        return self._system_actions.open_path(path)

    def delete_mod(self, mod: Mod) -> bool:
        return self._model.delete_mod(mod)

    def import_mod_async(self, archive_path: str) -> None:
        game_mods_directory = self._model.get_game_mods_directory()
        self.import_started.emit()
        worker = Worker(
            self._mod_import_service.import_mod,
            archive_path,
            game_mods_directory,
        )

        worker.signals.result.connect(self._on_import_result, Qt.QueuedConnection)
        worker.signals.error.connect(self.import_error.emit, Qt.QueuedConnection)
        worker.signals.finished.connect(self.import_finished.emit, Qt.QueuedConnection)
        worker.signals.finished.connect(
            lambda w=worker: self._workers.remove(w), Qt.QueuedConnection
        )
        self._workers.append(worker)
        run_in_thread(worker)

    @Slot(object)
    def _on_import_result(self, success: bool) -> None:
        if success:
            self.import_succeeded.emit()
        else:
            self.import_error.emit(
                "Failed to import mod. Check the file format and try again."
            )
