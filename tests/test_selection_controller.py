from contextlib import nullcontext
from types import SimpleNamespace
from typing import Any

from src.ui.controllers import selection_controller as sc


class _DummyWidget:
    def clear_selection(self):
        return None

    def get_mod_id_at(self, _pos):
        return None

    def map_list_pos_to_global(self, pos):
        return pos


class _DummyDetails:
    def display_mod(self, _mod):
        return None


class _DummyParent:
    def tr(self, text: str) -> str:
        return text


class _FakeMenu:
    def __init__(self, _parent):
        self.actions = []
        self.select_last = False

    def addAction(self, text):
        action = SimpleNamespace(text=text)
        self.actions.append(action)
        return action

    def exec(self, _global_pos):
        if self.select_last and self.actions:
            return self.actions[-1]
        return None


def _build_controller(get_mod_by_id):
    controller_cls: Any = sc.SelectionController
    return controller_cls(
        parent=_DummyParent(),
        catalogue_widget=_DummyWidget(),
        active_mods_widget=_DummyWidget(),
        mod_details_widget=_DummyDetails(),
        get_mod_by_id=get_mod_by_id,
        signals_blocked=lambda *_args: nullcontext(),
        show_warning_message=lambda *_args: None,
    )


def test_local_mod_context_menu_cancel_does_not_open_workshop(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)

    opened_urls: list[str] = []

    def mock_open_url(url: str) -> None:
        opened_urls.append(url)

    monkeypatch.setattr(sc.system_actions, "open_url", mock_open_url)

    mod = SimpleNamespace(is_local=True, path="C:/mods/template")
    controller = _build_controller(lambda _mod_id: mod)

    controller._show_mod_context_menu("template", (0, 0))

    assert opened_urls == []


def test_workshop_action_opens_steam_for_workshop_mod(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)

    opened_urls: list[str] = []

    def mock_open_url(url: str) -> None:
        opened_urls.append(url)

    monkeypatch.setattr(sc.system_actions, "open_url", mock_open_url)

    mod = SimpleNamespace(is_local=False, path="C:/mods/123456")
    controller = _build_controller(lambda _mod_id: mod)

    fake_menu.select_last = True
    controller._show_mod_context_menu("123456", (0, 0))

    assert opened_urls == ["steam://url/CommunityFilePage/123456"]
