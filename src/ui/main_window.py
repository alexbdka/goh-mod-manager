import datetime
import os
import platform
from contextlib import contextmanager

import qtawesome as qta
from PySide6.QtCore import Qt, QThreadPool, QTimer
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
from src.core.exceptions import (
    InvalidShareCodeError,
    ModImportError,
    ProfileWriteError,
)
from src.core.manager import ModManager
from src.core.mod import ModInfo
from src.ui.appearance_manager import AppearanceManager
from src.ui.dialogs.about_dialog import AboutDialog
from src.ui.dialogs.import_mod_dialog import ImportModDialog
from src.ui.dialogs.missing_mods_dialog import MissingModsDialog
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.ui.dialogs.share_code_dialog import ImportShareCodeDialog
from src.ui.translation_manager import TranslationManager
from src.ui.widgets.active_mods_widget import ActiveModsWidget
from src.ui.widgets.catalogue_widget import CatalogueWidget
from src.ui.widgets.main_menu_bar import MainMenuBar
from src.ui.widgets.main_tool_bar import MainToolBar
from src.ui.widgets.mod_details_widget import ModDetailsWidget
from src.ui.workers.mod_import_worker import ModImportWorker
from src.utils import app_paths, system_actions


class MainWindow(QMainWindow):
    def __init__(self, app_model: ModManager):
        super().__init__()
        self.app_model = app_model

        self.resize(1000, 1000)

        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

        self._setup_menu()
        self._setup_toolbar()
        self._setup_ui()
        self._connect_signals()
        self._connect_menu_signals()
        self._connect_model_events()
        self.retranslate_ui()

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
        main_splitter.setHandleWidth(6)

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
        self.btn_remove = QPushButton()
        self.btn_remove.setIcon(qta.icon("fa5s.angle-double-left"))
        middle_layout.addStretch()
        middle_layout.addWidget(self.btn_add)
        middle_layout.addWidget(self.btn_remove)
        middle_layout.addStretch()

        lists_layout.addWidget(self.catalogue_widget, stretch=1)
        lists_layout.addWidget(middle_widget, stretch=0)
        lists_layout.addWidget(self.active_mods_widget, stretch=1)

        top_container = QWidget()
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(0, 0, 0, 6)
        top_container_layout.addWidget(top_widget)
        main_splitter.addWidget(top_container)

        self.mod_details_widget = ModDetailsWidget()
        bottom_container = QWidget()
        bottom_container_layout = QVBoxLayout(bottom_container)
        bottom_container_layout.setContentsMargins(0, 6, 0, 0)
        bottom_container_layout.addWidget(self.mod_details_widget)
        main_splitter.addWidget(bottom_container)

        # Set initial sizes for the splitter (e.g., 70% lists, 30% details)
        main_splitter.setSizes([400, 150])

        main_layout.addWidget(main_splitter)

        # Status Bar
        self.statusBar().showMessage("")
        self._apply_view_fonts()
        self.refresh_icons()
        QTimer.singleShot(0, self.refresh_icons)

    @contextmanager
    def _signals_blocked(self, *widgets: QWidget):
        blockers = []
        try:
            for widget in widgets:
                blocker = getattr(widget, "block_list_signals", widget.blockSignals)
                blocker(True)
                blockers.append(blocker)
            yield
        finally:
            for blocker in blockers:
                blocker(False)

    def _get_mod_by_id(self, mod_id: str) -> ModInfo | None:
        return next(
            (mod for mod in self.app_model.get_all_mods() if mod.id == mod_id), None
        )

    def _current_preset_name(self) -> str:
        return self.active_mods_widget.preset_selector.current_preset_name()

    def _populate_catalogue(self):
        active_mod_ids = [mod.id for mod in self.app_model.get_active_mods()]
        self.catalogue_widget.set_active_mod_ids(active_mod_ids)
        self.catalogue_widget.populate(self.app_model.get_all_mods())

    def _populate_active_mods(self):
        self.active_mods_widget.populate(self.app_model.get_active_mods())

    def _populate_presets(self):
        presets = self.app_model.get_all_presets()
        self.active_mods_widget.preset_selector.populate(
            list(presets.keys()), self._current_preset_name()
        )

    def _show_missing_mods_dialog(
        self,
        title: str,
        description: str,
        missing_mods: list[str] | list[dict[str, str]],
    ):
        dialog = MissingModsDialog(self, title, description, missing_mods)
        dialog.exec()

    def _show_info_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def _show_error_message(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def _show_warning_message(self, title: str, message: str):
        QMessageBox.warning(self, title, message)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("GoH Mod Manager"))
        self.btn_add.setToolTip(self.tr("Add selected mod"))
        self.btn_remove.setToolTip(self.tr("Remove selected mod"))
        self.main_menu_bar.retranslate_ui()
        self.toolbar.retranslate_ui()
        self.catalogue_widget.retranslate_ui()
        self.active_mods_widget.retranslate_ui()
        self.mod_details_widget.retranslate_ui()
        if not self.statusBar().currentMessage():
            self.statusBar().showMessage(self.tr("Ready"))

    def _apply_view_fonts(self):
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if not app:
            return

        app_font = app.font()

        self.catalogue_widget.setFont(app_font)
        self.catalogue_widget.list_widget.setFont(app_font)
        self.catalogue_widget.search_bar.setFont(app_font)
        self.catalogue_widget.tab_bar.setFont(app_font)
        self.catalogue_widget.btn_toggle_view.setFont(app_font)

        self.active_mods_widget.setFont(app_font)
        self.active_mods_widget.list_widget.setFont(app_font)
        self.active_mods_widget.list_widget.header().setFont(app_font)
        self.active_mods_widget.preset_selector.setFont(app_font)
        self.active_mods_widget.preset_selector.combo.setFont(app_font)

    def _handle_profile_write_error(self, error: ProfileWriteError):
        with self._signals_blocked(self.catalogue_widget, self.active_mods_widget):
            self.app_model.reload()

        self._show_error_message(
            self.tr("Profile Update Failed"),
            self.tr(
                "Could not update the game's profile file:\n{0}\n\n"
                "Close the game or any tool using options.set, then try again.\n\n"
                "Technical details:\n{1}"
            ).format(error.path, error.reason),
        )
        self.statusBar().showMessage(self.tr("Profile update failed."), 5000)

    def _connect_signals(self):
        self._connect_catalogue_signals()
        self._connect_active_mods_signals()
        self._connect_preset_signals()
        self.toolbar.play_requested.connect(self._on_launch_game)

    def _connect_catalogue_signals(self):
        self.btn_add.clicked.connect(self._on_add_mod)
        self.btn_remove.clicked.connect(self._on_remove_mod_selected)
        self.catalogue_widget.mod_double_clicked.connect(self._on_add_mod)
        self.catalogue_widget.selection_changed.connect(
            self._on_catalogue_selection_changed
        )
        self.catalogue_widget.context_menu_requested.connect(
            self._show_catalogue_context_menu
        )

    def _connect_active_mods_signals(self):
        self.active_mods_widget.move_up_requested.connect(self._on_move_up)
        self.active_mods_widget.move_down_requested.connect(self._on_move_down)
        self.active_mods_widget.clear_requested.connect(self._on_clear_mods)
        self.active_mods_widget.mod_double_clicked.connect(self._on_remove_mod)
        self.active_mods_widget.selection_changed.connect(
            self._on_active_mods_selection_changed
        )
        self.active_mods_widget.context_menu_requested.connect(
            self._show_active_mods_context_menu
        )
        self.active_mods_widget.order_changed.connect(
            self._on_active_mods_order_changed
        )

    def _connect_preset_signals(self):
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

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors(self)
        self.btn_add.setIcon(qta.icon("fa5s.angle-double-right", **icon_colors))
        self.btn_remove.setIcon(qta.icon("fa5s.angle-double-left", **icon_colors))
        self.toolbar.refresh_icons()
        self.active_mods_widget.preset_selector.refresh_icons()
        self.catalogue_widget.refresh_icons()

    def _connect_model_events(self):
        """Subscribe to backend model events for automatic UI refreshing."""
        self.app_model.subscribe(
            EventType.CATALOGUE_CHANGED, self._on_catalogue_changed
        )
        self.app_model.subscribe(
            EventType.ACTIVE_MODS_CHANGED, self._on_active_mods_changed
        )
        self.app_model.subscribe(EventType.PRESETS_CHANGED, self._on_presets_changed)

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
        mod_id = self.catalogue_widget.get_mod_id_at(pos)
        if not mod_id:
            return
        self._show_mod_context_menu(
            mod_id, self.catalogue_widget.map_list_pos_to_global(pos)
        )

    def _show_active_mods_context_menu(self, pos):
        mod_id = self.active_mods_widget.get_mod_id_at(pos)
        if not mod_id:
            return
        self._show_mod_context_menu(
            mod_id, self.active_mods_widget.map_list_pos_to_global(pos)
        )

    def _show_mod_context_menu(self, mod_id: str, global_pos):
        mod = self._get_mod_by_id(mod_id)
        if not mod:
            return

        menu = QMenu(self)

        open_folder_action = menu.addAction(self.tr("Open Mod Folder"))
        open_workshop_action = None
        if not mod.isLocal and mod_id.isdigit():
            open_workshop_action = menu.addAction(self.tr("Open in Steam Workshop"))

        action = menu.exec(global_pos)

        if action == open_folder_action:
            self._open_existing_path(mod.path)
        elif open_workshop_action and action == open_workshop_action:
            system_actions.open_url(f"steam://url/CommunityFilePage/{mod_id}")

    def _on_catalogue_selection_changed(self):
        mod_id = self.catalogue_widget.get_selected_mod_id()
        if mod_id:
            # Clear active mods selection to avoid two mods selected at once
            with self._signals_blocked(self.active_mods_widget):
                self.active_mods_widget.clear_selection()

            mod = self._get_mod_by_id(mod_id)
            self.mod_details_widget.display_mod(mod)

    def _on_active_mods_selection_changed(self):
        mod_id = self.active_mods_widget.get_selected_mod_id()
        if mod_id:
            # Clear catalogue selection
            with self._signals_blocked(self.catalogue_widget):
                self.catalogue_widget.clear_selection()

            mod = self._get_mod_by_id(mod_id)
            self.mod_details_widget.display_mod(mod)

    def refresh_ui(self):
        """
        Fetches the latest state from the ModManager and updates the widgets.
        """
        self._populate_catalogue()
        self._populate_active_mods()
        self._populate_presets()
        self._update_preset_unsaved_state()

    def _update_preset_unsaved_state(self):
        current_preset = self._current_preset_name()
        if not self.active_mods_widget.preset_selector.has_selected_preset():
            self.active_mods_widget.preset_selector.set_unsaved_state(False)
            return

        presets = self.app_model.get_all_presets()
        preset_mods = presets.get(current_preset, [])
        active_mods = [m.id for m in self.app_model.get_active_mods()]

        is_unsaved = preset_mods != active_mods
        self.active_mods_widget.preset_selector.set_unsaved_state(is_unsaved)

    def _on_add_mod(self):
        mod_ids = self.catalogue_widget.get_selected_mod_ids()
        if not mod_ids:
            return

        activated_mods = []
        all_missing_deps = []

        for mod_id in mod_ids:
            if not self.app_model.is_mod_active(mod_id):
                try:
                    missing_deps = self.app_model.toggle_mod(mod_id)
                except ProfileWriteError as error:
                    self._handle_profile_write_error(error)
                    return
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
                    mod = self._get_mod_by_id(mod_id)
                    mod_name = mod.name if mod else mod_id
                    desc = self.tr(
                        "The mod '<b>{0}</b>' was activated, but the following required dependencies are missing from your catalogue. You must subscribe to them on the Workshop:"
                    ).format(mod_name)
                else:
                    desc = self.tr(
                        "The selected mods were activated, but the following required dependencies are missing from your catalogue. You must subscribe to them on the Workshop:"
                    )

                self._show_missing_mods_dialog(
                    self.tr("Missing Dependencies"),
                    desc,
                    unique_missing,
                )

    def _on_remove_mod_selected(self):
        mod_id = self.active_mods_widget.get_selected_mod_id()
        if mod_id:
            self._on_remove_mod(mod_id)

    def _on_clear_mods(self):
        if self.app_model.get_active_mods():
            # Clear all active mods
            try:
                self.app_model.clear_active_mods()
            except ProfileWriteError as error:
                self._handle_profile_write_error(error)
                return
            self.statusBar().showMessage(self.tr("Cleared all active mods"), 3000)

    def _on_remove_mod(self, mod_id: str):
        if self.app_model.is_mod_active(mod_id):
            try:
                self.app_model.toggle_mod(mod_id)
            except ProfileWriteError as error:
                self._handle_profile_write_error(error)
                return
            self.statusBar().showMessage(
                self.tr("Deactivated mod: {0}").format(mod_id), 3000
            )

    def _on_move_up(self, mod_id: str):
        try:
            self.app_model.move_mod_up(mod_id)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        self.statusBar().showMessage(self.tr("Moved mod {0} up").format(mod_id), 3000)

    def _on_move_down(self, mod_id: str):
        try:
            self.app_model.move_mod_down(mod_id)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        self.statusBar().showMessage(self.tr("Moved mod {0} down").format(mod_id), 3000)

    def _on_active_mods_order_changed(self, new_order: list[str]):
        try:
            self.app_model.set_active_mods_order(new_order)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        self.statusBar().showMessage(self.tr("Mod load order updated"), 3000)

    def _on_apply_preset(self, name: str):
        try:
            success, missing = self.app_model.apply_preset(name)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        if success:
            self.active_mods_widget.preset_selector.set_current_preset(name)
            self.statusBar().showMessage(
                self.tr("Applied preset: {0}").format(name), 3000
            )

            if missing:
                self._show_missing_mods_dialog(
                    self.tr("Preset Applied with Warnings"),
                    self.tr(
                        "The preset was applied, but the following mods are missing from your catalogue. You must subscribe to them on the Workshop:"
                    ),
                    missing,
                )

    def _on_save_preset(self, name: str):
        try:
            self.app_model.save_preset(name)
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
            return
        self.active_mods_widget.preset_selector.set_current_preset(name)
        self._update_preset_unsaved_state()
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

            try:
                self.app_model.save_preset(name)
            except ProfileWriteError as error:
                self._handle_profile_write_error(error)
                return
            self.active_mods_widget.preset_selector.set_current_preset(name)
            self._update_preset_unsaved_state()
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
            self._show_info_message(
                self.tr("Export Failed"),
                self.tr("There are no active mods to export."),
            )
            return

        code = self.app_model.export_share_code()
        if code:
            self._copy_to_clipboard(code)
            self._show_info_message(
                self.tr("Export Success"),
                self.tr(
                    "Share Code has been copied to your clipboard!\n\nYou can now paste it to your friends."
                ),
            )
        else:
            self._show_error_message(
                self.tr("Export Error"), self.tr("Failed to generate Share Code.")
            )

    def _on_import_mod(self):
        path = self._prompt_import_mod_path()
        if not path:
            return

        self.statusBar().showMessage(
            self.tr("Importing mod from {0}... Please wait.").format(path)
        )
        worker = self._create_import_worker(path)
        self.import_progress = self._create_import_progress_dialog()
        self.import_progress.show()
        self.thread_pool.start(worker)

    def _prompt_import_mod_path(self) -> str | None:
        dialog = ImportModDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.get_path()

    def _create_import_worker(self, path: str) -> ModImportWorker:
        worker = ModImportWorker(self.app_model, path)
        worker.signals.success.connect(self._on_import_success)
        worker.signals.error.connect(self._on_import_error)
        worker.signals.progress.connect(self._on_import_progress)
        worker.signals.conflict.connect(
            lambda mod_name: self._on_import_conflict(mod_name, worker)
        )
        return worker

    def _create_import_progress_dialog(self) -> QProgressDialog:
        progress = QProgressDialog(
            self.tr("Importing mod..."), self.tr("Cancel"), 0, 100, self
        )
        progress.setWindowTitle(self.tr("Import Mod"))
        progress.setCancelButton(None)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        progress.setValue(0)
        return progress

    def _on_import_progress(self, percent: int, message: str):
        if hasattr(self, "import_progress"):
            self.import_progress.setLabelText(self.tr(message))
            self.import_progress.setValue(percent)

    def _on_import_success(self):
        self.app_model.reload()
        if hasattr(self, "import_progress"):
            self.import_progress.setValue(100)
        self._show_info_message(
            self.tr("Import Success"), self.tr("Mod successfully imported!")
        )
        self.statusBar().showMessage(self.tr("Mod import complete."), 3000)

    def _on_import_error(self, error_msg: str):
        if hasattr(self, "import_progress"):
            self.import_progress.cancel()
        self._show_error_message(
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
        code = self._prompt_share_code()
        if not code:
            return

        try:
            success, missing_mods = self.app_model.import_share_code(code)

            if success:
                self._handle_imported_share_code(missing_mods)

        except InvalidShareCodeError:
            self._show_error_message(
                self.tr("Import Error"),
                self.tr("Invalid or corrupted Share Code."),
            )
        except ProfileWriteError as error:
            self._handle_profile_write_error(error)
        except Exception as e:
            self._show_error_message(
                self.tr("Import Error"),
                self.tr("An unexpected error occurred:\n{0}").format(e),
            )

    def _prompt_share_code(self) -> str | None:
        dialog = ImportShareCodeDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        return dialog.get_code()

    def _handle_imported_share_code(self, missing_mods: list[dict[str, str]]):
        self.active_mods_widget.preset_selector.reset_to_custom_load_order()

        if missing_mods:
            self._show_missing_mods_dialog(
                self.tr("Imported with Missing Mods"),
                self.tr(
                    "The load order was imported, but you are missing the following mods. You must subscribe to them on the Workshop for the preset to work perfectly:"
                ),
                missing_mods,
            )
            return

        self._show_info_message(
            self.tr("Import Success"),
            self.tr("Share Code successfully applied!"),
        )

    def _open_existing_path(self, path: str):
        if not path or not os.path.exists(path):
            self._show_warning_message(
                self.tr("Not Found"),
                self.tr("Cannot find path:\n{0}").format(path),
            )
            return

        system_actions.open_path(path)

    def _on_open_game_dir(self):
        config = self.app_model.get_config()
        if config.game_path:
            self._open_existing_path(config.game_path)

    def _on_open_profile(self):
        config = self.app_model.get_config()
        if config.profile_path:
            self._open_existing_path(config.profile_path)

    def _on_open_log_file(self):
        self._open_existing_path(str(app_paths.get_log_file_path()))

    def _on_refresh_data(self):
        # Prevent UI issues during reload
        with self._signals_blocked(
            self.catalogue_widget, self.active_mods_widget
        ):
            self.app_model.reload()

        self.statusBar().showMessage(self.tr("All data refreshed from disk."), 3000)

    def open_settings_dialog(self):
        config = self.app_model.get_config()
        dialog = self._create_settings_dialog(config)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_settings(dialog.get_paths(), config)

    def _on_open_settings(self):
        self.open_settings_dialog()

    def _create_settings_dialog(self, config):
        return SettingsDialog(
            current_game_path=config.game_path,
            current_workshop_path=config.workshop_path,
            current_profile_path=config.profile_path,
            current_language=config.language,
            current_theme=config.theme,
            current_font=config.font,
            parent=self,
        )

    def _apply_settings(self, new_paths: dict, config):
        path_changed = any(
            [
                new_paths["game_path"] != config.game_path,
                new_paths["workshop_path"] != config.workshop_path,
                new_paths["profile_path"] != config.profile_path,
            ]
        )
        language_changed = new_paths.get("language") != config.language
        appearance_changed = any(
            [
                new_paths.get("theme") != config.theme,
                new_paths.get("font") != config.font,
            ]
        )

        self.app_model.update_paths(
            game_path=new_paths["game_path"],
            workshop_path=new_paths["workshop_path"],
            profile_path=new_paths["profile_path"],
            language=new_paths.get("language"),
            theme=new_paths.get("theme"),
            font=new_paths.get("font"),
        )

        if appearance_changed:
            self._apply_appearance_settings(new_paths, config)

        if language_changed:
            self._apply_language_settings(new_paths, config)

        if path_changed:
            self._on_refresh_data()
            self.statusBar().showMessage(
                self.tr("Settings saved and data reloaded."), 3000
            )
        elif language_changed and appearance_changed:
            self.statusBar().showMessage(
                self.tr("Language and appearance settings applied."), 3000
            )
        elif language_changed:
            self.statusBar().showMessage(
                self.tr("Language settings applied."), 3000
            )
        elif appearance_changed:
            self.statusBar().showMessage(
                self.tr("Appearance settings applied."), 3000
            )
        else:
            self.statusBar().showMessage(self.tr("Settings saved."), 3000)

    def _apply_appearance_settings(self, new_paths: dict, config):
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            AppearanceManager.setup_appearance(
                app,
                theme=new_paths.get("theme", config.theme),
                font_name=new_paths.get("font", config.font),
            )
            self._apply_view_fonts()

            # Rebuild visible item views so custom-rendered and tree-based rows pick
            # up the new application font immediately.
            self.refresh_ui()
            self.catalogue_widget.list_widget.doItemsLayout()
            self.catalogue_widget.list_widget.viewport().update()
            self.active_mods_widget.list_widget.doItemsLayout()
            self.active_mods_widget.list_widget.viewport().update()
            self.refresh_icons()

    def _apply_language_settings(self, new_paths: dict, config):
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            TranslationManager.apply_language(
                app,
                new_paths.get("language", config.language),
            )
            self.retranslate_ui()

    def _on_generate_report(self):
        file_path = self._prompt_debug_report_path()
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self._build_debug_report())

            self._show_info_message(
                self.tr("Success"),
                self.tr("Debug report saved successfully to:\n{0}").format(file_path),
            )
        except Exception as e:
            self._show_error_message(
                self.tr("Error"),
                self.tr("Failed to save debug report:\n{0}").format(e),
            )

    def _prompt_debug_report_path(self) -> str:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Debug Report"),
            "goh_mod_manager_debug.txt",
            self.tr("Text Files (*.txt);;All Files (*)"),
        )
        return file_path

    def _build_debug_report(self) -> str:
        lines = [
            "--- GoH Mod Manager Debug Report ---",
            f"Generated at: {datetime.datetime.now()}",
            f"OS: {platform.system()} {platform.release()} ({platform.version()})",
            f"App Version: {app_paths.read_version()}",
            "",
            "--- Configuration ---",
        ]

        config = self.app_model.get_config()
        lines.extend(
            [
                f"Game Path: {config.game_path}",
                f"Workshop Path: {config.workshop_path}",
                f"Profile Path: {config.profile_path}",
                "",
                "--- Catalogue Stats ---",
            ]
        )

        local_mods = self.app_model.get_local_mods()
        workshop_mods = self.app_model.get_workshop_mods()
        all_mods = self.app_model.get_all_mods()
        lines.extend(
            [
                f"Total Installed Mods: {len(all_mods)}",
                f"Local Mods: {len(local_mods)}",
                f"Workshop Mods: {len(workshop_mods)}",
                "",
                "--- Active Mods Load Order ---",
            ]
        )

        active_mods = self.app_model.get_active_mods()
        if not active_mods:
            lines.append("No active mods.")
        else:
            for i, mod in enumerate(active_mods):
                mod_type = "Local" if mod.isLocal else "Workshop"
                lines.append(f"{i + 1}. {mod.name} (ID: {mod.id}) - {mod_type}")

        lines.extend(["", "--- Recent Logs (Last 100 Lines) ---"])
        lines.extend(self._read_recent_log_lines())
        return "\n".join(lines) + "\n"

    def _read_recent_log_lines(self) -> list[str]:
        log_path = app_paths.get_log_file_path()
        if not log_path.exists():
            return ["No log file found."]

        with open(log_path, "r", encoding="utf-8") as log_file:
            return [line.rstrip("\n") for line in log_file.readlines()[-100:]]

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtGui import QGuiApplication

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def _on_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def _on_catalogue_changed(self):
        self._populate_catalogue()

    def _on_active_mods_changed(self):
        self._populate_catalogue()
        self._populate_active_mods()
        self._update_preset_unsaved_state()

    def _on_presets_changed(self):
        self._populate_presets()
        self._update_preset_unsaved_state()

    def _on_launch_game(self):
        success = self.app_model.launch_game()
        if success:
            self.statusBar().showMessage(
                self.tr("Launching Call to Arms - Gates of Hell..."), 5000
            )
        else:
            self._show_error_message(
                self.tr("Launch Failed"),
                self.tr(
                    "Failed to launch the game. Make sure Steam is installed and running."
                ),
            )
