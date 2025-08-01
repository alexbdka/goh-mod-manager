import sys

from PySide6 import QtWidgets

from goh_mod_manager.controllers.mod_manager_controller import ModManagerController
from goh_mod_manager.models.mod_manager_model import ModManagerModel
from goh_mod_manager.views.mod_manager_view import ModManagerView


class App:
    def __init__(self):
        self.model = ModManagerModel()
        self.view = ModManagerView()
        self.controller = ModManagerController(self.model, self.view)

    def run(self):
        self.controller.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Call to Arms: Gates of Hell | Mod Manager")
    app.setOrganizationName("alex6")
    app.setOrganizationDomain("alexbdka.github.io")
    app.setApplicationVersion("1.0.1")

    modManager = App()
    modManager.run()

    sys.exit(app.exec())
