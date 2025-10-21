from PySide6.QtWidgets import (
    QDialog,
)

from goh_mod_manager.view.ui.user_manual_dialog import Ui_UserManualDialog


class UserManualDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_UserManualDialog()
        self.ui.setupUi(self)
        self._connect_signals()

    def _connect_signals(self):
        self.ui.ok_button.clicked.connect(self.accept)
