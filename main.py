import logging
import os
import sys

from PySide6.QtCore import QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from src.core.manager import ModManager
from src.ui.appearance_manager import AppearanceManager
from src.ui.main_window import MainWindow


def main():
    # Setup basic logging to help with debugging (Console and File)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "mod_manager.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Initialize the Qt Application
    app = QApplication(sys.argv)

    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "logo.png"
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Initialize the backend orchestrator (Model/Controller)
    manager = ModManager()
    init_success = manager.initialize()

    # Load configuration
    config = manager.config_service.get_config()

    # Setup global styling
    AppearanceManager.setup_appearance(app, theme=config.theme, font_name=config.font)

    # Load translation
    language = config.language
    translator = QTranslator()
    i18n_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "src", "ui", "i18n"
    )
    if translator.load(f"{language}.qm", i18n_path):
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
        window._on_open_settings()

    window.show()

    # Start the Qt event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
