from pathlib import Path

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.services.mod_files_service import ModFilesService


def _make_mod(mod_id: str) -> Mod:
    return Mod(
        id=mod_id,
        name=f"Mod {mod_id}",
        desc="",
        minGameVersion="any",
        maxGameVersion="any",
        require="",
        folderPath=".",
        manualInstall=False,
    )


def test_generate_help_file_creates_file(tmp_path: Path) -> None:
    options_file = tmp_path / "options.set"
    options_file.write_text("{mods\n}\n", encoding="utf-8")

    service = ModFilesService()
    success, result = service.generate_help_file(
        options_file=str(options_file),
        game_folder="C:/Game",
        mods_folder="C:/Mods",
        load_order=[_make_mod("1"), _make_mod("2")],
        output_dir=str(tmp_path),
    )

    assert success is True
    output_path = Path(result)
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "=== HELP FILE ===" in content
    assert "Mod 1" in content
