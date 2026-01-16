from goh_mod_manager.core.mod import Mod
from goh_mod_manager.services.share_code_service import ShareCodeService


def _make_mod(mod_id: str, name: str) -> Mod:
    return Mod(
        id=mod_id,
        name=name,
        desc="",
        minGameVersion="any",
        maxGameVersion="any",
        require="",
        folderPath=".",
        manualInstall=False,
    )


def test_encode_decode_versioned_roundtrip() -> None:
    service = ShareCodeService()
    mods = [_make_mod("100", "Mod A"), _make_mod("200", "Mod B")]

    code = service.encode_versioned(mods)
    decoded = service.decode(code)

    assert decoded == [{"name": "Mod A", "id": "100"}, {"name": "Mod B", "id": "200"}]


def test_encode_decode_list_roundtrip() -> None:
    service = ShareCodeService()
    mods = [_make_mod("100", "Mod A")]

    code = service.encode_mods_list(mods)
    decoded = service.decode(code)

    assert decoded == [{"id": "100", "name": "Mod A"}]


def test_resolve_mods_prefers_id_then_name() -> None:
    service = ShareCodeService()
    installed = [_make_mod("100", "Alpha"), _make_mod("200", "Beta")]

    mod_data = [{"id": "200", "name": "Alpha"}, {"name": "Alpha"}]
    found, missing = service.resolve_mods(mod_data, installed)

    assert [mod.id for mod in found] == ["200", "100"]
    assert missing == []


def test_resolve_mods_tracks_missing() -> None:
    service = ShareCodeService()
    installed = [_make_mod("100", "Alpha")]

    mod_data = [{"id": "999", "name": "Ghost"}]
    found, missing = service.resolve_mods(mod_data, installed)

    assert found == []
    assert missing == [{"id": "999", "name": "Ghost"}]
