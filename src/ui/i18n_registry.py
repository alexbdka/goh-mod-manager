from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QLocale

from src.utils import app_paths

DEFAULT_LANGUAGE_CODE = "en_US"
LOCALE_CODE_RE = re.compile(r"^[a-z]{2}(?:_[A-Z]{2})?$")


@dataclass(frozen=True)
class TranslationLocale:
    """Description of one locale available in the repository or at runtime."""

    code: str
    label: str
    ts_path: Path | None = None
    qm_path: Path | None = None


def get_i18n_dir() -> Path:
    """Return the directory that stores Qt translation sources and binaries."""
    return app_paths.get_resource_path("src", "ui", "i18n")


def is_valid_locale_code(locale_code: str) -> bool:
    """Return ``True`` when ``locale_code`` matches the repository convention."""
    return bool(LOCALE_CODE_RE.fullmatch(locale_code))


def read_ts_language(path: Path) -> str | None:
    """Read the ``language`` attribute from a Qt ``.ts`` file."""
    root = ET.parse(path).getroot()
    if root.tag != "TS":
        raise ValueError(f"{path.name} is not a valid Qt TS file.")

    language = root.attrib.get("language")
    if language:
        return language
    return None


def discover_source_languages(i18n_dir: Path | None = None) -> list[TranslationLocale]:
    """Return locales that have a source ``.ts`` file in the repository."""
    return _discover_locales(
        i18n_dir=i18n_dir,
        include_source=True,
        include_runtime=False,
    )


def discover_runtime_languages(
    i18n_dir: Path | None = None,
) -> list[TranslationLocale]:
    """Return locales that can be selected at runtime."""
    return _discover_locales(
        i18n_dir=i18n_dir,
        include_source=True,
        include_runtime=True,
    )


def validate_translation_tree(i18n_dir: Path | None = None) -> list[str]:
    """
    Validate the translation directory layout and return human-readable errors.

    This intentionally validates only repository conventions:
    file naming, source file presence, ``.ts`` XML readability, and language
    attribute consistency.
    """
    base_dir = i18n_dir or get_i18n_dir()
    errors: list[str] = []

    ts_files = sorted(base_dir.glob("*.ts"))
    qm_files = sorted(base_dir.glob("*.qm"))

    if not (base_dir / f"{DEFAULT_LANGUAGE_CODE}.ts").exists():
        errors.append(
            f"Missing required source translation file: {DEFAULT_LANGUAGE_CODE}.ts"
        )

    seen_codes: set[str] = set()
    for path in ts_files:
        locale_code = path.stem
        lowered = locale_code.lower()
        if lowered in seen_codes:
            errors.append(f"Duplicate translation locale code: {locale_code}")
            continue
        seen_codes.add(lowered)

        if not is_valid_locale_code(locale_code):
            errors.append(
                f"Invalid translation file name '{path.name}'. "
                "Expected names like en_US.ts or zh_CN.ts."
            )
            continue

        try:
            language_attr = read_ts_language(path)
        except (ET.ParseError, ValueError) as error:
            errors.append(f"{path.name}: {error}")
            continue

        if locale_code == DEFAULT_LANGUAGE_CODE:
            if language_attr not in {None, "", DEFAULT_LANGUAGE_CODE}:
                errors.append(
                    f"{path.name}: source file language attribute must be empty "
                    f"or '{DEFAULT_LANGUAGE_CODE}', got '{language_attr}'."
                )
        elif language_attr != locale_code:
            errors.append(
                f'{path.name}: expected <TS language="{locale_code}">, '
                f"got '{language_attr or '<missing>'}'."
            )

    for path in qm_files:
        locale_code = path.stem
        if not is_valid_locale_code(locale_code):
            errors.append(
                f"Invalid compiled translation file name '{path.name}'. "
                "Expected names like en_US.qm or zh_CN.qm."
            )
            continue

        ts_path = base_dir / f"{locale_code}.ts"
        if not ts_path.exists():
            errors.append(
                f"{path.name}: compiled file has no matching source file "
                f"{ts_path.name}."
            )

    return errors


def _discover_locales(
    *,
    i18n_dir: Path | None,
    include_source: bool,
    include_runtime: bool,
) -> list[TranslationLocale]:
    base_dir = i18n_dir or get_i18n_dir()
    ts_by_code = _translation_files_by_code(base_dir, ".ts")
    qm_by_code = _translation_files_by_code(base_dir, ".qm")

    locale_codes: set[str] = set()
    if include_source:
        locale_codes.update(ts_by_code)
    if include_runtime:
        locale_codes.update(qm_by_code)

    if include_runtime and DEFAULT_LANGUAGE_CODE in ts_by_code:
        locale_codes.add(DEFAULT_LANGUAGE_CODE)

    locales = [
        TranslationLocale(
            code=locale_code,
            label=language_label(locale_code),
            ts_path=ts_by_code.get(locale_code),
            qm_path=qm_by_code.get(locale_code),
        )
        for locale_code in locale_codes
        if _is_runtime_selectable(locale_code, ts_by_code, qm_by_code, include_runtime)
    ]

    locales.sort(key=_locale_sort_key)
    return locales


def _translation_files_by_code(base_dir: Path, suffix: str) -> dict[str, Path]:
    files_by_code: dict[str, Path] = {}
    for path in sorted(base_dir.glob(f"*{suffix}")):
        locale_code = path.stem
        if is_valid_locale_code(locale_code):
            files_by_code[locale_code] = path
    return files_by_code


def _is_runtime_selectable(
    locale_code: str,
    ts_by_code: dict[str, Path],
    qm_by_code: dict[str, Path],
    include_runtime: bool,
) -> bool:
    if not include_runtime:
        return True
    if locale_code == DEFAULT_LANGUAGE_CODE:
        return locale_code in ts_by_code or locale_code in qm_by_code
    return locale_code in qm_by_code


def _locale_sort_key(locale: TranslationLocale) -> tuple[int, str]:
    if locale.code == DEFAULT_LANGUAGE_CODE:
        return (0, locale.label.casefold())
    return (1, locale.label.casefold())


def language_label(locale_code: str) -> str:
    """Return a stable display label for a locale code."""
    qt_locale = QLocale(locale_code)
    language_name = (
        qt_locale.nativeLanguageName()
        or QLocale.languageToString(qt_locale.language())
        or locale_code
    )
    territory_name = qt_locale.nativeTerritoryName() or QLocale.territoryToString(
        qt_locale.territory()
    )

    if territory_name:
        return f"{language_name} ({territory_name}) [{locale_code}]"
    return f"{language_name} [{locale_code}]"
