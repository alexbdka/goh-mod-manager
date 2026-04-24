import json
import logging
import os

from src.core.config import AppConfig
from src.core.exceptions import ConfigLoadError, ConfigWriteError
from src.utils import app_paths
from src.utils.file_utils import atomic_write_text

logger = logging.getLogger(__name__)


class ConfigService:
    """
    Load and persist application configuration independently from the UI layer.

    Configuration is stored as JSON and contains machine-local paths plus user
    preferences such as language, theme, font, presets, and onboarding state.
    """

    def __init__(self, config_path: str | None = None):
        if config_path is None:
            self.config_path = str(app_paths.get_config_file_path())
        else:
            self.config_path = config_path
        self._config: AppConfig | None = None

    def get_config(self) -> AppConfig:
        """Return the cached config, loading it from disk on first access."""
        if self._config is None:
            self.load()
        config = self._config
        if config is None:
            raise ConfigLoadError(self.config_path, "Configuration failed to load.")
        return config

    def load(self) -> AppConfig:
        """Load configuration from disk, or return a default config if missing."""
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

            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ConfigLoadError(
                    self.config_path, "Configuration root must be a JSON object."
                )

            self._config.game_path = data.get("game_path")
            self._config.workshop_path = data.get("workshop_path")
            self._config.profile_path = data.get("profile_path")
            self._config.presets = data.get("presets", {})
            self._config.language = data.get("language", "en_US")
            self._config.theme = data.get("theme", "auto")
            self._config.font = data.get("font", "Inter")
            self._config.onboarding_seen = bool(data.get("onboarding_seen", False))

            logger.info(f"Configuration loaded from {self.config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse config file {self.config_path}: {e}")
            raise ConfigLoadError(self.config_path, str(e)) from e
        except ConfigLoadError:
            raise
        except Exception as e:
            logger.error(f"Error loading config file {self.config_path}: {e}")
            raise ConfigLoadError(self.config_path, str(e)) from e

        return self._config

    def save(self, config: AppConfig | None = None) -> None:
        """Persist the provided config, or the cached config when omitted."""
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
            "onboarding_seen": self._config.onboarding_seen,
        }

        try:
            atomic_write_text(self.config_path, json.dumps(data, indent=4))

            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {self.config_path}: {e}")
            raise ConfigWriteError(self.config_path, str(e)) from e

    def update_paths(
        self,
        game_path: str | None = None,
        workshop_path: str | None = None,
        profile_path: str | None = None,
        language: str | None = None,
        theme: str | None = None,
        font: str | None = None,
        onboarding_seen: bool | None = None,
    ) -> None:
        """Update selected config fields and save only when something changed."""
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

        if onboarding_seen is not None and config.onboarding_seen != onboarding_seen:
            config.onboarding_seen = onboarding_seen
            modified = True

        if modified:
            self.save()

    def set_onboarding_seen(self, seen: bool) -> None:
        """Store whether the first-run interface tour has already been completed."""
        config = self.get_config()
        if config.onboarding_seen == seen:
            return

        config.onboarding_seen = seen
        self.save()
