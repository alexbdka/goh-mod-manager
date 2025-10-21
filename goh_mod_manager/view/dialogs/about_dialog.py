from PySide6.QtWidgets import QDialog

from goh_mod_manager.view.ui.about_dialog import Ui_AboutDialog


class AboutDialog(QDialog):
    def __init__(self, parent=None, app_version=0.0):
        super().__init__(parent)
        self.ui = Ui_AboutDialog()
        self.ui.setupUi(self)
        self._version = app_version
        self._load()

    def _load(self):
        self.ui.versionLabel.setText(self._version)
