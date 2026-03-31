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


class SettingsDialog(QDialog):
    """
    Dialog for application preferences and settings.
    Designed with a TabWidget to allow future expansion (Appearance, Language, etc.).
    """

    def __init__(
        self,
        current_game_path: str = "",
        current_workshop_path: str = "",
        current_profile_path: str = "",
        current_language: str = "en_US",
        current_theme: str = "auto",
        current_font: str = "Inter",
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Settings"))
        self.resize(550, 300)

        self.current_game_path = current_game_path or ""
        self.current_workshop_path = current_workshop_path or ""
        self.current_profile_path = current_profile_path or ""
        self.current_language = current_language
        self.current_theme = current_theme
        self.current_font = current_font

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Tab Widget for modularity
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Paths
        self.paths_tab = QWidget()
        self._setup_paths_tab()
        self.tabs.addTab(self.paths_tab, self.tr("Paths"))

        # Tab 2: Appearance
        self.appearance_tab = QWidget()
        self._setup_appearance_tab()
        self.tabs.addTab(self.appearance_tab, self.tr("Appearance"))

        # Tab 3: Language
        self.language_tab = QWidget()
        self._setup_language_tab()
        self.tabs.addTab(self.language_tab, self.tr("Language"))

        # Dialog Buttons (OK / Cancel)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _setup_paths_tab(self):
        layout = QVBoxLayout(self.paths_tab)

        info_label = QLabel(
            self.tr(
                "Configure the paths used by the Mod Manager to interact with the game."
            )
        )
        info_label.setObjectName("SettingsInfo")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        # Game Path
        self.game_path_input = QLineEdit(self.current_game_path)
        btn_browse_game = QPushButton(self.tr("Browse..."))
        btn_browse_game.clicked.connect(self._browse_game_path)

        game_layout = QHBoxLayout()
        game_layout.addWidget(self.game_path_input)
        game_layout.addWidget(btn_browse_game)
        form_layout.addRow(self.tr("Game Directory:"), game_layout)

        # Workshop Path
        self.workshop_path_input = QLineEdit(self.current_workshop_path)
        btn_browse_workshop = QPushButton(self.tr("Browse..."))
        btn_browse_workshop.clicked.connect(self._browse_workshop_path)

        workshop_layout = QHBoxLayout()
        workshop_layout.addWidget(self.workshop_path_input)
        workshop_layout.addWidget(btn_browse_workshop)
        form_layout.addRow(self.tr("Workshop Directory:"), workshop_layout)

        # Profile Path
        self.profile_path_input = QLineEdit(self.current_profile_path)
        btn_browse_profile = QPushButton(self.tr("Browse..."))
        btn_browse_profile.clicked.connect(self._browse_profile_path)

        profile_layout = QHBoxLayout()
        profile_layout.addWidget(self.profile_path_input)
        profile_layout.addWidget(btn_browse_profile)
        form_layout.addRow(self.tr("Preset (options.set):"), profile_layout)

        layout.addLayout(form_layout)
        layout.addStretch()

    def _setup_appearance_tab(self):
        layout = QVBoxLayout(self.appearance_tab)

        info_label = QLabel(
            self.tr("Configure the visual appearance of the application.")
        )
        info_label.setObjectName("SettingsInfo")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self.tr("System Default"), "auto")
        self.theme_combo.addItem(self.tr("Dark"), "dark")
        self.theme_combo.addItem(self.tr("Light"), "light")

        idx = self.theme_combo.findData(self.current_theme)
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        form_layout.addRow(self.tr("Theme:"), self.theme_combo)

        self.font_combo = QComboBox()
        self.font_combo.addItem(self.tr("System Default"), "default")
        self.font_combo.addItem("Inter", "Inter")
        self.font_combo.addItem("OpenDyslexic", "OpenDyslexic")

        idx_font = self.font_combo.findData(self.current_font)
        if idx_font >= 0:
            self.font_combo.setCurrentIndex(idx_font)

        form_layout.addRow(self.tr("Font:"), self.font_combo)

        layout.addLayout(form_layout)
        layout.addStretch()

    def _setup_language_tab(self):
        layout = QVBoxLayout(self.language_tab)

        info_label = QLabel(
            self.tr("Select the application language. A restart may be required.")
        )
        info_label.setObjectName("SettingsInfo")
        layout.addWidget(info_label)

        form_layout = QFormLayout()

        self.language_combo = QComboBox()
        self.language_combo.addItem(self.tr("English"), "en_US")
        self.language_combo.addItem(self.tr("Français"), "fr_FR")

        # Set current
        idx = self.language_combo.findData(self.current_language)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)

        form_layout.addRow(self.tr("Language:"), self.language_combo)

        layout.addLayout(form_layout)
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
        """
        Returns the paths and settings currently entered in the dialog.
        """
        return {
            "game_path": self.game_path_input.text().strip(),
            "workshop_path": self.workshop_path_input.text().strip(),
            "profile_path": self.profile_path_input.text().strip(),
            "language": self.language_combo.currentData(),
            "theme": self.theme_combo.currentData(),
            "font": self.font_combo.currentData(),
        }
