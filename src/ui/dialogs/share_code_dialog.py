from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class ImportShareCodeDialog(QDialog):
    """
    Dialog specifically designed to prompt the user for a Share Code.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(400)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel()
        layout.addWidget(self.label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(self.tr("e.g. eJzT0y..."))
        layout.addWidget(self.code_input)

        # OK / Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def get_code(self) -> str:
        """Returns the cleaned string entered by the user."""
        return self.code_input.text().strip()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Import Share Code"))
        self.label.setText(self.tr("Paste the Share Code below:"))
        self.code_input.setPlaceholderText(self.tr("e.g. eJzT0y..."))
