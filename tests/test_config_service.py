import json
import os
import tempfile

import pytest

from src.core.config import AppConfig
from src.services.config_service import ConfigService


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
        with open(self.config_path, "r", encoding="utf-8") as f:
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
