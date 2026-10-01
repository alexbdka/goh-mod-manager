"""
Unit tests for src/utils/game_version.py

These tests cover version-string parsing, compatibility checking, and the
PE-binary reader without requiring a real game executable.
"""

import os
import struct

from src.utils.game_version import (
    _VS_FIXED_FILE_INFO_SIGNATURE,
    _get_version_from_pe,
    get_game_version,
    is_mod_version_compatible,
    normalize_game_version,
    parse_version_str,
)

# ---------------------------------------------------------------------------
# parse_version_str
# ---------------------------------------------------------------------------


class TestParseVersionStr:
    def test_three_component(self):
        assert parse_version_str("1.062.0") == (1, 62, 0)

    def test_two_component(self):
        assert parse_version_str("1.961") == (1, 961)

    def test_four_component(self):
        assert parse_version_str("1.062.0.0") == (1, 62, 0, 0)

    def test_leading_zeros_treated_as_decimal(self):
        # "062" → 62, not octal
        assert parse_version_str("1.062") == (1, 62)

    def test_strips_whitespace(self):
        assert parse_version_str("  1.2.3  ") == (1, 2, 3)


# ---------------------------------------------------------------------------
# is_mod_version_compatible
# ---------------------------------------------------------------------------


class TestIsModVersionCompatible:
    GAME = (1, 100, 0, 0)  # representative installed game version

    # --- None / 'any' → always compatible ---

    def test_none_min_is_compatible(self):
        assert is_mod_version_compatible(self.GAME, None, None) is True

    def test_any_alone_is_compatible(self):
        assert is_mod_version_compatible(self.GAME, "any", None) is True

    def test_any_case_insensitive(self):
        assert is_mod_version_compatible(self.GAME, "ANY", None) is True

    # 'any' as min still enforces maxGameVersion
    def test_any_min_with_max_game_above_max(self):
        # game=1.100, maxGameVersion="1.062" → incompatible
        assert is_mod_version_compatible((1, 100, 0, 0), "any", "1.062") is False

    def test_any_min_with_max_game_below_max(self):
        # game=1.061, maxGameVersion="1.062" → compatible
        assert is_mod_version_compatible((1, 61, 0, 0), "any", "1.062") is True

    def test_any_min_with_max_any_is_always_compatible(self):
        assert is_mod_version_compatible((2, 0, 0, 0), "any", "any") is True

    # --- plain minimum version ---

    def test_game_equals_min(self):
        assert is_mod_version_compatible((1, 62, 0, 0), "1.062.0", None) is True

    def test_game_above_min(self):
        assert is_mod_version_compatible((1, 100, 0, 0), "1.062.0", None) is True

    def test_game_below_min(self):
        assert is_mod_version_compatible((1, 61, 0, 0), "1.062.0", None) is False

    def test_two_component_min(self):
        assert is_mod_version_compatible((1, 61, 0, 0), "1.061", None) is True
        assert is_mod_version_compatible((1, 60, 0, 0), "1.061", None) is False

    # --- separate min + max ---

    def test_game_within_range(self):
        assert is_mod_version_compatible((1, 500, 0, 0), "1.062.0", "1.960.0") is True

    def test_game_equals_max(self):
        assert is_mod_version_compatible((1, 960, 0, 0), "1.062.0", "1.960.0") is True

    def test_game_above_max(self):
        assert is_mod_version_compatible((1, 961, 0, 0), "1.062.0", "1.960.0") is False

    def test_game_below_min_with_max(self):
        assert is_mod_version_compatible((1, 61, 0, 0), "1.062.0", "1.960.0") is False

    def test_max_any_means_no_upper_bound(self):
        assert is_mod_version_compatible((2, 0, 0, 0), "1.062.0", "any") is True

    # --- inline range in minGameVersion ---

    def test_inline_range_within(self):
        assert (
            is_mod_version_compatible((1, 500, 0, 0), "1.062.0 - 1.960.0", None) is True
        )

    def test_inline_range_equals_min(self):
        assert (
            is_mod_version_compatible((1, 62, 0, 0), "1.062.0 - 1.960.0", None) is True
        )

    def test_inline_range_equals_max(self):
        assert (
            is_mod_version_compatible((1, 960, 0, 0), "1.062.0 - 1.960.0", None) is True
        )

    def test_inline_range_below_min(self):
        assert (
            is_mod_version_compatible((1, 61, 0, 0), "1.062.0 - 1.960.0", None) is False
        )

    def test_inline_range_above_max(self):
        assert (
            is_mod_version_compatible((1, 961, 0, 0), "1.062.0 - 1.960.0", None)
            is False
        )

    def test_inline_range_ignores_separate_max(self):
        # When an inline range is detected, the separate maxGameVersion is ignored.
        assert (
            is_mod_version_compatible((1, 961, 0, 0), "1.062.0 - 1.960.0", "2.000.0")
            is False
        )

    # --- inline range with 'any' on the left side ---

    def test_inline_any_min_game_below_max(self):
        # "any - 1.062.0": game 1.061 is within bound
        assert is_mod_version_compatible((1, 61, 0, 0), "any - 1.062.0", None) is True

    def test_inline_any_min_game_equals_max(self):
        assert is_mod_version_compatible((1, 62, 0, 0), "any - 1.062.0", None) is True

    def test_inline_any_min_game_above_max(self):
        # "any - 1.062.0": game 1.067 exceeds the upper bound
        assert is_mod_version_compatible((1, 67, 0, 0), "any - 1.062.0", None) is False

    def test_inline_any_max(self):
        # "1.062.0 - any": no upper bound, only lower
        assert is_mod_version_compatible((9, 999, 0, 0), "1.062.0 - any", None) is True

    # --- two-component versionsnt versions (as seen in actual mod.info files) ---

    def test_two_component_exact(self):
        assert is_mod_version_compatible((1, 61, 5, 0), "1.061", "1.061") is True

    def test_two_component_above_max(self):
        assert is_mod_version_compatible((1, 62, 0, 0), "1.061", "1.061") is False


# ---------------------------------------------------------------------------
# PE binary reader
# ---------------------------------------------------------------------------


def _build_fake_pe(major: int, minor: int, build: int, revision: int) -> bytes:
    """Build a minimal byte sequence containing a VS_FIXEDFILEINFO record."""
    ms = (major << 16) | (minor & 0xFFFF)
    ls = (build << 16) | (revision & 0xFFFF)
    record = (
        _VS_FIXED_FILE_INFO_SIGNATURE
        + struct.pack("<I", 0x00010000)  # dwStrucVersion
        + struct.pack("<I", ms)
        + struct.pack("<I", ls)
        + b"\x00" * 36  # remaining VS_FIXEDFILEINFO fields
    )
    return b"\x00" * 128 + record + b"\x00" * 64


# ---------------------------------------------------------------------------
# normalize_game_version
# ---------------------------------------------------------------------------


class TestNormalizeGameVersion:
    def test_known_real_version(self):
        # PE 1.0.6.7 → game version 1.067.0
        assert normalize_game_version((1, 0, 6, 7)) == (1, 67, 0)

    def test_hundreds_digit(self):
        # PE 1.1.0.0 → game version 1.100.0
        assert normalize_game_version((1, 1, 0, 0)) == (1, 100, 0)

    def test_zero_minor(self):
        # PE 1.0.0.0 → game version 1.0.0
        assert normalize_game_version((1, 0, 0, 0)) == (1, 0, 0)

    def test_short_tuple_returned_unchanged(self):
        assert normalize_game_version((1, 2)) == (1, 2)


class TestGetVersionFromPE:
    def test_reads_version_from_fake_pe(self, tmp_path):
        # _get_version_from_pe returns the raw PE tuple (no normalization).
        data = _build_fake_pe(1, 0, 6, 2)
        exe = tmp_path / "game.exe"
        exe.write_bytes(data)
        result = _get_version_from_pe(str(exe))
        assert result == (1, 0, 6, 2)

    def test_returns_none_when_signature_absent(self, tmp_path):
        exe = tmp_path / "game.exe"
        exe.write_bytes(b"\x00" * 256)
        assert _get_version_from_pe(str(exe)) is None

    def test_returns_none_for_missing_file(self, tmp_path):
        result = _get_version_from_pe(str(tmp_path / "missing.exe"))
        assert result is None

    def test_returns_none_when_data_truncated(self, tmp_path):
        # Signature present but not enough bytes after it.
        data = b"\x00" * 4 + _VS_FIXED_FILE_INFO_SIGNATURE + b"\x00" * 4
        exe = tmp_path / "game.exe"
        exe.write_bytes(data)
        assert _get_version_from_pe(str(exe)) is None


# ---------------------------------------------------------------------------
# get_game_version (integration with filesystem)
# ---------------------------------------------------------------------------


class TestGetGameVersion:
    _EXE_REL = os.path.join("binaries", "x64", "call_to_arms.exe")

    def _write_exe_pe(self, game_root, major, pe_minor, pe_build, pe_revision):
        """Write a fake exe using raw PE field values."""
        exe_path = game_root / self._EXE_REL
        exe_path.parent.mkdir(parents=True, exist_ok=True)
        exe_path.write_bytes(_build_fake_pe(major, pe_minor, pe_build, pe_revision))

    def test_normalizes_real_encoding(self, tmp_path):
        # PE 1.0.6.7 → normalized (1, 67, 0), i.e. game version 1.067.0
        self._write_exe_pe(tmp_path, 1, 0, 6, 7)
        assert get_game_version(str(tmp_path)) == (1, 67, 0)

    def test_returns_none_when_exe_missing(self, tmp_path):
        assert get_game_version(str(tmp_path)) is None
