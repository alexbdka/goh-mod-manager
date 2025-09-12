from PySide6.QtWidgets import QDialog

from goh_mod_manager.views.ui.import_code_dialog import Ui_ImportCodeDialog


class ImportCodeDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ImportCodeDialog()
        self.ui.setupUi(self)