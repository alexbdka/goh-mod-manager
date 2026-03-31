import os

import qdarktheme
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


class AppearanceManager:
    """
    Centralized manager for application styling.
    Replaces local stylesheets with global QSS.
    """

    @staticmethod
    def setup_appearance(
        app: QApplication, theme: str = "auto", font_name: str = "Inter"
    ):
        # Load custom fonts
        font_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts")
        )
        inter_path = os.path.join(font_dir, "Inter-Regular.otf")
        opendyslexic_path = os.path.join(font_dir, "OpenDyslexic-Regular.otf")

        QFontDatabase.addApplicationFont(opendyslexic_path)
        QFontDatabase.addApplicationFont(inter_path)

        if font_name == "default":
            app_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
        else:
            app_font = QFont(font_name)

        app_font.setPointSize(10)  # Roughly equivalent to 13px
        app.setFont(app_font)

        global_qss = """
        /* Specific Labels */
        QLabel#SectionTitle {
            font-size: 15px;
            font-weight: bold;
            padding-bottom: 5px;
        }

        QLabel#PresetLabel {
            font-weight: bold;
        }

        QLabel#ModTitle {
            font-size: 18px;
            font-weight: bold;
            padding-bottom: 5px;
        }

        QLabel#ModMeta {
            color: #666666;
            margin-top: 5px;
            margin-bottom: 10px;
        }

        QLabel#SettingsInfo {
            color: gray;
            margin-bottom: 10px;
        }

        QLabel#DropZoneLabel {
            color: gray;
            font-size: 16px;
            border: 2px dashed gray;
            padding: 40px;
        }

        QLabel#DropZoneLabel[dragHover="true"] {
            color: #2e7d32;
            border-color: #2e7d32;
        }

        /* Lists */
        QListWidget {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        }

        QListWidget::item {
            padding: 2px;
        }

        QListWidget::item:selected {
            background-color: #3498db;
            color: #ffffff;
        }

        /* Main Toolbar */
        QToolBar {
            spacing: 5px;
        }

        QToolButton {
            padding: 4px 8px;
            border-radius: 4px;
        }

        QPushButton#PlayButton {
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 4px;
        }

        QPushButton#PlayButton:hover {
            background-color: #388e3c;
        }

        QPushButton#PlayButton:pressed {
            background-color: #1b5e20;
        }
        """
        try:
            qdarktheme.setup_theme(theme, additional_qss=global_qss)
        except Exception:
            app.setStyleSheet(global_qss)
