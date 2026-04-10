from pathlib import Path

import pytest

from src.core.exceptions import ProfileWriteError
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.mods_catalogue_service import ModsCatalogueService


def test_save_to_profile_raises_profile_write_error_on_atomic_write_failure(
    monkeypatch, tmp_path: Path
):
    profile_path = tmp_path / "options.set"
    profile_path.write_text("{options\n\t{mods}\n}\n", encoding="utf-8")

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        "12345": ModInfo(id="12345", name="Test", desc="", isLocal=False)
    }
    service = ActiveModsService(catalogue)
    service.active_mods_ids = ["12345"]

    def fail_atomic_write(_path, _content, encoding="utf-8"):
        raise OSError("file is locked")

    monkeypatch.setattr(
        "src.services.active_mods_service.atomic_write_text", fail_atomic_write
    )

    with pytest.raises(ProfileWriteError, match="file is locked"):
        service.save_to_profile(str(profile_path), catalogue_service=catalogue)
