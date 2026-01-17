from pathlib import Path
from typing import Iterable

from PySide6.QtCore import QCoreApplication, QLocale, QTranslator

LANGUAGE_FILE_PREFIX = "goh_mod_manager_"


def normalize_language(language: str, supported: Iterable[str]) -> str:
    if not language:
        return "en"

    normalized = language.replace("-", "_").lower()
    supported_set = set(supported)

    if normalized in supported_set:
        return normalized

    lang_code = normalized.split("_", maxsplit=1)[0]
    return lang_code if lang_code in supported_set else "en"


class TranslationManager:
    def __init__(self, translations_dir: Path):
        self._translations_dir = translations_dir
        self._translator = QTranslator()

    def _discover_language_files(self) -> dict[str, tuple[bool, bool]]:
        status: dict[str, list[bool]] = {}
        if not self._translations_dir.exists():
            return {}

        for ext, idx in (("qm", 0), ("ts", 1)):
            for path in self._translations_dir.glob(f"{LANGUAGE_FILE_PREFIX}*.{ext}"):
                stem = path.stem
                if not stem.startswith(LANGUAGE_FILE_PREFIX):
                    continue
                code = stem[len(LANGUAGE_FILE_PREFIX) :].lower()
                if not code:
                    continue
                entry = status.setdefault(code, [False, False])
                entry[idx] = True

        return {code: (flags[0], flags[1]) for code, flags in status.items()}

    def _find_translation_file(self, language: str) -> Path | None:
        if not self._translations_dir.exists():
            return None

        language = language.lower()
        for path in self._translations_dir.glob(f"{LANGUAGE_FILE_PREFIX}*.qm"):
            stem = path.stem
            if not stem.startswith(LANGUAGE_FILE_PREFIX):
                continue
            code = stem[len(LANGUAGE_FILE_PREFIX) :].lower()
            if code == language:
                return path
        return None

    def available_languages(self) -> set[str]:
        available = {"en"}
        for code, (has_qm, _) in self._discover_language_files().items():
            if has_qm:
                available.add(code)
        return available

    def language_file_status(self) -> dict[str, tuple[bool, bool]]:
        """
        Return the presence of translation files discovered in the translations folder.

        Returns:
            dict[code, (has_qm, has_ts)]
        """
        return self._discover_language_files()

    def load(self, language: str) -> str:
        normalized = normalize_language(language, self.available_languages())
        translation_path = (
            self._translations_dir / f"{LANGUAGE_FILE_PREFIX}{normalized}.qm"
        )

        if not translation_path.exists():
            resolved = self._find_translation_file(normalized)
            if resolved is not None:
                translation_path = resolved

        if translation_path.exists():
            QCoreApplication.removeTranslator(self._translator)
            self._translator = QTranslator()
            if self._translator.load(str(translation_path)):
                QCoreApplication.installTranslator(self._translator)

        return normalized

    @staticmethod
    def detect_system_language() -> str:
        return QLocale.system().name()
