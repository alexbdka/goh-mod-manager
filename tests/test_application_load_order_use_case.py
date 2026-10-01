import os
import struct

import pytest
from src.application.use_cases import ApplicationLoadOrderUseCase
from src.core.exceptions import ProfileWriteError
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.utils.game_version import _VS_FIXED_FILE_INFO_SIGNATURE

GAME_EXE_REL = os.path.join("binaries", "x64", "call_to_arms.exe")


def _write_fake_exe(game_root: str, major: int, mod_minor: int) -> None:
    """
    Write a fake game exe for a given version in mod format.

    ``mod_minor`` is the minor version as used in mod.info (e.g. 61, 62, 100).
    It is encoded into the PE Minor/Build/Revision fields using the same
    split-digit scheme the real game uses:
        mod_minor=67 → PE (major=1, minor=0, build=6, revision=7)
    """
    pe_minor = mod_minor // 100
    pe_build = (mod_minor % 100) // 10
    pe_revision = mod_minor % 10
    exe_path = os.path.join(game_root, GAME_EXE_REL)
    os.makedirs(os.path.dirname(exe_path), exist_ok=True)
    ms = (major << 16) | (pe_minor & 0xFFFF)
    ls = (pe_build << 16) | (pe_revision & 0xFFFF)
    record = (
        _VS_FIXED_FILE_INFO_SIGNATURE
        + struct.pack("<I", 0x00010000)
        + struct.pack("<I", ms)
        + struct.pack("<I", ls)
        + b"\x00" * 36
    )
    with open(exe_path, "wb") as f:
        f.write(b"\x00" * 128 + record + b"\x00" * 64)


def _make_use_case(tmp_path):
    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.profile_path = str(tmp_path / "options.set")
    (tmp_path / "options.set").write_text("{options\n\t{mods}\n}\n", encoding="utf-8")

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        "dep": ModInfo(id="dep", name="Dependency", desc="", isLocal=True),
        "main": ModInfo(
            id="main", name="Main", desc="", dependencies=["dep"], isLocal=True
        ),
        "other": ModInfo(id="other", name="Other", desc="", isLocal=True),
    }

    active_mods = ActiveModsService(catalogue)
    use_case = ApplicationLoadOrderUseCase(
        active_mods,
        catalogue,
        config_service,
    )
    return use_case, active_mods


def test_activate_mods_resolves_dependencies_and_persists_once(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)

    result = use_case.activate_mods(["main"])

    assert result.changed is True
    assert result.activated_mod_ids == ["main"]
    assert result.missing_dependencies == []
    assert active_mods.active_mods_ids == ["dep", "main"]


def test_activate_mods_reports_no_change_when_ref_is_already_active(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mod_refs = ["local::dep"]

    result = use_case.activate_mods(["dep"])

    assert result.changed is False
    assert result.activated_mod_ids == []
    assert active_mods.active_mod_refs == ["local::dep"]


def test_deactivate_mod_reports_no_change_when_mod_is_not_active(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)

    result = use_case.deactivate_mod("ghost")

    assert result.changed is False
    assert result.active_mod_ids == active_mods.active_mods_ids


def test_move_and_reorder_return_changed_state(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    move_result = use_case.move_up("other")
    assert move_result.changed is True
    assert active_mods.active_mods_ids == ["dep", "other", "main"]

    reorder_result = use_case.reorder(["other", "dep", "main"])
    assert reorder_result.changed is True
    assert active_mods.active_mods_ids == ["other", "dep", "main"]


def test_deactivate_mod_blocks_active_dependency_removal(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.deactivate_mod("dep")

    assert result.changed is False
    assert result.blocked_reason == "required_by_active_mods"
    assert result.blocking_mod_refs == ["local::main"]
    assert active_mods.active_mods_ids == ["dep", "main", "other"]


def test_reorder_blocks_dependency_after_dependent(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.reorder(["main", "dep", "other"])

    assert result.changed is False
    assert result.blocked_reason == "invalid_dependency_order"
    assert result.blocking_mod_refs == ["local::main"]
    assert active_mods.active_mods_ids == ["dep", "main", "other"]


def test_reorder_blocks_payload_missing_active_mod(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.reorder(["dep", "main"])

    assert result.changed is False
    assert result.blocked_reason == "invalid_order_payload"
    assert active_mods.active_mods_ids == ["dep", "main", "other"]


def test_reorder_blocks_payload_with_unknown_mod(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.reorder(["dep", "main", "ghost"])

    assert result.changed is False
    assert result.blocked_reason == "invalid_order_payload"
    assert active_mods.active_mods_ids == ["dep", "main", "other"]


def test_move_blocks_dependency_after_dependent(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.move_down("dep")

    assert result.changed is False
    assert result.blocked_reason == "invalid_dependency_order"
    assert result.blocking_mod_refs == ["local::main"]
    assert active_mods.active_mods_ids == ["dep", "main", "other"]


def test_clear_returns_changed_only_when_needed(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)

    empty_result = use_case.clear()
    assert empty_result.changed is False

    active_mods.active_mods_ids = ["dep", "main"]
    clear_result = use_case.clear()
    assert clear_result.changed is True
    assert active_mods.active_mods_ids == []


def test_mutating_load_order_requires_profile_path(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    use_case._config_service.get_config().profile_path = None

    with pytest.raises(ProfileWriteError):
        use_case.activate_mods(["main"])

    assert active_mods.active_mods_ids == []


def test_deactivate_mod_allows_dependency_removal_when_enforcement_disabled(
    tmp_path,
):
    use_case, active_mods = _make_use_case(tmp_path)
    use_case._config_service.get_config().enforce_dependency_order = False
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.deactivate_mod("dep")

    assert result.changed is True
    assert result.blocked_reason is None
    assert active_mods.active_mods_ids == ["main", "other"]


def test_reorder_allows_dependency_after_dependent_when_enforcement_disabled(
    tmp_path,
):
    use_case, active_mods = _make_use_case(tmp_path)
    use_case._config_service.get_config().enforce_dependency_order = False
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.reorder(["main", "dep", "other"])

    assert result.changed is True
    assert result.blocked_reason is None
    assert active_mods.active_mods_ids == ["main", "dep", "other"]


def test_move_allows_dependency_after_dependent_when_enforcement_disabled(
    tmp_path,
):
    use_case, active_mods = _make_use_case(tmp_path)
    use_case._config_service.get_config().enforce_dependency_order = False
    active_mods.active_mods_ids = ["dep", "main", "other"]

    result = use_case.move_down("dep")

    assert result.changed is True
    assert result.blocked_reason is None
    assert active_mods.active_mods_ids == ["main", "dep", "other"]


# Game version enforcement tests


def _make_use_case_with_versioned_mods(tmp_path):
    """Use case fixture whose catalogue has mods with minGameVersion constraints."""
    game_root = str(tmp_path / "game")
    os.makedirs(game_root, exist_ok=True)

    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.profile_path = str(tmp_path / "options.set")
    config.game_path = game_root
    (tmp_path / "options.set").write_text("{options\n\t{mods}\n}\n", encoding="utf-8")

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        # compatible with any game version
        "no_version": ModInfo(
            id="no_version", name="No Version", desc="", isLocal=True
        ),
        # requires exactly 1.100
        "needs_100": ModInfo(
            id="needs_100",
            name="Needs 1.100",
            desc="",
            isLocal=True,
            minGameVersion="1.100",
            maxGameVersion="1.100",
        ),
        # requires 1.062 or newer (no upper bound)
        "needs_062_plus": ModInfo(
            id="needs_062_plus",
            name="Needs 1.062+",
            desc="",
            isLocal=True,
            minGameVersion="1.062",
        ),
        # inline range 1.062 – 1.960
        "inline_range": ModInfo(
            id="inline_range",
            name="Inline Range",
            desc="",
            isLocal=True,
            minGameVersion="1.062.0 - 1.960.0",
        ),
    }

    active_mods = ActiveModsService(catalogue)
    use_case = ApplicationLoadOrderUseCase(active_mods, catalogue, config_service)
    return use_case, active_mods, config_service, game_root


def test_enforce_game_version_blocks_incompatible_mod(tmp_path):
    use_case, active_mods, config_service, game_root = (
        _make_use_case_with_versioned_mods(tmp_path)
    )
    # Game is version 1.061 — too old for "needs_062_plus" and "needs_100"
    _write_fake_exe(game_root, 1, 61)
    config_service.get_config().enforce_game_version = True

    result = use_case.activate_mods(["needs_062_plus"])

    assert result.changed is False
    assert result.version_incompatible_mods == ["local::needs_062_plus"]
    assert active_mods.active_mods_ids == []


def test_enforce_game_version_allows_compatible_mod(tmp_path):
    use_case, active_mods, config_service, game_root = (
        _make_use_case_with_versioned_mods(tmp_path)
    )
    # Game is version 1.100 — exactly what "needs_100" requires
    _write_fake_exe(game_root, 1, 100)
    config_service.get_config().enforce_game_version = True

    result = use_case.activate_mods(["needs_100"])

    assert result.changed is True
    assert result.version_incompatible_mods == []
    assert "needs_100" in active_mods.active_mods_ids


def test_enforce_game_version_allows_mod_with_no_version_constraint(tmp_path):
    use_case, active_mods, config_service, game_root = (
        _make_use_case_with_versioned_mods(tmp_path)
    )
    _write_fake_exe(game_root, 1, 50)  # very old game
    config_service.get_config().enforce_game_version = True

    result = use_case.activate_mods(["no_version"])

    assert result.changed is True
    assert result.version_incompatible_mods == []


def test_enforce_game_version_inline_range_blocks_too_new(tmp_path):
    use_case, active_mods, config_service, game_root = (
        _make_use_case_with_versioned_mods(tmp_path)
    )
    # Game 1.961 exceeds the inline range 1.062 – 1.960
    _write_fake_exe(game_root, 1, 961)
    config_service.get_config().enforce_game_version = True

    result = use_case.activate_mods(["inline_range"])

    assert result.changed is False
    assert result.version_incompatible_mods == ["local::inline_range"]


def test_enforce_game_version_disabled_allows_all(tmp_path):
    use_case, active_mods, config_service, game_root = (
        _make_use_case_with_versioned_mods(tmp_path)
    )
    _write_fake_exe(game_root, 1, 50)  # outdated game
    # Enforcement is OFF by default — incompatible mods should still activate.
    assert config_service.get_config().enforce_game_version is False

    result = use_case.activate_mods(["needs_062_plus"])

    assert result.changed is True
    assert result.version_incompatible_mods == []


def test_enforce_game_version_skipped_when_exe_missing(tmp_path):
    use_case, active_mods, config_service, game_root = (
        _make_use_case_with_versioned_mods(tmp_path)
    )
    # Do NOT write the fake exe — version undetectable.
    config_service.get_config().enforce_game_version = True

    # Should fall through and activate normally.
    result = use_case.activate_mods(["needs_062_plus"])

    assert result.changed is True
    assert result.version_incompatible_mods == []
