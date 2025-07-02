import sys

from PySide6 import QtWidgets

from goh_mod_manager.controllers.mod_manager_controller import ModManagerController
from goh_mod_manager.models.mod_manager_model import ModManagerModel
from goh_mod_manager.views.mod_manager_view import ModManagerView


class App:
    def __init__(self):
        self.__version__ = "1.0.0"
        self.model = ModManagerModel()
        self.view = ModManagerView()
        self.controller = ModManagerController(self.model, self.view)
        self.controller.set_version(self.__version__)

    def run(self):
        self.controller.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    modManager = App()
    modManager.run()

    sys.exit(app.exec())
