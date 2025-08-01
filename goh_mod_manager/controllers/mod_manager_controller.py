import base64
import json
import time
from typing import Optional, List, Dict

from PySide6.QtCore import QObject
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QListWidgetItem, QDialog, QMessageBox, QApplication

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.models.mod_manager_model import ModManagerModel
from goh_mod_manager.utils.config_manager import ConfigManager
from goh_mod_manager.views.dialogs.about_dialog import AboutDialog
from goh_mod_manager.views.dialogs.check_update_dialog import CheckUpdateDialog
from goh_mod_manager.views.dialogs.import_dialog import ImportDialog
from goh_mod_manager.views.dialogs.preferences_dialog import PreferencesDialog
from goh_mod_manager.views.dialogs.preset_dialog import PresetDialog
from goh_mod_manager.views.dialogs.user_manual_dialog import UserManualDialog
from goh_mod_manager.views.mod_manager_view import ModManagerView


class ModManagerController(QObject):
    def __init__(self, model: ModManagerModel, view: ModManagerView):
        super().__init__()
        self._model = model
        self._view = view
        self._config = ConfigManager()

        self._initialize()

    def show(self):
        self._view.show()

    def _initialize(self):
        self._ensure_config_valid()
        self._model.set_config(self._config)
        self._load_data()
        self._connect_signals()
        self._change_font(self._config.get_font())

    def _ensure_config_valid(self):
        if not self._config.get_mods_directory() or not self._config.get_options_file():
            self._open_user_manual()
            dialog = PreferencesDialog(self._config, self._view)
            if dialog.exec() == QDialog.DialogCode.Rejected:
                exit(1)

    def _load_data(self):
        self._model.set_mods_directory(self._config.get_mods_directory())
        self._model.set_options_file(self._config.get_options_file())
        self._model.set_presets(self._config.get_presets())

        self._update_view()
        self._view.update_active_mods_count(self._model.get_active_mods_count())
        self._on_preset_selection_changed(self._view.get_current_preset_name())

    # noinspection DuplicatedCode
    def _connect_signals(self):
        self._model.mods_updated.connect(self._update_view)
        self._model.presets_updated.connect(self._update_view)
        self._model.active_mods_count_updated.connect(
            self._view.update_active_mods_count
        )

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
        self._view.ui.comboBox_presets.currentTextChanged.connect(
            self._on_preset_selection_changed
        )

        self._view.ui.lineEdit_search_installed.textChanged.connect(
            self._filter_installed_mods
        )
        self._view.ui.lineEdit_search_active.textChanged.connect(
            self._filter_active_mods
        )

    def _enable_mod_from_item(self, item: QListWidgetItem):
        mod = self._get_mod_from_item(item)
        if mod:
            self._model.enable_mod(mod)

    def _disable_mod_from_item(self, item: QListWidgetItem):
        mod = self._get_mod_from_item(item)
        if mod:
            self._model.disable_mod(mod)

    def _enable_mod_from_data(self, mod: Mod):
        if mod:
            self._model.enable_mod(mod)

    def _disable_mod_from_data(self, mod: Mod):
        if mod:
            self._model.disable_mod(mod)

    def _enable_selected_mod(self):
        items = self._view.get_current_available_mod()
        mods_data = [self._get_mod_from_item(item) for item in items]

        for mod in mods_data:
            self._enable_mod_from_data(mod)

    def _disable_selected_mod(self):
        items = self._view.get_current_active_mod()
        mods_data = [self._get_mod_from_item(item) for item in items]

        for mod in mods_data:
            self._disable_mod_from_data(mod)

    def _move_up(self):
        if self._view.move_active_mod_up():
            self._save_mods_order()

    def _move_down(self):
        if self._view.move_active_mod_down():
            self._save_mods_order()

    def _save_mods_order(self):
        reordered_mods = self._view.get_active_mods_order()
        self._model.set_mods_order(reordered_mods)

    def _clear_active_mods(self):
        self._model.clear_active_mods()

    def _refresh_all(self):
        self._model.refresh_all()
        self._clear_search_filters()

    def _refresh_installed_mods(self):
        self._model.refresh_installed_mods()

    def _update_view(self):
        self._view.populate_mod_lists(
            self._model.get_installed_mods(), self._model.get_active_mods()
        )
        self._view.update_presets(
            self._model.get_preset_names(), self._view.get_current_preset_name()
        )

    def _update_presets(self):
        current_selection = self._view.get_current_preset_name()
        preset_names = self._model.get_preset_names()
        self._view.update_presets(preset_names, current_selection)

    def _on_mod_selected(self, current: QListWidgetItem):
        mod = self._get_mod_from_item(current) if current else None
        self._view.update_mod_details(mod)

    def _toggle_mod_details(self, checked: bool):
        self._view.ui.groupBox_mod_info.setVisible(checked)

    def _save_preset(self):
        if self._model.get_active_mods_count() == 0:
            QMessageBox.warning(
                self._view,
                "Empty Preset",
                "Cannot save an empty preset. Add mods to the list first.",
            )
            return

        existing_presets = self._model.get_preset_names()
        dialog = PresetDialog(parent=self._view, existing_presets=existing_presets)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            preset_name = dialog.get_preset_name()
            if not preset_name:
                return

            if self._model.has_preset(preset_name):
                if not self._confirm_preset_overwrite(preset_name):
                    return

            if self._model.save_preset(preset_name):
                QMessageBox.information(
                    self._view,
                    "Preset Saved",
                    f"Preset '{preset_name}' has been saved.",
                )

    def _load_preset(self):
        preset_name = self._view.get_current_preset_name()

        if not preset_name:
            QMessageBox.warning(
                self._view, "Preset Not Selected", "Please select a preset first."
            )
            return

        if not self._model.has_preset(preset_name):
            QMessageBox.warning(
                self._view, "Preset Not Found", f"Preset '{preset_name}' was not found."
            )
            return

        if self._confirm_preset_load(preset_name):
            self._model.load_preset(preset_name)

    def _delete_preset(self):
        preset_name = self._view.get_current_preset_name()

        if not preset_name:
            QMessageBox.warning(
                self._view, "Preset Not Selected", "Please select a preset to delete."
            )
            return

        if not self._model.has_preset(preset_name):
            return

        if self._confirm_preset_deletion(preset_name):
            if self._model.delete_preset(preset_name):
                QMessageBox.information(
                    self._view,
                    "Preset Deleted",
                    f"Preset '{preset_name}' has been deleted.",
                )

    def _confirm_preset_overwrite(self, preset_name: str) -> bool:
        reply = QMessageBox.question(
            self._view,
            "Existing Preset",
            f"Preset '{preset_name}' already exists. Overwrite?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _confirm_preset_load(self, preset_name: str) -> bool:
        reply = QMessageBox.question(
            self._view,
            "Load Preset",
            f"Loading preset '{preset_name}' will clear the current list of mods. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _confirm_preset_deletion(self, preset_name: str) -> bool:
        reply = QMessageBox.question(
            self._view,
            "Delete Preset",
            f"Are you sure you want to delete preset '{preset_name}'? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _on_preset_selection_changed(self, preset_name: str):
        if not preset_name or not self._model.has_preset(preset_name):
            self._view.ui.listWidget_presets.clear()
            return

        preset_mods = self._model.get_preset_mods(preset_name)
        self._view.ui.listWidget_presets.clear()

        for mod in preset_mods:
            item = QListWidgetItem(mod.name)
            item.setData(256, mod)
            self._view.ui.listWidget_presets.addItem(item)

    def _filter_installed_mods(self, search_text: str):
        list_widget = self._view.ui.listWidget_available_mods
        self._filter_list_widget(list_widget, search_text)

    def _filter_active_mods(self, search_text: str):
        list_widget = self._view.ui.listWidget_active_mods
        self._filter_list_widget(list_widget, search_text)

    def _filter_list_widget(self, list_widget, search_text: str):
        search_text = search_text.lower().strip()

        for i in range(list_widget.count()):
            item = list_widget.item(i)
            mod = self._get_mod_from_item(item)

            if not search_text:
                item.setHidden(False)
            else:
                mod_name = mod.name.lower() if mod and mod.name else ""
                mod_desc = mod.desc.lower() if mod and mod.desc else ""

                visible = search_text in mod_name or search_text in mod_desc
                item.setHidden(not visible)

    def _clear_search_filters(self):
        self._view.ui.lineEdit_search_installed.clear()
        self._view.ui.lineEdit_search_active.clear()

    def _export_share_code(self):
        active_mods = self._model.get_active_mods()

        if not active_mods:
            QMessageBox.warning(
                self._view, "No Active Mods", "Add mods to the active list first."
            )
            return

        share_data = {
            "version": 1,
            "mods": [{"name": mod.name} for mod in active_mods],
            "timestamp": int(time.time()),
        }

        try:
            json_str = json.dumps(share_data, separators=(",", ":"))
            encoded = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

            self._view.ui.lineEdit_share_code.setText(encoded)

            QMessageBox.information(
                self._view,
                "Code Generated",
                "Share code has been generated and copied to the field.",
            )

        except Exception as e:
            QMessageBox.critical(
                self._view, "Export Error", f"Failed to generate code: {str(e)}"
            )

    def _import_share_code(self):
        code = self._view.ui.lineEdit_share_code.text().strip()

        if not code:
            QMessageBox.warning(self._view, "Empty Code", "Enter a share code first.")
            return

        try:
            json_str = base64.b64decode(code.encode("utf-8")).decode("utf-8")
            share_data = json.loads(json_str)

            if not self._validate_share_data(share_data):
                raise ValueError("Invalid share code format")

            if not self._confirm_code_import(len(share_data["mods"])):
                return

            self._apply_share_code(share_data["mods"])

            QMessageBox.information(
                self._view,
                "Code Imported",
                f"Successfully imported {len(share_data['mods'])} mods.",
            )

        except Exception as e:
            QMessageBox.critical(
                self._view, "Import Error", f"Invalid share code: {str(e)}"
            )

    def _apply_share_code(self, mod_list: List[Dict]):
        self._model.clear_active_mods()

        installed_mods = {mod.name: mod for mod in self._model.get_installed_mods()}
        applied_count = 0

        for mod_data in mod_list:
            mod_name = mod_data["name"]
            if mod_name in installed_mods:
                self._model.enable_mod(installed_mods[mod_name])
                applied_count += 1

        if applied_count < len(mod_list):
            missing = len(mod_list) - applied_count
            QMessageBox.warning(
                self._view,
                "Some Mods Missing",
                f"{missing} mods from the code are not installed.",
            )

    def _confirm_code_import(self, mod_count: int) -> bool:
        reply = QMessageBox.question(
            self._view,
            "Import Share Code",
            f"This will replace your current active mods with {mod_count} mods from the code. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _import_mod(self):
        dialog = ImportDialog(self._view)
        dialog.mod_import_requested.connect(self._handle_import_mod)
        dialog.exec()

    def _handle_import_mod(self, archive_path: str):
        if self._model.import_mod(archive_path):
            self._update_view()

    def _open_preferences(self):
        dialog = PreferencesDialog(self._config, self._view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_data()
            self._model.refresh_all()

    def _open_user_manual(self):
        dialog = UserManualDialog(self._view)
        dialog.exec()

    def _open_about(self):
        dialog = AboutDialog(self._view, QApplication.applicationVersion())
        dialog.exec()

    def _check_app_update(self):
        CheckUpdateDialog(self._view, QApplication.applicationVersion())

    def _change_font(self, font_name):
        if font_name == "default":
            font = QFont("Inter-Regular", 10)
            self._view.set_font(font)
            self._config.set_font("default")
        elif font_name == "dyslexia":
            QFontDatabase.addApplicationFont(":/assets/fonts/OpenDyslexic-Regular.otf")
            font = QFont("OpenDyslexic", 10)
            self._view.set_font(font)
            self._config.set_font("dyslexia")

    @staticmethod
    def _get_mod_from_item(item: Optional[QListWidgetItem]) -> Optional[Mod]:
        return item.data(256) if item else None

    @staticmethod
    def _validate_share_data(data: Dict) -> bool:
        required_keys = ["version", "mods"]
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data["mods"], list):
            return False

        for mod_data in data["mods"]:
            if not isinstance(mod_data, dict) or "name" not in mod_data:
                return False

        return True
