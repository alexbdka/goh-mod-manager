from src.application.state import (
    ActiveModsState,
    CatalogueState,
    PresetsState,
    SettingsState,
    ShareCodeExportResult,
)
from src.cli import main as cli_main


class _FakeManager:
    def initialize(self) -> bool:
        return True

    def get_settings_state(self) -> SettingsState:
        return SettingsState(
            game_path="C:/game",
            workshop_path="C:/workshop",
            profile_path="C:/profile/options.set",
            language="en_US",
            theme="dark",
            font="Inter",
        )

    def get_catalogue_state(self) -> CatalogueState:
        return CatalogueState(items=[])

    def get_active_mods_state(self) -> ActiveModsState:
        return ActiveModsState(items=[])

    def get_presets_state(self) -> PresetsState:
        return PresetsState(
            preset_names=[],
            current_preset_name=None,
            is_unsaved=False,
        )

    def build_share_code_export(self) -> ShareCodeExportResult:
        return ShareCodeExportResult(has_active_mods=True, code="abc123")


def test_status_lines_use_state_surface():
    manager = _FakeManager()

    lines = cli_main._status_lines(manager, True)

    assert "initialized: True" in lines
    assert "game_path: C:/game" in lines
    assert "catalogue_count: 0" in lines


def test_share_code_lines_use_export_result_surface():
    manager = _FakeManager()

    lines = cli_main._share_code_lines(manager)

    assert lines == ["abc123"]
