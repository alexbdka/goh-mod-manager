import os
import tempfile

from src.services.mods_catalogue_service import ModsCatalogueService


class TestModsCatalogueService:
    def setup_method(self):
        self.service = ModsCatalogueService()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.local_path = os.path.join(self.temp_dir.name, "local")
        self.workshop_path = os.path.join(self.temp_dir.name, "workshop")

        os.makedirs(self.local_path)
        os.makedirs(self.workshop_path)

    def teardown_method(self):
        self.temp_dir.cleanup()

    def _create_mock_mod(self, base_path, mod_id, name="Test Mod"):
        mod_dir = os.path.join(base_path, mod_id)
        os.makedirs(mod_dir)
        info_path = os.path.join(mod_dir, "mod.info")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(f'{{mod {{name "{name}"}} {{desc "Test Description"}} }}')
        return mod_dir

    def test_load_catalogue_empty(self):
        self.service.load_catalogue(self.local_path, self.workshop_path)
        assert len(self.service.all_mods) == 0
        assert len(self.service.local_mods) == 0
        assert len(self.service.workshop_mods) == 0

    def test_load_catalogue_with_mods(self):
        self._create_mock_mod(self.local_path, "local_mod_1", "Local 1")
        self._create_mock_mod(self.workshop_path, "12345", "Workshop 1")
        self._create_mock_mod(self.workshop_path, "67890", "Workshop 2")

        self.service.load_catalogue(self.local_path, self.workshop_path)

        assert len(self.service.all_mods) == 3
        assert len(self.service.local_mods) == 1
        assert len(self.service.workshop_mods) == 2

        local_mod = self.service.get_mod("local_mod_1")
        assert local_mod is not None
        assert local_mod.name == "Local 1"
        assert local_mod.isLocal

        workshop_mod = self.service.get_mod("12345")
        assert workshop_mod is not None
        assert workshop_mod.name == "Workshop 1"
        assert not workshop_mod.isLocal

    def test_get_mod_not_found(self):
        self.service.load_catalogue(self.local_path, self.workshop_path)
        mod = self.service.get_mod("non_existent_mod")
        assert mod is None
