from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class AboutDialog(QDialog):
    """
    Dialog displaying information about the application.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("About GoH Mod Manager"))
        self.setFixedSize(350, 180)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        try:
            with open(".app-version", "r", encoding="utf-8") as f:
                version = f.read().strip()
        except Exception:
            version = self.tr("Unknown")

        # Application Info (Rich Text)
        desc = self.tr(
            "A modern, lightweight mod manager for Call to Arms - Gates of Hell."
        )
        dev = self.tr("Developed with PySide6.")
        icons = self.tr(
            'Icons by QtAwesome and <a href="https://github.com/philippedward">awsde</a>.'
        )
        made = self.tr(
            'Made with ♥ by <a href="https://github.com/alexbdka">alexbdka</a>.'
        )

        text = (
            "<h3 style='margin-bottom: 5px;'>Gates of Hell - Mod Manager</h3>"
            f"<p>{desc}</p>"
            f"<p>v{version}</p>"
            "<hr>"
            f"<p style='color: gray; font-size: 10px;'>{dev}<br>"
            f"{icons}<br>"
            f"{made}</p>"
        )
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        # Open links in browser if we ever add any
        label.setOpenExternalLinks(True)

        layout.addWidget(label)

        # OK Button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)

        # Center the button
        button_box.setCenterButtons(True)
        layout.addWidget(button_box)
