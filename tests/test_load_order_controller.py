from typing import Any, cast

from src.application.state import LoadOrderMutationResult, ModState
from src.ui.controllers.load_order_controller import LoadOrderController


class _DummyCatalogueWidget:
    def get_selected_mod_refs(self):
        return []


class _DummyActiveModsWidget:
    def get_selected_mod_ref(self):
        return None


def test_remove_mod_blocked_warning_strips_mod_name_markup():
    warning_messages: list[tuple[str, str]] = []

    def get_mod_by_id(mod_id: str, _is_local: bool | None):
        names = {
            "dep": "<c(FFFFFF)>GOH Framework</c>",
            "main": "[=<c(B22222)>Valour</c>=]",
        }
        return ModState(id=mod_id, name=names[mod_id], description="")

    controller = LoadOrderController(
        catalogue_widget=cast(Any, _DummyCatalogueWidget()),
        active_mods_widget=cast(Any, _DummyActiveModsWidget()),
        activate_mods=lambda _refs: None,  # type: ignore[arg-type, return-value]
        deactivate_mod=lambda _ref: LoadOrderMutationResult(
            changed=False,
            blocked_reason="required_by_active_mods",
            blocking_mod_refs=["local::main"],
        ),
        clear_active_mods=lambda: LoadOrderMutationResult(),
        move_mod_up=lambda _ref: LoadOrderMutationResult(),
        move_mod_down=lambda _ref: LoadOrderMutationResult(),
        set_active_mods_order=lambda _refs: LoadOrderMutationResult(),
        status_message=lambda _message, _timeout: None,
        show_warning_message=lambda title, message: warning_messages.append(
            (title, message)
        ),
        show_missing_mods_dialog=lambda _title, _desc, _items: None,
        handle_profile_write_error=lambda _error: None,
        get_mod_by_id=get_mod_by_id,
        tr=lambda text: text,
    )

    controller.remove_mod("local::dep")

    assert warning_messages == [
        (
            "Dependency In Use",
            "Cannot remove 'GOH Framework': required by '[=Valour=]'.",
        )
    ]
