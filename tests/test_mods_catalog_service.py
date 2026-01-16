from pathlib import Path

from goh_mod_manager.services.mods_catalog_service import ModsCatalogService


def _write_mod_info(mod_dir: Path, name: str, require: str = "") -> None:
    content = [
        f'{{name "{name}"}}',
        '{desc "Test description"}',
        '{minGameVersion "1.0.0"}',
        '{maxGameVersion "2.0.0"}',
    ]
    if require:
        content.append(f'{{require "{require}"}}')

    mod_info = mod_dir / "mod.info"
    mod_info.write_text("\n".join(content) + "\n", encoding="utf-8")


def test_scan_installed_mods_across_directories(tmp_path: Path) -> None:
    mods_dir = tmp_path / "mods"
    game_mods_dir = tmp_path / "game_mods"
    mods_dir.mkdir()
    game_mods_dir.mkdir()

    mod_a = mods_dir / "111"
    mod_a.mkdir()
    _write_mod_info(mod_a, "Mod A", require="mod_222")

    mod_b = game_mods_dir / "222"
    mod_b.mkdir()
    _write_mod_info(mod_b, "Mod B")
    (mod_b / ".imported_by_mod_manager").write_text(
        "Imported by Mod Manager", encoding="utf-8"
    )

    service = ModsCatalogService()
    mods = service.scan_installed_mods(str(mods_dir), str(game_mods_dir))
    mods_by_id = {mod.id: mod for mod in mods}

    assert set(mods_by_id.keys()) == {"111", "222"}
    assert mods_by_id["111"].require == "222"
    assert mods_by_id["222"].manualInstall is True


def test_resolve_active_mods_keeps_order(tmp_path: Path) -> None:
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()

    mod_a = mods_dir / "111"
    mod_a.mkdir()
    _write_mod_info(mod_a, "Mod A")

    mod_b = mods_dir / "222"
    mod_b.mkdir()
    _write_mod_info(mod_b, "Mod B")

    service = ModsCatalogService()
    installed = service.scan_installed_mods(str(mods_dir), None)
    resolved = service.resolve_active_mods(["222", "111"], installed)

    assert [mod.id for mod in resolved] == ["222", "111"]
