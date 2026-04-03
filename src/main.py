import logging
import sys

from PySide6.QtCore import QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from src.core.manager import ModManager
from src.ui.appearance_manager import AppearanceManager
from src.ui.main_window import MainWindow
from src.utils import app_paths
from src.utils.logger import configure_logging


def main():
    configure_logging(level=logging.INFO)

    # Initialize the Qt Application
    app = QApplication(sys.argv)

    icon_path = app_paths.get_resource_path("assets", "icons", "logo.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Initialize the backend orchestrator (Model/Controller)
    manager = ModManager()
    init_success = manager.initialize()

    # Load configuration
    config = manager.get_config()

    # Setup global styling
    AppearanceManager.setup_appearance(app, theme=config.theme, font_name=config.font)

    # Load translation
    language = config.language
    translator = QTranslator()
    i18n_path = app_paths.get_resource_path("src", "ui", "i18n")
    if translator.load(f"{language}.qm", str(i18n_path)):
        app.installTranslator(translator)

    # Initialize and show the Main Window (View)
    # We inject the manager so the UI can read data and send commands.
    window = MainWindow(app_model=manager)

    # If paths couldn't be auto-detected, prompt the user via the Settings dialog.
    if not init_success:
        QMessageBox.warning(
            window,
            window.tr("Initialization Warning"),
            window.tr(
                "Could not automatically detect the game installation or profile path.\n"
                "Please configure them in the settings."
            ),
        )
        window.open_settings_dialog()

    window.show()

    # Start the Qt event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
