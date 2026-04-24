from pathlib import Path

from src.ui.i18n_registry import (
    DEFAULT_LANGUAGE_CODE,
    discover_runtime_languages,
    validate_translation_tree,
)


def _write_ts(path: Path, *, language: str | None) -> None:
    language_attr = f' language="{language}"' if language is not None else ""
    path.write_text(
        "\n".join(
            [
                '<?xml version="1.0" encoding="utf-8"?>',
                "<!DOCTYPE TS>",
                f'<TS version="2.1"{language_attr}>',
                "  <context>",
                "    <name>MainWindow</name>",
                "    <message>",
                "      <source>Hello</source>",
                '      <translation type="unfinished"></translation>',
                "    </message>",
                "  </context>",
                "</TS>",
            ]
        ),
        encoding="utf-8",
    )


def test_discover_runtime_languages_uses_qm_files_and_default_source(
    tmp_path: Path,
) -> None:
    _write_ts(tmp_path / f"{DEFAULT_LANGUAGE_CODE}.ts", language=DEFAULT_LANGUAGE_CODE)
    _write_ts(tmp_path / "fr.ts", language="fr")
    (tmp_path / "fr.qm").write_bytes(b"compiled")

    locales = discover_runtime_languages(tmp_path)

    assert [locale.code for locale in locales] == [DEFAULT_LANGUAGE_CODE, "fr"]
    assert locales[0].qm_path is None
    assert locales[1].qm_path == tmp_path / "fr.qm"


def test_validate_translation_tree_reports_invalid_locale_metadata_and_accepts_qt_codes(
    tmp_path: Path,
) -> None:
    _write_ts(tmp_path / f"{DEFAULT_LANGUAGE_CODE}.ts", language=DEFAULT_LANGUAGE_CODE)
    _write_ts(tmp_path / "fr.ts", language=None)
    _write_ts(tmp_path / "zh_Hans.ts", language="zh_Hans")
    _write_ts(tmp_path / "english.ts", language="english")

    errors = validate_translation_tree(tmp_path)

    assert not any(error.startswith("zh_Hans.ts:") for error in errors)
    assert any('expected <TS language="fr">' in error for error in errors)
    assert any(
        "Invalid translation file name 'english.ts'" in error for error in errors
    )
