import pytest
from src.application.share_code_service import ApplicationShareCodeService
from src.core.exceptions import InvalidShareCodeError, ProfileWriteError
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.share_code_service import ShareCodeService


def _make_services(tmp_path):
    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.profile_path = str(tmp_path / "options.set")
    (tmp_path / "options.set").write_text("{options\n\t{mods}\n}\n", encoding="utf-8")

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        "dep": ModInfo(id="dep", name="Dependency", desc="", isLocal=True),
        "main": ModInfo(
            id="main", name="Main", desc="", isLocal=True, dependencies=["dep"]
        ),
    }

    active_mods = ActiveModsService(catalogue)
    share_code_service = ShareCodeService()
    app_service = ApplicationShareCodeService(
        share_code_service, active_mods, catalogue, config_service
    )
    return app_service, share_code_service, active_mods


def test_export_active_mods_returns_code_when_load_order_exists(tmp_path):
    app_service, _, active_mods = _make_services(tmp_path)
    active_mods.active_mods_ids = ["main", "dep"]

    result = app_service.export_active_mods()

    assert result.has_active_mods is True
    assert result.code


def test_export_active_mods_reports_empty_when_no_mods_are_active(tmp_path):
    app_service, _, _ = _make_services(tmp_path)

    result = app_service.export_active_mods()

    assert result.has_active_mods is False
    assert result.code == ""


def test_import_share_code_applies_found_mods_and_reports_missing_dependencies(
    tmp_path,
):
    app_service, share_code_service, active_mods = _make_services(tmp_path)
    code = share_code_service.encode([ModInfo(id="main", name="Main", desc="")])

    result = app_service.import_share_code(code)

    assert result.success is True
    assert result.missing_mods == []
    assert active_mods.active_mods_ids == ["dep", "main"]


def test_import_share_code_raises_on_invalid_code(tmp_path):
    app_service, _, _ = _make_services(tmp_path)

    with pytest.raises(InvalidShareCodeError):
        app_service.import_share_code("not-a-valid-code")


def test_import_share_code_requires_profile_path_before_mutating(tmp_path):
    app_service, share_code_service, active_mods = _make_services(tmp_path)
    app_service._config_service.get_config().profile_path = None
    code = share_code_service.encode([ModInfo(id="main", name="Main", desc="")])

    with pytest.raises(ProfileWriteError):
        app_service.import_share_code(code)

    assert active_mods.active_mods_ids == []
