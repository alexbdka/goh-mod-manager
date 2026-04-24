from collections.abc import Callable

from src.application.state import (
    LoadOrderActivationResult,
    LoadOrderMutationResult,
    ModState,
)
from src.core.exceptions import ProfileWriteError
from src.ui.widgets.active_mods_widget import ActiveModsWidget
from src.ui.widgets.catalogue_widget import CatalogueWidget


class LoadOrderController:
    """
    Qt-specific controller for load order mutations.
    """

    def __init__(
        self,
        catalogue_widget: CatalogueWidget,
        active_mods_widget: ActiveModsWidget,
        activate_mods: Callable[[list[str]], LoadOrderActivationResult],
        deactivate_mod: Callable[[str], LoadOrderMutationResult],
        clear_active_mods: Callable[[], LoadOrderMutationResult],
        move_mod_up: Callable[[str], LoadOrderMutationResult],
        move_mod_down: Callable[[str], LoadOrderMutationResult],
        set_active_mods_order: Callable[[list[str]], LoadOrderMutationResult],
        status_message: Callable[[str, int], None],
        show_missing_mods_dialog: Callable[
            [str, str, list[str] | list[dict[str, str]]], None
        ],
        handle_profile_write_error: Callable[[ProfileWriteError], None],
        get_mod_by_id: Callable[[str], ModState | None],
        tr: Callable[[str], str],
    ):
        self._catalogue_widget = catalogue_widget
        self._active_mods_widget = active_mods_widget
        self._activate_mods = activate_mods
        self._deactivate_mod = deactivate_mod
        self._clear_active_mods = clear_active_mods
        self._move_mod_up = move_mod_up
        self._move_mod_down = move_mod_down
        self._set_active_mods_order = set_active_mods_order
        self._status_message = status_message
        self._show_missing_mods_dialog = show_missing_mods_dialog
        self._handle_profile_write_error = handle_profile_write_error
        self._get_mod_by_id = get_mod_by_id
        self._tr = tr

    def add_selected_mods(self) -> None:
        mod_ids = self._catalogue_widget.get_selected_mod_ids()
        if not mod_ids:
            return

        try:
            result = self._activate_mods(mod_ids)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return

        if not result.changed:
            return

        self._status_message(
            self._tr("Activated mod(s): {0}").format(
                ", ".join(result.activated_mod_ids)
            ),
            3000,
        )

        if result.missing_dependencies:
            if len(result.activated_mod_ids) == 1:
                mod_id = result.activated_mod_ids[0]
                mod = self._get_mod_by_id(mod_id)
                mod_name = mod.name if mod else mod_id
                desc = self._tr(
                    "The mod '<b>{0}</b>' was activated, but the following "
                    "required dependencies are missing from your catalogue. "
                    "You must subscribe to them on the Workshop:"
                ).format(mod_name)
            else:
                desc = self._tr(
                    "The selected mods were activated, but the following "
                    "required dependencies are missing from your catalogue. "
                    "You must subscribe to them on the Workshop:"
                )

            self._show_missing_mods_dialog(
                self._tr("Missing Dependencies"),
                desc,
                result.missing_dependencies,
            )

    def remove_selected_mod(self) -> None:
        mod_id = self._active_mods_widget.get_selected_mod_id()
        if mod_id:
            self.remove_mod(mod_id)

    def remove_mod(self, mod_id: str) -> None:
        try:
            result = self._deactivate_mod(mod_id)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return

        if result.changed:
            self._status_message(self._tr("Deactivated mod: {0}").format(mod_id), 3000)

    def clear_mods(self) -> None:
        try:
            result = self._clear_active_mods()
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return

        if result.changed:
            self._status_message(self._tr("Cleared all active mods"), 3000)

    def move_up(self, mod_id: str) -> None:
        try:
            result = self._move_mod_up(mod_id)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        if result.changed:
            self._status_message(self._tr("Moved mod {0} up").format(mod_id), 3000)

    def move_down(self, mod_id: str) -> None:
        try:
            result = self._move_mod_down(mod_id)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        if result.changed:
            self._status_message(self._tr("Moved mod {0} down").format(mod_id), 3000)

    def reorder(self, new_order: list[str]) -> None:
        try:
            result = self._set_active_mods_order(new_order)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        if result.changed:
            self._status_message(self._tr("Mod load order updated"), 3000)
