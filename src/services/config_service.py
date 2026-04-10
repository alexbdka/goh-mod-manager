import json
import logging
import os
from typing import Optional

from src.core.config import AppConfig
from src.utils import app_paths
from src.utils.file_utils import atomic_write_text

logger = logging.getLogger(__name__)


class ConfigService:
    """
    Manages the application's configuration independently of any UI framework.
    Stores user preferences and game paths in a portable JSON format.
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            self.config_path = str(app_paths.get_config_file_path())
        else:
            self.config_path = config_path
        self._config: Optional[AppConfig] = None

    def get_config(self) -> AppConfig:
        """
        Returns the current configuration. Loads it from disk if not already loaded.
        """
        if self._config is None:
            self.load()
        return self._config

    def load(self) -> AppConfig:
        """
        Loads the configuration from the JSON file.
        If the file doesn't exist, returns an empty default config.
        """
        self._config = AppConfig()

        if not os.path.exists(self.config_path):
            logger.info(f"Config file not found at {self.config_path}. Using defaults.")
            return self._config

        try:
            if os.path.getsize(self.config_path) == 0:
                logger.debug(
                    f"Config file {self.config_path} is empty. Using defaults."
                )
                return self._config

            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._config.game_path = data.get("game_path")
            self._config.workshop_path = data.get("workshop_path")
            self._config.profile_path = data.get("profile_path")
            self._config.presets = data.get("presets", {})
            self._config.language = data.get("language", "en_US")
            self._config.theme = data.get("theme", "auto")
            self._config.font = data.get("font", "Inter")

            logger.info(f"Configuration loaded from {self.config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file {self.config_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading config file {self.config_path}: {e}")

        return self._config

    def save(self, config: Optional[AppConfig] = None) -> None:
        """
        Saves the provided configuration (or the currently cached one) to the JSON file.
        """
        if config is not None:
            self._config = config

        if self._config is None:
            logger.warning("No configuration to save.")
            return

        data = {
            "game_path": self._config.game_path,
            "workshop_path": self._config.workshop_path,
            "profile_path": self._config.profile_path,
            "presets": self._config.presets,
            "language": self._config.language,
            "theme": self._config.theme,
            "font": self._config.font,
        }

        try:
            atomic_write_text(self.config_path, json.dumps(data, indent=4))

            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}")

    def update_paths(
        self,
        game_path: Optional[str] = None,
        workshop_path: Optional[str] = None,
        profile_path: Optional[str] = None,
        language: Optional[str] = None,
        theme: Optional[str] = None,
        font: Optional[str] = None,
    ) -> None:
        """
        Utility method to update specific paths and auto-save.
        """
        config = self.get_config()
        modified = False

        if game_path is not None and config.game_path != game_path:
            config.game_path = game_path
            modified = True

        if workshop_path is not None and config.workshop_path != workshop_path:
            config.workshop_path = workshop_path
            modified = True

        if profile_path is not None and config.profile_path != profile_path:
            config.profile_path = profile_path
            modified = True

        if language is not None and config.language != language:
            config.language = language
            modified = True

        if theme is not None and config.theme != theme:
            config.theme = theme
            modified = True

        if font is not None and config.font != font:
            config.font = font
            modified = True

        if modified:
            self.save()
