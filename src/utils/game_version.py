"""
Utilities for reading the game executable version and checking mod compatibility.

The game executable is a Windows PE binary.  On Windows we try ``win32api``
first (available when *pywin32* is installed); if that fails, or when running
on Linux / macOS (e.g. Proton / Wine setups), we fall back to scanning the raw
binary for the ``VS_FIXEDFILEINFO`` signature – a pure-Python approach that
requires no external dependencies.
"""

import logging
import os
import struct

logger = logging.getLogger(__name__)

GAME_EXE_RELATIVE_PATH = os.path.join("binaries", "x64", "call_to_arms.exe")

# Little-endian encoding of the VS_FIXEDFILEINFO magic 0xFEEF04BD.
_VS_FIXED_FILE_INFO_SIGNATURE = b"\xbd\x04\xef\xfe"


def get_game_version(game_path: str) -> tuple[int, ...] | None:
    """
    Read the file version from the game executable.

    Returns a 4-tuple ``(major, minor, build, revision)`` or ``None`` when the
    version cannot be determined (missing file, unreadable PE, etc.).

    Platform behaviour
    ------------------
    - **Windows**: uses the PE-binary parser directly.  This is
      sufficient because the game executable is always a Windows PE file, even
      when launched through Proton or Wine.
    - **Linux / macOS**: uses the PE-binary parser directly.  This is
      sufficient because the game executable is always a Windows PE file, even
      when launched through Proton or Wine.
    """
    exe_path = os.path.join(game_path, GAME_EXE_RELATIVE_PATH)
    if not os.path.isfile(exe_path):
        logger.warning("Game executable not found at: %s", exe_path)
        return None

    raw = _get_version_from_pe(exe_path)
    if raw is not None:
        version = normalize_game_version(raw)
        logger.info(
            "Game version (PE): %s (raw: %s)",
            ".".join(str(x) for x in version),
            ".".join(str(x) for x in raw),
        )
        return version
    return None


def normalize_game_version(pe_version: tuple[int, ...]) -> tuple[int, ...]:
    """
    Convert the raw PE FileVersion tuple to the version format used in mod.info.

    Gates of Hell encodes its displayed version (e.g. ``1.067.0``) across the
    four PE FileVersion fields by splitting each digit of the minor version
    number across Minor, Build, and Revision:

        PE: (major=1, minor=0, build=6, revision=7)
        game minor = minor*100 + build*10 + revision = 0+60+7 = 67
        → normalized: (1, 67, 0)   which maps to "1.067.0" in mod.info

    At least three components are required; fewer are returned unchanged.
    """
    if len(pe_version) < 4:
        return pe_version
    major, x, y, z = pe_version[:4]
    game_minor = x * 100 + y * 10 + z
    return (major, game_minor, 0)


def parse_version_str(version_str: str) -> tuple[int, ...]:
    """
    Parse a dot-separated version string into a tuple of integers.

    Leading zeros in each component are ignored – ``'062'`` becomes ``62``.

    >>> parse_version_str('1.062.0')
    (1, 62, 0)
    >>> parse_version_str('1.961')
    (1, 961)
    """
    return tuple(int(x) for x in version_str.strip().split("."))


def is_mod_version_compatible(
    game_version: tuple[int, ...],
    min_game_version: str | None,
    max_game_version: str | None,
) -> bool:
    """
    Return ``True`` when *game_version* satisfies the mod's version constraints.

    Recognised formats
    ------------------
    ``None``
        No restriction at all – always compatible.
    ``'any'`` (alone)
        No lower bound.  *max_game_version* is still evaluated.
    ``'1.062.0'``
        Minimum version; *max_game_version* sets the optional upper bound.
    ``'any - 1.062.0'``
        No lower bound, inline upper bound.
    ``'1.062.0 - 1.960.0'``
        Inline min–max range; separate *max_game_version* is ignored.

    In any position ``'any'`` means "unbounded" for that side.
    Comparison is component-by-component after truncating *game_version*
    to the same number of components as the bound being tested.
    """
    if min_game_version is None:
        return True

    raw = min_game_version.strip()

    # Resolve min_ver and max_ver from the raw string.
    min_ver: tuple[int, ...] | None
    max_ver: tuple[int, ...] | None

    if " - " in raw:
        # Inline range, e.g. "1.062.0 - 1.960.0" or "any - 1.062.0".
        left, _, right = raw.partition(" - ")
        left = left.strip()
        right = right.strip()
        min_ver = None if left.lower() == "any" else parse_version_str(left)
        max_ver = None if right.lower() == "any" else parse_version_str(right)
    else:
        # Plain version string or standalone 'any'.
        min_ver = None if raw.lower() == "any" else parse_version_str(raw)
        if max_game_version is not None and max_game_version.strip().lower() != "any":
            max_ver = parse_version_str(max_game_version)
        else:
            max_ver = None

    # When both bounds are absent the mod has no restriction.
    if min_ver is None and max_ver is None:
        return True

    # Lower bound check.
    if min_ver is not None and game_version[: len(min_ver)] < min_ver:
        return False

    # Upper bound check.
    if max_ver is not None and game_version[: len(max_ver)] > max_ver:
        return False

    return True


def _get_version_from_pe(exe_path: str) -> tuple[int, ...] | None:
    """
    Read ``VS_FIXEDFILEINFO`` from a PE binary by locating the 4-byte
    signature ``0xFEEF04BD`` (stored little-endian).

    ``VS_FIXEDFILEINFO`` layout (all little-endian 32-bit words):

    ======  =================  =============================================
    Offset  Field              Notes
    ======  =================  =============================================
    +0      dwSignature        ``0xFEEF04BD``
    +4      dwStrucVersion
    +8      dwFileVersionMS    high-word = major, low-word = minor
    +12     dwFileVersionLS    high-word = build,  low-word = revision
    ======  =================  =============================================
    """
    try:
        with open(exe_path, "rb") as f:
            data = f.read()

        pos = data.find(_VS_FIXED_FILE_INFO_SIGNATURE)
        if pos == -1:
            logger.warning("VS_FIXEDFILEINFO signature not found in: %s", exe_path)
            return None

        if pos + 16 > len(data):
            logger.warning("PE data truncated near VS_FIXEDFILEINFO in: %s", exe_path)
            return None

        ms = struct.unpack_from("<I", data, pos + 8)[0]
        ls = struct.unpack_from("<I", data, pos + 12)[0]

        return (
            (ms >> 16) & 0xFFFF,
            ms & 0xFFFF,
            (ls >> 16) & 0xFFFF,
            ls & 0xFFFF,
        )
    except OSError:
        logger.exception("Failed to read game executable: %s", exe_path)
        return None
