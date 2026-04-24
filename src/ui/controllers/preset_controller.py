from collections.abc import Callable

from PySide6.QtWidgets import QInputDialog, QMessageBox, QStatusBar, QWidget

from src.core.exceptions import ConfigWriteError, ProfileWriteError
from src.ui.widgets.preset_selector_widget import PresetSelectorWidget


class PresetController:
    """
    Qt-specific controller for preset actions.
    Keeps dialogs and flow orchestration out of MainWindow.
    """

    def __init__(
        self,
        parent: QWidget,
        preset_selector: PresetSelectorWidget,
        apply_preset: Callable[[str], tuple[bool, list[str]]],
        save_preset: Callable[[str], None],
        delete_preset: Callable[[str], bool],
        get_all_presets: Callable[[], dict[str, list[str]]],
        status_bar: QStatusBar,
        show_missing_mods_dialog: Callable[
            [str, str, list[str] | list[dict[str, str]]], None
        ],
        handle_profile_write_error: Callable[[ProfileWriteError], None],
        update_unsaved_state: Callable[[], None],
    ):
        self._parent = parent
        self._preset_selector = preset_selector
        self._apply_preset = apply_preset
        self._save_preset = save_preset
        self._delete_preset = delete_preset
        self._get_all_presets = get_all_presets
        self._status_bar = status_bar
        self._show_missing_mods_dialog = show_missing_mods_dialog
        self._handle_profile_write_error = handle_profile_write_error
        self._update_unsaved_state = update_unsaved_state

    def apply_preset(self, name: str):
        try:
            success, missing = self._apply_preset(name)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return

        if success:
            self._preset_selector.set_current_preset(name)
            self._status_bar.showMessage(
                self._parent.tr("Applied preset: {0}").format(name), 3000
            )

            if missing:
                self._show_missing_mods_dialog(
                    self._parent.tr("Preset Applied with Warnings"),
                    self._parent.tr(
                        "The preset was applied, but the following mods are "
                        "missing from your catalogue. You must subscribe to "
                        "them on the Workshop:"
                    ),
                    missing,
                )

    def save_preset(self, name: str):
        try:
            self._save_preset(name)
        except ConfigWriteError as error:
            self._show_config_write_error(error)
            return
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return

        self._preset_selector.set_current_preset(name)
        self._update_unsaved_state()
        self._status_bar.showMessage(
            self._parent.tr("Saved preset: {0}").format(name), 3000
        )

    def save_preset_as(self):
        name, ok = QInputDialog.getText(
            self._parent,
            self._parent.tr("Save Preset"),
            self._parent.tr("Enter a name for the new preset:"),
        )
        if not ok or not name:
            return

        if name in self._get_all_presets():
            reply = QMessageBox.question(
                self._parent,
                self._parent.tr("Overwrite Preset?"),
                self._parent.tr(
                    "A preset named '{0}' already exists. Overwrite?"
                ).format(name),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        try:
            self._save_preset(name)
        except ConfigWriteError as error:
            self._show_config_write_error(error)
            return
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return

        self._preset_selector.set_current_preset(name)
        self._update_unsaved_state()
        self._status_bar.showMessage(
            self._parent.tr("Saved new preset: {0}").format(name), 3000
        )

    def delete_preset(self, name: str):
        reply = QMessageBox.question(
            self._parent,
            self._parent.tr("Delete Preset"),
            self._parent.tr("Are you sure you want to delete the preset '{0}'?").format(
                name
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._delete_preset(name)
        except ConfigWriteError as error:
            self._show_config_write_error(error)
            return
        self._status_bar.showMessage(
            self._parent.tr("Deleted preset: {0}").format(name), 3000
        )

    def _show_config_write_error(self, error: ConfigWriteError):
        QMessageBox.critical(
            self._parent,
            self._parent.tr("Preset Update Failed"),
            self._parent.tr("Could not save presets:\n{0}\n\n{1}").format(
                error.path, error.reason
            ),
        )
        self._status_bar.showMessage(self._parent.tr("Preset update failed."), 5000)
