from goh_mod_manager.core.mod import Mod
from goh_mod_manager.services.presets_service import PresetsService


def _make_mod(mod_id: str) -> Mod:
    return Mod(
        id=mod_id,
        name=f"Mod {mod_id}",
        desc="",
        minGameVersion="any",
        maxGameVersion="any",
        require="",
        folderPath=".",
        manualInstall=False,
    )


def test_resolve_presets_filters_missing_mods() -> None:
    service = PresetsService()
    installed = [_make_mod("100"), _make_mod("200")]
    presets = {"test": ["200", "404", "100"]}

    resolved = service.resolve_presets(presets, installed)

    assert [mod.id for mod in resolved["test"]] == ["200", "100"]


def test_to_config_payload_serializes_ids() -> None:
    service = PresetsService()
    presets = {"alpha": [_make_mod("1"), _make_mod("2")]}

    payload = service.to_config_payload(presets)

    assert payload == {"alpha": ["1", "2"]}
