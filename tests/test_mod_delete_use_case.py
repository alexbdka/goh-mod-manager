from src.application.use_cases.mod_delete import ApplicationModDeleteUseCase
from src.core.events import EventBus, EventType
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
    active_mods = ActiveModsService(catalogue)
    event_bus = EventBus()
    use_case = ApplicationModDeleteUseCase(
        active_mods, catalogue, config_service, event_bus
    )
    return use_case, catalogue, active_mods, event_bus


def test_delete_local_mod_removes_directory_and_catalogue_entry(tmp_path):
    use_case, catalogue, active_mods, event_bus = _make_use_case(tmp_path)
    mod_dir = tmp_path / "mods" / "local_mod"
    mod_dir.mkdir(parents=True)
    (mod_dir / "mod.info").write_text('{mod {name "Local Mod"}}', encoding="utf-8")

    catalogue._local_mods["local_mod"] = ModInfo(
        id="local_mod",
        name="Local Mod",
        desc="",
        isLocal=True,
        path=str(mod_dir),
    )

    events = []
    event_bus.subscribe(EventType.CATALOGUE_CHANGED, lambda: events.append("catalogue"))

    result = use_case.delete_local_mod("local_mod")

    assert result is True
    assert not mod_dir.exists()
    assert "local_mod" not in catalogue._local_mods
    assert events == ["catalogue"]


def test_delete_local_mod_deactivates_first_when_active(tmp_path):
    use_case, catalogue, active_mods, event_bus = _make_use_case(tmp_path)
    mod_dir = tmp_path / "mods" / "active_mod"
    mod_dir.mkdir(parents=True)
    (mod_dir / "mod.info").write_text('{mod {name "Active Mod"}}', encoding="utf-8")

    catalogue._local_mods["active_mod"] = ModInfo(
        id="active_mod",
        name="Active Mod",
        desc="",
        isLocal=True,
        path=str(mod_dir),
    )
    active_mods.activate_mod("active_mod")

    events = []
    event_bus.subscribe(EventType.ACTIVE_MODS_CHANGED, lambda: events.append("active"))
    event_bus.subscribe(EventType.CATALOGUE_CHANGED, lambda: events.append("catalogue"))

    result = use_case.delete_local_mod("active_mod")

    assert result is True
    assert "active_mod" not in active_mods.active_mods_ids
    assert not mod_dir.exists()
    assert events == ["active", "catalogue"]


def test_delete_local_mod_blocked_when_required_by_active_mod(tmp_path):
    use_case, catalogue, active_mods, event_bus = _make_use_case(tmp_path)

    dep_dir = tmp_path / "mods" / "dep_mod"
    dep_dir.mkdir(parents=True)
    (dep_dir / "mod.info").write_text('{mod {name "Dependency"}}', encoding="utf-8")

    main_dir = tmp_path / "mods" / "main_mod"
    main_dir.mkdir(parents=True)
    (main_dir / "mod.info").write_text(
        '{mod {name "Main"} {require "dep_mod"}}', encoding="utf-8"
    )

    catalogue._local_mods["dep_mod"] = ModInfo(
        id="dep_mod",
        name="Dependency",
        desc="",
        isLocal=True,
        path=str(dep_dir),
    )
    catalogue._local_mods["main_mod"] = ModInfo(
        id="main_mod",
        name="Main",
        desc="",
        dependencies=["dep_mod"],
        isLocal=True,
        path=str(main_dir),
    )

    active_mods.activate_mod("main_mod")

    result = use_case.delete_local_mod("dep_mod")

    assert result is False
    assert dep_dir.exists()
    assert "dep_mod" in catalogue._local_mods


def test_delete_local_mod_returns_false_when_not_local(tmp_path):
    use_case, catalogue, _active_mods, _event_bus = _make_use_case(tmp_path)
    catalogue._workshop_mods["workshop_mod"] = ModInfo(
        id="workshop_mod", name="Workshop Mod", desc="", isLocal=False
    )

    result = use_case.delete_local_mod("workshop_mod")

    assert result is False


def test_delete_local_mod_returns_false_when_missing(tmp_path):
    use_case, _catalogue, _active_mods, _event_bus = _make_use_case(tmp_path)

    result = use_case.delete_local_mod("missing_mod")

    assert result is False
