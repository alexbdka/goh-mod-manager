from src.application.settings_service import ApplicationSettingsService
from src.application.state import SettingsState
from src.services.config_service import ConfigService


def test_apply_settings_returns_change_flags_and_updates_config(tmp_path):
    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.game_path = "C:/game"
    config.workshop_path = "C:/workshop"
    config.profile_path = "C:/profile/options.set"
    config.language = "en_US"
    config.theme = "dark"
    config.font = "Inter"

    service = ApplicationSettingsService(config_service)

    result = service.apply_settings(
        SettingsState(
            game_path="D:/game",
            workshop_path="C:/workshop",
            profile_path="D:/profile/options.set",
            language="fr_FR",
            theme="light",
            font="OpenDyslexic",
        )
    )

    assert result.path_changed is True
    assert result.language_changed is True
    assert result.appearance_changed is True

    updated = config_service.get_config()
    assert updated.game_path == "D:/game"
    assert updated.workshop_path == "C:/workshop"
    assert updated.profile_path == "D:/profile/options.set"
    assert updated.language == "fr_FR"
    assert updated.theme == "light"
    assert updated.font == "OpenDyslexic"


def test_apply_settings_reports_no_changes_when_state_is_identical(tmp_path):
    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.game_path = "C:/game"
    config.workshop_path = "C:/workshop"
    config.profile_path = "C:/profile/options.set"
    config.language = "en_US"
    config.theme = "dark"
    config.font = "Inter"

    service = ApplicationSettingsService(config_service)

    result = service.apply_settings(
        SettingsState(
            game_path="C:/game",
            workshop_path="C:/workshop",
            profile_path="C:/profile/options.set",
            language="en_US",
            theme="dark",
            font="Inter",
        )
    )

    assert result.path_changed is False
    assert result.language_changed is False
    assert result.appearance_changed is False
