import os
from pathlib import Path

from src.core import constants
from src.utils import steam_utils


def _write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_parse_library_info_supports_new_format(tmp_path):
    library_path = tmp_path / "SteamLibrary"
    manifest_path = library_path / "steamapps" / "appmanifest_400750.acf"
    _write_text(
        manifest_path,
        '"AppState"\n{\n'
        '\t"appid" "400750"\n'
        '\t"installdir" "Call to Arms - Gates of Hell"\n'
        "}\n",
    )

    library_vdf = tmp_path / "libraryfolders.vdf"
    escaped_path = str(library_path).replace("\\", "\\\\")
    _write_text(
        library_vdf,
        '"libraryfolders"\n{\n'
        '\t"0"\n\t{\n'
        f'\t\t"path" "{escaped_path}"\n'
        "\t}\n"
        '\t"contentstatsid" "123"\n'
        "}\n",
    )

    libraries = steam_utils.parse_library_info(library_vdf)

    assert len(libraries) == 1
    assert libraries[0].path == library_path
    assert len(libraries[0].games) == 1
    assert libraries[0].games[0].appid == constants.STEAM_APP_ID


def test_parse_library_info_supports_old_format(tmp_path):
    library_path = tmp_path / "OldSteamLibrary"
    manifest_path = library_path / "steamapps" / "appmanifest_400750.acf"
    _write_text(
        manifest_path,
        '"AppState"\n{\n'
        '\t"appid" "400750"\n'
        '\t"installdir" "Call to Arms - Gates of Hell"\n'
        "}\n",
    )

    library_vdf = tmp_path / "libraryfolders.vdf"
    escaped_path = str(library_path).replace("\\", "\\\\")
    _write_text(
        library_vdf,
        '"LibraryFolders"\n{\n'
        f'\t"1" "{escaped_path}"\n'
        '    "TimeNextStatsReport" "0"\n'
        "}\n",
    )

    libraries = steam_utils.parse_library_info(library_vdf)

    assert len(libraries) == 1
    assert libraries[0].path == library_path
    assert libraries[0].games[0].appid == constants.STEAM_APP_ID


def test_get_active_steam_id32_prefers_most_recent(tmp_path, monkeypatch):
    steam_root = tmp_path / "Steam"
    loginusers_path = steam_root / "config" / "loginusers.vdf"
    _write_text(
        loginusers_path,
        '"users"\n{\n'
        '\t"76561197960265729"\n\t{\n\t\t"MostRecent" "0"\n\t}\n'
        '\t"76561197960265730"\n\t{\n\t\t"MostRecent" "1"\n\t}\n'
        "}\n",
    )
    monkeypatch.setattr(steam_utils, "find_steam_path", lambda: steam_root)

    assert steam_utils.get_active_steam_id32() == "2"


def test_get_active_steam_id32_falls_back_to_first_user(tmp_path, monkeypatch):
    steam_root = tmp_path / "Steam"
    loginusers_path = steam_root / "config" / "loginusers.vdf"
    _write_text(
        loginusers_path,
        '"users"\n{\n'
        '\t"76561197960265729"\n\t{\n\t\t"MostRecent" "0"\n\t}\n'
        '\t"76561197960265730"\n\t{\n\t\t"MostRecent" "0"\n\t}\n'
        "}\n",
    )
    monkeypatch.setattr(steam_utils, "find_steam_path", lambda: steam_root)

    assert steam_utils.get_active_steam_id32() == "1"


def test_get_goh_profile_path_prefers_exact_active_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(steam_utils, "get_active_steam_id32", lambda: "12345")
    monkeypatch.setattr(steam_utils.Path, "home", classmethod(lambda cls: tmp_path))

    exact_profile = (
        tmp_path
        / "Documents"
        / "My Games"
        / "gates of hell"
        / "profiles"
        / "12345"
        / constants.OPTIONS_SET_FILE
    )
    _write_text(exact_profile, "{options}")

    assert steam_utils.get_goh_profile_path() == exact_profile


def test_get_goh_profile_path_falls_back_to_latest_non_offline(tmp_path, monkeypatch):
    monkeypatch.setattr(steam_utils, "get_active_steam_id32", lambda: None)
    monkeypatch.setattr(steam_utils.Path, "home", classmethod(lambda cls: tmp_path))

    profiles_root = tmp_path / "Documents" / "My Games" / "gates of hell" / "profiles"
    older = profiles_root / "111" / constants.OPTIONS_SET_FILE
    newer = profiles_root / "222" / constants.OPTIONS_SET_FILE
    offline = profiles_root / "offline" / constants.OPTIONS_SET_FILE

    _write_text(older, "{options}")
    _write_text(newer, "{options}")
    _write_text(offline, "{options}")

    os.utime(older, (100, 100))
    os.utime(newer, (200, 200))
    os.utime(offline, (300, 300))

    assert steam_utils.get_goh_profile_path() == newer


def test_get_goh_workshop_path_returns_workshop_directory(monkeypatch):
    game_path = Path("C:/SteamLibrary/steamapps/common/Call to Arms - Gates of Hell")
    workshop_path = (
        game_path.parent.parent / "workshop" / "content" / constants.STEAM_APP_ID
    )

    monkeypatch.setattr(steam_utils, "get_goh_game_path", lambda: game_path)
    monkeypatch.setattr(Path, "exists", lambda self: self == workshop_path)

    assert steam_utils.get_goh_workshop_path() == workshop_path
