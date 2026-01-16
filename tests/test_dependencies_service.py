from goh_mod_manager.core.mod import Mod
from goh_mod_manager.services.dependencies_service import DependenciesService


def _make_mod(mod_id: str, require: str = "") -> Mod:
    return Mod(
        id=mod_id,
        name=f"Mod {mod_id}",
        desc="",
        minGameVersion="any",
        maxGameVersion="any",
        require=require,
        folderPath=".",
        manualInstall=False,
    )


def test_missing_dependencies_returns_deep_first() -> None:
    mod_a = _make_mod("A", require="B")
    mod_b = _make_mod("B", require="C")
    mod_c = _make_mod("C")

    installed = [mod_a, mod_b, mod_c]
    active = []

    missing = DependenciesService.get_missing_dependencies(mod_a, active, installed)

    assert [mod.id for mod in missing] == ["C", "B"]


def test_missing_dependencies_skips_active() -> None:
    mod_a = _make_mod("A", require="B C")
    mod_b = _make_mod("B")
    mod_c = _make_mod("C")

    installed = [mod_a, mod_b, mod_c]
    active = [mod_b]

    missing = DependenciesService.get_missing_dependencies(mod_a, active, installed)

    assert [mod.id for mod in missing] == ["C"]


def test_missing_dependencies_handles_cycles() -> None:
    mod_a = _make_mod("A", require="B")
    mod_b = _make_mod("B", require="A")

    installed = [mod_a, mod_b]
    active = []

    missing = DependenciesService.get_missing_dependencies(mod_a, active, installed)

    assert [mod.id for mod in missing] == ["B"]
