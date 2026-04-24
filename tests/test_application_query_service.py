from src.application.query_service import ApplicationQueryService
from src.core.config import AppConfig
from src.core.mod import ModInfo
from src.services.active_mods_service import ActiveModsService
from src.services.config_service import ConfigService
from src.services.mods_catalogue_service import ModsCatalogueService
from src.services.preset_service import PresetService


def _build_queries() -> ApplicationQueryService:
    config_service = ConfigService(config_path=":memory:")
    config_service._config = AppConfig(
        game_path="C:/Games/GoH",
        workshop_path="C:/Steam/workshop",
        profile_path="C:/Users/test/options.set",
        presets={"Preset A": ["dep", "main"], "Preset B": ["other"]},
        language="fr_FR",
        theme="dark",
        font="OpenDyslexic",
    )

    catalogue = ModsCatalogueService()
    catalogue._local_mods = {
        "dep": ModInfo(id="dep", name="Dependency", desc="", isLocal=True),
        "main": ModInfo(
            id="main",
            name="Main Mod",
            desc="Desc",
            dependencies=["dep", "missing"],
            isLocal=True,
        ),
    }
    catalogue._workshop_mods = {
        "other": ModInfo(id="other", name="Other", desc="", isLocal=False)
    }

    active_mods = ActiveModsService(catalogue)
    active_mods.active_mods_ids = ["dep", "main"]

    presets = PresetService(config_service, catalogue, active_mods)

    return ApplicationQueryService(config_service, catalogue, active_mods, presets)


def test_get_settings_state_returns_view_neutral_settings_snapshot():
    queries = _build_queries()

    state = queries.get_settings_state()

    assert state.game_path == "C:/Games/GoH"
    assert state.language == "fr_FR"
    assert state.theme == "dark"
    assert state.font == "OpenDyslexic"


def test_get_catalogue_state_marks_active_and_missing_dependencies():
    queries = _build_queries()

    state = queries.get_catalogue_state()
    by_id = {item.id: item for item in state.items}

    assert by_id["dep"].is_active is True
    assert by_id["main"].is_active is True
    assert by_id["main"].missing_dependencies == ["missing"]
    assert by_id["other"].is_active is False


def test_get_active_mods_state_keeps_load_order():
    queries = _build_queries()

    state = queries.get_active_mods_state()

    assert [item.id for item in state.items] == ["dep", "main"]
    assert [item.load_order for item in state.items] == [1, 2]


def test_get_mod_state_returns_active_mod_snapshot():
    queries = _build_queries()

    state = queries.get_mod_state("main")

    assert state is not None
    assert state.id == "main"
    assert state.is_active is True
    assert state.load_order == 2
    assert state.missing_dependencies == ["missing"]


def test_get_presets_state_detects_current_matching_preset():
    queries = _build_queries()

    state = queries.get_presets_state()

    assert state.preset_names == ["Preset A", "Preset B"]
    assert state.current_preset_name == "Preset A"
    assert state.is_unsaved is False


def test_get_presets_state_tracks_selected_preset_with_unsaved_changes():
    queries = _build_queries()
    queries._active_mods_service.active_mods_ids = ["main", "dep"]

    state = queries.get_presets_state(selected_preset_name="Preset A")

    assert state.current_preset_name == "Preset A"
    assert state.is_unsaved is True


def test_get_presets_state_ignores_custom_selection_for_unsaved_state():
    queries = _build_queries()
    queries._active_mods_service.active_mods_ids = ["main", "dep"]

    state = queries.get_presets_state(selected_preset_name="")

    assert state.current_preset_name is None
    assert state.is_unsaved is False
