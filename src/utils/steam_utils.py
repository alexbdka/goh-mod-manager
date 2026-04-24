"""
Steam discovery helpers for game install, Workshop content, and profile files.

This module adapts ideas from ModOrganizer2's basic game support and from the
steam-library-setup-tool project to locate the Gates of Hell installation,
Workshop directory, and the most relevant ``options.set`` profile.
"""

import logging
import os
import sys

from src.core import constants

if sys.platform == "win32":
    import winreg
from pathlib import Path
from typing import TypedDict, cast

import vdf  # pyright: ignore[reportMissingTypeStubs]

logger = logging.getLogger(__name__)


class SteamGame:
    """Small value object describing one discovered Steam app entry."""

    def __init__(self, appid: str, installdir: str):
        self.appid = appid
        self.installdir = installdir

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.appid} ({self.installdir})"


class _AppState(TypedDict):
    appid: str
    installdir: str


class _AppManifest(TypedDict):
    AppState: _AppState


class _LibraryFolder(TypedDict):
    path: str


class _LibraryFolders(TypedDict, total=False):
    libraryfolders: dict[str, _LibraryFolder]
    LibraryFolders: dict[str, str]


class LibraryFolder:
    """Represent one Steam library and the app manifests discovered inside it."""

    def __init__(self, path: Path):
        self.path = path

        self.games: list[SteamGame] = []
        for filepath in path.joinpath("steamapps").glob("appmanifest_*.acf"):
            try:
                with open(filepath, encoding="utf-8") as fp:
                    info = cast(
                        _AppManifest,
                        vdf.load(fp),  # pyright: ignore[reportUnknownMemberType]
                    )
                    app_state = info["AppState"]
            except KeyError:
                logger.warning(
                    'Unable to read application state from "%s"',
                    filepath,
                )
                continue
            except Exception as e:
                logger.warning('Unable to parse file "%s": %s', filepath, e)
                continue

            try:
                app_id = app_state["appid"]
                install_dir = app_state["installdir"]
                self.games.append(SteamGame(app_id, install_dir))
            except KeyError:
                logger.warning(
                    'Unable to read application ID or installation folder from "%s"',
                    filepath,
                )
                continue

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"LibraryFolder at {self.path}: {self.games}"


def parse_library_info(library_vdf_path: Path) -> list[LibraryFolder]:
    """
    Read library folders from the main library file.

    Args:
        library_vdf_path: The main library file (from the Steam installation
            folder).

    Returns:
        A list of LibraryFolder, for each library found.
    """

    with open(library_vdf_path, encoding="utf-8") as f:
        info = cast(
            _LibraryFolders,
            vdf.load(f),  # pyright: ignore[reportUnknownMemberType]
        )

    info_folders: dict[str, str] | dict[str, _LibraryFolder]

    if "libraryfolders" in info:
        info_folders = info["libraryfolders"]

    elif "LibraryFolders" in info:
        info_folders = info["LibraryFolders"]

    else:
        raise ValueError(f'Unknown file format from "{library_vdf_path}"')

    library_folders: list[LibraryFolder] = []

    for key, value in info_folders.items():
        try:
            int(key)
        except ValueError:
            continue

        if isinstance(value, str):
            path = value
        else:
            path = value["path"]

        try:
            library_folders.append(LibraryFolder(Path(path)))
        except Exception as e:
            logger.warning('Failed to read steam library from "%s": %r', path, e)

    return library_folders


def find_steam_path() -> Path | None:
    """Return the Steam installation root for the current platform, if found."""
    if sys.platform == "win32":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam"
            ) as key:
                value = winreg.QueryValueEx(key, "SteamExe")
                return Path(value[0].replace("/", "\\")).parent
        except FileNotFoundError:
            return None

    possible_paths = [
        Path.home() / ".local/share/Steam",
        Path.home() / ".steam/steam",
        Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def find_games() -> dict[str, Path]:
    """
    Find the list of Steam games installed.

    Returns:
        A mapping from Steam game ID to install locations for available
        Steam games.
    """
    steam_path = find_steam_path()
    if not steam_path:
        return {}

    library_vdf_path = steam_path.joinpath("steamapps", "libraryfolders.vdf")

    try:
        library_folders = parse_library_info(library_vdf_path)
        library_folders.append(LibraryFolder(steam_path))
    except FileNotFoundError:
        return {}

    games: dict[str, Path] = {}
    for library in library_folders:
        for game in library.games:
            games[game.appid] = Path(library.path).joinpath(
                "steamapps", "common", game.installdir
            )

    return games


def get_goh_game_path() -> Path | None:
    """
    Returns the installation directory of Call to Arms - Gates of Hell.
    """
    games = find_games()
    for k, v in games.items():
        if k == constants.STEAM_APP_ID:
            return v
    return None


def get_goh_workshop_path() -> Path | None:
    """Return the Steam Workshop content directory for Gates of Hell."""
    game_path = get_goh_game_path()
    if game_path:
        workshop_path = (
            game_path.parent.parent / "workshop" / "content" / constants.STEAM_APP_ID
        )
        if workshop_path.exists():
            return workshop_path
    return None


def get_active_steam_id32() -> str | None:
    """Return the most recent Steam user as a SteamID32 string, if available."""
    steam_path = find_steam_path()
    if not steam_path:
        return None

    loginusers_path = steam_path / "config" / "loginusers.vdf"
    if not loginusers_path.exists():
        return None

    try:
        with open(loginusers_path, encoding="utf-8") as f:
            data = vdf.load(f)  # pyright: ignore[reportUnknownMemberType]

        users = data.get("users", {})
        recent_id64 = None

        for uid, info in users.items():
            if info.get("MostRecent") == "1":
                recent_id64 = uid
                break

        if not recent_id64 and users:
            recent_id64 = list(users.keys())[0]

        if recent_id64:
            id64_int = int(recent_id64)
            id32_int = id64_int - 76561197960265728
            return str(id32_int)
    except Exception as e:
        logger.warning("Error reading loginusers.vdf: %s", e)

    return None


def get_goh_profile_path() -> Path | None:
    """
    Return the best candidate ``options.set`` path for the current machine.

    The resolver first tries an exact match for the active Steam user and then
    falls back to scanning known profile roots for the newest file.
    """
    steam_id32 = get_active_steam_id32()

    potential_bases = [
        Path.home() / "Documents" / "My Games" / "gates of hell" / "profiles"
    ]

    if sys.platform == "win32":
        potential_bases.append(
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "digitalmindsoft"
            / "gates of hell"
        )

    if steam_id32:
        for base in potential_bases:
            exact_path = base / steam_id32 / constants.OPTIONS_SET_FILE
            if exact_path.exists():
                return exact_path

    options_files: list[Path] = []

    for base in potential_bases:
        if not base.exists():
            continue

        files = [
            f
            for f in base.rglob(constants.OPTIONS_SET_FILE)
            if "offline" not in f.parts
        ]
        options_files.extend(files)

    if not options_files:
        return None

    options_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return options_files[0]
