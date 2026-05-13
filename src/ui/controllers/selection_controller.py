from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any

try:
    from PySide6.QtWidgets import QMenu, QWidget  # type: ignore
except Exception:  # pragma: no cover - headless CI may lack Qt/graphics libs
    # Provide minimal stand-ins so module imports in CI/tests don't fail.
    class _DummyAction:
        def __init__(self, text: str) -> None:
            self.text = text

    class _DummyWidget:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def addAction(self, text: str):
            return _DummyAction(text)

        def addSeparator(self) -> None:
            return None

        def exec(self, global_pos=None):
            # Simulate no action selected in headless contexts.
            return None

    QMenu = _DummyWidget  # type: ignore
    QWidget = _DummyWidget  # type: ignore

from src.application.state import ModState
from src.core.mod_reference import parse_reference_key
from src.ui.widgets.active_mods_widget import ActiveModsWidget
from src.ui.widgets.catalogue_widget import CatalogueWidget
from src.ui.widgets.mod_details_widget import ModDetailsWidget
from src.utils import system_actions


class SelectionController:
    """
    Qt-specific controller for selection synchronization, context menus, and
    opening paths.
    """

    def __init__(
        self,
        parent: Any,
        catalogue_widget: CatalogueWidget,
        active_mods_widget: ActiveModsWidget,
        mod_details_widget: ModDetailsWidget,
        get_mod_by_id: Callable[[str, bool | None], ModState | None],
        signals_blocked: Callable[..., AbstractContextManager],
        show_warning_message: Callable[[str, str], None],
    ):
        self._parent = parent
        self._catalogue_widget = catalogue_widget
        self._active_mods_widget = active_mods_widget
        self._mod_details_widget = mod_details_widget
        self._get_mod_by_id = get_mod_by_id
        self._signals_blocked = signals_blocked
        self._show_warning_message = show_warning_message

    def show_catalogue_context_menu(self, pos):
        mod_ref = self._catalogue_widget.get_mod_ref_at(pos)
        if not mod_ref:
            return
        self._show_mod_context_menu(
            mod_ref, self._catalogue_widget.map_list_pos_to_global(pos)
        )

    def show_active_mods_context_menu(self, pos):
        mod_ref = self._active_mods_widget.get_mod_ref_at(pos)
        if not mod_ref:
            return
        self._show_mod_context_menu(
            mod_ref, self._active_mods_widget.map_list_pos_to_global(pos)
        )

    def handle_catalogue_selection_changed(self):
        mod_ref = self._catalogue_widget.get_selected_mod_ref()
        if not mod_ref:
            return
        reference = parse_reference_key(mod_ref)
        if reference is None:
            return

        with self._signals_blocked(self._active_mods_widget):
            self._active_mods_widget.clear_selection()

        self._mod_details_widget.display_mod(
            self._get_mod_by_id(reference.id, reference.is_local)
        )

    def handle_active_mods_selection_changed(self):
        mod_ref = self._active_mods_widget.get_selected_mod_ref()
        if not mod_ref:
            return
        reference = parse_reference_key(mod_ref)
        if reference is None:
            return

        with self._signals_blocked(self._catalogue_widget):
            self._catalogue_widget.clear_selection()

        self._mod_details_widget.display_mod(
            self._get_mod_by_id(reference.id, reference.is_local)
        )

    def open_existing_path(self, path: str):
        if not path or not system_actions.open_path(path):
            self._show_warning_message(
                self._parent.tr("Not Found"),
                self._parent.tr("Cannot find path:\n{0}").format(path),
            )

    def _show_mod_context_menu(self, mod_ref: str, global_pos):
        reference = parse_reference_key(mod_ref)
        if reference is None:
            return

        mod = self._get_mod_by_id(reference.id, reference.is_local)
        if not mod:
            return

        menu = QMenu(self._parent)

        open_folder_action = menu.addAction(self._parent.tr("Open Mod Folder"))
        open_workshop_action = None
        if not mod.is_local and mod.id.isdigit():
            open_workshop_action = menu.addAction(
                self._parent.tr("Open in Steam Workshop")
            )

        action = menu.exec(global_pos)

        if action is None:
            return

        if action == open_folder_action:
            self.open_existing_path(mod.path)
        elif open_workshop_action is not None and action == open_workshop_action:
            system_actions.open_url(f"steam://url/CommunityFilePage/{mod.id}")
