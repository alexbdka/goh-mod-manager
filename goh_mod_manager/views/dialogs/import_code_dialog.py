from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QApplication

from goh_mod_manager.views.ui.import_code_dialog import Ui_ImportCodeDialog


class ImportCodeDialog(QDialog):
    import_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ImportCodeDialog()
        self.ui.setupUi(self)

        self.ui.pushButton_import.clicked.connect(self._on_import_clicked)

        self._paste_from_clipboard()

    def _paste_from_clipboard(self):
        self.ui.lineEdit_code.setText(QApplication.clipboard().text())

    def _on_import_clicked(self):
        code = self.ui.lineEdit_code.text().strip()
        if code:
            self.import_requested.emit(code)
            self.accept()
