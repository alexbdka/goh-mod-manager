from unittest.mock import MagicMock

from src.core.config import AppConfig
from src.core.events import EventType
from src.core.manager import ModManager
from src.core.mod import ModInfo


class TestModManager:
    def test_import_mod_skips_reload_when_requested(self):
        manager = ModManager()
        manager.config_service.get_config = MagicMock(
            return_value=AppConfig(game_path="C:/Games/GoH")
        )
        manager.mod_import_service.import_mod = MagicMock(return_value=True)
        manager.reload = MagicMock()

        success = manager.import_mod("archive.zip", reload_on_success=False)

        assert success is True
        manager.reload.assert_not_called()

    def test_import_mod_reloads_on_success_by_default(self):
        manager = ModManager()
        manager.config_service.get_config = MagicMock(
            return_value=AppConfig(game_path="C:/Games/GoH")
        )
        manager.mod_import_service.import_mod = MagicMock(return_value=True)
        manager.reload = MagicMock()

        success = manager.import_mod("archive.zip")

        assert success is True
        manager.reload.assert_called_once()

    def test_import_share_code_resolves_installed_dependencies(self):
        manager = ModManager()
        manager.apply_changes = MagicMock()
        manager.events.emit = MagicMock()
        manager.catalogue._local_mods = {
            "dep_mod": ModInfo(id="dep_mod", name="Dependency", desc="", isLocal=True),
            "main_mod": ModInfo(
                id="main_mod",
                name="Main Mod",
                desc="",
                dependencies=["dep_mod"],
                isLocal=True,
            ),
        }

        code = manager.share_code_service.encode(
            [manager.catalogue.get_mod("main_mod")]
        )

        success, missing = manager.import_share_code(code)

        assert success is True
        assert missing == []
        assert manager.active_mods.active_mods_ids == ["dep_mod", "main_mod"]

    def test_import_share_code_reports_missing_dependencies(self):
        manager = ModManager()
        manager.apply_changes = MagicMock()
        manager.events.emit = MagicMock()
        manager.catalogue._local_mods = {
            "main_mod": ModInfo(
                id="main_mod",
                name="Main Mod",
                desc="",
                dependencies=["missing_dep"],
                isLocal=True,
            ),
        }

        code = manager.share_code_service.encode(
            [manager.catalogue.get_mod("main_mod")]
        )

        success, missing = manager.import_share_code(code)

        assert success is True
        assert missing == [{"id": "missing_dep", "name": "missing_dep"}]
        assert manager.active_mods.active_mods_ids == ["main_mod"]

    def test_subscribe_and_unsubscribe_proxy_event_bus(self):
        manager = ModManager()
        callback = MagicMock()

        manager.subscribe(EventType.CATALOGUE_CHANGED, callback)
        manager.events.emit(EventType.CATALOGUE_CHANGED)
        callback.assert_called_once()

        manager.unsubscribe(EventType.CATALOGUE_CHANGED, callback)
        manager.events.emit(EventType.CATALOGUE_CHANGED)
        callback.assert_called_once()
