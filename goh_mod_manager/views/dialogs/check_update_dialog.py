import requests
from PySide6.QtWidgets import QMessageBox, QDialog
from packaging import version

from goh_mod_manager.utils.mod_manager_logger import logger


class CheckUpdateDialog(QDialog):
    def __init__(self, parent, app_version):
        super().__init__(parent)
        self.parent = parent
        self.version = app_version
        self.check_for_updates()

    def check_for_updates(self):
        current_version = self.version
        repo = "alexbdka/goh-mod-manager"

        try:
            response = requests.get(
                f"https://api.github.com/repos/{repo}/releases/latest", timeout=5
            )
            logger.debug(f"Update check response: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                latest_version = data["tag_name"].lstrip("v")

                if version.parse(latest_version) > version.parse(current_version):
                    self._show_update_available(latest_version, data["html_url"])
                else:
                    self._show_up_to_date()
            else:
                self._show_error("Could not fetch update information.")

        except requests.RequestException as e:
            self._show_error(f"Network error: {e}")

    def _show_update_available(self, latest_version, url):
        QMessageBox.information(
            self.parent,
            "Update Available",
            f"A new version ({latest_version}) is available!\n\n"
            f"Visit the release page:\n{url}",
        )

    def _show_up_to_date(self):
        QMessageBox.information(
            self.parent,
            "Up to Date",
            "You are using the latest version of the application.",
        )

    def _show_error(self, message):
        QMessageBox.warning(self.parent, "Update Check Failed", message)
