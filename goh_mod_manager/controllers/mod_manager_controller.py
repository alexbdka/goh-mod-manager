import base64
import json
import time
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QPoint
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QMenu

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.models.mod_manager_model import ModManagerModel
from goh_mod_manager.views.dialogs.about_dialog import AboutDialog
from goh_mod_manager.views.dialogs.check_update_dialog import CheckUpdateDialog
from goh_mod_manager.views.dialogs.import_dialog import ImportDialog
from goh_mod_manager.views.dialogs.preferences_dialog import PreferencesDialog
from goh_mod_manager.views.dialogs.preset_dialog import PresetDialog
from goh_mod_manager.views.dialogs.user_manual_dialog import UserManualDialog
from goh_mod_manager.views.mod_manager_view import ModManagerView


class ModManagerController(QObject):
    """Controller for the mod manager application."""

    def __init__(self, model: ModManagerModel, view: ModManagerView):
        super().__init__()
        self._model = model
        self._view = view
        self._config = self._model.config
        self._initialize()

    def show(self):
        """Show the main application window."""
        self._view.show()

    def _initialize(self):
        """Initialize the controller by setting up configuration, loading data and connecting signals."""
        self._ensure_config_valid()
        self._model.set_config(self._config)
        self._load_data()
        self._connect_signals()
        self._change_font(self._config.get_font())

    def _ensure_config_valid(self):
        """Ensure configuration is valid, open preferences dialog if not."""
        if not self._config.get_mods_directory() or not self._config.get_options_file():
            self._open_user_manual()
            dialog = PreferencesDialog(self._config, self._view)
            if dialog.exec() == QDialog.DialogCode.Rejected:
                exit(1)

    def _load_data(self):
        """Load configuration data and update the view."""
        self._model.set_mods_directory(self._config.get_mods_directory())
        self._model.set_options_file(self._config.get_options_file())
        self._model.set_presets(self._config.get_presets())
        self._update_view()
        self._view.update_active_mods_count(self._model.active_mods_count)
        self._on_preset_selection_changed(self._view.get_current_preset_name())

    def _connect_signals(self):
        """Connect all signals from model and view to their respective handlers."""
        # Model signals
        self._model.mods_updated.connect(self._update_view)
        self._model.presets_updated.connect(self._update_view)
        self._model.active_mods_count_updated.connect(
            self._view.update_active_mods_count
        )

        # Menu actions
        self._view.ui.actionExit.triggered.connect(self._view.close)
        self._view.ui.actionRefresh.triggered.connect(self._refresh_all)
        self._view.ui.actionClear_Active_Mods.triggered.connect(self._clear_active_mods)
        self._view.ui.actionPreferences.triggered.connect(self._open_preferences)
        self._view.ui.actionImport_Mod.triggered.connect(self._import_mod)
        self._view.ui.actionShow_Mod_Details.triggered.connect(self._toggle_mod_details)
        self._view.ui.actionUser_Manual.triggered.connect(self._open_user_manual)
        self._view.ui.actionCheck_Updates.triggered.connect(self._check_app_update)
        self._view.ui.actionAbout.triggered.connect(self._open_about)
        self._view.ui.actionDefaultFont.triggered.connect(
            lambda: self._change_font("default")
        )
        self._view.ui.actionDyslexiaFont.triggered.connect(
            lambda: self._change_font("dyslexia")
        )

        # Button actions
        self._view.ui.pushButton_refresh_mods.clicked.connect(
            self._refresh_installed_mods
        )
        self._view.ui.pushButton_add_mod.clicked.connect(self._enable_selected_mod)
        self._view.ui.pushButton_remove_mod.clicked.connect(self._disable_selected_mod)
        self._view.ui.pushButton_move_up.clicked.connect(self._move_up)
        self._view.ui.pushButton_move_down.clicked.connect(self._move_down)
        self._view.ui.pushButton_clear_all.clicked.connect(self._clear_active_mods)
        self._view.ui.pushButton_save_preset.clicked.connect(self._save_preset)
        self._view.ui.pushButton_load_preset.clicked.connect(self._load_preset)
        self._view.ui.pushButton_delete_preset.clicked.connect(self._delete_preset)
        self._view.ui.pushButton_export_config.clicked.connect(self._export_share_code)
        self._view.ui.pushButton_import_config.clicked.connect(self._import_share_code)

        # List widget interactions
        self._view.ui.listWidget_available_mods.itemDoubleClicked.connect(
            self._enable_mod_from_item
        )
        self._view.ui.listWidget_active_mods.itemDoubleClicked.connect(
            self._disable_mod_from_item
        )
        self._view.ui.listWidget_active_mods.model().rowsMoved.connect(
            self._save_mods_order
        )
        self._view.ui.listWidget_available_mods.currentItemChanged.connect(
            self._on_mod_selected
        )
        self._view.ui.listWidget_active_mods.currentItemChanged.connect(
            self._on_mod_selected
        )
        self._view.ui.listWidget_available_mods.customContextMenuRequested.connect(
            self._handle_right_click
        )

        # Combo box and search
        self._view.ui.comboBox_presets.currentTextChanged.connect(
            self._on_preset_selection_changed
        )
        self._view.ui.lineEdit_search_installed.textChanged.connect(
            self._filter_installed_mods
        )
        self._view.ui.lineEdit_search_active.textChanged.connect(
            self._filter_active_mods
        )

    # Mod management
    def _enable_mod_from_item(self, item: QListWidgetItem):
        """Enable a mod from a list widget item."""
        mod = self._get_mod_from_item(item)
        if mod:
            self._model.enable_mod(mod)

    def _disable_mod_from_item(self, item: QListWidgetItem):
        """Disable a mod from a list widget item."""
        mod = self._get_mod_from_item(item)
        if mod:
            self._model.disable_mod(mod)

    def _enable_selected_mod(self):
        """Enable currently selected mods from available list."""
        for item in self._view.get_current_available_mod():
            mod = self._get_mod_from_item(item)
            if mod:
                self._model.enable_mod(mod)

    def _disable_selected_mod(self):
        """Disable currently selected mods from active list."""
        for item in self._view.get_current_active_mod():
            mod = self._get_mod_from_item(item)
            if mod:
                self._model.disable_mod(mod)

    def _move_up(self):
        """Move selected active mod up in the list."""
        if self._view.move_active_mod_up():
            self._save_mods_order()

    def _move_down(self):
        """Move selected active mod down in the list."""
        if self._view.move_active_mod_down():
            self._save_mods_order()

    def _save_mods_order(self):
        """Save the current order of active mods."""
        reordered_mods = self._view.get_active_mods_order()
        self._model.set_mods_order(reordered_mods)

    def _clear_active_mods(self):
        """Clear all active mods."""
        self._model.clear_active_mods()

    def _handle_right_click(self, pos: QPoint):
        """Handle right-click context menu on available mods list."""
        item = self._view.ui.listWidget_available_mods.itemAt(pos)
        if not item:
            return

        mod = item.data(256)
        if not mod.manualInstall:
            return

        menu = QMenu(self._view.ui.listWidget_available_mods)
        delete_action = menu.addAction("Delete")

        def on_delete():
            row = self._view.ui.listWidget_available_mods.row(item)
            self._view.ui.listWidget_available_mods.takeItem(row)
            self._model.delete_mod(mod)

        delete_action.triggered.connect(on_delete)
        menu.exec(self._view.ui.listWidget_available_mods.mapToGlobal(pos))

    # Data refresh methods
    def _refresh_all(self):
        """Refresh all data and clear search filters."""
        self._model.refresh_all()
        self._clear_search_filters()

    def _refresh_installed_mods(self):
        """Refresh only installed mods."""
        self._model.refresh_installed_mods()

    # View updates
    def _update_view(self):
        """Update the view with current model data."""
        self._view.populate_mod_lists(
            self._model.installed_mods, self._model.active_mods
        )
        self._view.update_presets(
            self._model.preset_names, self._view.get_current_preset_name()
        )

    def _on_mod_selected(self, current: QListWidgetItem):
        """Handle mod selection in lists."""
        mod = self._get_mod_from_item(current) if current else None
        self._view.update_mod_details(mod)

    def _toggle_mod_details(self, checked: bool):
        """Toggle mod details panel visibility."""
        self._view.ui.groupBox_mod_info.setVisible(checked)

    # Preset management
    def _save_preset(self):
        """Save current active mods as a preset."""
        if self._model.active_mods_count == 0:
            self._view.show_message(
                title="Empty Preset",
                text="Cannot save an empty preset. Add mods to the list first.",
                icon="warning",
            )
            return

        dialog = PresetDialog(
            parent=self._view, existing_presets=self._model.preset_names
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        preset_name = dialog.get_preset_name()
        if not preset_name:
            return

        if self._model.has_preset(preset_name) and not self._confirm_preset_overwrite(
            preset_name
        ):
            return

        if self._model.save_preset(preset_name):
            self._view.show_message(
                title="Preset Saved", text=f"Preset '{preset_name}' has been saved."
            )

    def _load_preset(self):
        """Load the selected preset."""
        preset_name = self._view.get_current_preset_name()
        if not preset_name:
            self._view.show_message(
                title="No Preset Selected",
                text="Please select a preset first.",
                icon="warning",
            )
            return

        if not self._model.has_preset(preset_name):
            self._view.show_message(
                title="Preset Not Found", text=f"Preset '{preset_name}' was not found."
            )
            return

        if self._confirm_preset_load(preset_name):
            self._model.load_preset(preset_name)

    def _delete_preset(self):
        """Delete the selected preset."""
        preset_name = self._view.get_current_preset_name()
        if not preset_name:
            self._view.show_message(
                title="Preset Not Selected", text="Please select a preset to delete."
            )
            return

        if not self._model.has_preset(preset_name):
            return

        if self._confirm_preset_deletion(preset_name) and self._model.delete_preset(
            preset_name
        ):
            self._view.show_message(
                title="Preset Deleted",
                text=f"Preset '{preset_name}' has been deleted.",
            )

    def _on_preset_selection_changed(self, preset_name: str):
        """Handle preset selection change."""
        if not preset_name or not self._model.has_preset(preset_name):
            self._view.ui.listWidget_presets.clear()
            return

        preset_mods = self._model.get_preset_mods(preset_name)
        self._view.ui.listWidget_presets.clear()

        for mod in preset_mods:
            item = QListWidgetItem(self._view.parse_clear_text(mod.name))
            item.setData(256, mod)
            self._view.ui.listWidget_presets.addItem(item)

    # Confirmation dialogs
    def _confirm_preset_overwrite(self, preset_name: str) -> bool:
        """Confirm preset overwrite."""
        return self._view.ask_confirmation(
            "Existing Preset", f"Preset '{preset_name}' already exists. Overwrite?"
        )

    def _confirm_preset_load(self, preset_name: str) -> bool:
        """Confirm preset loading."""
        return self._view.ask_confirmation(
            "Load Preset",
            f"Loading preset '{preset_name}' will clear the current list of mods. Continue?",
        )

    def _confirm_preset_deletion(self, preset_name: str) -> bool:
        """Confirm preset deletion."""
        return self._view.ask_confirmation(
            "Delete Preset",
            f"Are you sure you want to delete preset '{preset_name}'? This cannot be undone.",
        )

    def _confirm_code_import(self, mod_count: int) -> bool:
        """Confirm share code import."""
        return self._view.ask_confirmation(
            "Import Share Code",
            f"This will replace your current active mods with {mod_count} mods from the code. Continue?",
        )

    # Search filtering
    def _filter_installed_mods(self, search_text: str):
        """Filter installed mods list based on search text."""
        self._filter_list_widget(self._view.ui.listWidget_available_mods, search_text)

    def _filter_active_mods(self, search_text: str):
        """Filter active mods list based on search text."""
        self._filter_list_widget(self._view.ui.listWidget_active_mods, search_text)

    def _filter_list_widget(self, list_widget, search_text: str):
        """Filter items in a list widget based on search text."""
        search_text = search_text.lower().strip()

        for i in range(list_widget.count()):
            item = list_widget.item(i)
            mod = self._get_mod_from_item(item)

            if not search_text:
                item.setHidden(False)
            else:
                mod_name = mod.name.lower() if mod and mod.name else ""
                mod_desc = mod.desc.lower() if mod and mod.desc else ""
                is_visible = search_text in mod_name or search_text in mod_desc
                item.setHidden(not is_visible)

    def _clear_search_filters(self):
        """Clear all search filters."""
        self._view.ui.lineEdit_search_installed.clear()
        self._view.ui.lineEdit_search_active.clear()

    # Share code functionality
    def _export_share_code(self):
        """Export active mods as a share code."""
        if not self._model.active_mods:
            self._view.show_message(
                title="No Active Mods", text="Add mods to the active list first."
            )
            return

        share_data = {
            "version": 1,
            "mods": [{"name": mod.name} for mod in self._model.active_mods],
            "timestamp": int(time.time()),
        }

        try:
            json_str = json.dumps(share_data, separators=(",", ":"))
            encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
            self._view.ui.lineEdit_share_code.setText(encoded)
            self._view.show_message(
                title="Code Generated",
                text="Share code has been generated and copied to the field.",
            )
        except Exception as e:
            self._view.show_message(
                title="Export Error", text=f"Failed to generate code: {str(e)}"
            )

    def _import_share_code(self):
        """Import mods from a share code."""
        code = self._view.ui.lineEdit_share_code.text().strip()
        if not code:
            self._view.show_message(
                title="Empty Code", text="Enter a share code first."
            )
            return

        try:
            json_str = base64.b64decode(code.encode("utf-8")).decode("utf-8")
            share_data = json.loads(json_str)

            if not self._validate_share_data(share_data):
                raise ValueError("Invalid share code format")

            if not self._confirm_code_import(len(share_data["mods"])):
                return

            self._apply_share_code(share_data["mods"])
            self._view.show_message(
                title="Code Imported",
                text=f"Successfully imported {len(share_data['mods'])} mods.",
            )
        except Exception as e:
            self._view.show_message(
                title="Import Error", text=f"Invalid share code: {str(e)}"
            )

    def _apply_share_code(self, mod_list: List[Dict]):
        """Apply share code by enabling specified mods."""
        self._model.clear_active_mods()
        installed_mods = {mod.name: mod for mod in self._model.installed_mods}
        applied_count = 0

        for mod_data in mod_list:
            mod_name = mod_data["name"]
            if mod_name in installed_mods:
                self._model.enable_mod(installed_mods[mod_name])
                applied_count += 1

        if applied_count < len(mod_list):
            missing = len(mod_list) - applied_count
            self._view.show_message(
                title="Some Mods Missing",
                text=f"{missing} mods from the code are not installed.",
            )

    # Dialog management
    def _import_mod(self):
        """Open import mod dialog."""
        dialog = ImportDialog(self._view)
        dialog.mod_import_requested.connect(self._handle_import_mod)
        dialog.exec()

    def _handle_import_mod(self, archive_path: str):
        """Handle mod import from archive."""
        if self._model.import_mod(archive_path):
            self._update_view()

    def _open_preferences(self):
        """Open preferences dialog."""
        dialog = PreferencesDialog(self._config, self._view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_data()
            self._model.refresh_all()

    def _open_user_manual(self):
        """Open user manual dialog."""
        dialog = UserManualDialog(self._view)
        dialog.exec()

    def _open_about(self):
        """Open about dialog."""
        dialog = AboutDialog(self._view, QApplication.applicationVersion())
        dialog.exec()

    def _check_app_update(self):
        """Check for application updates."""
        CheckUpdateDialog(self._view, QApplication.applicationVersion())

    # Font management
    def _change_font(self, font_name: str):
        """Change application font."""
        if font_name == "default":
            font = QFont("Inter-Regular", 10)
            self._view.set_font(font)
            self._config.set_font("default")
        elif font_name == "dyslexia":
            QFontDatabase.addApplicationFont(":/assets/fonts/OpenDyslexic-Regular.otf")
            font = QFont("OpenDyslexic", 10)
            self._view.set_font(font)
            self._config.set_font("dyslexia")

    # Utility methods
    @staticmethod
    def _get_mod_from_item(item: Optional[QListWidgetItem]) -> Optional[Mod]:
        """Extract mod data from a list widget item."""
        return item.data(256) if item else None

    @staticmethod
    def _validate_share_data(data: Dict) -> bool:
        """Validate share code data structure."""
        required_keys = ["version", "mods"]
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data["mods"], list):
            return False

        for mod_data in data["mods"]:
            if not isinstance(mod_data, dict) or "name" not in mod_data:
                return False

        return True
