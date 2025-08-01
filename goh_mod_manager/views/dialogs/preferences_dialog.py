from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from goh_mod_manager.utils.config_manager import ConfigManager
from goh_mod_manager.views.ui.preferences_dialog import Ui_PreferencesDialog


class PreferencesDialog(QDialog):
    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self._connect_signals()
        self._config = config
        self._load()

    def _load(self):
        mods_path = self._config.get_mods_directory()
        options_path = self._config.get_options_file()
        self.ui.folderLineEdit.setText(mods_path)
        self.ui.fileLineEdit.setText(options_path)

    def _connect_signals(self):
        self.ui.folderBrowseButton.clicked.connect(self._browse_mods)
        self.ui.fileBrowseButton.clicked.connect(self._browse_options)
        self.ui.okButton.clicked.connect(self._save)

    def _browse_mods(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Mods Directory", self.ui.folderLineEdit.text()
        )
        if path:
            self.ui.folderLineEdit.setText(path)

    def _browse_options(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Options File",
            self.ui.fileLineEdit.text(),
            "Options File (*.set);",
        )
        if path:
            self.ui.fileLineEdit.setText(path)

    def _save(self):
        mods_path = self.ui.folderLineEdit.text().strip()
        options_path = self.ui.fileLineEdit.text().strip()

        if not mods_path:
            QMessageBox.warning(
                self, "Invalid Path", "Please specify a mods directory."
            )
            return

        if not options_path:
            QMessageBox.warning(self, "Invalid Path", "Please specify an options file.")
            return

        self._config.set_mods_directory(mods_path)
        self._config.set_options_file(options_path)
        self.accept()
