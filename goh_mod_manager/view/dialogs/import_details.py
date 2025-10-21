from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
)


class DetailedMessageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Information")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.message_label)

        separator = QFrame()
        separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        layout.addWidget(separator)

        self.details_label = QLabel()
        self.details_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.details_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)

        layout.addWidget(self.details_text)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        self.ok_button.setMinimumWidth(80)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)

    def set_title(self, title: str):
        self.setWindowTitle(title)

    def set_message(self, message: str):
        self.message_label.setText(message)

    def set_details(self, details_title: str, details_text: str):
        self.details_label.setText(details_title)
        self.details_text.setPlainText(details_text)
