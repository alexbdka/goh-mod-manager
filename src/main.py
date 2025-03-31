import sys
from PyQt6.QtWidgets import QApplication
from ui.mod_manager_ui import ModManagerUI

def main():
    app = QApplication(sys.argv)
    window = ModManagerUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()