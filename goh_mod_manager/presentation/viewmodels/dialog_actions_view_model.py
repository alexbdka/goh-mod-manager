from typing import Callable, Optional

from PySide6.QtWidgets import QDialog

from goh_mod_manager.infrastructure.config_manager import ConfigManager
from goh_mod_manager.presentation.view.dialogs.about_dialog import AboutDialog
from goh_mod_manager.presentation.view.dialogs.preferences_dialog import (
    PreferencesDialog,
)


class DialogActionsViewModel:
    def __init__(self, config: ConfigManager):
        self._config = config

    def open_preferences(
        self, parent, on_start_guided_tour: Optional[Callable[[], None]] = None
    ) -> bool:
        dialog = PreferencesDialog(
            self._config, parent, on_start_guided_tour=on_start_guided_tour
        )
        return dialog.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def open_about(parent, version: str) -> None:
        dialog = AboutDialog(parent, version)
        dialog.exec()
