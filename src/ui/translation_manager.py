from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication

from src.ui.i18n_registry import DEFAULT_LANGUAGE_CODE, get_i18n_dir


class TranslationManager:
    _translator: QTranslator | None = None

    @classmethod
    def apply_language(cls, app: QApplication, language: str) -> bool:
        if cls._translator is not None:
            app.removeTranslator(cls._translator)
            cls._translator = None

        if language == DEFAULT_LANGUAGE_CODE:
            app.setProperty("current_language", language)
            return True

        translator = QTranslator(app)
        i18n_path = get_i18n_dir()
        if not translator.load(f"{language}.qm", str(i18n_path)):
            return False

        app.installTranslator(translator)
        cls._translator = translator
        app.setProperty("current_language", language)
        return True
