import qtawesome as qta
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMenuBar
from src.ui.appearance_manager import AppearanceManager
from src.ui.language_change_mixin import LanguageChangeMixin


class MainMenuBar(LanguageChangeMixin, QMenuBar):
    """
    Modular component for the application's main menu bar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_menus()
        self.retranslate_ui()
        self.refresh_icons()

    def _setup_menus(self):
        # File Menu
        self.file_menu = self.addMenu("")

        self.import_code_action = QAction(self)
        self.import_code_action.setShortcut("Ctrl+Shift+I")
        self.export_code_action = QAction(self)
        self.export_code_action.setShortcut("Ctrl+Shift+E")

        self.file_menu.addAction(self.import_code_action)
        self.file_menu.addAction(self.export_code_action)
        self.file_menu.addSeparator()

        self.import_mod_action = QAction(self)
        self.import_mod_action.setShortcut("Ctrl+I")
        self.file_menu.addAction(self.import_mod_action)
        self.file_menu.addSeparator()

        # Open Submenu
        self.open_menu = self.file_menu.addMenu("")
        self.open_game_dir_action = QAction(self)
        self.open_profile_file_action = QAction(self)
        self.open_config_folder_action = QAction(self)
        self.open_log_file_action = QAction(self)

        self.open_menu.addAction(self.open_game_dir_action)
        self.open_menu.addAction(self.open_profile_file_action)
        self.open_menu.addSeparator()
        self.open_menu.addAction(self.open_config_folder_action)
        self.open_menu.addAction(self.open_log_file_action)

        self.file_menu.addSeparator()

        self.exit_action = QAction(self)
        self.exit_action.setShortcut("Ctrl+Q")
        parent_window = self.parentWidget()
        if isinstance(parent_window, QMainWindow):
            self.exit_action.triggered.connect(parent_window.close)

        self.file_menu.addAction(self.exit_action)

        # Edit Menu
        self.edit_menu = self.addMenu("")
        self.settings_action = QAction(self)
        self.settings_action.setShortcut("Ctrl+,")
        self.edit_menu.addAction(self.settings_action)

        # View Menu
        self.view_menu = self.addMenu("")
        self.refresh_action = QAction(self)
        self.refresh_action.setShortcuts([QKeySequence("F5"), QKeySequence("Ctrl+R")])
        self.view_menu.addAction(self.refresh_action)

        # Help Menu
        self.help_menu = self.addMenu("")
        self.generate_report_action = QAction(self)
        self.help_menu.addAction(self.generate_report_action)
        self.interface_tour_action = QAction(self)
        self.help_menu.addAction(self.interface_tour_action)
        self.help_menu.addSeparator()
        self.about_action = QAction(self)
        self.help_menu.addAction(self.about_action)

    def retranslate_ui(self):
        self.file_menu.setTitle(self.tr("&File"))
        self.import_code_action.setText(self.tr("Import Share Code..."))
        self.export_code_action.setText(self.tr("Export Share Code..."))
        self.import_mod_action.setText(self.tr("Import Mod..."))
        self.open_menu.setTitle(self.tr("Open..."))
        self.open_game_dir_action.setText(self.tr("Game Directory"))
        self.open_config_folder_action.setText(self.tr("Config Folder"))
        self.open_profile_file_action.setText(self.tr("Profile (options.set)"))
        self.open_log_file_action.setText(self.tr("Log File"))
        self.exit_action.setText(self.tr("E&xit"))
        self.edit_menu.setTitle(self.tr("&Edit"))
        self.settings_action.setText(self.tr("Preferences..."))
        self.view_menu.setTitle(self.tr("&View"))
        self.refresh_action.setText(self.tr("Refresh"))
        self.help_menu.setTitle(self.tr("&Help"))
        self.generate_report_action.setText(self.tr("Generate Debug Report..."))
        self.interface_tour_action.setText(self.tr("Interface Tour..."))
        self.about_action.setText(self.tr("About"))

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors(self)
        self.import_code_action.setIcon(qta.icon("fa5s.file-import", **icon_colors))
        self.export_code_action.setIcon(qta.icon("fa5s.file-export", **icon_colors))
        self.import_mod_action.setIcon(qta.icon("fa5s.box-open", **icon_colors))
        self.open_game_dir_action.setIcon(qta.icon("fa5s.folder-open", **icon_colors))
        self.open_config_folder_action.setIcon(
            qta.icon("fa5s.folder-open", **icon_colors)
        )
        self.open_profile_file_action.setIcon(qta.icon("fa5s.file-alt", **icon_colors))
        self.open_log_file_action.setIcon(
            qta.icon("fa5s.file-medical-alt", **icon_colors)
        )
        self.exit_action.setIcon(qta.icon("fa5s.sign-out-alt", **icon_colors))
        self.settings_action.setIcon(qta.icon("fa5s.cog", **icon_colors))
        self.refresh_action.setIcon(qta.icon("fa5s.sync-alt", **icon_colors))
        self.generate_report_action.setIcon(qta.icon("fa5s.bug", **icon_colors))
        self.interface_tour_action.setIcon(qta.icon("fa5s.route", **icon_colors))
        self.about_action.setIcon(qta.icon("fa5s.info-circle", **icon_colors))
