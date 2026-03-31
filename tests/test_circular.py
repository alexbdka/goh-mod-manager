import pytest
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.mods_catalogue_service import ModsCatalogueService

class TestCircularDeps:
    def test_circular(self):
        cat = ModsCatalogueService()
        cat._local_mods["A"] = ModInfo(id="A", name="A", desc="", dependencies=["B"])
        cat._local_mods["B"] = ModInfo(id="B", name="B", desc="", dependencies=["A"])
        svc = ActiveModsService(cat)
        svc.activate_mod("A")
        print(svc.active_mods_ids)

