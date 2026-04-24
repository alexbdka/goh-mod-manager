import os
import tarfile
import tempfile
import zipfile

import pytest
from src.core.exceptions import (
    ArchiveExtractionError,
    InvalidModPathError,
    ModInfoNotFoundError,
)
from src.services.mod_import_service import ModImportService


class TestModImportService:
    def setup_method(self):
        self.service = ModImportService()
        self.test_dir = tempfile.TemporaryDirectory()
        self.game_mods_dir = os.path.join(self.test_dir.name, "mods")
        os.makedirs(self.game_mods_dir)

    def teardown_method(self):
        self.test_dir.cleanup()

    def test_import_invalid_directory(self):
        with pytest.raises(InvalidModPathError):
            self.service.import_mod("non_existent_path", self.game_mods_dir)

    def test_import_from_directory(self):
        # Create a mock mod directory structure
        mod_source = os.path.join(self.test_dir.name, "source_mod")
        os.makedirs(mod_source)

        # Valid mod (contains mod.info)
        with open(os.path.join(mod_source, "mod.info"), "w") as f:
            f.write('{mod {name "Test Mod"}}')

        success = self.service.import_mod(mod_source, self.game_mods_dir)
        assert success

        # Verify it was copied
        expected_dest = os.path.join(self.game_mods_dir, "source_mod")
        assert os.path.exists(expected_dest)
        assert os.path.exists(os.path.join(expected_dest, "mod.info"))

    def test_import_from_directory_no_mod_info(self):
        mod_source = os.path.join(self.test_dir.name, "empty_mod")
        os.makedirs(mod_source)

        with pytest.raises(ModInfoNotFoundError):
            self.service.import_mod(mod_source, self.game_mods_dir)

        assert not os.path.exists(os.path.join(self.game_mods_dir, "empty_mod"))

    def test_overwrite_failure_preserves_existing_mod(self, monkeypatch):
        mod_source = os.path.join(self.test_dir.name, "existing_mod")
        os.makedirs(mod_source)
        with open(os.path.join(mod_source, "mod.info"), "w", encoding="utf-8") as f:
            f.write('{mod {name "New"}}')

        existing_dest = os.path.join(self.game_mods_dir, "existing_mod")
        os.makedirs(existing_dest)
        existing_info = os.path.join(existing_dest, "mod.info")
        with open(existing_info, "w", encoding="utf-8") as f:
            f.write('{mod {name "Old"}}')

        def fail_copy(*_args, **_kwargs):
            raise OSError("copy failed")

        monkeypatch.setattr("src.services.mod_import_service.shutil.copy2", fail_copy)

        with pytest.raises(OSError):
            self.service.import_mod(
                mod_source,
                self.game_mods_dir,
                conflict_callback=lambda _name: "overwrite",
            )

        assert os.path.exists(existing_dest)
        with open(existing_info, encoding="utf-8") as f:
            assert f.read() == '{mod {name "Old"}}'

    def test_import_from_zip(self):
        # Create a dummy zip file containing a mod
        zip_path = os.path.join(self.test_dir.name, "test_mod.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            # Add mod.info inside a subfolder to simulate realistic archives
            zf.writestr("CoolMod/mod.info", '{mod {name "Cool"}}')
            zf.writestr("CoolMod/resource/test.txt", "data")

        success = self.service.import_mod(zip_path, self.game_mods_dir)
        assert success

        expected_dest = os.path.join(self.game_mods_dir, "CoolMod")
        assert os.path.exists(expected_dest)
        assert os.path.exists(os.path.join(expected_dest, "mod.info"))
        assert os.path.exists(os.path.join(expected_dest, "resource/test.txt"))

    def test_import_from_zip_rejects_path_traversal(self):
        zip_path = os.path.join(self.test_dir.name, "unsafe_mod.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("../evil/mod.info", '{mod {name "Unsafe"}}')

        with pytest.raises(ArchiveExtractionError, match="unsafe path entry"):
            self.service.import_mod(zip_path, self.game_mods_dir)

    def test_import_from_tar_rejects_path_traversal(self):
        tar_path = os.path.join(self.test_dir.name, "unsafe_mod.tar")
        payload_path = os.path.join(self.test_dir.name, "payload_mod.info")
        with open(payload_path, "w", encoding="utf-8") as f:
            f.write('{mod {name "Unsafe"}}')

        with tarfile.open(tar_path, "w") as tf:
            tf.add(payload_path, arcname="../evil/mod.info")

        with pytest.raises(ArchiveExtractionError, match="unsafe path entry"):
            self.service.import_mod(tar_path, self.game_mods_dir)
