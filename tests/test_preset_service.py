import os
import tempfile

import pytest

from src.core.config import AppConfig
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.preset_service import PresetService


class TestPresetService:
    def setup_method(self):
        # Create a temporary config file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.config_path = self.temp_file.name
        self.temp_file.close()

        self.config_service = ConfigService(config_path=self.config_path)

        # Mock Catalogue
        self.catalogue = ModsCatalogueService()
        self.catalogue._local_mods = {
            "mod_1": ModInfo(id="mod_1", name="Mod 1", desc="", isLocal=True),
            "mod_2": ModInfo(id="mod_2", name="Mod 2", desc="", isLocal=True),
            "mod_3": ModInfo(id="mod_3", name="Mod 3", desc="", isLocal=True),
        }

        # Setup Active Mods
        self.active_mods = ActiveModsService(self.catalogue)

        # Init PresetService
        self.preset_service = PresetService(
            self.config_service, self.catalogue, self.active_mods
        )

    def teardown_method(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_save_and_get_preset(self):
        # Save a preset explicitly
        self.preset_service.save_preset("TestPreset", ["mod_1", "mod_3"])

        # Check if it was saved
        presets = self.preset_service.get_all_presets()
        assert "TestPreset" in presets
        assert presets["TestPreset"] == ["mod_1", "mod_3"]

        # Check retrieval
        preset_data = self.preset_service.get_preset("TestPreset")
        assert preset_data == ["mod_1", "mod_3"]

    def test_save_from_active_mods(self):
        self.active_mods.activate_mod("mod_2")
        self.active_mods.activate_mod("mod_1")

        # Save without passing a list (should use active mods)
        self.preset_service.save_preset("ActivePreset")

        preset_data = self.preset_service.get_preset("ActivePreset")
        assert preset_data == ["mod_2", "mod_1"]

    def test_delete_preset(self):
        self.preset_service.save_preset("ToDelete", ["mod_1"])
        assert self.preset_service.delete_preset("ToDelete")
        assert self.preset_service.get_preset("ToDelete") is None
        assert not self.preset_service.delete_preset("NonExistent")

    def test_apply_preset(self):
        self.preset_service.save_preset("ApplyMe", ["mod_3", "mod_2"])

        # Initially active
        self.active_mods.activate_mod("mod_1")
        assert len(self.active_mods.active_mods_ids) == 1

        # Apply
        success, missing = self.preset_service.apply_preset("ApplyMe")
        assert success
        assert len(missing) == 0

        # Check if active mods were fully replaced and ordered correctly
        assert self.active_mods.active_mods_ids == ["mod_3", "mod_2"]

    def test_apply_preset_resolves_installed_dependencies(self):
        self.catalogue._local_mods["dep_mod"] = ModInfo(
            id="dep_mod", name="Dependency", desc="", isLocal=True
        )
        self.catalogue._local_mods["main_mod"] = ModInfo(
            id="main_mod",
            name="Main Mod",
            desc="",
            dependencies=["dep_mod"],
            isLocal=True,
        )
        self.preset_service.save_preset("WithDeps", ["main_mod"])

        success, missing = self.preset_service.apply_preset("WithDeps")

        assert success
        assert missing == []
        assert self.active_mods.active_mods_ids == ["dep_mod", "main_mod"]

    def test_apply_preset_with_missing_mods(self):
        # Save a preset with a mod that isn't in our mock catalogue
        self.preset_service.save_preset("MissingModPreset", ["mod_1", "ghost_mod"])

        success, missing = self.preset_service.apply_preset("MissingModPreset")
        assert success
        assert len(missing) == 1
        assert missing[0] == "ghost_mod"

        # Only the valid mod should have been applied
        assert self.active_mods.active_mods_ids == ["mod_1"]
