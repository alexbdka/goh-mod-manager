from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication

from src.utils import app_paths


class TranslationManager:
    _translator: QTranslator | None = None

    @classmethod
    def apply_language(cls, app: QApplication, language: str) -> bool:
        if cls._translator is not None:
            app.removeTranslator(cls._translator)
            cls._translator = None

        translator = QTranslator(app)
        i18n_path = app_paths.get_resource_path("src", "ui", "i18n")
        if not translator.load(f"{language}.qm", str(i18n_path)):
            return False

        app.installTranslator(translator)
        cls._translator = translator
        app.setProperty("current_language", language)
        return True
