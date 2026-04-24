from src.application.state import SettingsState, SettingsUpdateResult
from src.services.config_service import ConfigService


class ApplicationSettingsUseCase:
    """
    Applies settings changes and returns a neutral summary of what changed.
    """

    def __init__(self, config_service: ConfigService):
        self._config_service = config_service

    def apply(self, settings: SettingsState) -> SettingsUpdateResult:
        config = self._config_service.get_config()

        path_changed = any(
            [
                settings.game_path != config.game_path,
                settings.workshop_path != config.workshop_path,
                settings.profile_path != config.profile_path,
            ]
        )
        language_changed = settings.language != config.language
        appearance_changed = any(
            [
                settings.theme != config.theme,
                settings.font != config.font,
            ]
        )

        self._config_service.update_paths(
            game_path=settings.game_path,
            workshop_path=settings.workshop_path,
            profile_path=settings.profile_path,
            language=settings.language,
            theme=settings.theme,
            font=settings.font,
        )

        return SettingsUpdateResult(
            path_changed=path_changed,
            language_changed=language_changed,
            appearance_changed=appearance_changed,
        )
