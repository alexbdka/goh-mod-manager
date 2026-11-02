import logging

import requests
from packaging import version
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from src.ui.language_change_mixin import LanguageChangeMixin

logger = logging.getLogger(__name__)


class CheckUpdateDialog(LanguageChangeMixin, QDialog):
    def __init__(self, parent, app_version):
        super().__init__(parent)
        self.parent: QWidget = parent
        self.version = app_version
        self.setAccessibleName("checkUpdateDialog")
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Check for Updates"))
        self.status_label.setText(self.tr("Checking for updates..."))

    def check_for_updates(self):
        current_version = self.version
        logger.info(f"Checking for updates: current version is {current_version}")
        repo = "alexbdka/goh-mod-manager"

        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/releases/latest", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                latest_version = data["tag_name"].lstrip("v")

                if version.parse(latest_version) > version.parse(current_version):
                    logger.info(f"Update available: {latest_version}")
                    self._show_update_available(latest_version, data["html_url"])
                else:
                    logger.info(f"Up to date: {latest_version}")
                    self._show_up_to_date()
            else:
                self._show_error(self.tr("Could not fetch update information."))

        except requests.RequestException as e:
            self._show_error(self.tr("Network error: {0}").format(e))

    def _show_update_available(self, latest_version, url):
        QMessageBox.information(
            self.parent,
            self.tr("Update Available"),
            self.tr(
                "A new version ({0}) is available!\n\nVisit the release page:\n{1}"
            ).format(latest_version, url),
        )

    def _show_up_to_date(self):
        QMessageBox.information(
            self.parent,
            self.tr("Up to Date"),
            self.tr("You are using the latest version of the application."),
        )

    def _show_error(self, message):
        QMessageBox.warning(self.parent, self.tr("Update Check Failed"), message)
