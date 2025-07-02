# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QRect,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QFont,
    QIcon,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# noinspection PyUnresolvedReferences
import goh_mod_manager.resources.resources_rc


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        MainWindow.setMinimumSize(QSize(1200, 600))
        icon = QIcon()
        icon.addFile(
            ":/assets/icons/logo.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        MainWindow.setWindowIcon(icon)
        self.actionImport_Mod = QAction(MainWindow)
        self.actionImport_Mod.setObjectName("actionImport_Mod")
        self.actionRefresh = QAction(MainWindow)
        self.actionRefresh.setObjectName("actionRefresh")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.actionClear_Active_Mods = QAction(MainWindow)
        self.actionClear_Active_Mods.setObjectName("actionClear_Active_Mods")
        self.actionShow_Mod_Details = QAction(MainWindow)
        self.actionShow_Mod_Details.setObjectName("actionShow_Mod_Details")
        self.actionShow_Mod_Details.setCheckable(True)
        self.actionShow_Mod_Details.setChecked(True)
        self.actionUser_Manual = QAction(MainWindow)
        self.actionUser_Manual.setObjectName("actionUser_Manual")
        self.actionCheck_Updates = QAction(MainWindow)
        self.actionCheck_Updates.setObjectName("actionCheck_Updates")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionTheme = QAction(MainWindow)
        self.actionTheme.setObjectName("actionTheme")
        self.actionDefaultFont = QAction(MainWindow)
        self.actionDefaultFont.setObjectName("actionDefaultFont")
        self.actionDefaultFont.setCheckable(False)
        self.actionDyslexiaFont = QAction(MainWindow)
        self.actionDyslexiaFont.setObjectName("actionDyslexiaFont")
        self.actionDyslexiaFont.setCheckable(False)
        font = QFont()
        font.setFamilies(["OpenDyslexic"])
        self.actionDyslexiaFont.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_main = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_main.setSpacing(8)
        self.horizontalLayout_main.setObjectName("horizontalLayout_main")
        self.horizontalLayout_main.setContentsMargins(8, 8, 8, 8)
        self.splitter_main = QSplitter(self.centralwidget)
        self.splitter_main.setObjectName("splitter_main")
        self.splitter_main.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_main.setChildrenCollapsible(False)
        self.widget_left_panel = QWidget(self.splitter_main)
        self.widget_left_panel.setObjectName("widget_left_panel")
        self.widget_left_panel.setMinimumSize(QSize(250, 0))
        self.widget_left_panel.setMaximumSize(QSize(400, 16777215))
        self.verticalLayout_installed = QVBoxLayout(self.widget_left_panel)
        self.verticalLayout_installed.setSpacing(6)
        self.verticalLayout_installed.setObjectName("verticalLayout_installed")
        self.verticalLayout_installed.setContentsMargins(0, 0, 0, 0)
        self.groupBox_installed_mods = QGroupBox(self.widget_left_panel)
        self.groupBox_installed_mods.setObjectName("groupBox_installed_mods")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_installed_mods)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_search_installed = QHBoxLayout()
        self.horizontalLayout_search_installed.setSpacing(6)
        self.horizontalLayout_search_installed.setObjectName(
            "horizontalLayout_search_installed"
        )
        self.lineEdit_search_installed = QLineEdit(self.groupBox_installed_mods)
        self.lineEdit_search_installed.setObjectName("lineEdit_search_installed")
        self.lineEdit_search_installed.setClearButtonEnabled(True)

        self.horizontalLayout_search_installed.addWidget(self.lineEdit_search_installed)

        self.pushButton_refresh_mods = QPushButton(self.groupBox_installed_mods)
        self.pushButton_refresh_mods.setObjectName("pushButton_refresh_mods")
        self.pushButton_refresh_mods.setMinimumSize(QSize(32, 32))
        self.pushButton_refresh_mods.setMaximumSize(QSize(32, 32))
        icon1 = QIcon()
        icon1.addFile(
            ":/assets/icons/refresh-line.svg",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_refresh_mods.setIcon(icon1)
        self.pushButton_refresh_mods.setIconSize(QSize(16, 16))

        self.horizontalLayout_search_installed.addWidget(self.pushButton_refresh_mods)

        self.verticalLayout_2.addLayout(self.horizontalLayout_search_installed)

        self.listWidget_available_mods = QListWidget(self.groupBox_installed_mods)
        self.listWidget_available_mods.setObjectName("listWidget_available_mods")
        self.listWidget_available_mods.setProperty("showDropIndicator", False)
        self.listWidget_available_mods.setDragDropMode(
            QAbstractItemView.DragDropMode.NoDragDrop
        )
        self.listWidget_available_mods.setAlternatingRowColors(True)
        self.listWidget_available_mods.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.listWidget_available_mods.setUniformItemSizes(True)
        self.listWidget_available_mods.setSortingEnabled(True)

        self.verticalLayout_2.addWidget(self.listWidget_available_mods)

        self.horizontalLayout_mod_actions = QHBoxLayout()
        self.horizontalLayout_mod_actions.setObjectName("horizontalLayout_mod_actions")
        self.pushButton_add_mod = QPushButton(self.groupBox_installed_mods)
        self.pushButton_add_mod.setObjectName("pushButton_add_mod")
        self.pushButton_add_mod.setEnabled(True)

        self.horizontalLayout_mod_actions.addWidget(self.pushButton_add_mod)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_mod_actions.addItem(self.horizontalSpacer_2)

        self.verticalLayout_2.addLayout(self.horizontalLayout_mod_actions)

        self.verticalLayout_installed.addWidget(self.groupBox_installed_mods)

        self.splitter_main.addWidget(self.widget_left_panel)
        self.widget_center_panel = QWidget(self.splitter_main)
        self.widget_center_panel.setObjectName("widget_center_panel")
        self.widget_center_panel.setMinimumSize(QSize(300, 0))
        self.verticalLayout_active = QVBoxLayout(self.widget_center_panel)
        self.verticalLayout_active.setSpacing(6)
        self.verticalLayout_active.setObjectName("verticalLayout_active")
        self.verticalLayout_active.setContentsMargins(0, 0, 0, 0)
        self.groupBox_active_mods = QGroupBox(self.widget_center_panel)
        self.groupBox_active_mods.setObjectName("groupBox_active_mods")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_active_mods)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_search_active = QHBoxLayout()
        self.horizontalLayout_search_active.setSpacing(6)
        self.horizontalLayout_search_active.setObjectName(
            "horizontalLayout_search_active"
        )
        self.lineEdit_search_active = QLineEdit(self.groupBox_active_mods)
        self.lineEdit_search_active.setObjectName("lineEdit_search_active")
        self.lineEdit_search_active.setClearButtonEnabled(True)

        self.horizontalLayout_search_active.addWidget(self.lineEdit_search_active)

        self.label_mod_count = QLabel(self.groupBox_active_mods)
        self.label_mod_count.setObjectName("label_mod_count")
        self.label_mod_count.setMinimumSize(QSize(80, 0))

        self.horizontalLayout_search_active.addWidget(self.label_mod_count)

        self.verticalLayout_3.addLayout(self.horizontalLayout_search_active)

        self.listWidget_active_mods = QListWidget(self.groupBox_active_mods)
        self.listWidget_active_mods.setObjectName("listWidget_active_mods")
        self.listWidget_active_mods.setAcceptDrops(True)
        self.listWidget_active_mods.setDragEnabled(True)
        self.listWidget_active_mods.setDragDropMode(
            QAbstractItemView.DragDropMode.InternalMove
        )
        self.listWidget_active_mods.setAlternatingRowColors(True)
        self.listWidget_active_mods.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.listWidget_active_mods.setUniformItemSizes(True)

        self.verticalLayout_3.addWidget(self.listWidget_active_mods)

        self.horizontalLayout_load_order_controls = QHBoxLayout()
        self.horizontalLayout_load_order_controls.setSpacing(6)
        self.horizontalLayout_load_order_controls.setObjectName(
            "horizontalLayout_load_order_controls"
        )
        self.pushButton_move_up = QPushButton(self.groupBox_active_mods)
        self.pushButton_move_up.setObjectName("pushButton_move_up")
        self.pushButton_move_up.setEnabled(True)

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_move_up)

        self.pushButton_move_down = QPushButton(self.groupBox_active_mods)
        self.pushButton_move_down.setObjectName("pushButton_move_down")
        self.pushButton_move_down.setEnabled(True)

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_move_down)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_load_order_controls.addItem(self.horizontalSpacer)

        self.pushButton_remove_mod = QPushButton(self.groupBox_active_mods)
        self.pushButton_remove_mod.setObjectName("pushButton_remove_mod")
        self.pushButton_remove_mod.setEnabled(True)

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_remove_mod)

        self.pushButton_clear_all = QPushButton(self.groupBox_active_mods)
        self.pushButton_clear_all.setObjectName("pushButton_clear_all")
        self.pushButton_clear_all.setEnabled(True)

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_clear_all)

        self.verticalLayout_3.addLayout(self.horizontalLayout_load_order_controls)

        self.label_drag_info = QLabel(self.groupBox_active_mods)
        self.label_drag_info.setObjectName("label_drag_info")
        font1 = QFont()
        font1.setItalic(True)
        self.label_drag_info.setFont(font1)
        self.label_drag_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_drag_info.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.label_drag_info)

        self.verticalLayout_active.addWidget(self.groupBox_active_mods)

        self.splitter_main.addWidget(self.widget_center_panel)
        self.widget_right_panel = QWidget(self.splitter_main)
        self.widget_right_panel.setObjectName("widget_right_panel")
        self.widget_right_panel.setMinimumSize(QSize(250, 0))
        self.widget_right_panel.setMaximumSize(QSize(350, 16777215))
        self.verticalLayout_sidebar = QVBoxLayout(self.widget_right_panel)
        self.verticalLayout_sidebar.setSpacing(6)
        self.verticalLayout_sidebar.setObjectName("verticalLayout_sidebar")
        self.verticalLayout_sidebar.setContentsMargins(0, 0, 0, 0)
        self.groupBox_mod_info = QGroupBox(self.widget_right_panel)
        self.groupBox_mod_info.setObjectName("groupBox_mod_info")
        self.groupBox_mod_info.setMinimumSize(QSize(0, 150))
        self.verticalLayout_mod_info = QVBoxLayout(self.groupBox_mod_info)
        self.verticalLayout_mod_info.setSpacing(6)
        self.verticalLayout_mod_info.setObjectName("verticalLayout_mod_info")
        self.label_mod_name = QLabel(self.groupBox_mod_info)
        self.label_mod_name.setObjectName("label_mod_name")
        font2 = QFont()
        font2.setBold(True)
        self.label_mod_name.setFont(font2)
        self.label_mod_name.setWordWrap(True)
        self.label_mod_name.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.verticalLayout_mod_info.addWidget(self.label_mod_name)

        self.textEdit_mod_description = QTextEdit(self.groupBox_mod_info)
        self.textEdit_mod_description.setObjectName("textEdit_mod_description")
        self.textEdit_mod_description.setMinimumSize(QSize(0, 60))
        self.textEdit_mod_description.setMaximumSize(QSize(16777215, 100))
        self.textEdit_mod_description.setReadOnly(True)

        self.verticalLayout_mod_info.addWidget(self.textEdit_mod_description)

        self.verticalLayout_sidebar.addWidget(self.groupBox_mod_info)

        self.groupBox_presets = QGroupBox(self.widget_right_panel)
        self.groupBox_presets.setObjectName("groupBox_presets")
        self.groupBox_presets.setMinimumSize(QSize(0, 200))
        self.verticalLayout_presets = QVBoxLayout(self.groupBox_presets)
        self.verticalLayout_presets.setSpacing(6)
        self.verticalLayout_presets.setObjectName("verticalLayout_presets")
        self.comboBox_presets = QComboBox(self.groupBox_presets)
        self.comboBox_presets.addItem("")
        self.comboBox_presets.setObjectName("comboBox_presets")
        self.comboBox_presets.setEditable(True)

        self.verticalLayout_presets.addWidget(self.comboBox_presets)

        self.horizontalLayout_preset_controls = QHBoxLayout()
        self.horizontalLayout_preset_controls.setSpacing(6)
        self.horizontalLayout_preset_controls.setObjectName(
            "horizontalLayout_preset_controls"
        )
        self.pushButton_load_preset = QPushButton(self.groupBox_presets)
        self.pushButton_load_preset.setObjectName("pushButton_load_preset")
        self.pushButton_load_preset.setEnabled(True)

        self.horizontalLayout_preset_controls.addWidget(self.pushButton_load_preset)

        self.pushButton_save_preset = QPushButton(self.groupBox_presets)
        self.pushButton_save_preset.setObjectName("pushButton_save_preset")
        self.pushButton_save_preset.setEnabled(True)

        self.horizontalLayout_preset_controls.addWidget(self.pushButton_save_preset)

        self.pushButton_delete_preset = QPushButton(self.groupBox_presets)
        self.pushButton_delete_preset.setObjectName("pushButton_delete_preset")
        self.pushButton_delete_preset.setEnabled(True)

        self.horizontalLayout_preset_controls.addWidget(self.pushButton_delete_preset)

        self.verticalLayout_presets.addLayout(self.horizontalLayout_preset_controls)

        self.listWidget_presets = QListWidget(self.groupBox_presets)
        self.listWidget_presets.setObjectName("listWidget_presets")
        self.listWidget_presets.setAlternatingRowColors(True)
        self.listWidget_presets.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.listWidget_presets.setUniformItemSizes(True)

        self.verticalLayout_presets.addWidget(self.listWidget_presets)

        self.verticalLayout_sidebar.addWidget(self.groupBox_presets)

        self.groupBox_sharing = QGroupBox(self.widget_right_panel)
        self.groupBox_sharing.setObjectName("groupBox_sharing")
        self.groupBox_sharing.setMinimumSize(QSize(0, 120))
        self.verticalLayout_sharing = QVBoxLayout(self.groupBox_sharing)
        self.verticalLayout_sharing.setSpacing(6)
        self.verticalLayout_sharing.setObjectName("verticalLayout_sharing")
        self.lineEdit_share_code = QLineEdit(self.groupBox_sharing)
        self.lineEdit_share_code.setObjectName("lineEdit_share_code")
        self.lineEdit_share_code.setClearButtonEnabled(True)

        self.verticalLayout_sharing.addWidget(self.lineEdit_share_code)

        self.horizontalLayout_sharing_controls = QHBoxLayout()
        self.horizontalLayout_sharing_controls.setSpacing(6)
        self.horizontalLayout_sharing_controls.setObjectName(
            "horizontalLayout_sharing_controls"
        )
        self.pushButton_import_config = QPushButton(self.groupBox_sharing)
        self.pushButton_import_config.setObjectName("pushButton_import_config")
        self.pushButton_import_config.setEnabled(True)

        self.horizontalLayout_sharing_controls.addWidget(self.pushButton_import_config)

        self.pushButton_export_config = QPushButton(self.groupBox_sharing)
        self.pushButton_export_config.setObjectName("pushButton_export_config")
        self.pushButton_export_config.setEnabled(True)

        self.horizontalLayout_sharing_controls.addWidget(self.pushButton_export_config)

        self.verticalLayout_sharing.addLayout(self.horizontalLayout_sharing_controls)

        self.verticalLayout_sidebar.addWidget(self.groupBox_sharing)

        self.verticalSpacer_sidebar = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_sidebar.addItem(self.verticalSpacer_sidebar)

        self.splitter_main.addWidget(self.widget_right_panel)

        self.horizontalLayout_main.addWidget(self.splitter_main)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        self.menuStyle = QMenu(self.menuView)
        self.menuStyle.setObjectName("menuStyle")
        self.menuFont = QMenu(self.menuStyle)
        self.menuFont.setObjectName("menuFont")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QWidget.setTabOrder(
            self.lineEdit_search_installed, self.pushButton_refresh_mods
        )
        QWidget.setTabOrder(
            self.pushButton_refresh_mods, self.listWidget_available_mods
        )
        QWidget.setTabOrder(self.listWidget_available_mods, self.pushButton_add_mod)
        QWidget.setTabOrder(self.pushButton_add_mod, self.lineEdit_search_active)
        QWidget.setTabOrder(self.lineEdit_search_active, self.listWidget_active_mods)
        QWidget.setTabOrder(self.listWidget_active_mods, self.pushButton_move_up)
        QWidget.setTabOrder(self.pushButton_move_up, self.pushButton_move_down)
        QWidget.setTabOrder(self.pushButton_move_down, self.pushButton_remove_mod)
        QWidget.setTabOrder(self.pushButton_remove_mod, self.pushButton_clear_all)
        QWidget.setTabOrder(self.pushButton_clear_all, self.textEdit_mod_description)
        QWidget.setTabOrder(self.textEdit_mod_description, self.comboBox_presets)
        QWidget.setTabOrder(self.comboBox_presets, self.pushButton_load_preset)
        QWidget.setTabOrder(self.pushButton_load_preset, self.pushButton_save_preset)
        QWidget.setTabOrder(self.pushButton_save_preset, self.pushButton_delete_preset)
        QWidget.setTabOrder(self.pushButton_delete_preset, self.listWidget_presets)
        QWidget.setTabOrder(self.listWidget_presets, self.lineEdit_share_code)
        QWidget.setTabOrder(self.lineEdit_share_code, self.pushButton_import_config)
        QWidget.setTabOrder(
            self.pushButton_import_config, self.pushButton_export_config
        )

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionImport_Mod)
        self.menuFile.addAction(self.actionRefresh)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionPreferences)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionClear_Active_Mods)
        self.menuView.addAction(self.actionShow_Mod_Details)
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuStyle.menuAction())
        self.menuStyle.addAction(self.menuFont.menuAction())
        self.menuFont.addAction(self.actionDefaultFont)
        self.menuFont.addAction(self.actionDyslexiaFont)
        self.menuHelp.addAction(self.actionUser_Manual)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionCheck_Updates)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate(
                "MainWindow", "Call to Arms: Gates of Hell | Mod Manager", None
            )
        )
        self.actionImport_Mod.setText(
            QCoreApplication.translate("MainWindow", "&Import Mod...", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionImport_Mod.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Install a new mod from file or folder", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionImport_Mod.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+I", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionRefresh.setText(
            QCoreApplication.translate("MainWindow", "&Refresh", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionRefresh.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Refresh mod lists and scan for changes", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionRefresh.setShortcut(
            QCoreApplication.translate("MainWindow", "F5", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "&Exit", None))
        # if QT_CONFIG(tooltip)
        self.actionExit.setToolTip(
            QCoreApplication.translate("MainWindow", "Close the mod manager", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+Q", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionPreferences.setText(
            QCoreApplication.translate("MainWindow", "&Preferences...", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionPreferences.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Configure mod manager settings", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionPreferences.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+,", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionClear_Active_Mods.setText(
            QCoreApplication.translate("MainWindow", "&Clear Active Mods", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionClear_Active_Mods.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Deactivate all mods and clear load order", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionClear_Active_Mods.setShortcut(
            QCoreApplication.translate("MainWindow", "Ctrl+Shift+C", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionShow_Mod_Details.setText(
            QCoreApplication.translate("MainWindow", "Show &Mod Details", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionShow_Mod_Details.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Show or hide the mod information panel", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionUser_Manual.setText(
            QCoreApplication.translate("MainWindow", "&User Manual", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionUser_Manual.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Open the complete user guide", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionUser_Manual.setShortcut(
            QCoreApplication.translate("MainWindow", "F1", None)
        )
        # endif // QT_CONFIG(shortcut)
        self.actionCheck_Updates.setText(
            QCoreApplication.translate("MainWindow", "&Check for Updates", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionCheck_Updates.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Check for mod manager updates", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionAbout.setText(
            QCoreApplication.translate("MainWindow", "&About", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionAbout.setToolTip(
            QCoreApplication.translate("MainWindow", "About this mod manager", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionTheme.setText(
            QCoreApplication.translate("MainWindow", "Theme", None)
        )
        self.actionDefaultFont.setText(
            QCoreApplication.translate("MainWindow", "Default", None)
        )
        self.actionDyslexiaFont.setText(
            QCoreApplication.translate("MainWindow", "Dyslexia", None)
        )
        self.groupBox_installed_mods.setTitle(
            QCoreApplication.translate("MainWindow", "Available Mods", None)
        )
        # if QT_CONFIG(tooltip)
        self.lineEdit_search_installed.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Type to search through your installed mods library", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lineEdit_search_installed.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "Filter available mods by name...", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_refresh_mods.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Scan for newly installed mods and refresh the list", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_refresh_mods.setText("")
        # if QT_CONFIG(tooltip)
        self.listWidget_available_mods.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Select one or multiple mods to add to your active configuration. Use Ctrl+Click for multiple selection.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.pushButton_add_mod.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Add the selected mods to your active mod list", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_add_mod.setText(
            QCoreApplication.translate("MainWindow", "Add Selected", None)
        )
        self.groupBox_active_mods.setTitle(
            QCoreApplication.translate("MainWindow", "Active Mods (Load Order)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lineEdit_search_active.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Quickly find mods in your current load order", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lineEdit_search_active.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Search active mods...", None)
        )
        # if QT_CONFIG(tooltip)
        self.label_mod_count.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Number of mods currently in your load order", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.label_mod_count.setText(
            QCoreApplication.translate("MainWindow", "0 mods active", None)
        )
        # if QT_CONFIG(tooltip)
        self.listWidget_active_mods.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Your active mod configuration. Mods at the top load first. Drag and drop to reorder, or use the buttons below.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.pushButton_move_up.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Move selected mods higher in load order (loads earlier)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_move_up.setText(
            QCoreApplication.translate("MainWindow", "Move Up", None)
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_move_down.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Move selected mods lower in load order (loads later)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_move_down.setText(
            QCoreApplication.translate("MainWindow", "Move Down", None)
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_remove_mod.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Deactivate selected mods (removes from load order)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_remove_mod.setText(
            QCoreApplication.translate("MainWindow", "Remove", None)
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_clear_all.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Deactivate all mods and clear the entire load order",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_clear_all.setText(
            QCoreApplication.translate("MainWindow", "Clear All", None)
        )
        self.label_drag_info.setStyleSheet(
            QCoreApplication.translate("MainWindow", "color: #666;", None)
        )
        self.label_drag_info.setText(
            QCoreApplication.translate(
                "MainWindow",
                "Tip: Drag and drop mods to reorder them instantly\n"
                "                                                        ",
                None,
            )
        )
        self.groupBox_mod_info.setTitle(
            QCoreApplication.translate("MainWindow", "Mod Information", None)
        )
        self.label_mod_name.setText(
            QCoreApplication.translate(
                "MainWindow", "Select a mod to view details", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.textEdit_mod_description.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Detailed information about the selected mod", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.textEdit_mod_description.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow",
                "Mod description, version info, and compatibility notes will appear here...",
                None,
            )
        )
        self.groupBox_presets.setTitle(
            QCoreApplication.translate("MainWindow", "Presets", None)
        )
        self.comboBox_presets.setItemText(
            0,
            QCoreApplication.translate(
                "MainWindow", "-- Select or Create Preset --", None
            ),
        )

        # if QT_CONFIG(tooltip)
        self.comboBox_presets.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Select an existing preset or type a new name to create one",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.pushButton_load_preset.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Load the selected preset configuration", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_load_preset.setText(
            QCoreApplication.translate("MainWindow", "Load", None)
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_save_preset.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Save your current mod configuration as a preset", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_save_preset.setText(
            QCoreApplication.translate("MainWindow", "Save", None)
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_delete_preset.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Delete the selected preset permanently", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_delete_preset.setText(
            QCoreApplication.translate("MainWindow", "Delete", None)
        )
        # if QT_CONFIG(tooltip)
        self.listWidget_presets.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Your saved mod configurations", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.groupBox_sharing.setTitle(
            QCoreApplication.translate("MainWindow", "Configuration Sharing", None)
        )
        # if QT_CONFIG(tooltip)
        self.lineEdit_share_code.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Enter a configuration code shared by another player",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lineEdit_share_code.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "Paste a shared configuration code here...", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_import_config.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Import and apply the configuration from the share code",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_import_config.setText(
            QCoreApplication.translate("MainWindow", "Import", None)
        )
        # if QT_CONFIG(tooltip)
        self.pushButton_export_config.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Generate a shareable code for your current mod setup",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pushButton_export_config.setText(
            QCoreApplication.translate("MainWindow", "Export", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "&File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", "&Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", "&View", None))
        self.menuStyle.setTitle(QCoreApplication.translate("MainWindow", "Style", None))
        self.menuFont.setTitle(QCoreApplication.translate("MainWindow", "Font", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", "&Help", None))

    # retranslateUi
