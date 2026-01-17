from pathlib import Path

from goh_mod_manager.infrastructure.options_set_parser import OptionsSetParser


def _write_options_file(path: Path, lines: list[str]) -> None:
    path.write_text("".join(lines), encoding="utf-8")


def test_get_mods_and_invalid_entries(tmp_path: Path) -> None:
    options_file = tmp_path / "options.set"
    lines = [
        "{options\n",
        "\t{mods\n",
        '\t\t"mod_123:0"\n',
        '\t\t"456:0"\n',
        '\t\t"mod_template:0"\n',
        '\t\t"bad_entry"\n',
        '\t\t"mod_abc:0"\n',
        "\t}\n",
        "}\n",
    ]
    _write_options_file(options_file, lines)

    parser = OptionsSetParser(str(options_file))
    assert parser.get_mods() == ["123", "456"]
    assert parser.get_invalid_mod_entries() == ['\t\t"bad_entry"', '\t\t"mod_abc:0"']


def test_clear_mods_section_removes_all_entries(tmp_path: Path) -> None:
    options_file = tmp_path / "options.set"
    lines = [
        "{options\n",
        "\t{mods\n",
        '\t\t"mod_123:0"\n',
        '\t\t"bad_entry"\n',
        "\t}\n",
        "}\n",
    ]
    _write_options_file(options_file, lines)

    parser = OptionsSetParser(str(options_file))
    assert parser.clear_mods_section() is True

    # Ensure mods section is empty (only braces remain)
    reloaded = OptionsSetParser(str(options_file))
    assert reloaded.get_mods() == []
    assert reloaded.get_invalid_mod_entries() == []
