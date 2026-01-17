from pathlib import Path

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.services.active_mods_service import ActiveModsService


def _make_mod(mod_id: str, manual: bool) -> Mod:
    return Mod(
        id=mod_id,
        name=f"Mod {mod_id}",
        desc="",
        minGameVersion="any",
        maxGameVersion="any",
        require="",
        folderPath=".",
        manualInstall=manual,
    )


def test_save_and_load_active_mods(tmp_path: Path) -> None:
    options_file = tmp_path / "options.set"
    options_file.write_text("", encoding="utf-8")

    mods = [_make_mod("100", manual=False), _make_mod("200", manual=True)]
    service = ActiveModsService()

    assert service.save_active_mods(str(options_file), mods) is True
    mod_ids, invalid_entries = service.load_active_mod_ids(str(options_file))
    assert mod_ids == ["100", "200"]
    assert invalid_entries == []


def test_load_active_mods_missing_file_returns_empty(tmp_path: Path) -> None:
    service = ActiveModsService()
    missing_file = tmp_path / "missing.set"

    mod_ids, invalid_entries = service.load_active_mod_ids(str(missing_file))
    assert mod_ids == []
    assert invalid_entries == []
