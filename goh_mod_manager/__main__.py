"""
Call to Arms: Gates of Hell - Mod Manager
Main application entry point.
"""

import sys

from PySide6 import QtWidgets

from goh_mod_manager.controllers.mod_manager_controller import ModManagerController
from goh_mod_manager.models.mod_manager_model import ModManagerModel
from goh_mod_manager.views.mod_manager_view import ModManagerView


class ModManagerApp:
    """Main application class following MVC pattern."""

    def __init__(self):
        """Initialize MVC components."""
        try:
            self.model = ModManagerModel()
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
    app.setApplicationName("Call to Arms: Gates of Hell - Mod Manager")
    app.setOrganizationName("alexbdka")
    app.setOrganizationDomain("alexbdka.github.io")
    app.setApplicationVersion("1.1.1")
    app.setApplicationDisplayName("GoH Mod Manager")


def main():
    """Main entry point."""
    try:
        # Create Qt application
        app = QtWidgets.QApplication(sys.argv)
        setup_application(app)

        # Create and run mod manager
        mod_manager = ModManagerApp()
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
