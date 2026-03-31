import os
import tempfile

import pytest

from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.mods_catalogue_service import ModsCatalogueService


class TestActiveModsService:
    def setup_method(self):
        # Create a real catalogue but inject fake mods for testing
        self.catalogue = ModsCatalogueService()
        self.catalogue._local_mods = {
            "A": ModInfo(id="A", name="Mod A", desc="", isLocal=True),
            "B": ModInfo(id="B", name="Mod B", desc="", isLocal=True),
            "C": ModInfo(id="C", name="Mod C", desc="", isLocal=True),
        }
        self.service = ActiveModsService(self.catalogue)

    def test_activate_and_deactivate_mod(self):
        assert len(self.service.active_mods_ids) == 0

        # Activate
        self.service.activate_mod("A")
        assert "A" in self.service.active_mods_ids
        assert len(self.service.active_mods_ids) == 1

        # Deactivate
        self.service.deactivate_mod("A")
        assert "A" not in self.service.active_mods_ids
        assert len(self.service.active_mods_ids) == 0

    def test_move_mod_up_and_down(self):
        self.service.activate_mod("A")
        self.service.activate_mod("B")
        self.service.activate_mod("C")

        # Initial order: A, B, C
        assert self.service.active_mods_ids == ["A", "B", "C"]

        # Move B up -> B, A, C
        self.service.move_mod_up("B")
        assert self.service.active_mods_ids == ["B", "A", "C"]

        # Move A down -> B, C, A
        self.service.move_mod_down("A")
        assert self.service.active_mods_ids == ["B", "C", "A"]

    def test_get_active_mods(self):
        self.service.activate_mod("A")
        self.service.activate_mod("C")

        active_mods = self.service.get_active_mods()
        assert len(active_mods) == 2
        assert active_mods[0].name == "Mod A"
        assert active_mods[1].name == "Mod C"

    def test_load_and_save_profile(self):
        # Create a temporary options.set file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".set", encoding="utf-8"
        ) as tf:
            tf.write(
                '{options\n\t{video {adapter "NVIDIA"}}\n\t{mods\n\t\t"mod_12345:0"\n\t}\n}'
            )
            temp_path = tf.name

        try:
            # Test Loading
            self.service.load_from_profile(temp_path)
            assert self.service.active_mods_ids == ["12345"]

            # Modify the active mods
            self.service.activate_mod("67890")

            # Test Saving
            self.service.save_to_profile(temp_path)

            # Read the file to ensure it was saved correctly and preserved other settings
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()

            assert '"mod_12345:0"' in content
            assert '"mod_67890:0"' in content
            assert "adapter" in content
            assert (
                '{video {adapter "NVIDIA"}}' in content
            )  # Verify we didn't wipe the file
        finally:
            os.remove(temp_path)

    def test_activate_with_dependencies(self):
        # Setup mods with dependencies
        self.catalogue._local_mods["Dep1"] = ModInfo(
            id="Dep1", name="Dependency 1", desc="", isLocal=True
        )
        self.catalogue._local_mods["Main"] = ModInfo(
            id="Main",
            name="Main Mod",
            desc="",
            dependencies=["Dep1", "MissingDep"],
            isLocal=True,
        )

        # Activate Main Mod
        missing = self.service.activate_mod("Main")

        # Check load order (Dep1 should be activated BEFORE Main)
        assert self.service.active_mods_ids == ["Dep1", "Main"]

        # Check missing dependencies
        assert missing == ["MissingDep"]
