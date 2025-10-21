import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from goh_mod_manager.util.mod_manager_logger import logger
from goh_mod_manager.view.ui.import_dialog import Ui_ImportDialog


class ImportDialog(QDialog):
    mod_import_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ImportDialog()
        self.ui.setupUi(self)
        self._connect_signals()

    def _connect_signals(self):
        self.ui.archive_button.clicked.connect(self.browse_archive)
        self.ui.folder_button.clicked.connect(self.browse_folder)
        self.ui.import_button.clicked.connect(self.import_clicked)
        self.ui.cancel_button.clicked.connect(self.reject)

    def browse_archive(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mod Archive",
            "",
            "Archives (*.zip *.tar *.tar.gz *.tar.xz *.7z *.rar);",
        )
        if path:
            self.ui.path_input.setText(path)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Mod Folder")
        if path:
            self.ui.path_input.setText(path)

    def import_clicked(self):
        path = self.ui.path_input.text().strip()
        if not path:
            QMessageBox.warning(
                self, "No Path Selected", "Please select a valid archive or folder."
            )
            return

        if not os.path.exists(path):
            QMessageBox.warning(
                self, "Invalid Path", "The selected path does not exist."
            )
            return

        logger.debug(f"Import requested for: {path}")
        self.mod_import_requested.emit(path)
        self.accept()
