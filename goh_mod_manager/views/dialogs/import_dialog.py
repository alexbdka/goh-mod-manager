import os

from PySide6.QtCore import Signal
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
    QSpacerItem,
    QSizePolicy,
    QFrame,
)

from goh_mod_manager.utils.mod_manager_logger import logger


class ImportDialog(QDialog):
    mod_import_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Mod")
        self.resize(500, 220)
        self.setModal(True)

        # Main layout with margins
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        title_label = QLabel("Import Mod")
        # title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Source group
        source_group = QGroupBox("Mod Source")
        source_layout = QVBoxLayout()
        source_layout.setSpacing(8)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            "Select a mod archive (.zip, .tar, .7z...) or folder"
        )
        self.path_input.setMinimumHeight(30)
        source_layout.addWidget(self.path_input)

        # Browse buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        archive_button = QPushButton("Browse Archive...")
        archive_button.setMinimumHeight(35)
        archive_button.clicked.connect(self.browse_archive)

        folder_button = QPushButton("Browse Folder...")
        folder_button.setMinimumHeight(35)
        folder_button.clicked.connect(self.browse_folder)

        button_layout.addWidget(archive_button)
        button_layout.addWidget(folder_button)
        source_layout.addLayout(button_layout)

        source_group.setLayout(source_layout)
        main_layout.addWidget(source_group)

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

        import_button = QPushButton("Import")
        import_button.setMinimumSize(80, 35)
        import_button.setDefault(True)
        # import_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        import_button.clicked.connect(self.import_clicked)

        action_layout.addWidget(cancel_button)
        action_layout.addWidget(import_button)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

    def browse_archive(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mod Archive",
            "",
            "Archives (*.zip *.tar *.tar.gz *.tar.xz *.7z *.rar);;All Files (*)",
        )
        if path:
            self.path_input.setText(path)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Mod Folder")
        if path:
            self.path_input.setText(path)

    def import_clicked(self):
        path = self.path_input.text().strip()
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
