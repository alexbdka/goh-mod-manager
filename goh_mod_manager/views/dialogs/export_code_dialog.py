from PySide6.QtWidgets import QDialog

from goh_mod_manager.views.ui.export_code_dialog import Ui_ExportCodeDialog


class ExportCodeDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ExportCodeDialog()
        self.ui.setupUi(self)
