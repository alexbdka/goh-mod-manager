from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton


class HelpButton(QToolButton):
    def __init__(self, help_text: str, parent=None):
        super().__init__(parent)
        self.setText("?")
        self.setToolTip(help_text)
        self.setCursor(Qt.WhatsThisCursor)  # pyright: ignore[reportAttributeAccessIssue]
