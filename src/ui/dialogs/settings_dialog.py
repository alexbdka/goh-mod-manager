import os

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from src.application.state import SettingsState
from src.ui.i18n_registry import (
    TranslationLocale,
    discover_runtime_languages,
    language_label,
)
from src.ui.language_change_mixin import LanguageChangeMixin


class SettingsDialog(LanguageChangeMixin, QDialog):
    """
    Dialog for editing application paths, appearance, and language settings.
    """

    def __init__(
        self,
        settings_state: SettingsState | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.resize(640, 360)

        settings_state = settings_state or SettingsState(
            game_path="",
            workshop_path="",
            profile_path="",
            language="en_US",
            theme="auto",
            font="Inter",
        )
        self.current_game_path = settings_state.game_path or ""
        self.current_workshop_path = settings_state.workshop_path or ""
        self.current_profile_path = settings_state.profile_path or ""
        self.current_language = settings_state.language
        self.current_theme = settings_state.theme
        self.current_font = settings_state.font

        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.paths_tab = QWidget()
        self._setup_paths_tab()
        self.tabs.addTab(self.paths_tab, "")

        self.appearance_tab = QWidget()
        self._setup_appearance_tab()
        self.tabs.addTab(self.appearance_tab, "")

        self.language_tab = QWidget()
        self._setup_language_tab()
        self.tabs.addTab(self.language_tab, "")

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _setup_paths_tab(self):
        layout = QVBoxLayout(self.paths_tab)

        self.paths_info_label = QLabel()
        layout.addWidget(self.paths_info_label)

        self.paths_form_layout = QFormLayout()

        self.game_path_input = QLineEdit(self.current_game_path)
        self.btn_browse_game = QPushButton()
        self.btn_browse_game.clicked.connect(self._browse_game_path)

        game_layout = QHBoxLayout()
        game_layout.addWidget(self.game_path_input)
        game_layout.addWidget(self.btn_browse_game)
        self.game_path_label = QLabel()
        self.paths_form_layout.addRow(self.game_path_label, game_layout)

        self.workshop_path_input = QLineEdit(self.current_workshop_path)
        self.btn_browse_workshop = QPushButton()
        self.btn_browse_workshop.clicked.connect(self._browse_workshop_path)

        workshop_layout = QHBoxLayout()
        workshop_layout.addWidget(self.workshop_path_input)
        workshop_layout.addWidget(self.btn_browse_workshop)
        self.workshop_path_label = QLabel()
        self.paths_form_layout.addRow(self.workshop_path_label, workshop_layout)

        self.profile_path_input = QLineEdit(self.current_profile_path)
        self.btn_browse_profile = QPushButton()
        self.btn_browse_profile.clicked.connect(self._browse_profile_path)

        profile_layout = QHBoxLayout()
        profile_layout.addWidget(self.profile_path_input)
        profile_layout.addWidget(self.btn_browse_profile)
        self.profile_path_label = QLabel()
        self.paths_form_layout.addRow(self.profile_path_label, profile_layout)

        layout.addLayout(self.paths_form_layout)
        layout.addStretch()

    def _setup_appearance_tab(self):
        layout = QVBoxLayout(self.appearance_tab)

        self.appearance_info_label = QLabel()
        layout.addWidget(self.appearance_info_label)

        self.appearance_form_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("", "auto")
        self.theme_combo.addItem("", "dark")
        self.theme_combo.addItem("", "light")

        idx = self.theme_combo.findData(self.current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        self.theme_label = QLabel()
        self.appearance_form_layout.addRow(self.theme_label, self.theme_combo)

        self.font_combo = QComboBox()
        self.font_combo.addItem("", "default")
        self.font_combo.addItem("Inter", "Inter")
        self.font_combo.addItem("OpenDyslexic", "OpenDyslexic")

        idx_font = self.font_combo.findData(self.current_font)
        if idx_font >= 0:
            self.font_combo.setCurrentIndex(idx_font)

        self.font_label = QLabel()
        self.appearance_form_layout.addRow(self.font_label, self.font_combo)

        layout.addLayout(self.appearance_form_layout)
        layout.addStretch()

    def _setup_language_tab(self):
        layout = QVBoxLayout(self.language_tab)

        self.language_info_label = QLabel()
        layout.addWidget(self.language_info_label)

        self.language_form_layout = QFormLayout()

        self.language_combo = QComboBox()
        self._populate_language_options()
        self.language_label = QLabel()
        self.language_form_layout.addRow(self.language_label, self.language_combo)

        layout.addLayout(self.language_form_layout)
        layout.addStretch()

    def _browse_game_path(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, self.tr("Select Game Directory"), self.game_path_input.text() or ""
        )
        if dir_path:
            self.game_path_input.setText(os.path.normpath(dir_path))

    def _browse_workshop_path(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            self.tr("Select Workshop Directory"),
            self.workshop_path_input.text() or "",
        )
        if dir_path:
            self.workshop_path_input.setText(os.path.normpath(dir_path))

    def _browse_profile_path(self):
        start_dir = (
            os.path.dirname(self.profile_path_input.text())
            if self.profile_path_input.text()
            else ""
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Preset File"),
            start_dir,
            self.tr("Options Set (options.set);;All Files (*)"),
        )
        if file_path:
            self.profile_path_input.setText(os.path.normpath(file_path))

    def get_paths(self) -> dict:
        """Return the current dialog values as a plain mapping."""
        return {
            "game_path": self.game_path_input.text().strip(),
            "workshop_path": self.workshop_path_input.text().strip(),
            "profile_path": self.profile_path_input.text().strip(),
            "language": self.language_combo.currentData(),
            "theme": self.theme_combo.currentData(),
            "font": self.font_combo.currentData(),
        }

    def _populate_language_options(self) -> None:
        """Populate the language selector from the runtime translation registry."""
        current_code = self.language_combo.currentData() or self.current_language
        locales = discover_runtime_languages()

        if not any(locale.code == current_code for locale in locales):
            locales.append(
                TranslationLocale(
                    code=current_code,
                    label=self.tr("{0} (Unavailable)").format(
                        language_label(current_code)
                    ),
                )
            )

        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        for locale in locales:
            self.language_combo.addItem(locale.label, locale.code)

        idx = self.language_combo.findData(current_code)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)
        self.language_combo.blockSignals(False)

    def get_settings_state(self) -> SettingsState:
        """Return the current dialog values as a typed ``SettingsState``."""
        return SettingsState(
            game_path=self.game_path_input.text().strip(),
            workshop_path=self.workshop_path_input.text().strip(),
            profile_path=self.profile_path_input.text().strip(),
            language=self.language_combo.currentData(),
            theme=self.theme_combo.currentData(),
            font=self.font_combo.currentData(),
        )

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Settings"))
        self.tabs.setTabText(0, self.tr("Paths"))
        self.tabs.setTabText(1, self.tr("Appearance"))
        self.tabs.setTabText(2, self.tr("Language"))

        self.paths_info_label.setText(
            self.tr(
                "Configure the paths used by the Mod Manager to interact with the game."
            )
        )
        self.btn_browse_game.setText(self.tr("Browse..."))
        self.game_path_label.setText(self.tr("Game Directory:"))
        self.btn_browse_workshop.setText(self.tr("Browse..."))
        self.workshop_path_label.setText(self.tr("Workshop Directory:"))
        self.btn_browse_profile.setText(self.tr("Browse..."))
        self.profile_path_label.setText(self.tr("Profile (options.set):"))

        self.appearance_info_label.setText(
            self.tr("Configure the visual appearance of the application.")
        )
        self.theme_combo.setItemText(0, self.tr("System Default"))
        self.theme_combo.setItemText(1, self.tr("Dark"))
        self.theme_combo.setItemText(2, self.tr("Light"))
        self.theme_label.setText(self.tr("Theme:"))
        self.font_combo.setItemText(0, self.tr("System Default"))
        self.font_label.setText(self.tr("Font:"))

        self.language_info_label.setText(
            self.tr("Select the application language. A restart may be required.")
        )
        self._populate_language_options()
        self.language_label.setText(self.tr("Language:"))
