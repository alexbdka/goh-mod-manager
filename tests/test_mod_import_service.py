from pathlib import Path

from goh_mod_manager.services.mod_import_service import ModImportService


def _create_mod_dir(base: Path, mod_id: str) -> Path:
    mod_dir = base / mod_id
    mod_dir.mkdir(parents=True, exist_ok=True)
    (mod_dir / "mod.info").write_text('{name "Test Mod"}\n', encoding="utf-8")
    return mod_dir


def test_import_mod_from_directory(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    _create_mod_dir(source_dir, "123")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    service = ModImportService()
    success = service.import_mod(str(source_dir), str(dest_dir))

    assert success is True
    assert (dest_dir / "123" / "mod.info").exists()
