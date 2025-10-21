from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
)

from goh_mod_manager.util.config_manager import ConfigManager
from goh_mod_manager.view.ui.preferences_dialog import Ui_PreferencesDialog


class PreferencesDialog(QDialog):
    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self._connect_signals()
        self._config = config
        self._load()

    def _load(self):
        game_path = self._config.get_game_directory()
        mods_path = self._config.get_mods_directory()
        options_path = self._config.get_options_file()

        self.ui.gameFolderLineEdit.setText(game_path)
        self.ui.modsFolderLineEdit.setText(mods_path)
        self.ui.settingsFileLineEdit.setText(options_path)

    def _connect_signals(self):
        self.ui.gameFolderButton.clicked.connect(self._browse_game)
        self.ui.modsFolderButton.clicked.connect(self._browse_mods)
        self.ui.settingsFileButton.clicked.connect(self._browse_options)
        self.ui.okButton.clicked.connect(self._save)

    def _browse_game(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Game Directory", self.ui.gameFolderLineEdit.text()
        )
        if path:
            self.ui.gameFolderLineEdit.setText(path)

    def _browse_mods(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Mods Directory", self.ui.modsFolderLineEdit.text()
        )
        if path:
            self.ui.modsFolderLineEdit.setText(path)

    def _browse_options(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Options File",
            self.ui.settingsFileLineEdit.text(),
            "Options File (*.set);;All Files (*)",
        )
        if path:
            self.ui.settingsFileLineEdit.setText(path)

    def _save(self):
        game_path = self.ui.gameFolderLineEdit.text().strip()
        mods_path = self.ui.modsFolderLineEdit.text().strip()
        options_path = self.ui.settingsFileLineEdit.text().strip()

        if not game_path:
            QMessageBox.warning(
                self, "Invalid Path", "Please specify a game directory."
            )
            return

        if not mods_path:
            QMessageBox.warning(
                self, "Invalid Path", "Please specify a mods directory."
            )
            return

        if not options_path:
            QMessageBox.warning(self, "Invalid Path", "Please specify an options file.")
            return

        self._config.set_game_directory(game_path)
        self._config.set_mods_directory(mods_path)
        self._config.set_options_file(options_path)
        self.accept()
