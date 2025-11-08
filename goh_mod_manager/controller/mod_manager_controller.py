import base64
import datetime
import platform
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QPoint
from PySide6.QtGui import QFont, QFontDatabase, Qt, QBrush, QColor, QPalette
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QMenu, QMessageBox
from loguru import logger

from goh_mod_manager.model.mod import Mod
from goh_mod_manager.model.mod_manager_model import ModManagerModel
from goh_mod_manager.view.dialogs.about_dialog import AboutDialog
from goh_mod_manager.view.dialogs.export_code_dialog import ExportCodeDialog
from goh_mod_manager.view.dialogs.import_code_dialog import ImportCodeDialog
from goh_mod_manager.view.dialogs.import_details import DetailedMessageDialog
from goh_mod_manager.view.dialogs.import_dialog import ImportDialog
from goh_mod_manager.view.dialogs.preferences_dialog import PreferencesDialog
from goh_mod_manager.view.dialogs.preset_dialog import PresetDialog
from goh_mod_manager.view.dialogs.user_manual_dialog import UserManualDialog
from goh_mod_manager.view.mod_manager_view import ModManagerView


class ModManagerController(QObject):
    """
    Controller for the Gates of Hell mod manager application.

    Manages interactions between the model and view, handles user input,
    and coordinates application functionality including mod management,
    presets, configuration, and import/export operations.
    """

    def __init__(self, model: ModManagerModel, view: ModManagerView):
        """
        Initialize the controller with model and view instances.

        Args:
            model: The mod manager model instance
            view: The mod manager view instance
        """
        super().__init__()
        self._model = model
        self._view = view
        self._config = self._model.get_config()
        self._initialize()

    def show(self) -> None:
        """Display the main application window."""
        self._view.show()

    # ================== INITIALIZATION ==================

    def _initialize(self) -> None:
        """
        Initialize the controller by setting up configuration, loading data, and connecting signals.

        This method ensures the application is properly configured before use.
        """
        self._ensure_config_valid()
        self._load_data()
        self._connect_signals()
        self._apply_user_preferences()

    def _ensure_config_valid(self) -> None:
        """
        Ensure configuration is valid, open setup dialogs if not.

        Shows user manual and preferences dialog if required paths are missing.
        Exits application if user cancels configuration setup.
        """
        if not self._config.get_mods_directory() or not self._config.get_options_file():
            self._open_user_manual()
            dialog = PreferencesDialog(self._config, self._view)
            if dialog.exec() == QDialog.DialogCode.Rejected:
                sys.exit(1)

    def _load_data(self) -> None:
        """Load configuration data and update the view with initial state."""
        self._model.set_mods_directory(self._config.get_mods_directory())
        self._model.set_options_file(self._config.get_options_file())
        self._model.set_presets(self._config.get_presets())
        self._update_view()
        self._view.update_active_mods_count(self._model.get_active_mods_count())
        self._on_preset_selection_changed(self._view.get_current_preset_name())

    def _apply_user_preferences(self) -> None:
        """Apply user preferences from configuration."""
        self._change_font(self._config.get_font())

    def _connect_signals(self) -> None:
        """Connect all signals from model and view to their respective handlers."""
        self._connect_model_signals()
        self._connect_menu_signals()
        self._connect_button_signals()
        self._connect_list_signals()
        self._connect_ui_signals()

    def _connect_model_signals(self) -> None:
        """Connect model signals to update handlers."""
        self._model.installed_mods_signal.connect(self._update_view)
        self._model.presets_signal.connect(self._update_view)
        self._model.mods_counter_signal.connect(self._view.update_active_mods_count)

    def _connect_menu_signals(self) -> None:
        """Connect menu action signals to their handlers."""
        # File menu
        self._view.ui.actionOpen_game_folder.triggered.connect(self._open_game_folder)
        self._view.ui.actionOpen_mods_folder.triggered.connect(self._open_mods_folder)
        self._view.ui.actionOpen_options_file.triggered.connect(self._open_options_file)
        self._view.ui.actionOpen_logs.triggered.connect(self._open_logs)
        self._view.ui.actionExit.triggered.connect(self._view.close)

        # Edit menu
        self._view.ui.actionSettings.triggered.connect(self._open_preferences)

        # View menu
        self._view.ui.actionRefresh.triggered.connect(self._refresh_all)
        self._view.ui.actionShow_mod_informations.triggered.connect(
            self._toggle_mod_details
        )
        # self._view.ui.actionZoom_in.triggered.connect()
        # self._view.ui.actionZoom_out.triggered.connect()
        # self._view.ui.actionReset_zoom.triggered.connect()

        # Font menu
        self._view.ui.actionDefault.triggered.connect(
            lambda: self._change_font("default")
        )
        self._view.ui.actionDyslexic.triggered.connect(
            lambda: self._change_font("dyslexia")
        )

        # Import menu
        self._view.ui.action_load_order_from_code.triggered.connect(
            self._open_import_code
        )
        self._view.ui.action_local_mod.triggered.connect(self._import_mod)

        # Export menu
        self._view.ui.action_load_order_as_code.triggered.connect(
            self._open_export_code
        )

        # Help menu
        self._view.ui.actionUser_manual.triggered.connect(self._open_user_manual)
        self._view.ui.actionGenerate_Help_File.triggered.connect(self._generate_help_file)
        self._view.ui.actionAbout.triggered.connect(self._open_about)

    def _connect_button_signals(self) -> None:
        """Connect button click signals to their handlers."""
        # Mod management buttons
        self._view.ui.pushButton_refresh_available_mods.clicked.connect(
            self._refresh_installed_mods
        )
        self._view.ui.pushButton_add.clicked.connect(self._enable_selected_mod)
        self._view.ui.pushButton_remove.clicked.connect(self._disable_selected_mod)
        self._view.ui.pushButton_move_up.clicked.connect(self._move_up)
        self._view.ui.pushButton_move_down.clicked.connect(self._move_down)
        self._view.ui.pushButton_clear_all.clicked.connect(self._clear_active_mods)

        # Preset management buttons
        self._view.ui.pushButton_save_preset.clicked.connect(self._save_preset)
        self._view.ui.pushButton_load_preset.clicked.connect(self._load_preset)
        self._view.ui.pushButton_delete_preset.clicked.connect(self._delete_preset)

    def _connect_list_signals(self) -> None:
        """Connect list widget signals to their handlers."""
        # Double-click actions
        self._view.ui.listWidget_available_mods.itemDoubleClicked.connect(
            self._enable_mod_from_item
        )
        self._view.ui.listWidget_active_mods.itemDoubleClicked.connect(
            self._disable_mod_from_item
        )

        # Selection changes
        self._view.ui.listWidget_available_mods.currentItemChanged.connect(
            self._on_mod_selected
        )
        self._view.ui.listWidget_active_mods.currentItemChanged.connect(
            self._on_mod_selected
        )

        # Drag and drop reordering
        self._view.ui.listWidget_active_mods.model().rowsMoved.connect(
            self._save_mods_order
        )

        # Context menu
        self._view.ui.listWidget_available_mods.customContextMenuRequested.connect(
            self._handle_context_menu
        )

    def _connect_ui_signals(self) -> None:
        """Connect UI element signals to their handlers."""
        # Preset selection
        self._view.ui.comboBox_presets.currentTextChanged.connect(
            self._on_preset_selection_changed
        )

        # Search filtering
        self._view.ui.lineEdit_search_available_mods.textChanged.connect(
            self._filter_installed_mods
        )
        self._view.ui.lineEdit_search_active_mods.textChanged.connect(
            self._filter_active_mods
        )

    # ================== MENU ACTIONS ==================

    def _open_game_folder(self):
        folder_path = self._config.get_game_directory()
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder_path)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            self._view.show_error(
                "Open Folder Error", f"Failed to open game folder: {str(e)}"
            )

    def _open_mods_folder(self):
        folder_path = self._config.get_mods_directory()
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder_path)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            self._view.show_error(
                "Open Folder Error", f"Failed to open mods folder: {str(e)}"
            )

    def _open_options_file(self):
        folder_path = self._config.get_options_file()
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder_path)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            self._view.show_error(
                "Open Folder Error", f"Failed to open game folder: {str(e)}"
            )

    def _open_logs(self):
        project_root = Path(__file__).resolve().parent.parent.parent
        log_file = project_root / "logs" / "goh_mod_manager.log"
        logger.info(f"Opening log file: {log_file}")
        try:
            if sys.platform.startswith("win"):
                os.startfile(log_file)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", log_file])
            else:
                subprocess.Popen(["xdg-open", log_file])
        except Exception as e:
            self._view.show_error(
                "Open Log Error", f"Failed to open log file: {str(e)}"
            )

    # ================== MOD MANAGEMENT ==================

    def _enable_mod_from_item(self, item: QListWidgetItem) -> None:
        """
        Enable a mod from a list widget item double-click.
        """
        mod = self._get_mod_from_item(item)
        if mod:
            self._enable_mods([mod])

    def _disable_mod_from_item(self, item: QListWidgetItem) -> None:
        """
        Disable a mod from a list widget item double-click.

        Args:
            item: The clicked list widget item containing mod data
        """
        mod = self._get_mod_from_item(item)
        if mod:
            self._model.disable_mod(mod)

    def _enable_selected_mod(self) -> None:
        """
        Enable all currently selected mods from the available list.
        """
        mods = [
            self._get_mod_from_item(item)
            for item in self._view.get_current_available_mod()
        ]
        mods = [m for m in mods if m]
        if not mods:
            return

        self._enable_mods(mods)

    def _enable_mods(self, mods: list) -> None:
        """
        Enable one or more mods, checking for missing dependencies.
        Asks the user for confirmation through the view if dependencies are missing.
        """
        active_mods = self._model.get_active_mods()
        installed_mods = self._model.get_installed_mods()

        for mod in mods:
            missing = self._get_missing_dependencies(mod, active_mods, installed_mods)

            if missing:
                dep_names = ", ".join(m.name for m in missing)

                # Format text properly (remove custom tags for dialogs)
                title = self._view.parse_formatted_text(f"Missing dependencies")
                text = self._view.parse_formatted_text(
                    f"The mod '{mod.name}' requires the following dependencies:\n\n"
                    f"{dep_names}\n\n"
                    "Would you like to enable them as well?"
                )

                if self._view.ask_confirmation(
                    title, text, default=QMessageBox.StandardButton.Yes
                ):
                    for dep in missing:
                        self._model.enable_mod(dep)

            # Finally, enable the main mod
            self._model.enable_mod(mod)

    def _get_missing_dependencies(self, mod, active_mods, installed_mods, visited=None):
        """
        Recursively return a list of missing dependency mods that are not yet enabled,
        in the correct load order (deepest dependencies first).

        Args:
            mod: The Mod object whose dependencies to resolve.
            active_mods: List of currently active mods.
            installed_mods: List of all installed mods.
            visited: Set of mod IDs that were already processed (prevents infinite loops).

        Returns:
            A list of Mod objects that are required but not currently enabled,
            ordered so that dependencies appear before the mods that depend on them.
        """

        # Initialize the visited set if this is the top-level call
        if visited is None:
            visited = set()

        # Skip if we've already processed this mod (prevents circular dependencies)
        if mod.id in visited:
            return []

        visited.add(mod.id)

        # If this mod has no dependencies, return empty
        if not mod.require:
            return []

        # Prepare lookup sets/dicts for quick access
        required_ids = str(mod.require).split()
        active_ids = {m.id for m in active_mods}
        installed_by_id = {m.id: m for m in installed_mods}

        missing = []

        for req_id in required_ids:
            # Skip dependencies that are not installed at all
            if req_id not in installed_by_id:
                continue

            req_mod = installed_by_id[req_id]

            # Recursively check dependencies of this dependency first
            sub_missing = self._get_missing_dependencies(
                req_mod, active_mods, installed_mods, visited
            )

            # Add the sub-dependencies first (deep dependencies first)
            for sub_mod in sub_missing:
                if sub_mod not in missing:
                    missing.append(sub_mod)

            # Then add the current required mod itself if it's not active
            if req_id not in active_ids and req_mod not in missing:
                missing.append(req_mod)

        return missing

    def _disable_selected_mod(self) -> None:
        """Disable all currently selected mods from the active list."""
        mods = [
            self._get_mod_from_item(item)
            for item in self._view.get_current_active_mod()
        ]
        for mod in mods:
            if mod:
                self._model.disable_mod(mod)

    def _move_up(self) -> None:
        """Move selected active mod up in the load order."""
        if self._view.move_active_mod_up():
            self._save_mods_order()

    def _move_down(self) -> None:
        """Move selected active mod down in the load order."""
        if self._view.move_active_mod_down():
            self._save_mods_order()

    def _save_mods_order(self) -> None:
        """Save the current order of active mods to the model."""
        reordered_mods = self._view.get_active_mods_order()
        self._model.set_mods_order(reordered_mods)

    def _clear_active_mods(self) -> None:
        """Clear all active mods after user confirmation."""
        if not self._model.get_active_mods():
            self._view.show_message(
                title="No Active Mods",
                text="There are no active mods to clear.",
                icon="information",
            )
            return

        if self._view.ask_confirmation(
            "Clear All Mods", "Are you sure you want to clear all active mods?"
        ):
            self._model.clear_active_mods()

    def _handle_context_menu(self, pos: QPoint) -> None:
        """
        Handle right-click context menu on available mods list.

        Args:
            pos: Position where the context menu was requested
        """
        item = self._view.ui.listWidget_available_mods.itemAt(pos)
        if not item:
            return

        mod = self._get_mod_from_item(item)
        if not mod:
            return

        menu = QMenu(self._view.ui.listWidget_available_mods)

        # Add "Open Folder" action
        open_folder_action = menu.addAction("Open Folder")
        open_folder_action.triggered.connect(
            lambda: self._open_mod_folder(mod.folderPath)
        )

        # Add "Open Workshop" action
        open_workshop_action = menu.addAction("Open Workshop")
        open_workshop_action.triggered.connect(lambda: self._open_steam_page(mod.id))

        # Add "Delete" action for manually installed mods
        if mod.manualInstall:
            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(
                lambda: self._delete_mod_with_confirmation(item, mod)
            )

        menu.exec(self._view.ui.listWidget_available_mods.mapToGlobal(pos))

    def _open_mod_folder(self, folder_path: str) -> None:
        """
        Open mod folder in system file explorer.

        Args:
            folder_path: Path to the mod folder
        """
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder_path)
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            self._view.show_error(
                "Open Folder Error", f"Failed to open mod folder: {str(e)}"
            )

    def _open_steam_page(self, mod_id: str) -> None:
        """
        Open the workshop page for a mod on Steam.

        Args:
            mod_id: The Steam mod ID
        """
        try:
            if sys.platform.startswith("win"):
                os.startfile(f"steam://url/CommunityFilePage/{mod_id}")
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", f"steam://url/CommunityFilePage/{mod_id}"])
            else:
                subprocess.Popen(
                    ["xdg-open", f"steam://url/CommunityFilePage/{mod_id}"]
                )
        except Exception as e:
            self._view.show_error(
                "Open Steam Page Error", f"Failed to open Steam page: {str(e)}"
            )

    def _delete_mod_with_confirmation(self, item: QListWidgetItem, mod: Mod) -> None:
        """
        Delete a mod after user confirmation.

        Args:
            item: The list widget item to remove
            mod: The mod to delete
        """
        if self._view.ask_confirmation(
            "Delete Mod",
            f"Are you sure you want to permanently delete '{mod.name}'?\nThis cannot be undone.",
        ):
            row = self._view.ui.listWidget_available_mods.row(item)
            self._view.ui.listWidget_available_mods.takeItem(row)

            if self._model.delete_mod(mod):
                self._view.show_message(
                    title="Mod Deleted", text=f"'{mod.name}' has been deleted."
                )
            else:
                self._view.show_error(
                    "Delete Error",
                    f"Failed to delete '{mod.name}'. Check file permissions.",
                )

    # ================== DATA REFRESH ==================

    def _refresh_all(self) -> None:
        """Refresh all data and clear search filters."""
        self._model.refresh_all()
        self._clear_search_filters()

    def _refresh_installed_mods(self) -> None:
        """Refresh only the installed mods list."""
        self._model.refresh_installed_mods()

    # ================== VIEW UPDATES ==================

    def _update_view(self) -> None:
        """Update the view with current model data."""
        self._view.populate_mod_lists(
            self._model.get_installed_mods(), self._model.get_active_mods()
        )
        self._view.update_presets(
            self._model.get_presets_names(), self._view.get_current_preset_name()
        )

    def _on_mod_selected(self, current: QListWidgetItem) -> None:
        """
        Handle mod selection changes in lists.
        """
        mod = self._get_mod_from_item(current) if current else None
        self._view.update_mod_details(mod)

        # Palette courante pour déterminer la couleur par défaut
        palette = self._view.ui.listWidget_available_mods.palette()
        default_text_color = palette.color(QPalette.Text)

        if not mod:
            self._reset_mod_colors(default_text_color)
            return

        required_ids = str(mod.require).split() if getattr(mod, "require", None) else []

        for i in range(self._view.ui.listWidget_available_mods.count()):
            item = self._view.ui.listWidget_available_mods.item(i)
            item_mod = item.data(Qt.UserRole)

            if item_mod.id in required_ids:
                item.setForeground(QBrush(QColor("#E67E22")))  # orange si dépendance
            else:
                item.setForeground(QBrush(default_text_color))  # couleur du thème

    def _reset_mod_colors(self, color=None):
        """Réinitialise les couleurs de tous les mods dans la liste."""
        palette = self._view.ui.listWidget_available_mods.palette()
        default_text_color = color or palette.color(QPalette.Text)

        for i in range(self._view.ui.listWidget_available_mods.count()):
            item = self._view.ui.listWidget_available_mods.item(i)
            item.setForeground(QBrush(default_text_color))

    def _toggle_mod_details(self, checked: bool) -> None:
        """
        Toggle mod details panel visibility.

        Args:
            checked: Whether the mod details should be visible
        """
        self._view.ui.groupBox_mod_informations.setVisible(checked)

    # ================== PRESET MANAGEMENT ==================

    def _save_preset(self) -> None:
        """Save current active mods as a new preset."""
        if self._model.get_active_mods_count() == 0:
            self._view.show_message(
                title="Empty Preset",
                text="Cannot save an empty preset. Add mods to the list first.",
                icon="warning",
            )
            return

        dialog = PresetDialog(
            parent=self._view, existing_presets=self._model.get_presets_names()
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        preset_name = dialog.get_preset_name()
        if not preset_name:
            return

        # Check for existing preset and confirm overwrite
        if self._model.has_preset(preset_name):
            if not self._confirm_preset_overwrite(preset_name):
                return

        if self._model.save_preset(preset_name):
            self._view.show_message(
                title="Preset Saved", text=f"Preset '{preset_name}' has been saved."
            )

    def _load_preset(self) -> None:
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
            self._view.show_error(
                title="Preset Not Found", text=f"Preset '{preset_name}' was not found."
            )
            return

        if self._confirm_preset_load(preset_name):
            success = self._model.load_preset(preset_name)
            if success:
                self._view.show_message(
                    title="Preset Loaded",
                    text=f"Preset '{preset_name}' has been loaded.",
                )

    def _delete_preset(self) -> None:
        """Delete the selected preset."""
        preset_name = self._view.get_current_preset_name()
        if not preset_name:
            self._view.show_message(
                title="No Preset Selected",
                text="Please select a preset to delete.",
                icon="warning",
            )
            return

        if not self._model.has_preset(preset_name):
            return

        if self._confirm_preset_deletion(preset_name):
            if self._model.delete_preset(preset_name):
                self._view.show_message(
                    title="Preset Deleted",
                    text=f"Preset '{preset_name}' has been deleted.",
                )

    def _on_preset_selection_changed(self, preset_name: str) -> None:
        """
        Handle preset selection changes in the dropdown.

        Args:
            preset_name: Name of the selected preset
        """
        if not preset_name or not self._model.has_preset(preset_name):
            self._view.ui.listWidget_presets.clear()
            return

        preset_mods = self._model.get_preset_mods(preset_name)
        self._view.ui.listWidget_presets.clear()

        for mod in preset_mods:
            item = QListWidgetItem(self._view.parse_clear_text(mod.name))
            item.setData(Qt.UserRole, mod)
            self._view.ui.listWidget_presets.addItem(item)

    # ================== CONFIRMATION DIALOGS ==================

    def _confirm_preset_overwrite(self, preset_name: str) -> bool:
        """
        Confirm preset overwrite with user.

        Args:
            preset_name: Name of the preset to overwrite

        Returns:
            True if user confirms overwrite
        """
        return self._view.ask_confirmation(
            "Existing Preset", f"Preset '{preset_name}' already exists. Overwrite?"
        )

    def _confirm_preset_load(self, preset_name: str) -> bool:
        """
        Confirm preset loading with user.

        Args:
            preset_name: Name of the preset to load

        Returns:
            True if user confirms loading
        """
        return self._view.ask_confirmation(
            "Load Preset",
            f"Loading preset '{preset_name}' will clear the current list of mods. Continue?",
        )

    def _confirm_preset_deletion(self, preset_name: str) -> bool:
        """
        Confirm preset deletion with user.

        Args:
            preset_name: Name of the preset to delete

        Returns:
            True if user confirms deletion
        """
        return self._view.ask_confirmation(
            "Delete Preset",
            f"Are you sure you want to delete preset '{preset_name}'?\nThis cannot be undone.",
        )

    def _confirm_share_code_import(self, mod_count: int) -> bool:
        """
        Confirm share code import with user.

        Args:
            mod_count: Number of mods in the share code

        Returns:
            True if user confirms import
        """
        return self._view.ask_confirmation(
            "Import Share Code",
            f"This will replace your current active mods with {mod_count} mods from the code. Continue?",
        )

    # ================== SEARCH FILTERING ==================

    def _filter_installed_mods(self, search_text: str) -> None:
        """
        Filter installed mods list based on search text.

        Args:
            search_text: Text to search for in mod names and descriptions
        """
        self._filter_list_widget(self._view.ui.listWidget_available_mods, search_text)

    def _filter_active_mods(self, search_text: str) -> None:
        """
        Filter active mods list based on search text.

        Args:
            search_text: Text to search for in mod names and descriptions
        """
        self._filter_list_widget(self._view.ui.listWidget_active_mods, search_text)

    def _filter_list_widget(self, list_widget, search_text: str) -> None:
        """
        Filter items in a list widget based on search text.

        Args:
            list_widget: The list widget to filter
            search_text: Text to search for
        """
        search_text = search_text.lower().strip()

        for i in range(list_widget.count()):
            item = list_widget.item(i)
            mod = self._get_mod_from_item(item)

            if not search_text:
                item.setHidden(False)
            else:
                # Search in mod name and description
                mod_name = mod.name.lower() if mod and mod.name else ""
                mod_desc = mod.desc.lower() if mod and mod.desc else ""
                mod_id = mod.id.lower() if mod and mod.id else ""

                is_visible = (
                    search_text in mod_name
                    or search_text in mod_desc
                    or search_text in mod_id
                )
                item.setHidden(not is_visible)

    def _clear_search_filters(self) -> None:
        """Clear all search filters and show all items."""
        self._view.ui.lineEdit_search_installed.clear()
        self._view.ui.lineEdit_search_active.clear()

    # ================== SHARE CODE FUNCTIONALITY ==================

    def _export_share_code(self) -> None:
        """Export active mods as a shareable base64 code."""
        active_mods = self._model.get_active_mods()
        if not active_mods:
            self._view.show_message(
                title="No Active Mods",
                text="Add mods to the active list first.",
                icon="warning",
            )
            return

        share_data = {
            "version": 1,
            "mods": [{"name": mod.name, "id": mod.id} for mod in active_mods],
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
            self._view.show_error(
                title="Export Error", text=f"Failed to generate share code: {str(e)}"
            )

    def _import_share_code(self) -> None:
        """Import mods from a share code."""
        code = self._view.ui.lineEdit_share_code.text().strip()
        if not code:
            self._view.show_message(
                title="Empty Code", text="Enter a share code first.", icon="warning"
            )
            return

        try:
            json_str = base64.b64decode(code.encode("utf-8")).decode("utf-8")
            share_data = json.loads(json_str)

            if not self._validate_share_data(share_data):
                raise ValueError("Invalid share code format")

            mod_count = len(share_data["mods"])
            if not self._confirm_share_code_import(mod_count):
                return

            applied_count = self._apply_share_code(share_data["mods"])

            if applied_count == mod_count:
                self._view.show_message(
                    title="Code Imported",
                    text=f"Successfully imported all {mod_count} mods.",
                )
            else:
                missing_count = mod_count - applied_count
                self._view.show_message(
                    title="Partial Import",
                    text=f"Imported {applied_count} of {mod_count} mods.\n{missing_count} mods are not installed.",
                    icon="warning",
                )

        except Exception as e:
            self._view.show_error(
                title="Import Error", text=f"Invalid share code: {str(e)}"
            )

    def _apply_share_code(self, mod_list: List[Dict]) -> int:
        """
        Apply share code by enabling specified mods.

        Args:
            mod_list: List of mod data from share code

        Returns:
            Number of mods successfully applied
        """
        self._model.clear_active_mods()

        # Create lookup maps for both name and ID
        installed_mods = self._model.get_installed_mods()
        mods_by_name = {mod.name: mod for mod in installed_mods}
        mods_by_id = {mod.id: mod for mod in installed_mods}

        applied_count = 0

        for mod_data in mod_list:
            mod = None

            # Try to find by ID first, then by name
            if "id" in mod_data and mod_data["id"] in mods_by_id:
                mod = mods_by_id[mod_data["id"]]
            elif "name" in mod_data and mod_data["name"] in mods_by_name:
                mod = mods_by_name[mod_data["name"]]

            if mod:
                self._model.enable_mod(mod)
                applied_count += 1

        return applied_count

    # ================== DIALOG MANAGEMENT ==================

    def _import_mod(self) -> None:
        """Open the mod import dialog."""
        dialog = ImportDialog(self._view)
        dialog.mod_import_requested.connect(self._handle_mod_import)
        dialog.exec()

    def _handle_mod_import(self, archive_path: str) -> None:
        """
        Handle mod import from file path.

        Args:
            archive_path: Path to the mod file/directory to import
        """
        if self._model.import_mod(archive_path):
            self._view.show_message(
                title="Import Successful", text="Mod has been imported successfully."
            )
            self._update_view()
        else:
            self._view.show_error(
                title="Import Failed",
                text="Failed to import mod. Check the file format and try again.",
            )

    def _open_preferences(self) -> None:
        """Open the preferences dialog."""
        dialog = PreferencesDialog(self._config, self._view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload data if preferences changed
            self._load_data()
            self._model.refresh_all()

    def _open_user_manual(self) -> None:
        """Open the user manual dialog."""
        dialog = UserManualDialog(self._view)
        dialog.exec()

    def _generate_help_file(self) -> None:
        """Generate a help file containing load order and configuration details."""
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"help-{now}.txt"
            output_dir = os.path.abspath(".")
            filepath = os.path.join(output_dir, filename)

            logger.info(f"Generating help file: {filepath}")

            options_file = self._config.get_options_file()
            load_order = self._model.get_active_mods()

            if os.path.exists(options_file):
                with open(options_file, "r", encoding="utf-8") as f:
                    config_content = f.read()
            else:
                config_content = f"[!] Options file not found: {options_file}"
                logger.warning(config_content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=== HELP FILE ===\n")
                f.write(f"Generated on: {datetime.datetime.now()}\n\n")

                f.write("=== LOAD ORDER ===\n")
                for i, mod in enumerate(load_order, start=1):
                    f.write(f"{i}. {mod}\n")

                f.write("\n=== CONFIGURATION FILE ===\n")
                f.write(f"Source: {options_file}\n\n")
                f.write(config_content)

            system = platform.system()
            try:
                if system == "Windows":
                    os.startfile(output_dir)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", output_dir], check=False)
                else:  # Linux
                    subprocess.run(["xdg-open", output_dir], check=False)

                logger.info(f"Opened folder: {output_dir}")
            except Exception as e:
                logger.warning(f"Could not open folder: {e}")

            logger.info(f"Help file successfully generated: {filepath}")

        except Exception as e:
            logger.error(f"Failed to generate help file: {e}", exc_info=True)

    def _open_about(self) -> None:
        """Open the about dialog."""
        dialog = AboutDialog(self._view, QApplication.applicationVersion())
        dialog.exec()

    def _open_export_code(self):
        active_mods = self._model.get_active_mods()
        if not active_mods:
            self._view.show_message(
                title="No Active Mods",
                text="Add mods to the active list first.",
                icon="warning",
            )
            return

        mod_data = [{"id": str(mod.id), "name": mod.name} for mod in active_mods]
        code = self._generate_code(mod_data)

        dialog = ExportCodeDialog(self._view)
        dialog.set_code(code, len(mod_data))
        dialog.exec()

    def _open_import_code(self):
        dialog = ImportCodeDialog(self._view)
        dialog.import_requested.connect(self._handle_import)
        dialog.exec()

    def _handle_import(self, code: str):
        try:
            mod_data = self._decode_code(code)
            found_mods, missing_mods = self._apply_mod_data(mod_data)

            self._show_import_result(found_mods, missing_mods, len(mod_data))

        except Exception as e:
            self._view.show_error(
                title="Import Error", text=f"Invalid share code: {str(e)}"
            )

    def _generate_code(self, mod_data: List[Dict]) -> str:
        # to JSON
        json_string = json.dumps(mod_data, separators=(",", ":"))

        # Encode to base64
        b64_bytes = base64.b64encode(json_string.encode("utf-8"))
        return b64_bytes.decode("utf-8")

    def _decode_code(self, code: str) -> List[Dict]:
        try:
            clean_code = code.strip().replace(" ", "").replace("\n", "")

            # Decode base64 code
            json_bytes = base64.b64decode(clean_code)
            json_string = json_bytes.decode("utf-8")

            # Parse JSON
            mod_data = json.loads(json_string)

            # Is valid
            if not isinstance(mod_data, list):
                raise ValueError("Invalid data structure")

            for item in mod_data:
                if not isinstance(item, dict) or "id" not in item:
                    raise ValueError("Invalid mod data structure")

            return mod_data

        except Exception as e:
            raise ValueError(f"Cannot decode share code: {str(e)}")

    def _apply_mod_data(self, mod_data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        self._model.clear_active_mods()

        installed_mods = {str(mod.id): mod for mod in self._model.get_installed_mods()}

        found_mods = []
        missing_mods = []

        for mod_info in mod_data:
            mod_id = str(mod_info["id"])

            if mod_id in installed_mods:
                mod = installed_mods[mod_id]
                self._model.enable_mod(mod)
                found_mods.append(
                    {
                        "id": mod_id,
                        "name": mod.name,
                    }
                )
            else:
                missing_mods.append(
                    {
                        "id": mod_id,
                        "name": mod_info.get("name", "Unknown Mod"),
                    }
                )

        return found_mods, missing_mods

    def _show_import_result(
        self, found_mods: List[Dict], missing_mods: List[Dict], total_count: int
    ):
        found_count = len(found_mods)
        missing_count = len(missing_mods)

        if missing_count == 0:
            self._view.show_message(
                title="Import Successful",
                text=f"Successfully loaded {total_count} mods.",
                icon="info",
            )
        else:
            self._show_missing_mods_dialog(found_count, missing_mods, total_count)

    def _show_missing_mods_dialog(
        self, found_count: int, missing_mods: List[Dict], total_count: int
    ):
        missing_count = len(missing_mods)

        missing_list = []
        for mod in missing_mods:
            missing_list.append(f"• {mod['name']} (ID: {mod['id']})")

        missing_text = "\n".join(missing_list)

        message = f"Loaded {found_count} of {total_count} mods.\n\n"
        message += f"Missing mods ({missing_count}):\n{missing_text}"

        dialog = DetailedMessageDialog(self._view)
        dialog.set_title("Partial Import")
        dialog.set_message(f"Loaded {found_count} of {total_count} mods.")
        dialog.set_details(f"Missing mods ({missing_count}):", missing_text)
        dialog.exec()

    # ================== FONT MANAGEMENT ==================

    def _change_font(self, font_name: str) -> None:
        """
        Change the application font.

        Args:
            font_name: Name of the font to apply ("default" or "dyslexia")
        """
        if font_name == "default" or font_name == "":
            QFontDatabase.addApplicationFont(":/assets/font/Inter-Regular.otf")
            font = QFont("Inter", 10)
            self._view.set_application_font(font)
            self._config.set_font("default")
        elif font_name == "dyslexia":
            QFontDatabase.addApplicationFont(":/assets/font/OpenDyslexic-Regular.otf")
            font = QFont("OpenDyslexic", 10)
            self._view.set_application_font(font)
            self._config.set_font("dyslexia")

    # ================== UTILITY METHODS ==================

    @staticmethod
    def _get_mod_from_item(item: Optional[QListWidgetItem]) -> Optional[Mod]:
        """
        Extract mod data from a list widget item.

        Args:
            item: The list widget item to extract data from

        Returns:
            The mod object stored in the item, or None if not found
        """
        return item.data(Qt.UserRole) if item else None

    @staticmethod
    def _validate_share_data(data: Dict) -> bool:
        """
        Validate the structure of share code data.

        Args:
            data: Decoded share code data

        Returns:
            True if data structure is valid
        """
        # Check required top-level keys
        required_keys = ["version", "mods"]
        if not all(key in data for key in required_keys):
            return False

        # Check mods list structure
        if not isinstance(data["mods"], list):
            return False

        # Validate each mod entry
        for mod_data in data["mods"]:
            if not isinstance(mod_data, dict):
                return False
            if "name" not in mod_data:
                return False

        return True
