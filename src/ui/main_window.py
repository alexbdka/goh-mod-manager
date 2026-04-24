from contextlib import contextmanager

import qtawesome as qta
from PySide6.QtCore import Qt, QThreadPool, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.application.state import SettingsState
from src.core.events import EventType
from src.core.exceptions import (
    ConfigWriteError,
    InvalidShareCodeError,
    ProfileWriteError,
)
from src.core.manager import ModManager
from src.ui.appearance_manager import AppearanceManager
from src.ui.controllers.app_actions_controller import AppActionsController
from src.ui.controllers.load_order_controller import LoadOrderController
from src.ui.controllers.mod_import_controller import ModImportController
from src.ui.controllers.preset_controller import PresetController
from src.ui.controllers.selection_controller import SelectionController
from src.ui.dialogs.missing_mods_dialog import MissingModsDialog
from src.ui.dialogs.settings_dialog import SettingsDialog
from src.ui.dialogs.share_code_dialog import ImportShareCodeDialog
from src.ui.language_change_mixin import LanguageChangeMixin
from src.ui.onboarding_overlay import OnboardingOverlay, OnboardingStep
from src.ui.translation_manager import TranslationManager
from src.ui.widgets.active_mods_widget import ActiveModsWidget
from src.ui.widgets.catalogue_widget import CatalogueWidget
from src.ui.widgets.main_menu_bar import MainMenuBar
from src.ui.widgets.main_tool_bar import MainToolBar
from src.ui.widgets.mod_details_widget import ModDetailsWidget
from src.utils import app_paths


class MainWindow(LanguageChangeMixin, QMainWindow):
    """Primary application window that wires Qt widgets to the application facade."""

    def __init__(self, app_model: ModManager):
        super().__init__()
        self.app_model = app_model
        self._onboarding_overlay: OnboardingOverlay | None = None

        self.resize(1000, 1000)

        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.mod_import_controller = ModImportController(
            parent=self,
            import_mod=self.app_model.import_mod,
            reload=self.app_model.reload,
            thread_pool=self.thread_pool,
            status_bar=self.statusBar(),
            show_info_message=self._show_info_message,
            show_error_message=self._show_error_message,
        )
        self.app_actions_controller = AppActionsController(
            parent=self,
            build_debug_report=self.app_model.build_debug_report,
            launch_game=self.app_model.launch_game,
            status_bar=self.statusBar(),
            show_info_message=self._show_info_message,
            show_error_message=self._show_error_message,
        )

        self._setup_menu()
        self._setup_toolbar()
        self._setup_ui()
        self.selection_controller = SelectionController(
            parent=self,
            catalogue_widget=self.catalogue_widget,
            active_mods_widget=self.active_mods_widget,
            mod_details_widget=self.mod_details_widget,
            get_mod_by_id=self._get_mod_by_id,
            signals_blocked=self._signals_blocked,
            show_warning_message=self._show_warning_message,
        )
        self.load_order_controller = LoadOrderController(
            catalogue_widget=self.catalogue_widget,
            active_mods_widget=self.active_mods_widget,
            activate_mods=self.app_model.activate_mods,
            deactivate_mod=self.app_model.deactivate_mod,
            clear_active_mods=self.app_model.clear_active_mods,
            move_mod_up=self.app_model.move_mod_up,
            move_mod_down=self.app_model.move_mod_down,
            set_active_mods_order=self.app_model.set_active_mods_order,
            status_message=self.statusBar().showMessage,
            show_missing_mods_dialog=self._show_missing_mods_dialog,
            handle_profile_write_error=self._handle_profile_write_error,
            get_mod_by_id=self._get_mod_by_id,
            tr=self.tr,
        )
        self.preset_controller = PresetController(
            parent=self,
            preset_selector=self.active_mods_widget.preset_selector,
            apply_preset=self.app_model.apply_preset,
            save_preset=self.app_model.save_preset,
            delete_preset=self.app_model.delete_preset,
            get_all_presets=self.app_model.get_all_presets,
            status_bar=self.statusBar(),
            show_missing_mods_dialog=self._show_missing_mods_dialog,
            handle_profile_write_error=self._handle_profile_write_error,
            update_unsaved_state=self._update_preset_unsaved_state,
        )
        self._connect_signals()
        self._connect_menu_signals()
        self._connect_model_events()
        self.retranslate_ui()

        self.refresh_ui()
        QTimer.singleShot(0, self._show_onboarding_if_needed)

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

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setHandleWidth(6)

        top_widget = QWidget()
        lists_layout = QHBoxLayout(top_widget)
        lists_layout.setContentsMargins(0, 0, 0, 0)

        self.catalogue_widget = CatalogueWidget()
        self.active_mods_widget = ActiveModsWidget()

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

        main_splitter.setSizes([400, 150])

        main_layout.addWidget(main_splitter)

        self.statusBar().showMessage("")
        self._apply_view_fonts()
        self.refresh_icons()
        QTimer.singleShot(0, self.refresh_icons)

    @contextmanager
    def _signals_blocked(self, *widgets: QWidget):
        """Temporarily block list widget signals during bulk UI refreshes."""
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

    def _get_mod_by_id(self, mod_id: str):
        return self.app_model.get_mod_state(mod_id)

    def _current_preset_name(self) -> str:
        return self.active_mods_widget.preset_selector.current_preset_name()

    def _populate_catalogue(self):
        self.catalogue_widget.populate(self.app_model.get_catalogue_state())

    def _populate_active_mods(self):
        self.active_mods_widget.populate(self.app_model.get_active_mods_state())

    def _populate_presets(self):
        presets_state = self.app_model.get_presets_state(self._current_preset_name())
        self.active_mods_widget.preset_selector.populate(
            presets_state.preset_names, presets_state.current_preset_name or ""
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
        if not self.statusBar().currentMessage():
            self.statusBar().showMessage(self.tr("Ready"))

    def _apply_view_fonts(self):
        app = QApplication.instance()
        if not isinstance(app, QApplication):
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
        self.btn_add.clicked.connect(self.load_order_controller.add_selected_mods)
        self.btn_remove.clicked.connect(self.load_order_controller.remove_selected_mod)
        self.catalogue_widget.mod_double_clicked.connect(
            self.load_order_controller.add_selected_mods
        )
        self.catalogue_widget.selection_changed.connect(
            self.selection_controller.handle_catalogue_selection_changed
        )
        self.catalogue_widget.context_menu_requested.connect(
            self.selection_controller.show_catalogue_context_menu
        )

    def _connect_active_mods_signals(self):
        self.active_mods_widget.move_up_requested.connect(
            self.load_order_controller.move_up
        )
        self.active_mods_widget.move_down_requested.connect(
            self.load_order_controller.move_down
        )
        self.active_mods_widget.clear_requested.connect(
            self.load_order_controller.clear_mods
        )
        self.active_mods_widget.mod_double_clicked.connect(
            self.load_order_controller.remove_mod
        )
        self.active_mods_widget.selection_changed.connect(
            self.selection_controller.handle_active_mods_selection_changed
        )
        self.active_mods_widget.context_menu_requested.connect(
            self.selection_controller.show_active_mods_context_menu
        )
        self.active_mods_widget.order_changed.connect(
            self.load_order_controller.reorder
        )

    def _connect_preset_signals(self):
        self.active_mods_widget.preset_selector.preset_applied.connect(
            self.preset_controller.apply_preset
        )
        self.active_mods_widget.preset_selector.save_requested.connect(
            self.preset_controller.save_preset
        )
        self.active_mods_widget.preset_selector.save_as_requested.connect(
            self.preset_controller.save_preset_as
        )
        self.active_mods_widget.preset_selector.delete_requested.connect(
            self.preset_controller.delete_preset
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
        self.main_menu_bar.interface_tour_action.triggered.connect(
            self._show_onboarding_overlay
        )
        self.main_menu_bar.about_action.triggered.connect(self._on_about)

    def refresh_ui(self):
        """Refresh all top-level widgets from the latest application state."""
        self._populate_catalogue()
        self._populate_active_mods()
        self._populate_presets()
        self._update_preset_unsaved_state()

    def _update_preset_unsaved_state(self):
        presets_state = self.app_model.get_presets_state(self._current_preset_name())
        self.active_mods_widget.preset_selector.set_unsaved_state(
            presets_state.is_unsaved
        )

    def _on_export_share_code(self):
        result = self.app_model.build_share_code_export()
        if not result.has_active_mods:
            self._show_info_message(
                self.tr("Export Failed"),
                self.tr("There are no active mods to export."),
            )
            return

        code = result.code
        if code:
            self.app_actions_controller.copy_to_clipboard(code)
            self._show_info_message(
                self.tr("Export Success"),
                self.tr(
                    "Share Code has been copied to your clipboard!\n\n"
                    "You can now paste it to your friends."
                ),
            )
        else:
            self._show_error_message(
                self.tr("Export Error"), self.tr("Failed to generate Share Code.")
            )

    def _on_import_mod(self):
        self.mod_import_controller.start_import_flow()

    def _on_import_share_code(self):
        code = self._prompt_share_code()
        if not code:
            return

        try:
            result = self.app_model.apply_share_code(code)
            if result.success:
                self._handle_imported_share_code(result.missing_mods)

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
                    "The load order was imported, but you are missing the "
                    "following mods. You must subscribe to them on the "
                    "Workshop for the preset to work perfectly:"
                ),
                missing_mods,
            )
            return

        self._show_info_message(
            self.tr("Import Success"),
            self.tr("Share Code successfully applied!"),
        )

    def _on_open_game_dir(self):
        config = self.app_model.get_config()
        if config.game_path:
            self.selection_controller.open_existing_path(config.game_path)

    def _on_open_profile(self):
        config = self.app_model.get_config()
        if config.profile_path:
            self.selection_controller.open_existing_path(config.profile_path)

    def _on_open_log_file(self):
        self.selection_controller.open_existing_path(str(app_paths.get_log_file_path()))

    def _on_refresh_data(self):
        """Reload data from disk while suppressing intermediate list signals."""
        with self._signals_blocked(self.catalogue_widget, self.active_mods_widget):
            self.app_model.reload()

        self.statusBar().showMessage(self.tr("All data refreshed from disk."), 3000)

    def open_settings_dialog(self):
        dialog = self._create_settings_dialog()

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_settings(dialog.get_settings_state())

    def _on_open_settings(self):
        self.open_settings_dialog()

    def _create_settings_dialog(self):
        return SettingsDialog(
            settings_state=self.app_model.get_settings_state(), parent=self
        )

    def _apply_settings(self, settings_state: SettingsState):
        previous_settings = self.app_model.get_settings_state()
        try:
            result = self.app_model.apply_settings(settings_state)
        except ConfigWriteError as error:
            self._show_error_message(
                self.tr("Settings Save Failed"),
                self.tr("Could not save settings:\n{0}\n\n{1}").format(
                    error.path, error.reason
                ),
            )
            self.statusBar().showMessage(self.tr("Settings save failed."), 5000)
            return

        if result.appearance_changed:
            self._apply_appearance_settings(settings_state, previous_settings)

        if result.language_changed:
            self._apply_language_settings(settings_state, previous_settings)

        if result.path_changed:
            self._on_refresh_data()
            self.statusBar().showMessage(
                self.tr("Settings saved and data reloaded."), 3000
            )
        elif result.language_changed and result.appearance_changed:
            self.statusBar().showMessage(
                self.tr("Language and appearance settings applied."), 3000
            )
        elif result.language_changed:
            self.statusBar().showMessage(self.tr("Language settings applied."), 3000)
        elif result.appearance_changed:
            self.statusBar().showMessage(self.tr("Appearance settings applied."), 3000)
        else:
            self.statusBar().showMessage(self.tr("Settings saved."), 3000)

    def _apply_appearance_settings(
        self, settings_state: SettingsState, previous_settings: SettingsState
    ):
        app = QApplication.instance()
        if isinstance(app, QApplication):
            AppearanceManager.setup_appearance(
                app,
                theme=settings_state.theme or previous_settings.theme,
                font_name=settings_state.font or previous_settings.font,
            )
            self._apply_view_fonts()

            # Rebuild visible item views so delegate-rendered content picks up the
            # updated application font immediately.
            self.refresh_ui()
            self.catalogue_widget.list_widget.doItemsLayout()
            self.catalogue_widget.list_widget.viewport().update()
            self.active_mods_widget.list_widget.doItemsLayout()
            self.active_mods_widget.list_widget.viewport().update()
            self.refresh_icons()

    def _apply_language_settings(
        self, settings_state: SettingsState, previous_settings: SettingsState
    ):
        app = QApplication.instance()
        if isinstance(app, QApplication):
            TranslationManager.apply_language(
                app,
                settings_state.language or previous_settings.language,
            )

    def _on_generate_report(self):
        self.app_actions_controller.generate_report()

    def _on_about(self):
        self.app_actions_controller.show_about()

    def _show_onboarding_if_needed(self):
        if not self.app_model.has_seen_onboarding():
            self._show_onboarding_overlay()

    def _show_onboarding_overlay(self):
        if self._onboarding_overlay and self._onboarding_overlay.isVisible():
            self._onboarding_overlay.raise_()
            self._onboarding_overlay.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
            return

        self._onboarding_overlay = OnboardingOverlay(
            self,
            self._build_onboarding_steps(),
            on_finished=self._finish_onboarding,
        )
        self._onboarding_overlay.start()

    def _finish_onboarding(self):
        try:
            self.app_model.mark_onboarding_seen()
        except ConfigWriteError as error:
            self._show_error_message(
                self.tr("Onboarding Save Failed"),
                self.tr("Could not save onboarding progress:\n{0}\n\n{1}").format(
                    error.path, error.reason
                ),
            )
            self.statusBar().showMessage(
                self.tr("Onboarding progress was not saved."), 5000
            )
        finally:
            self._onboarding_overlay = None

    def _build_onboarding_steps(self) -> list[OnboardingStep]:
        return [
            OnboardingStep(
                target=self.catalogue_widget,
                title=self.tr("Available Mods"),
                body=self.tr(
                    "This catalogue lists the mods detected in your local "
                    "mods folder and subscribed Workshop content."
                ),
            ),
            OnboardingStep(
                target=[
                    self.catalogue_widget.search_bar,
                    self.catalogue_widget.tab_bar,
                ],
                title=self.tr("Find What You Need"),
                body=self.tr(
                    "Use search and filters to narrow the catalogue by "
                    "name and by source."
                ),
            ),
            OnboardingStep(
                target=[self.btn_add, self.btn_remove],
                title=self.tr("Manage the Load Order"),
                body=self.tr(
                    "Use these controls, double-click, or drag and drop "
                    "to move mods between the catalogue and the active "
                    "load order."
                ),
            ),
            OnboardingStep(
                target=self.active_mods_widget,
                title=self.tr("Active Mods"),
                body=self.tr(
                    "This list is the load order that will be written to "
                    "the game's profile. Lower entries load later and can "
                    "override earlier ones."
                ),
            ),
            OnboardingStep(
                target=self.active_mods_widget.preset_selector,
                title=self.tr("Presets"),
                body=self.tr(
                    "Save the current load order as a preset, reapply it "
                    "later, or compare the current state against a saved "
                    "setup."
                ),
            ),
            OnboardingStep(
                target=self.mod_details_widget,
                title=self.tr("Mod Details"),
                body=self.tr(
                    "The details panel shows the selected mod's "
                    "description, metadata, and dependency status."
                ),
            ),
        ]

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
        self.app_actions_controller.launch_game()
