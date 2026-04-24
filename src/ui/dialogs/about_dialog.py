from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from src.ui.language_change_mixin import LanguageChangeMixin
from src.utils import app_paths


class AboutDialog(LanguageChangeMixin, QDialog):
    """
    Dialog displaying information about the application.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 180)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        layout.addWidget(self.label)

        # OK Button
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)

        # Center the button
        self.button_box.setCenterButtons(True)
        layout.addWidget(self.button_box)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("About GoH Mod Manager"))

        version = app_paths.read_version(default=self.tr("Unknown"))
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
        self.label.setText(text)
