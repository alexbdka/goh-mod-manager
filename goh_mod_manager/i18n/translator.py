from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QCoreApplication, QLocale, QTranslator

SUPPORTED_LANGUAGES = ("en", "fr", "ru", "zh", "de")


def normalize_language(language: str, supported: Iterable[str]) -> str:
    if not language:
        return "en"

    normalized = language.replace("-", "_")
    lang_code = normalized.split("_", maxsplit=1)[0].lower()

    return lang_code if lang_code in supported else "en"


class TranslationManager:
    def __init__(self, translations_dir: Path):
        self._translations_dir = translations_dir
        self._translator = QTranslator()

    def available_languages(self) -> set[str]:
        available = {"en"}
        for code in SUPPORTED_LANGUAGES:
            if code == "en":
                continue
            translation_path = self._translations_dir / f"goh_mod_manager_{code}.qm"
            if translation_path.exists():
                available.add(code)
        return available

    def load(self, language: str) -> str:
        normalized = normalize_language(language, SUPPORTED_LANGUAGES)
        file_name = f"goh_mod_manager_{normalized}.qm"
        translation_path = self._translations_dir / file_name

        if translation_path.exists():
            QCoreApplication.removeTranslator(self._translator)
            self._translator = QTranslator()
            if self._translator.load(str(translation_path)):
                QCoreApplication.installTranslator(self._translator)

        return normalized

    @staticmethod
    def detect_system_language() -> str:
        return QLocale.system().name()
