from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class AboutDialog(QDialog):
    def __init__(self, parent=None, app_version=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(400, 250)
        self.app_version = app_version

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Thank you message
        thank_you_label = QLabel("<b>Thank you for using this Mod Manager!</b>")
        thank_you_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(thank_you_label)

        # Description
        description = QLabel(
            "This application is a friendly mod manager designed to make your life easier.\n"
            "Built with ❤️ using Python and PySide6."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        # Credits
        credits = QLabel(
            "<b>Credits:</b><br>"
            "• Interface: <a href='https://doc.qt.io/qtforpython/'>Qt for Python (PySide6)</a><br>"
            "• Icons: <a href='https://remixicon.com/'>Remix Icon</a><br>"
            "• Developer: <a href='https://github.com/alexbdka'>alex6</a>"
        )
        credits.setTextFormat(Qt.TextFormat.RichText)
        credits.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        credits.setOpenExternalLinks(True)
        credits.setWordWrap(True)
        layout.addWidget(credits)

        # Version
        version_label = QLabel(f"Version : <b>{self.app_version}</b>")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
