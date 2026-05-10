import json
import logging
from ast import literal_eval
from collections.abc import Callable, Mapping, Sequence
from typing import Any

# QSettings will be resolved at runtime inside migrate_from_legacy_qsettings
# so tests that monkeypatch src.services.config_service.QSettings are honored.
QSettings = None

logger = logging.getLogger(__name__)

LEGACY_QSETTINGS_ORGANIZATION = "alex6"
LEGACY_QSETTINGS_APPLICATION = "GoH Mod Manager"


def migrate_from_legacy_qsettings(
    *,
    config: Any,
    save_fn: Callable[[], None],
    allow_legacy_migration: bool,
    config_path: str,
) -> None:
    """
    Try a one-shot migration from legacy QSettings into the provided in-memory
    config object and persist using save_fn when something changed.

    Parameters:
    - config: AppConfig-like object with attributes used by the original migration
    - save_fn: callable to persist the config (no-arg, uses the mutated config)
    - allow_legacy_migration: guard flag copied from ConfigService
    - config_path: path to the JSON config file (used only for logging context)
    """
    if not allow_legacy_migration:
        return

    # Resolve QSettings from the config_service at runtime so test monkeypatches
    # take effect (tests set src.services.config_service.QSettings).
    try:
        from src.services import config_service as _config_service

        QSettings_local = getattr(_config_service, "QSettings", None)
    except Exception:
        QSettings_local = None

    if QSettings_local is None:
        return

    settings = QSettings_local(
        LEGACY_QSETTINGS_ORGANIZATION, LEGACY_QSETTINGS_APPLICATION
    )
    migrated = False

    game_directory = settings.value("game_directory", "")
    if isinstance(game_directory, str) and game_directory.strip():
        config.game_path = game_directory.strip()
        migrated = True

    mods_directory = settings.value("mods_directory", "")
    if isinstance(mods_directory, str) and mods_directory.strip():
        config.workshop_path = mods_directory.strip()
        migrated = True

    options_file = settings.value("options_file", "")
    if isinstance(options_file, str) and options_file.strip():
        config.profile_path = options_file.strip()
        migrated = True

    raw_presets = settings.value("presets", {})
    decoded_presets = _decode_legacy_presets(raw_presets)
    if decoded_presets:
        config.presets = decoded_presets
        migrated = True

    if migrated:
        try:
            save_fn()
        except Exception:
            logger.exception(
                "Failed to save configuration after migrating legacy QSettings"
            )

        logger.info(
            "Migrated configuration from legacy QSettings "
            f"({LEGACY_QSETTINGS_ORGANIZATION}/{LEGACY_QSETTINGS_APPLICATION}). "
            f"Presets raw type: {type(raw_presets).__name__}. "
            f"Presets decoded: {_presets_preview(decoded_presets)}"
        )


def _decode_legacy_presets(raw_presets: Any) -> dict[str, list[str]]:
    parsed = _parse_legacy_mapping(raw_presets)
    if parsed is None:
        if raw_presets not in ({}, None, ""):
            logger.warning(
                "Legacy presets could not be parsed. "
                f"Raw type: {type(raw_presets).__name__}. "
                f"Raw preview: {_value_preview(raw_presets)}"
            )
        return {}

    normalized: dict[str, list[str]] = {}
    for raw_name, raw_value in parsed.items():
        if not isinstance(raw_name, str):
            continue

        preset_name = raw_name.strip()
        if not preset_name:
            continue

        mod_ids = _normalize_legacy_mod_ids(raw_value)
        if mod_ids:
            normalized[preset_name] = mod_ids
        else:
            logger.warning(
                f"Legacy preset '{preset_name}' ignored: unsupported value "
                f"type {type(raw_value).__name__} with preview "
                f"{_value_preview(raw_value)}"
            )

    return normalized


def _presets_preview(presets: dict[str, list[str]]) -> str:
    if not presets:
        return "{}"
    preview_entries = list(presets.items())[:3]
    compact = {name: values[:5] for name, values in preview_entries}
    suffix = " ..." if len(presets) > 3 else ""
    return f"{compact}{suffix}"


def _value_preview(value: Any) -> str:
    preview = repr(value)
    if len(preview) > 220:
        return f"{preview[:220]}..."
    return preview


def _parse_legacy_mapping(value: Any) -> Mapping[Any, Any] | None:
    if isinstance(value, Mapping):
        return value
    if not isinstance(value, str):
        return None

    payload = value.strip()
    if not payload:
        return None

    parsed: Any | None = None
    try:
        parsed = json.loads(payload)
    except (TypeError, ValueError):
        try:
            parsed = literal_eval(payload)
        except (SyntaxError, ValueError):
            return None

    if isinstance(parsed, Mapping):
        return parsed
    return None


def _normalize_legacy_mod_ids(value: Any) -> list[str]:
    parsed_value = value
    if isinstance(parsed_value, str):
        stripped = parsed_value.strip()
        if not stripped:
            return []

        if stripped.startswith("[") or stripped.startswith("("):
            try:
                parsed_value = json.loads(stripped)
            except (TypeError, ValueError):
                try:
                    parsed_value = literal_eval(stripped)
                except (SyntaxError, ValueError):
                    parsed_value = [stripped]
        else:
            parsed_value = [stripped]

    if not isinstance(parsed_value, Sequence) or isinstance(
        parsed_value, (str, bytes, bytearray)
    ):
        return []

    normalized: list[str] = []
    for item in parsed_value:
        if item is None:
            continue
        item_str = str(item).strip()
        if item_str:
            normalized.append(item_str)

    return normalized
