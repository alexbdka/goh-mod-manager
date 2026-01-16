import sys
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QPoint, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QMenu, QMessageBox

from goh_mod_manager.core.mod import Mod
from goh_mod_manager.core.mod_manager_model import ModManagerModel
from goh_mod_manager.i18n.translator import TranslationManager
from goh_mod_manager.infrastructure.mod_manager_logger import logger
from goh_mod_manager.presentation.view.dialogs.export_code_dialog import (
    ExportCodeDialog,
)
from goh_mod_manager.presentation.view.dialogs.import_code_dialog import (
    ImportCodeDialog,
)
from goh_mod_manager.presentation.view.dialogs.import_details import (
    DetailedMessageDialog,
)
from goh_mod_manager.presentation.view.dialogs.import_dialog import ImportDialog
from goh_mod_manager.presentation.view.dialogs.preset_dialog import PresetDialog
from goh_mod_manager.presentation.view.guided_tour_overlay import (
    GuidedTourOverlay,
    GuidedTourStep,
    GuidedTourTargetAction,
)
from goh_mod_manager.presentation.view.mod_manager_view import ModManagerView
from goh_mod_manager.presentation.viewmodels.appearance_view_model import (
    AppearanceViewModel,
)
from goh_mod_manager.presentation.viewmodels.dialog_actions_view_model import (
    DialogActionsViewModel,
)
from goh_mod_manager.presentation.viewmodels.file_actions_view_model import (
    FileActionsViewModel,
)
from goh_mod_manager.presentation.viewmodels.import_export_view_model import (
    ImportExportViewModel,
)
from goh_mod_manager.presentation.viewmodels.main_view_model import MainViewModel
from goh_mod_manager.presentation.viewmodels.mod_actions_view_model import (
    ModActionsViewModel,
)
from goh_mod_manager.presentation.viewmodels.mod_details_view_model import (
    ModDetailsViewModel,
)
from goh_mod_manager.presentation.viewmodels.presets_view_model import PresetsViewModel


class ModManagerController(QObject):
    """
    UI coordinator that wires views to viewmodels and handles user interactions.
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
        self._view_model = MainViewModel(self._model)
        self._import_export_view_model = ImportExportViewModel(self._model)
        self._presets_view_model = PresetsViewModel(self._model)
        self._mod_actions_view_model = ModActionsViewModel(self._model)
        self._file_actions_view_model = FileActionsViewModel(self._model, self._config)
        self._appearance_view_model = AppearanceViewModel(self._config)
        self._dialog_actions_view_model = DialogActionsViewModel(self._config)
        self._mod_details_view_model = ModDetailsViewModel()
        self._initialize()

    def show(self) -> None:
        """Display the main application window."""
        self._view.show()
        QTimer.singleShot(0, self._maybe_start_guided_tour)

    def _initialize(self) -> None:
        """
        Initialize the controller by setting up configuration, loading data, and connecting signals.

        This method ensures the application is properly configured before use.
        """
        self._ensure_config_valid()
        self._connect_signals()
        self._load_data()
        self._apply_user_preferences()
        self._setup_guided_tour()

    def _ensure_config_valid(self) -> None:
        """
        Ensure configuration is valid, open setup dialogs if not.

        Shows preferences dialog if required paths are missing.
        Exits application if user cancels configuration setup.
        """
        if not self._config.get_mods_directory() or not self._config.get_options_file():
            current_language = self._config.get_language()
            if not self._dialog_actions_view_model.open_preferences(
                self._view, on_start_guided_tour=self._start_guided_tour
            ):
                sys.exit(1)
            if self._config.get_language() != current_language:
                self._apply_language_change(self._config.get_language())

    def _load_data(self) -> None:
        """Load configuration data and update the view with initial state."""
        self._view_model.load_from_config(
            self._config.get_mods_directory(),
            self._config.get_options_file(),
            self._config.get_presets(),
        )
        self._on_preset_selection_changed(self._view.get_current_preset_name())

    def _apply_user_preferences(self) -> None:
        """Apply user preferences from configuration."""
        font = self._appearance_view_model.apply_saved_font()
        self._view.set_application_font(font)

    def _connect_signals(self) -> None:
        """Connect all signals from model and view to their respective handlers."""
        self._connect_view_model_signals()
        self._connect_menu_signals()
        self._connect_button_signals()
        self._connect_list_signals()
        self._connect_ui_signals()

    def _connect_view_model_signals(self) -> None:
        """Connect view model signals to update handlers."""
        self._view_model.mods_lists_changed.connect(self._on_mods_lists_changed)
        self._view_model.presets_changed.connect(self._on_presets_changed)
        self._view_model.active_mods_count_changed.connect(
            self._view.update_active_mods_count
        )
        self._mod_actions_view_model.refresh_installed_started.connect(
            self._on_refresh_started
        )
        self._mod_actions_view_model.refresh_installed_finished.connect(
            self._on_refresh_finished
        )
        self._mod_actions_view_model.refresh_installed_error.connect(
            self._on_refresh_error
        )
        self._file_actions_view_model.import_started.connect(self._on_import_started)
        self._file_actions_view_model.import_finished.connect(self._on_import_finished)
        self._file_actions_view_model.import_succeeded.connect(
            self._on_import_succeeded
        )
        self._file_actions_view_model.import_error.connect(self._on_import_error)

    def _connect_menu_signals(self) -> None:
        """Connect menu action signals to their handlers."""
        self._view.ui.actionOpen_game_folder.triggered.connect(self._open_game_folder)
        self._view.ui.actionOpen_mods_folder.triggered.connect(self._open_mods_folder)
        self._view.ui.actionOpen_options_file.triggered.connect(self._open_options_file)
        self._view.ui.actionOpen_logs.triggered.connect(self._open_logs)
        self._view.ui.actionExit.triggered.connect(self._view.close)

        self._view.ui.actionSettings.triggered.connect(self._open_preferences)

        self._view.ui.actionRefresh.triggered.connect(self._refresh_all)
        self._view.ui.actionShow_mod_information.triggered.connect(
            self._toggle_mod_details
        )

        self._view.ui.actionDefault.triggered.connect(
            lambda: self._change_font("default")
        )
        self._view.ui.actionDyslexic.triggered.connect(
            lambda: self._change_font("dyslexia")
        )

        self._view.ui.action_load_order_from_code.triggered.connect(
            self._open_import_code
        )
        self._view.ui.action_local_mod.triggered.connect(self._import_mod)

        self._view.ui.action_load_order_as_code.triggered.connect(
            self._open_export_code
        )

        self._view.ui.actionGuided_tour.triggered.connect(self._start_guided_tour)
        self._view.ui.actionGenerate_Help_File.triggered.connect(
            self._generate_help_file
        )
        self._view.ui.actionAbout.triggered.connect(self._open_about)

        # Hide placeholder zoom actions until implemented
        self._view.ui.actionZoom_in.setVisible(False)
        self._view.ui.actionZoom_out.setVisible(False)
        self._view.ui.actionReset_zoom.setVisible(False)

    def _connect_button_signals(self) -> None:
        """Connect button click signals to their handlers."""
        self._view.ui.pushButton_refresh_installed_mods.clicked.connect(
            self._refresh_installed_mods
        )
        self._view.ui.pushButton_activate.clicked.connect(self._enable_selected_mod)
        self._view.ui.pushButton_remove.clicked.connect(self._disable_selected_mod)
        self._view.ui.pushButton_move_up.clicked.connect(self._move_up)
        self._view.ui.pushButton_move_down.clicked.connect(self._move_down)
        self._view.ui.pushButton_clear_all.clicked.connect(self._clear_active_mods)

        self._view.ui.pushButton_save_preset.clicked.connect(self._save_preset)
        self._view.ui.pushButton_load_preset.clicked.connect(self._load_preset)
        self._view.ui.pushButton_delete_preset.clicked.connect(self._delete_preset)

    def _connect_list_signals(self) -> None:
        """Connect list widget signals to their handlers."""
        self._view.ui.listWidget_installed_mods.itemDoubleClicked.connect(
            self._enable_mod_from_item
        )
        self._view.ui.listWidget_active_mods.itemDoubleClicked.connect(
            self._disable_mod_from_item
        )

        self._view.ui.listWidget_installed_mods.currentItemChanged.connect(
            self._on_mod_selected
        )
        self._view.ui.listWidget_active_mods.currentItemChanged.connect(
            self._on_mod_selected
        )

        self._view.ui.listWidget_active_mods.model().rowsMoved.connect(
            self._save_mods_order
        )

        self._view.ui.listWidget_installed_mods.customContextMenuRequested.connect(
            self._handle_context_menu
        )

    def _connect_ui_signals(self) -> None:
        """Connect UI element signals to their handlers."""
        self._view.ui.comboBox_presets.currentTextChanged.connect(
            self._on_preset_selection_changed
        )

        self._view.ui.lineEdit_search_installed_mods.textChanged.connect(
            self._filter_installed_mods
        )
        self._view.ui.lineEdit_search_active_mods.textChanged.connect(
            self._filter_active_mods
        )

    # Menu Actions
    def _open_game_folder(self):
        success, error = self._file_actions_view_model.open_game_folder()
        if not success:
            self._view.show_error(
                self.tr("Open Folder Error"),
                self.tr("Failed to open game folder: {error}").format(error=error),
            )

    def _open_mods_folder(self):
        success, error = self._file_actions_view_model.open_mods_folder()
        if not success:
            self._view.show_error(
                self.tr("Open Folder Error"),
                self.tr("Failed to open mods folder: {error}").format(error=error),
            )

    def _open_options_file(self):
        success, error = self._file_actions_view_model.open_options_file()
        if not success:
            self._view.show_error(
                self.tr("Open Folder Error"),
                self.tr("Failed to open game folder: {error}").format(error=error),
            )

    def _open_logs(self):
        success, error = self._file_actions_view_model.open_logs()
        if not success:
            self._view.show_error(
                self.tr("Open Log Error"),
                self.tr("Failed to open log file: {error}").format(error=error),
            )

    # Mod Management
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
            self._mod_actions_view_model.disable_mod(mod)
            self._view.show_status_message(
                self.tr("Disabled {count} mods.").format(count=1)
            )

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
        before = {mod.id for mod in self._mod_actions_view_model.get_active_mods()}
        for mod in mods:
            missing = self._mod_actions_view_model.get_missing_dependencies(mod)

            if missing:
                dep_names = ", ".join(m.name for m in missing)

                title = self._view.parse_formatted_text(self.tr("Missing dependencies"))
                text = self._view.parse_formatted_text(
                    self.tr(
                        "The mod '{mod_name}' requires the following dependencies:\n\n"
                        "{dep_names}\n\n"
                        "Would you like to enable them as well?"
                    ).format(mod_name=mod.name, dep_names=dep_names)
                )

                if self._view.ask_confirmation(
                    title, text, default=QMessageBox.StandardButton.Yes
                ):
                    for dep in missing:
                        self._mod_actions_view_model.enable_mod(dep)

            # Finally, enable the main mod
            self._mod_actions_view_model.enable_mod(mod)

        after = {mod.id for mod in self._mod_actions_view_model.get_active_mods()}
        added = len(after - before)
        if added:
            self._view.show_status_message(
                self.tr("Enabled {count} mods.").format(count=added)
            )

    def _disable_selected_mod(self) -> None:
        """Disable all currently selected mods from the active list."""
        before = {mod.id for mod in self._mod_actions_view_model.get_active_mods()}
        mods = [
            self._get_mod_from_item(item)
            for item in self._view.get_current_active_mod()
        ]
        for mod in mods:
            if mod:
                self._mod_actions_view_model.disable_mod(mod)
        after = {mod.id for mod in self._mod_actions_view_model.get_active_mods()}
        removed = len(before - after)
        if removed:
            self._view.show_status_message(
                self.tr("Disabled {count} mods.").format(count=removed)
            )

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
        self._mod_actions_view_model.set_mods_order(reordered_mods)

    def _clear_active_mods(self) -> None:
        """Clear all active mods after user confirmation."""
        if not self._mod_actions_view_model.get_active_mods():
            self._view.show_message(
                title=self.tr("No Active Mods"),
                text=self.tr("There are no active mods to clear."),
                icon="information",
            )
            return

        if self._view.ask_confirmation(
            self.tr("Clear All Mods"),
            self.tr("Are you sure you want to clear all active mods?"),
        ):
            self._mod_actions_view_model.clear_active_mods()
            self._view.show_status_message(self.tr("All active mods cleared."))

    def _handle_context_menu(self, pos: QPoint) -> None:
        """
        Handle right-click context menu on available mods list.

        Args:
            pos: Position where the context menu was requested
        """
        item = self._view.ui.listWidget_installed_mods.itemAt(pos)
        if not item:
            return

        mod = self._get_mod_from_item(item)
        if not mod:
            return

        menu = QMenu(self._view.ui.listWidget_installed_mods)

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

        menu.exec(self._view.ui.listWidget_installed_mods.mapToGlobal(pos))

    def _open_mod_folder(self, folder_path: str) -> None:
        """
        Open mod folder in system file explorer.

        Args:
            folder_path: Path to the mod folder
        """
        success, error = self._file_actions_view_model.open_mod_folder(folder_path)
        if not success:
            self._view.show_error(
                self.tr("Open Folder Error"),
                self.tr("Failed to open mod folder: {error}").format(error=error),
            )

    def _open_steam_page(self, mod_id: str) -> None:
        """
        Open the workshop page for a mod on Steam.

        Args:
            mod_id: The Steam mod ID
        """
        success, error = self._file_actions_view_model.open_steam_page(mod_id)
        if not success:
            self._view.show_error(
                self.tr("Open Steam Page Error"),
                self.tr("Failed to open Steam page: {error}").format(error=error),
            )

    def _delete_mod_with_confirmation(self, item: QListWidgetItem, mod: Mod) -> None:
        """
        Delete a mod after user confirmation.

        Args:
            item: The list widget item to remove
            mod: The mod to delete
        """
        if self._view.ask_confirmation(
            self.tr("Delete Mod"),
            self.tr(
                "Are you sure you want to permanently delete '{mod_name}'?\nThis cannot be undone."
            ).format(mod_name=mod.name),
        ):
            row = self._view.ui.listWidget_installed_mods.row(item)
            self._view.ui.listWidget_installed_mods.takeItem(row)

            if self._file_actions_view_model.delete_mod(mod):
                self._view.show_message(
                    title=self.tr("Mod Deleted"),
                    text=self.tr("'{mod_name}' has been deleted.").format(
                        mod_name=mod.name
                    ),
                )
            else:
                self._view.show_error(
                    self.tr("Delete Error"),
                    self.tr(
                        "Failed to delete '{mod_name}'. Check file permissions."
                    ).format(mod_name=mod.name),
                )

    # Refresh Data
    def _refresh_all(self) -> None:
        """Refresh all data and clear search filters."""
        self._view.show_status_message(self.tr("Refreshing all mods..."))
        self._mod_actions_view_model.refresh_all_async()
        self._clear_search_filters()

    def _refresh_installed_mods(self) -> None:
        """Refresh only the installed mods list."""
        self._view.show_status_message(self.tr("Refreshing installed mods..."))
        self._mod_actions_view_model.refresh_installed_mods_async()

    # View Update
    def _update_view(self) -> None:
        """Update the view with current model data."""
        self._view_model.emit_all()

    def _on_mods_lists_changed(self, installed_mods, active_mods) -> None:
        self._view.populate_mod_lists(installed_mods, active_mods)

    def _on_presets_changed(self, preset_names) -> None:
        self._view.update_presets(preset_names, self._view.get_current_preset_name())

    def _on_mod_selected(self, current: QListWidgetItem) -> None:
        """
        Handle mod selection changes in lists.
        """
        mod = self._get_mod_from_item(current) if current else None
        self._view.update_mod_details(mod)
        if not mod:
            self._view.reset_mod_colors()
            return

        required_ids = self._mod_details_view_model.get_required_ids(mod)
        self._view.highlight_required_mods(required_ids)

    def _on_refresh_started(self) -> None:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._view.set_busy(True)

    def _on_refresh_finished(self) -> None:
        self._restore_cursor()
        self._view.set_busy(False)
        self._view.show_status_message(self.tr("Refresh complete."))

    def _on_refresh_error(self, message: str) -> None:
        self._restore_cursor()
        self._view.set_busy(False)
        self._view.show_error(self.tr("Refresh Error"), message)

    def _on_import_started(self) -> None:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self._view.set_busy(True)

    def _on_import_finished(self) -> None:
        self._restore_cursor()
        self._view.set_busy(False)

    def _on_import_succeeded(self) -> None:
        self._view.show_message(
            title=self.tr("Import Successful"),
            text=self.tr("Mod has been imported successfully."),
        )
        self._update_view()
        self._view.show_status_message(self.tr("Import completed."))

    def _on_import_error(self, message: str) -> None:
        self._view.show_error(title=self.tr("Import Failed"), text=message)

    @staticmethod
    def _restore_cursor() -> None:
        while QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()

    def _toggle_mod_details(self, checked: bool) -> None:
        """
        Toggle mod details panel visibility.

        Args:
            checked: Whether the mod details should be visible
        """
        self._view.ui.groupBox_mod_information.setVisible(checked)

    # Presets Management
    def _save_preset(self) -> None:
        """Save current active mods as a new preset."""
        if self._presets_view_model.get_active_mods_count() == 0:
            self._view.show_message(
                title=self.tr("Empty Preset"),
                text=self.tr(
                    "Cannot save an empty preset. Add mods to the list first."
                ),
                icon="warning",
            )
            return

        dialog = PresetDialog(parent=self._view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        preset_name = dialog.get_preset_name()
        if not preset_name:
            return

        # Check for existing preset and confirm overwrite
        if self._presets_view_model.has_preset(preset_name):
            if not self._confirm_preset_overwrite(preset_name):
                return

        if self._presets_view_model.save_preset(preset_name):
            self._view.show_message(
                title=self.tr("Preset Saved"),
                text=self.tr("Preset '{preset_name}' has been saved.").format(
                    preset_name=preset_name
                ),
            )

    def _load_preset(self) -> None:
        """Load the selected preset."""
        preset_name = self._view.get_current_preset_name()
        if not preset_name:
            self._view.show_message(
                title=self.tr("No Preset Selected"),
                text=self.tr("Please select a preset first."),
                icon="warning",
            )
            return

        if not self._presets_view_model.has_preset(preset_name):
            self._view.show_error(
                title=self.tr("Preset Not Found"),
                text=self.tr("Preset '{preset_name}' was not found.").format(
                    preset_name=preset_name
                ),
            )
            return

        if self._confirm_preset_load(preset_name):
            success = self._presets_view_model.load_preset(preset_name)
            if success:
                self._view.show_message(
                    title=self.tr("Preset Loaded"),
                    text=self.tr("Preset '{preset_name}' has been loaded.").format(
                        preset_name=preset_name
                    ),
                )

    def _delete_preset(self) -> None:
        """Delete the selected preset."""
        preset_name = self._view.get_current_preset_name()
        if not preset_name:
            self._view.show_message(
                title=self.tr("No Preset Selected"),
                text=self.tr("Please select a preset to delete."),
                icon="warning",
            )
            return

        if not self._presets_view_model.has_preset(preset_name):
            return

        if self._confirm_preset_deletion(preset_name):
            if self._presets_view_model.delete_preset(preset_name):
                self._view.show_message(
                    title=self.tr("Preset Deleted"),
                    text=self.tr("Preset '{preset_name}' has been deleted.").format(
                        preset_name=preset_name
                    ),
                )

    def _on_preset_selection_changed(self, preset_name: str) -> None:
        """
        Handle preset selection changes in the dropdown.

        Args:
            preset_name: Name of the selected preset
        """
        if not preset_name or not self._presets_view_model.has_preset(preset_name):
            self._view.ui.listWidget_presets.clear()
            return

        preset_mods = self._presets_view_model.get_preset_mods(preset_name)
        self._view.ui.listWidget_presets.clear()

        for mod in preset_mods:
            item = QListWidgetItem(self._view.parse_clear_text(mod.name))
            item.setData(Qt.UserRole, mod)
            self._view.ui.listWidget_presets.addItem(item)

    # Confirmation Dialogs
    def _confirm_preset_overwrite(self, preset_name: str) -> bool:
        """
        Confirm preset overwrite with user.

        Args:
            preset_name: Name of the preset to overwrite

        Returns:
            True if user confirms overwrite
        """
        return self._view.ask_confirmation(
            self.tr("Existing Preset"),
            self.tr("Preset '{preset_name}' already exists. Overwrite?").format(
                preset_name=preset_name
            ),
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
            self.tr("Load Preset"),
            self.tr(
                "Loading preset '{preset_name}' will clear the current list of mods. Continue?"
            ).format(preset_name=preset_name),
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
            self.tr("Delete Preset"),
            self.tr(
                "Are you sure you want to delete preset '{preset_name}'?\nThis cannot be undone."
            ).format(preset_name=preset_name),
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
            self.tr("Import Share Code"),
            self.tr(
                "This will replace your current active mods with {mod_count} mods from the code. Continue?"
            ).format(mod_count=mod_count),
        )

    # Search Filtering
    def _filter_installed_mods(self, search_text: str) -> None:
        """
        Filter installed mods list based on search text.

        Args:
            search_text: Text to search for in mod names and descriptions
        """
        self._filter_list_widget(self._view.ui.listWidget_installed_mods, search_text)

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
        self._view.ui.lineEdit_search_installed_mods.clear()
        self._view.ui.lineEdit_search_active_mods.clear()

    # Share Code
    def _export_share_code(self) -> None:
        """Export active mods as a shareable base64 code."""
        code, mod_count = self._import_export_view_model.get_share_code()
        if mod_count == 0:
            self._view.show_message(
                title=self.tr("No Active Mods"),
                text=self.tr("Add mods to the active list first."),
                icon="warning",
            )
            return

        try:
            self._view.ui.lineEdit_share_code.setText(code)
            self._view.show_message(
                title=self.tr("Code Generated"),
                text=self.tr("Share code has been generated and copied to the field."),
            )
        except Exception as e:
            self._view.show_error(
                title=self.tr("Export Error"),
                text=self.tr("Failed to generate share code: {error}").format(
                    error=str(e)
                ),
            )

    def _import_share_code(self) -> None:
        """Import mods from a share code."""
        code = self._view.ui.lineEdit_share_code.text().strip()
        if not code:
            self._view.show_message(
                title=self.tr("Empty Code"),
                text=self.tr("Enter a share code first."),
                icon="warning",
            )
            return

        try:
            found_mods, missing_mods, mod_count = (
                self._import_export_view_model.import_code(code)
            )
            if not self._confirm_share_code_import(mod_count):
                return

            applied_count = len(found_mods)

            if applied_count == mod_count:
                self._view.show_message(
                    title=self.tr("Code Imported"),
                    text=self.tr("Successfully imported all {mod_count} mods.").format(
                        mod_count=mod_count
                    ),
                )
            else:
                missing_count = mod_count - applied_count
                self._view.show_message(
                    title=self.tr("Partial Import"),
                    text=self.tr(
                        "Imported {applied_count} of {mod_count} mods.\n"
                        "{missing_count} mods are not installed."
                    ).format(
                        applied_count=applied_count,
                        mod_count=mod_count,
                        missing_count=missing_count,
                    ),
                    icon="warning",
                )

        except Exception as e:
            self._view.show_error(
                title=self.tr("Import Error"),
                text=self.tr("Invalid share code: {error}").format(error=str(e)),
            )

    # Dialog Management
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
        self._file_actions_view_model.import_mod_async(archive_path)

    def _open_preferences(self) -> None:
        """Open the preferences dialog."""
        current_language = self._config.get_language()
        if self._dialog_actions_view_model.open_preferences(
            self._view, on_start_guided_tour=self._start_guided_tour
        ):
            if self._config.get_language() != current_language:
                self._apply_language_change(self._config.get_language())
            # Reload data if preferences changed
            self._load_data()
            self._mod_actions_view_model.refresh_all_async()

    def _setup_guided_tour(self) -> None:
        steps = [
            GuidedTourStep(
                self._view.ui.groupBox_installed_mods,
                self.tr("Installed Mods"),
                self.tr(
                    "Browse installed mods, search to filter, and refresh to rescan."
                ),
            ),
            GuidedTourStep(
                [
                    self._view.ui.pushButton_activate,
                    self._view.ui.pushButton_remove,
                    self._view.ui.pushButton_clear_all,
                ],
                self.tr("Activate or Deactivate"),
                self.tr(
                    "Activate, deactivate, or clear active mods with these buttons."
                ),
            ),
            GuidedTourStep(
                [
                    self._view.ui.pushButton_move_up,
                    self._view.ui.pushButton_move_down,
                ],
                self.tr("Reorder Mods"),
                self.tr("Reorder active mods with Move Up or Move Down."),
            ),
            GuidedTourStep(
                self._view.ui.listWidget_active_mods,
                self.tr("Active Mods"),
                self.tr("These mods load in this order."),
            ),
            GuidedTourStep(
                self._view.ui.groupBox_presets,
                self.tr("Presets"),
                self.tr("Save and load different mod setups."),
            ),
            GuidedTourStep(
                self._view.ui.groupBox_mod_information,
                self.tr("Mod Information"),
                self.tr("View details for the selected mod."),
            ),
            GuidedTourStep(
                GuidedTourTargetAction(
                    self._view.menuBar(), self._view.ui.menuImport.menuAction()
                ),
                self.tr("Import Mods"),
                self.tr("Import local mods or load a shared setup from code."),
            ),
            GuidedTourStep(
                GuidedTourTargetAction(
                    self._view.menuBar(), self._view.ui.menuExport.menuAction()
                ),
                self.tr("Export and Share"),
                self.tr("Export your load order as a shareable code."),
            ),
            GuidedTourStep(
                GuidedTourTargetAction(
                    self._view.menuBar(), self._view.ui.menuEdit.menuAction()
                ),
                self.tr("Preferences"),
                self.tr("Open Preferences from the Edit menu."),
            ),
        ]
        self._guided_tour = GuidedTourOverlay(
            self._view,
            steps,
            on_finish=self._on_guided_tour_finished,
        )

    def _apply_language_change(self, language: str) -> None:
        translator = getattr(QApplication.instance(), "translation_manager", None)
        if translator is None:
            translations_dir = Path(__file__).resolve().parents[2] / "i18n"
            translator = TranslationManager(translations_dir)
            QApplication.instance().translation_manager = translator
        translator.load(language)
        self._view.retranslate()
        self._setup_guided_tour()

    def _maybe_start_guided_tour(self) -> None:
        if self._config.get_show_guided_tour():
            self._start_guided_tour(update_config=True)

    def _start_guided_tour(self, update_config: bool = False) -> None:
        if not hasattr(self, "_guided_tour"):
            self._setup_guided_tour()
        self._guided_tour_updates_config = update_config
        self._guided_tour.start()

    def _on_guided_tour_finished(self, show_on_startup: bool) -> None:
        if getattr(self, "_guided_tour_updates_config", False):
            self._config.set_show_guided_tour(show_on_startup)
        elif not show_on_startup:
            self._config.set_show_guided_tour(False)

    def _generate_help_file(self) -> None:
        """Generate a help file containing load order and configuration details."""
        success, result = self._file_actions_view_model.generate_help_file()
        if not success:
            logger.error(f"Failed to generate help file: {result}")
            return

        _, open_error = self._file_actions_view_model.open_path(".")
        if open_error:
            logger.warning(f"Could not open folder: {open_error}")

    def _open_about(self) -> None:
        """Open the about dialog."""
        self._dialog_actions_view_model.open_about(
            self._view, QApplication.applicationVersion()
        )

    def _open_export_code(self):
        code, mod_count = self._import_export_view_model.get_export_code()
        if mod_count == 0:
            self._view.show_message(
                title=self.tr("No Active Mods"),
                text=self.tr("Add mods to the active list first."),
                icon="warning",
            )
            return

        dialog = ExportCodeDialog(self._view)
        dialog.set_code(code, mod_count)
        dialog.exec()

    def _open_import_code(self):
        dialog = ImportCodeDialog(self._view)
        dialog.import_requested.connect(self._handle_import)
        dialog.exec()

    def _handle_import(self, code: str):
        try:
            found_payload, missing_mods, total_count = (
                self._import_export_view_model.import_code(code)
            )
            self._show_import_result(found_payload, missing_mods, total_count)

        except Exception as e:
            self._view.show_error(
                title=self.tr("Import Error"),
                text=self.tr("Invalid share code: {error}").format(error=str(e)),
            )

    def _show_import_result(
        self, found_mods: List[Dict], missing_mods: List[Dict], total_count: int
    ):
        found_count = len(found_mods)
        missing_count = len(missing_mods)

        if missing_count == 0:
            self._view.show_message(
                title=self.tr("Import Successful"),
                text=self.tr("Successfully loaded {total_count} mods.").format(
                    total_count=total_count
                ),
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
            missing_list.append(f"- {mod['name']} (ID: {mod['id']})")

        missing_text = "\n".join(missing_list)

        message = f"Loaded {found_count} of {total_count} mods.\n\n"
        message += f"Missing mods ({missing_count}):\n{missing_text}"

        dialog = DetailedMessageDialog(self._view)
        dialog.set_title(self.tr("Partial Import"))
        dialog.set_message(
            self.tr("Loaded {found_count} of {total_count} mods.").format(
                found_count=found_count, total_count=total_count
            )
        )
        dialog.set_details(
            self.tr("Missing mods ({missing_count}):").format(
                missing_count=missing_count
            ),
            missing_text,
        )
        dialog.exec()

    # Font Management
    def _change_font(self, font_name: str) -> None:
        """
        Change the application font.

        Args:
            font_name: Name of the font to apply ("default" or "dyslexia")
        """
        normalized = font_name if font_name else "default"
        font = self._appearance_view_model.set_font(normalized)
        self._view.set_application_font(font)

    # Utility
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
