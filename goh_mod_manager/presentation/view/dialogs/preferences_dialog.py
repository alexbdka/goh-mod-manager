from typing import Callable, Optional

from PySide6.QtCore import Qt, QLocale
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

from goh_mod_manager.i18n.translator import normalize_language
from goh_mod_manager.infrastructure.config_manager import ConfigManager
from goh_mod_manager.presentation.view.ui.preferences_dialog import Ui_PreferencesDialog


class PreferencesDialog(QDialog):
    def __init__(
        self,
        config: ConfigManager,
        parent=None,
        on_start_guided_tour: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent)
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self._connect_signals()
        self._config = config
        self._on_start_guided_tour = on_start_guided_tour
        self._load()

    def _load(self):
        game_path = self._config.get_game_directory()
        mods_path = self._config.get_mods_directory()
        options_path = self._config.get_options_file()
        show_guided_tour = self._config.get_show_guided_tour()
        language = self._config.get_language()

        self.ui.gameFolderLineEdit.setText(game_path)
        self.ui.modsFolderLineEdit.setText(mods_path)
        self.ui.settingsFileLineEdit.setText(options_path)
        self.ui.checkBox_show_guided_tour.setChecked(show_guided_tour)
        self._populate_languages(language)

    def _populate_languages(self, current_language: str) -> None:
        translator = getattr(QApplication.instance(), "translation_manager", None)
        status = translator.language_file_status() if translator else {}
        available = {"en"} | {
            code for code, (has_qm, _) in status.items() if has_qm
        }
        current_language = normalize_language(current_language, available)

        codes = set(status.keys()) | {"en"}
        ordered_codes = ["en"] + sorted(code for code in codes if code != "en")
        self.ui.comboBox_language.clear()
        for code in ordered_codes:
            self.ui.comboBox_language.addItem(
                self._format_language_label(code), code
            )
            has_qm, has_ts = status.get(code, (code == "en", False))
            if not has_qm:
                index = self.ui.comboBox_language.count() - 1
                self.ui.comboBox_language.setItemData(
                    index, 0, Qt.ItemDataRole.UserRole - 1
                )
                if has_ts:
                    self.ui.comboBox_language.setItemData(
                        index,
                        self.tr("Translation source available (.ts), compile to enable."),
                        Qt.ItemDataRole.ToolTipRole,
                    )
                else:
                    self.ui.comboBox_language.setItemData(
                        index,
                        self.tr("Translation not available."),
                        Qt.ItemDataRole.ToolTipRole,
                    )
        index = self.ui.comboBox_language.findData(current_language)
        if index >= 0:
            self.ui.comboBox_language.setCurrentIndex(index)

    @staticmethod
    def _format_language_label(code: str) -> str:
        locale = QLocale(code)
        if locale.language() == QLocale.Language.C:
            return code

        language = locale.nativeLanguageName()
        if not language:
            language = QLocale.languageToString(locale.language())

        territory = locale.nativeTerritoryName()
        if territory:
            return f"{language} ({territory})"

        return language

    def _connect_signals(self):
        self.ui.gameFolderButton.clicked.connect(self._browse_game)
        self.ui.modsFolderButton.clicked.connect(self._browse_mods)
        self.ui.settingsFileButton.clicked.connect(self._browse_options)
        self.ui.pushButton_start_guided_tour.clicked.connect(self._start_guided_tour)
        try:
            self.ui.okButton.clicked.disconnect()
        except RuntimeError:
            pass
        self.ui.okButton.clicked.connect(self._save)

    def _browse_game(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Game Directory"),
            self.ui.gameFolderLineEdit.text(),
        )
        if path:
            self.ui.gameFolderLineEdit.setText(path)

    def _browse_mods(self):
        path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Mods Directory"),
            self.ui.modsFolderLineEdit.text(),
        )
        if path:
            self.ui.modsFolderLineEdit.setText(path)

    def _browse_options(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Options File"),
            self.ui.settingsFileLineEdit.text(),
            self.tr("Options File (*.set);;All Files (*)"),
        )
        if path:
            self.ui.settingsFileLineEdit.setText(path)

    def _save(self) -> bool:
        game_path = self.ui.gameFolderLineEdit.text().strip()
        mods_path = self.ui.modsFolderLineEdit.text().strip()
        options_path = self.ui.settingsFileLineEdit.text().strip()
        show_guided_tour = self.ui.checkBox_show_guided_tour.isChecked()
        language = self.ui.comboBox_language.currentData()

        if not game_path:
            QMessageBox.warning(
                self,
                self.tr("Invalid Path"),
                self.tr("Please specify a game directory."),
            )
            return False

        if not mods_path:
            QMessageBox.warning(
                self,
                self.tr("Invalid Path"),
                self.tr("Please specify a mods directory."),
            )
            return False

        if not options_path:
            QMessageBox.warning(
                self,
                self.tr("Invalid Path"),
                self.tr("Please specify an options file."),
            )
            return False

        self._config.set_game_directory(game_path)
        self._config.set_mods_directory(mods_path)
        self._config.set_options_file(options_path)
        self._config.set_show_guided_tour(show_guided_tour)
        if language:
            self._config.set_language(language)
        self.accept()
        return True

    def _start_guided_tour(self) -> None:
        if self._save() and self._on_start_guided_tour:
            self._on_start_guided_tour()
