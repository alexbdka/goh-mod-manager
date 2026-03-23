import sys
from pathlib import Path

from PySide6 import QtWidgets

from goh_mod_manager.core.mod_manager_model import ModManagerModel
from goh_mod_manager.i18n.translator import TranslationManager
from goh_mod_manager.infrastructure.config_manager import ConfigManager
from goh_mod_manager.presentation.controller.mod_manager_controller import (
    ModManagerController,
)
from goh_mod_manager.presentation.view.mod_manager_view import ModManagerView
from goh_mod_manager.services.active_mods_service import ActiveModsService
from goh_mod_manager.services.mod_import_service import ModImportService
from goh_mod_manager.services.mods_catalog_service import ModsCatalogService
from goh_mod_manager.services.presets_service import PresetsService


class ModManagerApp:
    """Main application class"""

    def __init__(self, config: ConfigManager):
        """Initialize MVC components."""
        try:
            self.model = ModManagerModel(
                config=config,
                mods_catalog=ModsCatalogService(),
                active_mods_service=ActiveModsService(),
                presets_service=PresetsService(),
                mod_import_service=ModImportService(),
            )
            self.view = ModManagerView()
            self.controller = ModManagerController(self.model, self.view)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize application components: {e}")

    def run(self):
        """Start the application."""
        try:
            self.controller.show()
        except Exception as e:
            raise RuntimeError(f"Failed to start application: {e}")


def setup_application(app: QtWidgets.QApplication):
    """Configure Qt application properties."""
    from goh_mod_manager import __version__

    app.setOrganizationName("alexbdka")
    app.setOrganizationDomain("alexbdka.github.io")
    app.setApplicationName("GoH Mod Manager")
    app.setApplicationVersion(__version__)


def main():
    """Main entry point."""
    try:
        # Create Qt application
        app = QtWidgets.QApplication(sys.argv)
        setup_application(app)

        config = ConfigManager()
        translations_dir = Path(__file__).resolve().parent / "i18n"
        translator = TranslationManager(translations_dir)
        translator.load(config.get_language())
        app.translation_manager = translator

        # Create and run mod manager
        mod_manager = ModManagerApp(config)
        mod_manager.run()

        # Start event loop
        return app.exec()

    except KeyboardInterrupt:
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        QtWidgets.QMessageBox.critical(
            None,
            "Critical Error",
            f"A critical error occurred:\n{e}\n\nPlease check the application logs for details.",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
