from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)


class PresetDialog(QDialog):
    def __init__(self, parent=None, existing_presets=None):
        super().__init__(parent)
        self.existing_presets = existing_presets or []
        self.preset_name = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Save Preset")
        self.setModal(True)
        self.resize(400, 180)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Save Current Configuration as Preset")
        main_layout.addWidget(title_label)

        input_group = QGroupBox("Preset Details")
        input_layout = QVBoxLayout()
        input_layout.setSpacing(8)

        name_label = QLabel("Preset Name:")
        input_layout.addWidget(name_label)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Enter a descriptive name for this preset")
        self.line_edit.setMinimumHeight(30)
        self.line_edit.returnPressed.connect(self.validate_and_accept)
        input_layout.addWidget(self.line_edit)

        self.error_label = QLabel()
        self.error_label.setMinimumHeight(20)
        input_layout.addWidget(self.error_label)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        main_layout.addItem(
            QSpacerItem(
                20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        action_layout = QHBoxLayout()
        action_layout.addItem(
            QSpacerItem(
                40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
            )
        )

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumSize(80, 35)
        self.cancel_button.clicked.connect(self.reject)

        self.ok_button = QPushButton("Save Preset")
        self.ok_button.setMinimumSize(100, 35)
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.validate_and_accept)

        action_layout.addWidget(self.cancel_button)
        action_layout.addWidget(self.ok_button)
        main_layout.addLayout(action_layout)

        self.setLayout(main_layout)

        self.line_edit.setFocus()

    def validate_and_accept(self):
        name = self.line_edit.text().strip()

        if not name:
            self.error_label.setText("⚠ Please enter a preset name")
            self.line_edit.setFocus()
            return

        if len(name) < 2:
            self.error_label.setText("⚠ Preset name must be at least 2 characters long")
            self.line_edit.setFocus()
            return

        if name in self.existing_presets:
            reply = QMessageBox.question(
                self,
                "Preset Already Exists",
                f'A preset named "{name}" already exists.\n\nDo you want to overwrite it?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                self.line_edit.selectAll()
                self.line_edit.setFocus()
                return

        self.preset_name = name
        self.accept()

    def get_preset_name(self):
        return self.preset_name
