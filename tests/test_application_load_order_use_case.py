import pytest
from src.application.use_cases import ApplicationLoadOrderUseCase
from src.core.exceptions import ProfileWriteError
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService


def _make_use_case(tmp_path):
    config_service = ConfigService(config_path=str(tmp_path / "config.json"))
    config = config_service.get_config()
    config.profile_path = str(tmp_path / "options.set")
    (tmp_path / "options.set").write_text("{options\n\t{mods}\n}\n", encoding="utf-8")

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        "dep": ModInfo(id="dep", name="Dependency", desc="", isLocal=True),
        "main": ModInfo(
            id="main", name="Main", desc="", dependencies=["dep"], isLocal=True
        ),
        "other": ModInfo(id="other", name="Other", desc="", isLocal=True),
    }

    active_mods = ActiveModsService(catalogue)
    use_case = ApplicationLoadOrderUseCase(
        active_mods,
        catalogue,
        config_service,
    )
    return use_case, active_mods


def test_activate_mods_resolves_dependencies_and_persists_once(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)

    result = use_case.activate_mods(["main"])

    assert result.changed is True
    assert result.activated_mod_ids == ["main"]
    assert result.missing_dependencies == []
    assert active_mods.active_mods_ids == ["dep", "main"]


def test_deactivate_mod_reports_no_change_when_mod_is_not_active(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)

    result = use_case.deactivate_mod("ghost")

    assert result.changed is False
    assert result.active_mod_ids == active_mods.active_mods_ids


def test_move_and_reorder_return_changed_state(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    active_mods.active_mods_ids = ["dep", "main", "other"]

    move_result = use_case.move_down("dep")
    assert move_result.changed is True
    assert active_mods.active_mods_ids == ["main", "dep", "other"]

    reorder_result = use_case.reorder(["other", "main", "dep"])
    assert reorder_result.changed is True
    assert active_mods.active_mods_ids == ["other", "main", "dep"]


def test_clear_returns_changed_only_when_needed(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)

    empty_result = use_case.clear()
    assert empty_result.changed is False

    active_mods.active_mods_ids = ["dep", "main"]
    clear_result = use_case.clear()
    assert clear_result.changed is True
    assert active_mods.active_mods_ids == []


def test_mutating_load_order_requires_profile_path(tmp_path):
    use_case, active_mods = _make_use_case(tmp_path)
    use_case._config_service.get_config().profile_path = None

    with pytest.raises(ProfileWriteError):
        use_case.activate_mods(["main"])

    assert active_mods.active_mods_ids == []
