import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from goh_mod_manager.infrastructure.mod_manager_logger import logger
from goh_mod_manager.presentation.view.ui.import_dialog import Ui_ImportDialog


class ImportDialog(QDialog):
    """Dialog to select a mod archive or folder for import."""

    mod_import_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ImportDialog()
        self.ui.setupUi(self)
        self._connect_signals()

    def _connect_signals(self):
        self.ui.archive_button.clicked.connect(self._browse_archive)
        self.ui.folder_button.clicked.connect(self._browse_folder)
        self.ui.import_button.clicked.connect(self._import_clicked)
        self.ui.cancel_button.clicked.connect(self.reject)

    def _browse_archive(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Mod Archive"),
            "",
            self.tr("Archives (*.zip *.tar *.tar.gz *.tar.xz *.7z *.rar);"),
        )
        if path:
            self.ui.path_input.setText(path)

    def _browse_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, self.tr("Select Mod Folder")
        )
        if path:
            self.ui.path_input.setText(path)

    def _import_clicked(self) -> None:
        path = self.ui.path_input.text().strip()
        if not path:
            QMessageBox.warning(
                self,
                self.tr("No Path Selected"),
                self.tr("Please select a valid archive or folder."),
            )
            return

        if not os.path.exists(path):
            QMessageBox.warning(
                self,
                self.tr("Invalid Path"),
                self.tr("The selected path does not exist."),
            )
            return

        logger.debug(f"Import requested for: {path}")
        self.mod_import_requested.emit(path)
        self.accept()
