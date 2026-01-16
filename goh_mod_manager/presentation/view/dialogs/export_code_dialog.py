from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QApplication

from goh_mod_manager.presentation.view.ui.export_code_dialog import Ui_ExportCodeDialog


class ExportCodeDialog(QDialog):
    """Dialog for sharing the active mods as an export code."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ExportCodeDialog()
        self.ui.setupUi(self)

        self.ui.pushButton_copy.clicked.connect(self._copy_to_clipboard)

    def set_code(self, code: str, mod_count: int) -> None:
        self.ui.lineEdit_code.setText(code)
        self.setWindowTitle(
            self.tr("Export Code ({mod_count} mods)").format(mod_count=mod_count)
        )
        self._copy_to_clipboard()

    def _copy_to_clipboard(self) -> None:
        code = self.ui.lineEdit_code.text()
        QApplication.clipboard().setText(code)

        original_text = self.ui.pushButton_copy.text()
        self.ui.pushButton_copy.setText(self.tr("Copied!"))
        self.ui.pushButton_copy.setEnabled(False)

        QTimer.singleShot(
            3000,
            lambda: [
                self.ui.pushButton_copy.setText(original_text),
                self.ui.pushButton_copy.setEnabled(True),
            ],
        )
