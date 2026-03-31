# The code below is taken from https://github.com/ModOrganizer2/modorganizer-basic_games/blob/master/steam_utils.py
# which is greatly inspired by https://github.com/LostDragonist/steam-library-setup-tool with some adjustments

import os
import sys

from src.core import constants

if sys.platform == "win32":
    import winreg
from pathlib import Path
from typing import TypedDict, cast

import vdf  # pyright: ignore[reportMissingTypeStubs]


class SteamGame:
    def __init__(self, appid: str, installdir: str):
        self.appid = appid
        self.installdir = installdir

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{} ({})".format(self.appid, self.installdir)


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
    def __init__(self, path: Path):
        self.path = path

        self.games: list[SteamGame] = []
        for filepath in path.joinpath("steamapps").glob("appmanifest_*.acf"):
            try:
                with open(filepath, "r", encoding="utf-8") as fp:
                    info = cast(
                        _AppManifest,
                        vdf.load(fp),  # pyright: ignore[reportUnknownMemberType]
                    )
                    app_state = info["AppState"]
            except KeyError:
                print(
                    f'Unable to read application state from "{filepath}"',
                    file=sys.stderr,
                )
                continue
            except Exception as e:
                print(f'Unable to parse file "{filepath}": {e}', file=sys.stderr)
                continue

            try:
                app_id = app_state["appid"]
                install_dir = app_state["installdir"]
                self.games.append(SteamGame(app_id, install_dir))
            except KeyError:
                print(
                    f"Unable to read application ID or installation folder "
                    f'from "{filepath}"',
                    file=sys.stderr,
                )
                continue

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "LibraryFolder at {}: {}".format(self.path, self.games)


def parse_library_info(library_vdf_path: Path) -> list[LibraryFolder]:
    """
    Read library folders from the main library file.

    Args:
        library_vdf_path: The main library file (from the Steam installation
            folder).

    Returns:
        A list of LibraryFolder, for each library found.
    """

    with open(library_vdf_path, "r", encoding="utf-8") as f:
        info = cast(
            _LibraryFolders,
            vdf.load(f),  # pyright: ignore[reportUnknownMemberType]
        )

    info_folders: dict[str, str] | dict[str, _LibraryFolder]

    if "libraryfolders" in info:
        # new format
        info_folders = info["libraryfolders"]

    elif "LibraryFolders" in info:
        # old format
        info_folders = info["LibraryFolders"]

    else:
        raise ValueError(f'Unknown file format from "{library_vdf_path}"')

    library_folders: list[LibraryFolder] = []

    for key, value in info_folders.items():
        # only keys that are integer values contains library folder
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
            print(
                'Failed to read steam library from "{}", {}'.format(path, repr(e)),
                file=sys.stderr,
            )

    return library_folders


def find_steam_path() -> Path | None:
    """
    Retrieve the Steam path, if available.
    Works on Windows and Linux.
    """
    # Windows
    if sys.platform == "win32":
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, "Software\\Valve\\Steam"
            ) as key:
                value = winreg.QueryValueEx(key, "SteamExe")
                return Path(value[0].replace("/", "\\")).parent
        except FileNotFoundError:
            return None

    # Linux / macOS
    possible_paths = [
        Path.home() / ".local/share/Steam",
        Path.home() / ".steam/steam",
        Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam",  # Flatpak
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
    """
    Returns the workshop directory for Call to Arms - Gates of Hell.
    """
    game_path = get_goh_game_path()
    if game_path:
        # game_path is typically something like "C:/SteamLibrary/steamapps/common/Call to Arms - Gates of Hell"
        # The workshop is at "C:/SteamLibrary/steamapps/workshop/content/400750"
        workshop_path = (
            game_path.parent.parent / "workshop" / "content" / constants.STEAM_APP_ID
        )
        if workshop_path.exists():
            return workshop_path
    return None


def get_active_steam_id32() -> str | None:
    """
    Parses Steam's loginusers.vdf to find the most recent user's SteamID32.
    """
    steam_path = find_steam_path()
    if not steam_path:
        return None

    loginusers_path = steam_path / "config" / "loginusers.vdf"
    if not loginusers_path.exists():
        return None

    try:
        with open(loginusers_path, "r", encoding="utf-8") as f:
            data = vdf.load(f)  # pyright: ignore[reportUnknownMemberType]

        users = data.get("users", {})
        recent_id64 = None

        # Find the most recently logged in user
        for uid, info in users.items():
            if info.get("MostRecent") == "1":
                recent_id64 = uid
                break

        # Fallback to the first user if MostRecent isn't found
        if not recent_id64 and users:
            recent_id64 = list(users.keys())[0]

        if recent_id64:
            # Convert SteamID64 to SteamID32
            # The magic constant is 76561197960265728
            id64_int = int(recent_id64)
            id32_int = id64_int - 76561197960265728
            return str(id32_int)
    except Exception as e:
        print(f"Error reading loginusers.vdf: {e}", file=sys.stderr)

    return None


def get_goh_profile_path() -> Path | None:
    """
    Returns the path to the most recently modified options.set file for the game.
    First tries to use the active Steam User ID to precisely locate the folder.
    Falls back to scanning and finding the most recently modified file.
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

    # Attempt to find exactly matching the SteamID32 folder first
    if steam_id32:
        for base in potential_bases:
            exact_path = base / steam_id32 / constants.OPTIONS_SET_FILE
            if exact_path.exists():
                return exact_path

    # Fallback: scan all potential bases and pick the most recently modified options.set
    options_files: list[Path] = []

    for base in potential_bases:
        if not base.exists():
            continue

        # There might be multiple profiles (like user ID folders)
        # We ignore the "offline" profile folder as it's rarely the main one
        files = [
            f
            for f in base.rglob(constants.OPTIONS_SET_FILE)
            if "offline" not in f.parts
        ]
        options_files.extend(files)

    if not options_files:
        return None

    # Sort by modification time to get the most recently played profile
    options_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return options_files[0]
