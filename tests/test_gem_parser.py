import os
from typing import cast

import pytest
from src.utils.gem_parser import (
    GemNodeValue,
    GemParseError,
    parse_gem,
    parse_gem_file,
    repair_gem_braces,
    validate_gem,
)

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")


def test_parse_real_mod_info_fixture():
    nodes = parse_gem_file(os.path.join(RESOURCES_DIR, "mod.info"))

    assert len(nodes) == 1
    mod = cast(dict[str, GemNodeValue], nodes[0].to_dict())

    assert nodes[0].name == "mod"
    assert "GOH ARm" in cast(str, mod["name"])
    assert mod["minGameVersion"] == "1.061"
    assert mod["require"] == "mod_2905667604"


def test_parse_real_options_set_fixture():
    nodes = parse_gem_file(os.path.join(RESOURCES_DIR, "options.set"))

    assert len(nodes) == 1
    options = cast(dict[str, GemNodeValue], nodes[0].to_dict())
    mods = cast(list[str], options["mods"])

    assert nodes[0].name == "options"
    assert "mod_2905667604:0" in mods
    assert "mod_2867922286:0" in mods


def test_comments_are_ignored_outside_quoted_strings():
    nodes = parse_gem('{mod ; comment\n {name "Visible"}}')

    data = cast(dict[str, GemNodeValue], nodes[0].to_dict())

    assert data["name"] == "Visible"


def test_semicolon_inside_quoted_string_is_preserved():
    nodes = parse_gem('{mod {desc "Balance; realism overhaul"}}')

    data = cast(dict[str, GemNodeValue], nodes[0].to_dict())

    assert data["desc"] == "Balance; realism overhaul"


def test_quoted_strings_support_escaped_quotes_and_backslashes():
    nodes = parse_gem(r'{mod {desc "A \"quoted\" path C:\\mods\\arm"}}')

    data = cast(dict[str, GemNodeValue], nodes[0].to_dict())

    assert data["desc"] == 'A "quoted" path C:\\mods\\arm'


def test_braces_inside_quoted_string_do_not_affect_structure():
    nodes = parse_gem('{mod {desc "Uses {curly} braces"} {name Test}}')

    data = cast(dict[str, GemNodeValue], nodes[0].to_dict())

    assert data["desc"] == "Uses {curly} braces"
    assert data["name"] == "Test"


def test_repeated_keys_still_become_lists():
    nodes = parse_gem('{mod {require "mod_a"} {require "mod_b"}}')

    data = cast(dict[str, GemNodeValue], nodes[0].to_dict())

    assert data["require"] == ["mod_a", "mod_b"]


def test_parse_rejects_extra_closing_brace():
    with pytest.raises(GemParseError, match="Unexpected closing brace"):
        parse_gem("{mod {name Test}}}")


def test_parse_rejects_unclosed_block():
    with pytest.raises(GemParseError, match="Unclosed block"):
        parse_gem("{mod {name Test}")


def test_parse_rejects_unterminated_quoted_string():
    with pytest.raises(GemParseError, match="Unterminated quoted string"):
        parse_gem('{mod {name "Test}}')


def test_validate_gem_reports_errors_without_raising():
    result = validate_gem("{mod {name Test}")

    assert result.is_valid is False
    assert len(result.errors) == 1
    assert "Unclosed block" in str(result.errors[0])


def test_repair_gem_braces_appends_missing_closing_braces():
    result = repair_gem_braces("{mod {name Test}")

    assert result.changed is True
    assert result.added_closing_braces == 1
    assert parse_gem(result.content)[0].name == "mod"


def test_repair_gem_braces_removes_extra_closing_braces():
    result = repair_gem_braces("{mod {name Test}}}")

    assert result.changed is True
    assert result.removed_extra_closing_braces == 1
    assert parse_gem(result.content)[0].name == "mod"


def test_repair_gem_braces_ignores_braces_in_strings_and_comments():
    result = repair_gem_braces('{mod {desc "{ text }"}} ; }\n')

    assert result.changed is False
    assert result.content == '{mod {desc "{ text }"}} ; }\n'
