from PySide6.QtGui import QFont, QFontDatabase


class FontService:
    @staticmethod
    def load_font(font_name: str) -> QFont:
        if font_name == "dyslexia":
            QFontDatabase.addApplicationFont(":/assets/font/OpenDyslexic-Regular.otf")
            return QFont("OpenDyslexic", 10)

        QFontDatabase.addApplicationFont(":/assets/font/Inter-Regular.otf")
        return QFont("Inter", 10)
