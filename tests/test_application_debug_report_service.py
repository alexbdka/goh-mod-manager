from src.application.debug_report_service import ApplicationDebugReportService
from src.application.query_service import ApplicationQueryService
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.preset_service import PresetService


def _make_service(tmp_path):
    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.game_path = "C:/game"
    config.workshop_path = "C:/workshop"
    config.profile_path = "C:/profile/options.set"

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        "local_mod": ModInfo(id="local_mod", name="Local Mod", desc="", isLocal=True)
    }
    catalogue._workshop_mods = {
        "workshop_mod": ModInfo(
            id="workshop_mod", name="Workshop Mod", desc="", isLocal=False
        )
    }

    active_mods = ActiveModsService(catalogue)
    active_mods.active_mods_ids = ["workshop_mod", "local_mod"]

    preset_service = PresetService(config_service, catalogue, active_mods)
    query_service = ApplicationQueryService(
        config_service, catalogue, active_mods, preset_service
    )
    return ApplicationDebugReportService(query_service)


def test_build_report_includes_configuration_and_active_mods(tmp_path, monkeypatch):
    service = _make_service(tmp_path)
    log_path = tmp_path / "app.log"
    log_path.write_text("line1\nline2\n", encoding="utf-8")

    monkeypatch.setattr(
        "src.application.debug_report_service.app_paths.read_version",
        lambda: "2.0.0-test",
    )
    monkeypatch.setattr(
        "src.application.debug_report_service.app_paths.get_log_file_path",
        lambda: log_path,
    )

    report = service.build_report()

    assert "App Version: 2.0.0-test" in report
    assert "Game Path: C:/game" in report
    assert "Total Installed Mods: 2" in report
    assert "Local Mods: 1" in report
    assert "Workshop Mods: 1" in report
    assert "1. Workshop Mod (ID: workshop_mod) - Workshop" in report
    assert "2. Local Mod (ID: local_mod) - Local" in report
    assert "line1" in report
    assert "line2" in report


def test_build_report_handles_missing_log_file(tmp_path, monkeypatch):
    service = _make_service(tmp_path)
    missing_log = tmp_path / "missing.log"

    monkeypatch.setattr(
        "src.application.debug_report_service.app_paths.read_version",
        lambda: "2.0.0-test",
    )
    monkeypatch.setattr(
        "src.application.debug_report_service.app_paths.get_log_file_path",
        lambda: missing_log,
    )

    report = service.build_report()

    assert "No log file found." in report
