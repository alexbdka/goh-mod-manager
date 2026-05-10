import json
import os
import shutil
import tempfile
from typing import Any

import pytest
from src.core.config import AppConfig
from src.core.exceptions import ConfigLoadError, ConfigWriteError
from src.services.config_service import ConfigService
from src.utils import app_paths


class TestConfigService:
    def setup_method(self):
        # Create a temporary file path for the config
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.config_path = self.temp_file.name
        self.temp_file.close()

        # Remove it so we can test the "file not found" creation logic
        os.remove(self.config_path)

        self.service = ConfigService(config_path=self.config_path)

    def teardown_method(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def test_load_nonexistent_file(self):
        config = self.service.get_config()
        assert config.game_path is None
        assert config.workshop_path is None
        assert config.profile_path is None

    def test_save_and_load(self):
        config = AppConfig(
            game_path="C:/Games/GoH",
            workshop_path="C:/Steam/workshop",
            profile_path="C:/Users/test/Documents/My Games/GoH/profiles/options.set",
        )
        self.service.save(config)

        assert os.path.exists(self.config_path)

        # Create a new service instance to force a fresh load from disk
        new_service = ConfigService(config_path=self.config_path)
        loaded_config = new_service.get_config()

        assert loaded_config.game_path == "C:/Games/GoH"
        assert loaded_config.workshop_path == "C:/Steam/workshop"
        assert (
            loaded_config.profile_path
            == "C:/Users/test/Documents/My Games/GoH/profiles/options.set"
        )
        assert loaded_config.onboarding_seen is False

    def test_update_paths(self):
        self.service.get_config()

        # Update one path
        self.service.update_paths(
            game_path="D:/SteamLibrary/steamapps/common/Call to Arms"
        )

        config = self.service.get_config()
        assert config.game_path == "D:/SteamLibrary/steamapps/common/Call to Arms"
        assert config.workshop_path is None

        # Check if it was actually saved to disk
        with open(self.config_path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["game_path"] == "D:/SteamLibrary/steamapps/common/Call to Arms"

        # Update another path
        self.service.update_paths(
            workshop_path="D:/SteamLibrary/steamapps/workshop/content/400750"
        )
        config = self.service.get_config()
        assert (
            config.workshop_path == "D:/SteamLibrary/steamapps/workshop/content/400750"
        )

    def test_set_onboarding_seen_persists_flag(self):
        self.service.set_onboarding_seen(True)

        new_service = ConfigService(config_path=self.config_path)
        loaded_config = new_service.get_config()

        assert loaded_config.onboarding_seen is True

    def test_default_config_path_uses_app_paths(self, monkeypatch):
        expected_path = app_paths.Path("X:/workspace/config.json")
        monkeypatch.setattr(app_paths, "get_config_file_path", lambda: expected_path)

        service = ConfigService()

        assert app_paths.Path(service.config_path) == expected_path

    def test_invalid_json_raises_load_error(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("{invalid")

        with pytest.raises(ConfigLoadError):
            self.service.load()

    def test_save_failure_raises_write_error(self, monkeypatch):
        def fail_write(*_args, **_kwargs):
            raise OSError("disk full")

        monkeypatch.setattr("src.services.config_service.atomic_write_text", fail_write)

        with pytest.raises(ConfigWriteError):
            self.service.save(AppConfig(game_path="C:/Games/GoH"))

    def test_empty_file_migrates_selected_legacy_qsettings_fields(self, monkeypatch):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("")

        class FakeQSettings:
            def __init__(self, _organization, _application):
                self._values = {
                    "game_directory": "C:/Legacy/Game",
                    "mods_directory": "C:/Legacy/Workshop",
                    "options_file": "C:/Legacy/Profile/options.set",
                    "presets": '{"Main":[101, "202"], "Skirmish":"[\\"303\\", 404]"}',
                    "language": "fr_FR",
                    "font": "LegacyFont",
                }

            def value(self, key, default=None):
                return self._values.get(key, default)

        monkeypatch.setattr("src.services.config_service.QSettings", FakeQSettings)
        self.service._allow_legacy_migration = True

        loaded = self.service.load()

        assert loaded.game_path == "C:/Legacy/Game"
        assert loaded.workshop_path == "C:/Legacy/Workshop"
        assert loaded.profile_path == "C:/Legacy/Profile/options.set"
        assert loaded.presets == {"Main": ["101", "202"], "Skirmish": ["303", "404"]}
        assert loaded.language == "en_US"
        assert loaded.font == "Inter"

        reloaded = ConfigService(config_path=self.config_path).get_config()
        assert reloaded.game_path == "C:/Legacy/Game"
        assert reloaded.workshop_path == "C:/Legacy/Workshop"
        assert reloaded.profile_path == "C:/Legacy/Profile/options.set"
        assert reloaded.presets == {"Main": ["101", "202"], "Skirmish": ["303", "404"]}

    def test_effectively_empty_json_payload_triggers_legacy_migration(
        self, monkeypatch
    ):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump({"presets": {}}, f)

        class FakeQSettings:
            def __init__(self, _organization, _application):
                self._values = {
                    "game_directory": "C:/Legacy/Game",
                    "mods_directory": "C:/Legacy/Workshop",
                    "options_file": "C:/Legacy/Profile/options.set",
                    "presets": {"Main": ["111", 222]},
                }

            def value(self, key, default=None):
                return self._values.get(key, default)

        monkeypatch.setattr("src.services.config_service.QSettings", FakeQSettings)
        self.service._allow_legacy_migration = True

        loaded = self.service.load()

        assert loaded.game_path == "C:/Legacy/Game"
        assert loaded.workshop_path == "C:/Legacy/Workshop"
        assert loaded.profile_path == "C:/Legacy/Profile/options.set"
        assert loaded.presets == {"Main": ["111", "222"]}

    def test_missing_file_triggers_legacy_migration(self, monkeypatch):
        class FakeQSettings:
            def __init__(self, _organization, _application):
                self._values = {
                    "game_directory": "C:/Legacy/Game",
                    "mods_directory": "C:/Legacy/Workshop",
                    "options_file": "C:/Legacy/Profile/options.set",
                    "presets": {"Campaign": ["9001"]},
                }

            def value(self, key, default=None):
                return self._values.get(key, default)

        monkeypatch.setattr("src.services.config_service.QSettings", FakeQSettings)
        self.service._allow_legacy_migration = True

        loaded = self.service.get_config()

        assert loaded.game_path == "C:/Legacy/Game"
        assert loaded.workshop_path == "C:/Legacy/Workshop"
        assert loaded.profile_path == "C:/Legacy/Profile/options.set"
        assert loaded.presets == {"Campaign": ["9001"]}

    def test_qsettings_roundtrip_payload_is_migrated(self, monkeypatch):
        from PySide6.QtCore import QSettings

        qsettings_cls: Any = QSettings
        ini_format = qsettings_cls.IniFormat
        user_scope = qsettings_cls.UserScope
        native_format = qsettings_cls.NativeFormat

        settings_dir = tempfile.mkdtemp()
        try:
            qsettings_cls.setDefaultFormat(ini_format)
            qsettings_cls.setPath(ini_format, user_scope, settings_dir)

            writer = qsettings_cls("alex6", "GoH Mod Manager")
            writer.clear()
            writer.setValue("presets", {"Main": ["123", 456]})
            writer.sync()

            class QtSettingsBacked:
                def __init__(self, organization, application):
                    self._settings = qsettings_cls(organization, application)

                def value(self, key, default=None):
                    return self._settings.value(key, default)

            monkeypatch.setattr(
                "src.services.config_service.QSettings", QtSettingsBacked
            )
            self.service._allow_legacy_migration = True

            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write("")

            loaded = self.service.get_config()
            assert loaded.presets == {"Main": ["123", "456"]}
        finally:
            qsettings_cls.setDefaultFormat(native_format)
            shutil.rmtree(settings_dir, ignore_errors=True)

    def test_migration_reads_legacy_single_identity(self, monkeypatch):
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("")

        class FakeQSettings:
            def __init__(self, organization, application):
                assert organization == "alex6"
                assert application == "GoH Mod Manager"

            def value(self, key, default=None):
                if key == "presets":
                    return {"LegacyPreset": ["42"]}
                return default

        monkeypatch.setattr("src.services.config_service.QSettings", FakeQSettings)
        self.service._allow_legacy_migration = True

        loaded = self.service.get_config()

        assert loaded.presets == {"LegacyPreset": ["42"]}
