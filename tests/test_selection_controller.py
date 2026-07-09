from contextlib import nullcontext
from types import SimpleNamespace
from typing import Any

from src.ui.controllers import selection_controller as sc


class _DummyWidget:
    def clear_selection(self):
        return None

    def get_mod_id_at(self, _pos):
        return None

    def get_mod_ref_at(self, _pos):
        return None

    def get_selected_mod_ref(self):
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
        self.select_action = None

    def addAction(self, text):
        action = SimpleNamespace(text=text)
        self.actions.append(action)
        return action

    def addSeparator(self):
        return None

    def exec(self, _global_pos):
        return self.select_action


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
        show_info_message=lambda *_args: None,
        delete_local_mod=lambda _mod_id: True,
    )


def test_local_mod_context_menu_cancel_does_not_open_workshop(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)

    opened_urls: list[str] = []

    def mock_open_url(url: str) -> None:
        opened_urls.append(url)

    monkeypatch.setattr(sc.system_actions, "open_url", mock_open_url)

    mod = SimpleNamespace(id="template", is_local=True, path="C:/mods/template")
    controller = _build_controller(lambda _mod_id, _is_local: mod)

    controller._show_mod_context_menu("local::template", (0, 0))

    assert opened_urls == []


def test_workshop_action_opens_steam_for_workshop_mod(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)

    opened_urls: list[str] = []

    def mock_open_url(url: str) -> None:
        opened_urls.append(url)

    monkeypatch.setattr(sc.system_actions, "open_url", mock_open_url)

    mod = SimpleNamespace(id="123456", is_local=False, path="C:/mods/123456")
    controller = _build_controller(lambda _mod_id, _is_local: mod)

    controller._show_mod_context_menu("workshop::123456", (0, 0))
    assert len(fake_menu.actions) == 2
    fake_menu.select_action = fake_menu.actions[-1]
    controller._show_mod_context_menu("workshop::123456", (0, 0))

    assert opened_urls == ["steam://url/CommunityFilePage/123456"]


def test_local_mod_context_menu_includes_delete_action(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)

    mod = SimpleNamespace(id="template", is_local=True, path="C:/mods/template")
    controller = _build_controller(lambda _mod_id, _is_local: mod)

    controller._show_mod_context_menu("local::template", (0, 0))

    assert any(action.text == "Delete Mod" for action in fake_menu.actions)


def test_workshop_mod_context_menu_excludes_delete_action(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)

    mod = SimpleNamespace(id="123456", is_local=False, path="C:/mods/123456")
    controller = _build_controller(lambda _mod_id, _is_local: mod)

    controller._show_mod_context_menu("workshop::123456", (0, 0))

    assert not any(action.text == "Delete Mod" for action in fake_menu.actions)


def test_delete_action_confirms_and_calls_delete_local_mod(monkeypatch):
    fake_menu = _FakeMenu(None)
    monkeypatch.setattr(sc, "QMenu", lambda _parent: fake_menu)
    monkeypatch.setattr(sc.QMessageBox, "question", lambda *_args, **_kwargs: 16384)

    deleted: list[str] = []
    info_messages: list[tuple[str, str]] = []

    def _build_tracking_controller(get_mod_by_id):
        controller_cls: Any = sc.SelectionController
        return controller_cls(
            parent=_DummyParent(),
            catalogue_widget=_DummyWidget(),
            active_mods_widget=_DummyWidget(),
            mod_details_widget=_DummyDetails(),
            get_mod_by_id=get_mod_by_id,
            signals_blocked=lambda *_args: nullcontext(),
            show_warning_message=lambda *_args: None,
            show_info_message=lambda title, message: info_messages.append(
                (title, message)
            ),
            delete_local_mod=lambda mod_id: deleted.append(mod_id) or True,
        )

    mod = SimpleNamespace(
        id="template", name="Template", is_local=True, path="C:/mods/template"
    )
    controller = _build_tracking_controller(lambda _mod_id, _is_local: mod)

    controller._show_mod_context_menu("local::template", (0, 0))
    delete_action = next(a for a in fake_menu.actions if a.text == "Delete Mod")
    fake_menu.select_action = delete_action

    controller._show_mod_context_menu("local::template", (0, 0))

    assert deleted == ["template"]
    assert info_messages == [("Mod Deleted", "Deleted local mod: Template")]
