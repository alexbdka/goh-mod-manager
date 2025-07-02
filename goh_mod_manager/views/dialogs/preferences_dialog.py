from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)


class PreferencesDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.resize(450, 280)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.config = config_manager

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Application Preferences")
        # title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Settings group
        settings_group = QGroupBox("Configuration Paths")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(10)
        settings_layout.setColumnStretch(1, 1)

        # Mods directory
        mods_label = QLabel("Mods Directory:")
        # mods_label.setStyleSheet("font-weight: bold;")
        self.mods_path_input = QLineEdit(self.config.get_mods_directory())
        self.mods_path_input.setMinimumHeight(30)

        mods_button = QPushButton("Browse...")
        mods_button.setMinimumHeight(30)
        mods_button.setMaximumWidth(100)
        mods_button.clicked.connect(self.browse_mods)

        settings_layout.addWidget(mods_label, 0, 0)
        settings_layout.addWidget(self.mods_path_input, 1, 0, 1, 2)
        settings_layout.addWidget(mods_button, 1, 2)

        # Options file
        options_label = QLabel("Options File:")
        # options_label.setStyleSheet("font-weight: bold;")
        self.options_file_input = QLineEdit(self.config.get_options_file())
        self.options_file_input.setMinimumHeight(30)

        options_button = QPushButton("Browse...")
        options_button.setMinimumHeight(30)
        options_button.setMaximumWidth(100)
        options_button.clicked.connect(self.browse_options)

        settings_layout.addWidget(options_label, 2, 0)
        settings_layout.addWidget(self.options_file_input, 3, 0, 1, 2)
        settings_layout.addWidget(options_button, 3, 2)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # Spacer
        main_layout.addItem(
            QSpacerItem(
                20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumSize(80, 35)
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save")
        save_button.setMinimumSize(80, 35)
        save_button.setDefault(True)
        # save_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        save_button.clicked.connect(self.save)

        action_layout.addWidget(cancel_button)
        action_layout.addWidget(save_button)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def browse_mods(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Mods Directory", self.mods_path_input.text()
        )
        if path:
            self.mods_path_input.setText(path)

    def browse_options(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Options File",
            self.options_file_input.text(),
            "Configuration Files (*.set *.cfg *.ini);;All Files (*)",
        )
        if path:
            self.options_file_input.setText(path)

    def save(self):
        mods_path = self.mods_path_input.text().strip()
        options_path = self.options_file_input.text().strip()

        if not mods_path:
            QMessageBox.warning(
                self, "Invalid Path", "Please specify a mods directory."
            )
            return

        if not options_path:
            QMessageBox.warning(self, "Invalid Path", "Please specify an options file.")
            return

        self.config.set_mods_directory(mods_path)
        self.config.set_options_file(options_path)
        self.accept()
