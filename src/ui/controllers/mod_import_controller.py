from collections.abc import Callable

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox,
    QProgressDialog,
    QStatusBar,
    QWidget,
)

from src.ui.dialogs.import_mod_dialog import ImportModDialog
from src.ui.workers.mod_import_worker import ModImportWorker


class ModImportController:
    """
    Qt-specific controller for the mod import flow.
    Keeps worker/progress/conflict orchestration out of MainWindow.
    """

    def __init__(
        self,
        parent: QWidget,
        import_mod: Callable[..., bool],
        reload: Callable[[], None],
        thread_pool: QThreadPool,
        status_bar: QStatusBar,
        show_info_message: Callable[[str, str], None],
        show_error_message: Callable[[str, str], None],
    ):
        self._parent = parent
        self._import_mod = import_mod
        self._reload = reload
        self._thread_pool = thread_pool
        self._status_bar = status_bar
        self._show_info_message = show_info_message
        self._show_error_message = show_error_message
        self._import_progress: QProgressDialog | None = None

    def start_import_flow(self):
        """Prompt for an import target and launch the background worker."""
        path = self._prompt_import_mod_path()
        if not path:
            return

        self._status_bar.showMessage(
            self._parent.tr("Importing mod from {0}... Please wait.").format(path)
        )
        worker = self._create_import_worker(path)
        self._import_progress = self._create_import_progress_dialog()
        self._import_progress.show()
        self._thread_pool.start(worker)

    def _prompt_import_mod_path(self) -> str | None:
        """Open the import dialog and return the selected path, if any."""
        dialog = ImportModDialog(self._parent)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.get_path()

    def _create_import_worker(self, path: str) -> ModImportWorker:
        """Create and wire the background worker for one import request."""
        worker = ModImportWorker(self._import_mod, path)
        worker.signals.success.connect(self._on_import_success)
        worker.signals.error.connect(self._on_import_error)
        worker.signals.progress.connect(self._on_import_progress)
        worker.signals.conflict.connect(
            lambda mod_name: self._on_import_conflict(mod_name, worker)
        )
        return worker

    def _create_import_progress_dialog(self) -> QProgressDialog:
        """Create the modal progress dialog used during long-running imports."""
        progress = QProgressDialog(
            self._parent.tr("Importing mod..."),
            self._parent.tr("Cancel"),
            0,
            100,
            self._parent,
        )
        progress.setWindowTitle(self._parent.tr("Import Mod"))
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.setValue(0)
        return progress

    def _on_import_progress(self, percent: int, message: str):
        """Update the progress dialog with worker progress information."""
        if self._import_progress is not None:
            self._import_progress.setLabelText(self._parent.tr(message))
            self._import_progress.setValue(percent)

    def _on_import_success(self):
        """Reload state and report a successful import back to the user."""
        self._reload()
        if self._import_progress is not None:
            self._import_progress.setValue(100)
        self._show_info_message(
            self._parent.tr("Import Success"),
            self._parent.tr("Mod successfully imported!"),
        )
        self._status_bar.showMessage(self._parent.tr("Mod import complete."), 3000)

    def _on_import_error(self, error_msg: str):
        """Dismiss progress UI and display an import error message."""
        if self._import_progress is not None:
            self._import_progress.cancel()
        self._show_error_message(
            self._parent.tr("Import Failed"),
            self._parent.tr("Failed to import mod:\n\n{0}").format(error_msg),
        )
        self._status_bar.clearMessage()

    def _on_import_conflict(self, mod_name: str, worker: ModImportWorker):
        """Ask the user how to resolve an existing destination mod directory."""
        msg_box = QMessageBox(self._parent)
        msg_box.setWindowTitle(self._parent.tr("Mod Conflict"))
        msg_box.setText(
            self._parent.tr("The mod '{0}' already exists.").format(mod_name)
        )
        msg_box.setInformativeText(self._parent.tr("What would you like to do?"))

        overwrite_btn = msg_box.addButton(
            self._parent.tr("Overwrite"), QMessageBox.ButtonRole.AcceptRole
        )
        skip_btn = msg_box.addButton(
            self._parent.tr("Skip"), QMessageBox.ButtonRole.RejectRole
        )
        msg_box.addButton(QMessageBox.StandardButton.Cancel)

        msg_box.exec()

        if msg_box.clickedButton() == overwrite_btn:
            worker.set_conflict_resolution("overwrite")
        elif msg_box.clickedButton() == skip_btn:
            worker.set_conflict_resolution("skip")
        else:
            worker.set_conflict_resolution("cancel")
