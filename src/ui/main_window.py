import datetime
import os
import platform
import sys

import qtawesome as qta
from PySide6.QtCore import Qt, QThreadPool, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.core.events import EventType
from src.core.exceptions import InvalidShareCodeError, ModImportError
from src.core.manager import ModManager
from src.ui.dialogs.about_dialog import AboutDialog
from src.ui.dialogs.import_mod_dialog import ImportModDialog
from src.ui.dialogs.missing_mods_dialog import MissingModsDialog
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.ui.dialogs.share_code_dialog import ImportShareCodeDialog
from src.ui.widgets.active_mods_widget import ActiveModsWidget
from src.ui.widgets.catalogue_widget import CatalogueWidget
from src.ui.widgets.main_menu_bar import MainMenuBar
from src.ui.widgets.main_tool_bar import MainToolBar
from src.ui.widgets.mod_details_widget import ModDetailsWidget
from src.ui.workers.mod_import_worker import ModImportWorker


class MainWindow(QMainWindow):
    def __init__(self, app_model: ModManager):
        super().__init__()
        self.app_model = app_model

        self.setWindowTitle(self.tr("GoH Mod Manager"))
        self.resize(1000, 1000)

        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

        self._setup_menu()
        self._setup_toolbar()
        self._setup_ui()
        self._connect_signals()
        self._connect_menu_signals()
        self._connect_model_events()

        # Initial UI population
        self.refresh_ui()

    def _setup_menu(self):
        self.main_menu_bar = MainMenuBar(self)
        self.setMenuBar(self.main_menu_bar)

    def _setup_toolbar(self):
        self.toolbar = MainToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Main vertical splitter
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section containing the lists
        top_widget = QWidget()
        lists_layout = QHBoxLayout(top_widget)
        lists_layout.setContentsMargins(0, 0, 0, 0)

        self.catalogue_widget = CatalogueWidget()
        self.active_mods_widget = ActiveModsWidget()

        # Middle controls (Add/Remove buttons)
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(5, 0, 5, 0)
        self.btn_add = QPushButton()
        self.btn_add.setIcon(qta.icon("fa5s.angle-double-right"))
        self.btn_add.setToolTip(self.tr("Add selected mod"))
        self.btn_remove = QPushButton()
        self.btn_remove.setIcon(qta.icon("fa5s.angle-double-left"))
        self.btn_remove.setToolTip(self.tr("Remove selected mod"))
        middle_layout.addStretch()
        middle_layout.addWidget(self.btn_add)
        middle_layout.addWidget(self.btn_remove)
        middle_layout.addStretch()

        lists_layout.addWidget(self.catalogue_widget, stretch=1)
        lists_layout.addWidget(middle_widget)
        lists_layout.addWidget(self.active_mods_widget, stretch=1)

        main_splitter.addWidget(top_widget)

        self.mod_details_widget = ModDetailsWidget()
        main_splitter.addWidget(self.mod_details_widget)

        # Set initial sizes for the splitter (e.g., 70% lists, 30% details)
        main_splitter.setSizes([400, 150])

        main_layout.addWidget(main_splitter)

        # Status Bar
        self.statusBar().showMessage(self.tr("Ready"))

    def _connect_signals(self):
        # Catalogue actions
        self.btn_add.clicked.connect(self._on_add_mod)
        self.btn_remove.clicked.connect(self._on_remove_mod_selected)
        self.catalogue_widget.list_widget.itemDoubleClicked.connect(self._on_add_mod)
        self.catalogue_widget.list_widget.itemSelectionChanged.connect(
            self._on_catalogue_selection_changed
        )
        self.catalogue_widget.list_widget.customContextMenuRequested.connect(
            self._show_catalogue_context_menu
        )

        # Active mods actions
        self.active_mods_widget.move_up_requested.connect(self._on_move_up)
        self.active_mods_widget.move_down_requested.connect(self._on_move_down)

        self.active_mods_widget.clear_requested.connect(self._on_clear_mods)
        self.active_mods_widget.list_widget.itemDoubleClicked.connect(
            self._on_remove_mod_from_item
        )
        self.active_mods_widget.list_widget.itemSelectionChanged.connect(
            self._on_active_mods_selection_changed
        )
        self.active_mods_widget.list_widget.customContextMenuRequested.connect(
            self._show_active_mods_context_menu
        )
        self.active_mods_widget.order_changed.connect(
            self._on_active_mods_order_changed
        )

        # Launch Action
        self.toolbar.play_requested.connect(self._on_launch_game)

        # Preset Actions
        self.active_mods_widget.preset_selector.preset_applied.connect(
            self._on_apply_preset
        )
        self.active_mods_widget.preset_selector.save_requested.connect(
            self._on_save_preset
        )
        self.active_mods_widget.preset_selector.save_as_requested.connect(
            self._on_save_preset_as
        )
        self.active_mods_widget.preset_selector.delete_requested.connect(
            self._on_delete_preset
        )

    def _connect_model_events(self):
        """Subscribe to backend model events for automatic UI refreshing."""
        self.app_model.events.subscribe(
            EventType.CATALOGUE_CHANGED, self._on_catalogue_changed
        )
        self.app_model.events.subscribe(
            EventType.ACTIVE_MODS_CHANGED, self._on_active_mods_changed
        )
        self.app_model.events.subscribe(
            EventType.PRESETS_CHANGED, self._on_presets_changed
        )

    def _connect_menu_signals(self):
        self.main_menu_bar.import_code_action.triggered.connect(
            self._on_import_share_code
        )
        self.main_menu_bar.export_code_action.triggered.connect(
            self._on_export_share_code
        )
        self.main_menu_bar.import_mod_action.triggered.connect(self._on_import_mod)
        self.main_menu_bar.open_game_dir_action.triggered.connect(
            self._on_open_game_dir
        )
        self.main_menu_bar.open_profile_file_action.triggered.connect(
            self._on_open_profile
        )
        self.main_menu_bar.open_log_file_action.triggered.connect(
            self._on_open_log_file
        )
        self.main_menu_bar.settings_action.triggered.connect(self._on_open_settings)
        self.main_menu_bar.refresh_action.triggered.connect(self._on_refresh_data)
        self.main_menu_bar.generate_report_action.triggered.connect(
            self._on_generate_report
        )
        self.main_menu_bar.about_action.triggered.connect(self._on_about)

    def _show_catalogue_context_menu(self, pos):
        item = self.catalogue_widget.list_widget.itemAt(pos)
        if not item:
            return
        mod_id = item.data(Qt.ItemDataRole.UserRole)
        self._show_mod_context_menu(
            mod_id, self.catalogue_widget.list_widget.mapToGlobal(pos)
        )

    def _show_active_mods_context_menu(self, pos):
        item = self.active_mods_widget.list_widget.itemAt(pos)
        if not item:
            return
        mod_id = item.data(Qt.ItemDataRole.UserRole)
        self._show_mod_context_menu(
            mod_id, self.active_mods_widget.list_widget.mapToGlobal(pos)
        )

    def _show_mod_context_menu(self, mod_id: str, global_pos):
        mod = next((m for m in self.app_model.get_all_mods() if m.id == mod_id), None)
        if not mod:
            return

        menu = QMenu(self)

        open_folder_action = menu.addAction(self.tr("Open Mod Folder"))
        open_workshop_action = None
        if not mod.isLocal and mod_id.isdigit():
            open_workshop_action = menu.addAction(self.tr("Open in Steam Workshop"))

        action = menu.exec(global_pos)

        if action == open_folder_action:
            self._open_path(mod.path)
        elif open_workshop_action and action == open_workshop_action:
            url = QUrl(f"steam://url/CommunityFilePage/{mod_id}")
            QDesktopServices.openUrl(url)

    def _on_catalogue_selection_changed(self):
        mod_id = self.catalogue_widget.get_selected_mod_id()
        if mod_id:
            # Clear active mods selection to avoid two mods selected at once
            self.active_mods_widget.list_widget.blockSignals(True)
            self.active_mods_widget.list_widget.clearSelection()
            self.active_mods_widget.list_widget.blockSignals(False)

            all_mods = self.app_model.get_all_mods()
            mod = next((m for m in all_mods if m.id == mod_id), None)
            self.mod_details_widget.display_mod(mod)

    def _on_active_mods_selection_changed(self):
        mod_id = self.active_mods_widget.get_selected_mod_id()
        if mod_id:
            # Clear catalogue selection
            self.catalogue_widget.list_widget.blockSignals(True)
            self.catalogue_widget.list_widget.clearSelection()
            self.catalogue_widget.list_widget.blockSignals(False)

            all_mods = self.app_model.get_all_mods()
            mod = next((m for m in all_mods if m.id == mod_id), None)
            self.mod_details_widget.display_mod(mod)

    def refresh_ui(self):
        """
        Fetches the latest state from the ModManager and updates the widgets.
        """
        # Populate Catalogue
        all_mods = self.app_model.get_all_mods()
        self.catalogue_widget.populate(all_mods)

        # It's a common practice to grey out or highlight mods that are already active in the catalogue
        # but for simplicity, we just display them all for now.

        # Populate Active
        active_mods = self.app_model.get_active_mods()
        self.active_mods_widget.populate(active_mods)

        # Populate Presets
        presets = self.app_model.get_all_presets()
        current_preset = self.active_mods_widget.preset_selector.combo.currentText()
        self.active_mods_widget.preset_selector.populate(
            list(presets.keys()), current_preset
        )

    def _on_add_mod(self):
        mod_ids = self.catalogue_widget.get_selected_mod_ids()
        if not mod_ids:
            return

        all_mods = self.app_model.get_all_mods()
        activated_mods = []
        all_missing_deps = []

        for mod_id in mod_ids:
            if not self.app_model.is_mod_active(mod_id):
                missing_deps = self.app_model.toggle_mod(mod_id)
                activated_mods.append(mod_id)
                if missing_deps:
                    all_missing_deps.extend(missing_deps)

        if activated_mods:
            self.statusBar().showMessage(
                self.tr("Activated mod(s): {0}").format(", ".join(activated_mods)), 3000
            )

            if all_missing_deps:
                unique_missing = []
                for dep in all_missing_deps:
                    if dep not in unique_missing:
                        unique_missing.append(dep)

                if len(activated_mods) == 1:
                    mod_id = activated_mods[0]
                    mod = next((m for m in all_mods if m.id == mod_id), None)
                    mod_name = mod.name if mod else mod_id
                    desc = self.tr(
                        "The mod '<b>{0}</b>' was activated, but the following required dependencies are missing from your catalogue. You must subscribe to them on the Workshop:"
                    ).format(mod_name)
                else:
                    desc = self.tr(
                        "The selected mods were activated, but the following required dependencies are missing from your catalogue. You must subscribe to them on the Workshop:"
                    )

                dialog = MissingModsDialog(
                    self,
                    self.tr("Missing Dependencies"),
                    desc,
                    unique_missing,
                )
                dialog.exec()

    def _on_remove_mod_selected(self):
        mod_id = self.active_mods_widget.get_selected_mod_id()
        if mod_id:
            self._on_remove_mod(mod_id)

    def _on_clear_mods(self):
        if self.app_model.get_active_mods():
            # Clear all active mods
            self.app_model.clear_active_mods()
            self.statusBar().showMessage(self.tr("Cleared all active mods"), 3000)

    def _on_remove_mod(self, mod_id: str):
        if self.app_model.is_mod_active(mod_id):
            self.app_model.toggle_mod(mod_id)
            self.statusBar().showMessage(
                self.tr("Deactivated mod: {0}").format(mod_id), 3000
            )

    def _on_remove_mod_from_item(self, item):
        mod_id = item.data(Qt.ItemDataRole.UserRole)
        if mod_id:
            self._on_remove_mod(mod_id)

    def _on_move_up(self, mod_id: str):
        self.app_model.move_mod_up(mod_id)
        self.statusBar().showMessage(self.tr("Moved mod {0} up").format(mod_id), 3000)

    def _on_move_down(self, mod_id: str):
        self.app_model.move_mod_down(mod_id)
        self.statusBar().showMessage(self.tr("Moved mod {0} down").format(mod_id), 3000)

    def _on_active_mods_order_changed(self, new_order: list[str]):
        self.app_model.set_active_mods_order(new_order)
        self.statusBar().showMessage(self.tr("Mod load order updated"), 3000)

    def _on_apply_preset(self, name: str):
        success, missing = self.app_model.apply_preset(name)
        if success:
            self.active_mods_widget.preset_selector.set_current_preset(name)
            self.statusBar().showMessage(
                self.tr("Applied preset: {0}").format(name), 3000
            )

            if missing:
                dialog = MissingModsDialog(
                    self,
                    self.tr("Preset Applied with Warnings"),
                    self.tr(
                        "The preset was applied, but the following mods are missing from your catalogue. You must subscribe to them on the Workshop:"
                    ),
                    missing,
                )
                dialog.exec()

    def _on_save_preset(self, name: str):
        self.app_model.save_preset(name)
        self.active_mods_widget.preset_selector.set_current_preset(name)
        self.statusBar().showMessage(self.tr("Saved preset: {0}").format(name), 3000)

    def _on_save_preset_as(self):
        name, ok = QInputDialog.getText(
            self, self.tr("Save Preset"), self.tr("Enter a name for the new preset:")
        )
        if ok and name:
            if name in self.app_model.get_all_presets():
                reply = QMessageBox.question(
                    self,
                    self.tr("Overwrite Preset?"),
                    self.tr("A preset named '{0}' already exists. Overwrite?").format(
                        name
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            self.app_model.save_preset(name)
            self.active_mods_widget.preset_selector.set_current_preset(name)
            self.statusBar().showMessage(
                self.tr("Saved new preset: {0}").format(name), 3000
            )

    def _on_delete_preset(self, name: str):
        reply = QMessageBox.question(
            self,
            self.tr("Delete Preset"),
            self.tr("Are you sure you want to delete the preset '{0}'?").format(name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.app_model.delete_preset(name)
            self.statusBar().showMessage(
                self.tr("Deleted preset: {0}").format(name), 3000
            )

    def _on_export_share_code(self):
        active_mods = self.app_model.get_active_mods()
        if not active_mods:
            QMessageBox.information(
                self,
                self.tr("Export Failed"),
                self.tr("There are no active mods to export."),
            )
            return

        code = self.app_model.export_share_code()
        if code:
            # Copy to clipboard
            from PySide6.QtGui import QGuiApplication

            clipboard = QGuiApplication.clipboard()
            clipboard.setText(code)
            QMessageBox.information(
                self,
                self.tr("Export Success"),
                self.tr(
                    "Share Code has been copied to your clipboard!\n\nYou can now paste it to your friends."
                ),
            )
        else:
            QMessageBox.critical(
                self, self.tr("Export Error"), self.tr("Failed to generate Share Code.")
            )

    def _on_import_mod(self):
        dialog = ImportModDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            path = dialog.get_path()
            if not path:
                return

            self.statusBar().showMessage(
                self.tr("Importing mod from {0}... Please wait.").format(path)
            )

            # Run the import in a background worker thread
            worker = ModImportWorker(self.app_model, path)
            worker.signals.success.connect(self._on_import_success)
            worker.signals.error.connect(self._on_import_error)
            worker.signals.progress.connect(self._on_import_progress)
            worker.signals.conflict.connect(
                lambda mod_name: self._on_import_conflict(mod_name, worker)
            )

            # Setup Progress Dialog
            self.import_progress = QProgressDialog(
                self.tr("Importing mod..."), self.tr("Cancel"), 0, 100, self
            )
            self.import_progress.setWindowTitle(self.tr("Import Mod"))
            self.import_progress.setCancelButton(None)
            self.import_progress.setWindowModality(Qt.WindowModality.WindowModal)
            self.import_progress.setAutoClose(True)
            self.import_progress.setAutoReset(True)
            self.import_progress.setValue(0)
            self.import_progress.show()

            # Start worker in thread pool
            self.thread_pool.start(worker)

    def _on_import_progress(self, percent: int, message: str):
        if hasattr(self, "import_progress"):
            self.import_progress.setLabelText(self.tr(message))
            self.import_progress.setValue(percent)

    def _on_import_success(self):
        if hasattr(self, "import_progress"):
            self.import_progress.setValue(100)
        QMessageBox.information(
            self, self.tr("Import Success"), self.tr("Mod successfully imported!")
        )
        self.statusBar().showMessage(self.tr("Mod import complete."), 3000)

    def _on_import_error(self, error_msg: str):
        if hasattr(self, "import_progress"):
            self.import_progress.cancel()
        QMessageBox.critical(
            self,
            self.tr("Import Failed"),
            self.tr("Failed to import mod:\n\n{0}").format(error_msg),
        )
        self.statusBar().clearMessage()

    def _on_import_conflict(self, mod_name: str, worker: ModImportWorker):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr("Mod Conflict"))
        msg_box.setText(self.tr("The mod '{0}' already exists.").format(mod_name))
        msg_box.setInformativeText(self.tr("What would you like to do?"))

        overwrite_btn = msg_box.addButton(
            self.tr("Overwrite"), QMessageBox.ButtonRole.AcceptRole
        )
        skip_btn = msg_box.addButton(self.tr("Skip"), QMessageBox.ButtonRole.RejectRole)
        cancel_btn = msg_box.addButton(QMessageBox.StandardButton.Cancel)

        msg_box.exec()

        if msg_box.clickedButton() == overwrite_btn:
            worker.set_conflict_resolution("overwrite")
        elif msg_box.clickedButton() == skip_btn:
            worker.set_conflict_resolution("skip")
        else:
            worker.set_conflict_resolution("cancel")

    def _on_import_share_code(self):
        dialog = ImportShareCodeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            code = dialog.get_code()
            if not code:
                return

            try:
                success, missing_mods = self.app_model.import_share_code(code)

                if success:
                    # Visually reset preset selector since we are now in a custom state
                    self.active_mods_widget.preset_selector.combo.setCurrentIndex(0)

                    if missing_mods:
                        dialog = MissingModsDialog(
                            self,
                            self.tr("Imported with Missing Mods"),
                            self.tr(
                                "The load order was imported, but you are missing the following mods. You must subscribe to them on the Workshop for the preset to work perfectly:"
                            ),
                            missing_mods,
                        )
                        dialog.exec()
                    else:
                        QMessageBox.information(
                            self,
                            self.tr("Import Success"),
                            self.tr("Share Code successfully applied!"),
                        )

            except InvalidShareCodeError:
                QMessageBox.critical(
                    self,
                    self.tr("Import Error"),
                    self.tr("Invalid or corrupted Share Code."),
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Import Error"),
                    self.tr("An unexpected error occurred:\n{0}").format(e),
                )

    def _open_path(self, path: str):
        """Cross-platform path opening."""
        if not path or not os.path.exists(path):
            QMessageBox.warning(
                self,
                self.tr("Not Found"),
                self.tr("Cannot find path:\n{0}").format(path),
            )
            return

        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            import subprocess

            subprocess.Popen(["open", path])
        else:
            import subprocess

            subprocess.Popen(["xdg-open", path])

    def _on_open_game_dir(self):
        config = self.app_model.get_config()
        if config.game_path:
            self._open_path(config.game_path)

    def _on_open_profile(self):
        config = self.app_model.get_config()
        if config.profile_path:
            # We open the directory containing the file to select it
            dir_path = os.path.dirname(config.profile_path)
            self._open_path(dir_path)

    def _on_open_log_file(self):
        log_path = os.path.abspath(os.path.join("logs", "mod_manager.log"))
        self._open_path(log_path)

    def _on_refresh_data(self):
        # Prevent UI issues during reload
        self.catalogue_widget.list_widget.blockSignals(True)
        self.active_mods_widget.list_widget.blockSignals(True)

        self.app_model.reload()

        self.catalogue_widget.list_widget.blockSignals(False)
        self.active_mods_widget.list_widget.blockSignals(False)

        self.statusBar().showMessage(self.tr("All data refreshed from disk."), 3000)

    def _on_open_settings(self):
        config = self.app_model.get_config()
        dialog = SettingsDialog(
            current_game_path=config.game_path,
            current_workshop_path=config.workshop_path,
            current_profile_path=config.profile_path,
            current_language=config.language,
            current_theme=config.theme,
            current_font=config.font,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_paths = dialog.get_paths()

            # Update paths and auto-save
            try:
                self.app_model.update_paths(
                    game_path=new_paths["game_path"],
                    workshop_path=new_paths["workshop_path"],
                    profile_path=new_paths["profile_path"],
                    language=new_paths.get("language"),
                    theme=new_paths.get("theme"),
                    font=new_paths.get("font"),
                )
            except TypeError:
                # Fallback if ModManager.update_paths doesn't support the new arguments yet
                self.app_model.config_service.update_paths(
                    game_path=new_paths["game_path"],
                    workshop_path=new_paths["workshop_path"],
                    profile_path=new_paths["profile_path"],
                    language=new_paths.get("language"),
                    theme=new_paths.get("theme"),
                    font=new_paths.get("font"),
                )

            # Apply new appearance dynamically
            from PySide6.QtWidgets import QApplication

            from src.ui.appearance_manager import AppearanceManager

            app = QApplication.instance()
            if app:
                AppearanceManager.setup_appearance(
                    app,
                    theme=new_paths.get("theme", config.theme),
                    font_name=new_paths.get("font", config.font),
                )

            # Reload data with new paths
            self._on_refresh_data()
            self.statusBar().showMessage(
                self.tr("Settings saved and data reloaded."), 3000
            )

    def _on_generate_report(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Debug Report"),
            "goh_mod_manager_debug.txt",
            self.tr("Text Files (*.txt);;All Files (*)"),
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("--- GoH Mod Manager Debug Report ---\n")
                f.write(f"Generated at: {datetime.datetime.now()}\n")
                f.write(
                    f"OS: {platform.system()} {platform.release()} ({platform.version()})\n"
                )

                try:
                    with open(".app-version", "r", encoding="utf-8") as vfile:
                        version = vfile.read().strip()
                except Exception:
                    version = "Unknown"
                f.write(f"App Version: {version}\n")

                f.write("\n--- Configuration ---\n")
                config = self.app_model.get_config()
                f.write(f"Game Path: {config.game_path}\n")
                f.write(f"Workshop Path: {config.workshop_path}\n")
                f.write(f"Profile Path: {config.profile_path}\n")

                f.write("\n--- Catalogue Stats ---\n")
                local_mods = self.app_model.get_local_mods()
                workshop_mods = self.app_model.get_workshop_mods()
                all_mods = self.app_model.get_all_mods()
                f.write(f"Total Installed Mods: {len(all_mods)}\n")
                f.write(f"Local Mods: {len(local_mods)}\n")
                f.write(f"Workshop Mods: {len(workshop_mods)}\n")

                f.write("\n--- Active Mods Load Order ---\n")
                active_mods = self.app_model.get_active_mods()
                if not active_mods:
                    f.write("No active mods.\n")
                for i, mod in enumerate(active_mods):
                    mod_type = "Local" if mod.isLocal else "Workshop"
                    f.write(f"{i + 1}. {mod.name} (ID: {mod.id}) - {mod_type}\n")

                f.write("\n--- Recent Logs (Last 100 Lines) ---\n")
                log_path = os.path.abspath(os.path.join("logs", "mod_manager.log"))
                if os.path.exists(log_path):
                    with open(log_path, "r", encoding="utf-8") as log_file:
                        lines = log_file.readlines()
                        f.writelines(lines[-100:])
                else:
                    f.write("No log file found.\n")

            QMessageBox.information(
                self,
                self.tr("Success"),
                self.tr("Debug report saved successfully to:\n{0}").format(file_path),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to save debug report:\n{0}").format(e),
            )

    def _on_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def _on_catalogue_changed(self):
        all_mods = self.app_model.get_all_mods()
        self.catalogue_widget.populate(all_mods)

    def _on_active_mods_changed(self):
        active_mods = self.app_model.get_active_mods()
        self.active_mods_widget.populate(active_mods)

    def _on_presets_changed(self):
        presets = self.app_model.get_all_presets()
        current_preset = self.active_mods_widget.preset_selector.combo.currentText()
        self.active_mods_widget.preset_selector.populate(
            list(presets.keys()), current_preset
        )

    def _on_launch_game(self):
        success = self.app_model.launch_game()
        if success:
            self.statusBar().showMessage(
                self.tr("Launching Call to Arms - Gates of Hell..."), 5000
            )
        else:
            QMessageBox.critical(
                self,
                self.tr("Launch Failed"),
                self.tr(
                    "Failed to launch the game. Make sure Steam is installed and running."
                ),
            )
