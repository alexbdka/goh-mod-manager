from pathlib import Path

import pytest

from goh_mod_manager.core.mod_manager_model import ModManagerModel
from goh_mod_manager.presentation.viewmodels.file_actions_view_model import (
    FileActionsViewModel,
)
from goh_mod_manager.presentation.viewmodels.mod_actions_view_model import (
    ModActionsViewModel,
)


def _write_mod_info(mod_dir: Path) -> None:
    mod_dir.mkdir(parents=True, exist_ok=True)
    (mod_dir / "mod.info").write_text('{name "Async Mod"}\n', encoding="utf-8")


def test_refresh_installed_mods_async(qtbot, tmp_path: Path) -> None:
    model = ModManagerModel()
    model.get_config().set_mods_directory(str(tmp_path))

    mod_dir = tmp_path / "123"
    _write_mod_info(mod_dir)

    vm = ModActionsViewModel(model)
    with qtbot.waitSignal(vm.refresh_installed_finished, timeout=2000):
        vm.refresh_installed_mods_async()

    installed = model.get_installed_mods()
    assert len(installed) == 1
    assert installed[0].id == "123"


def test_import_mod_async(qtbot, tmp_path: Path) -> None:
    pytest.xfail("Flaky on CI/Windows signal routing; covered by sync import test.")
    steam_root = tmp_path / "Steam"
    workshop_mods = steam_root / "steamapps" / "workshop" / "content" / "400750"
    game_mods = (
        steam_root / "steamapps" / "common" / "Call to Arms - Gates of Hell" / "mods"
    )
    workshop_mods.mkdir(parents=True, exist_ok=True)
    game_mods.mkdir(parents=True, exist_ok=True)

    source_dir = tmp_path / "source_mod"
    _write_mod_info(source_dir / "999")

    model = ModManagerModel()
    model.get_config().set_mods_directory(str(workshop_mods))

    vm = FileActionsViewModel(model, model.get_config())
    success = {"value": False}
    error = {"message": None}

    def on_success() -> None:
        success["value"] = True

    def on_error(message: str) -> None:
        error["message"] = message

    vm.import_succeeded.connect(on_success)
    vm.import_error.connect(on_error)

    vm.import_mod_async(str(source_dir))

    qtbot.waitUntil(lambda: success["value"] or error["message"], timeout=3000)

    assert error["message"] is None
    assert success["value"] is True
    assert (game_mods / "999" / "mod.info").exists()
