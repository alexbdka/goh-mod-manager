import logging
import threading

from PySide6.QtCore import QObject, QRunnable, Signal

logger = logging.getLogger(__name__)


class ModImportSignals(QObject):
    """
    Defines the signals available from a running mod import worker thread.
    QRunnable does not inherit from QObject natively, so we use a separate class.
    """

    success = Signal()
    error = Signal(str)
    progress = Signal(int, str)
    conflict = Signal(str)


class ModImportWorker(QRunnable):
    """
    Worker thread to handle the potentially long-running task of extracting
    and copying mods into the game directory without freezing the main UI.
    """

    def __init__(self, import_target, file_path: str):
        super().__init__()
        self.import_target = import_target
        self.file_path = file_path
        self.signals = ModImportSignals()
        self._conflict_event = threading.Event()
        self._conflict_resolution = "cancel"

    def set_conflict_resolution(self, resolution: str):
        self._conflict_resolution = resolution
        self._conflict_event.set()

    def _on_conflict(self, mod_name: str) -> str:
        self._conflict_event.clear()
        self.signals.conflict.emit(mod_name)
        self._conflict_event.wait()
        return self._conflict_resolution

    def run(self):
        """
        Executes the import process in a background thread.
        """
        try:
            import_func = (
                self.import_target.import_mod
                if hasattr(self.import_target, "import_mod")
                else self.import_target
            )
            success = import_func(
                self.file_path,
                progress_callback=self._emit_progress,
                conflict_callback=self._on_conflict,
                reload_on_success=False,
            )
            if success:
                self.signals.success.emit()
            else:
                self.signals.error.emit(
                    "Mod import returned False for an unknown reason."
                )
        except Exception as e:
            logger.error(f"Background worker caught import error: {e}")
            self.signals.error.emit(str(e))

    def _emit_progress(self, percent: int, message: str):
        self.signals.progress.emit(percent, message)
