from collections.abc import Callable

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFileDialog, QStatusBar, QWidget

from src.ui.dialogs.about_dialog import AboutDialog


class AppActionsController:
    """
    Qt-specific controller for generic app actions:
    debug report, clipboard, about dialog, launch game.
    """

    def __init__(
        self,
        parent: QWidget,
        build_debug_report: Callable[[], str],
        launch_game: Callable[[], bool],
        status_bar: QStatusBar,
        show_info_message: Callable[[str, str], None],
        show_error_message: Callable[[str, str], None],
    ):
        self._parent = parent
        self._build_debug_report = build_debug_report
        self._launch_game = launch_game
        self._status_bar = status_bar
        self._show_info_message = show_info_message
        self._show_error_message = show_error_message

    def generate_report(self):
        file_path = self._prompt_debug_report_path()
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._build_debug_report())

            self._show_info_message(
                self._parent.tr("Success"),
                self._parent.tr("Debug report saved successfully to:\n{0}").format(
                    file_path
                ),
            )
        except Exception as e:
            self._show_error_message(
                self._parent.tr("Error"),
                self._parent.tr("Failed to save debug report:\n{0}").format(e),
            )

    def show_about(self):
        dialog = AboutDialog(self._parent)
        dialog.exec()

    def launch_game(self):
        success = self._launch_game()
        if success:
            self._status_bar.showMessage(
                self._parent.tr("Launching Call to Arms - Gates of Hell..."), 5000
            )
        else:
            self._show_error_message(
                self._parent.tr("Launch Failed"),
                self._parent.tr(
                    "Failed to launch the game. Make sure Steam is installed "
                    "and running."
                ),
            )

    @staticmethod
    def copy_to_clipboard(text: str):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def _prompt_debug_report_path(self) -> str:
        file_path, _ = QFileDialog.getSaveFileName(
            self._parent,
            self._parent.tr("Save Debug Report"),
            "goh_mod_manager_debug.txt",
            self._parent.tr("Text Files (*.txt);;All Files (*)"),
        )
        return file_path
