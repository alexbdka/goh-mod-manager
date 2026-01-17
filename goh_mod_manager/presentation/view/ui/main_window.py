# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QGroupBox,
    QHBoxLayout, QLCDNumber, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QStatusBar, QTextEdit, QToolBar,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 600)
        MainWindow.setMinimumSize(QSize(1200, 600))
        icon = QIcon()
        icon.addFile(u":/icons/icon/logo.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actionImport_mod = QAction(MainWindow)
        self.actionImport_mod.setObjectName(u"actionImport_mod")
        self.actionRefresh = QAction(MainWindow)
        self.actionRefresh.setObjectName(u"actionRefresh")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionSettings = QAction(MainWindow)
        self.actionSettings.setObjectName(u"actionSettings")
        self.actionClear_Active_Mods = QAction(MainWindow)
        self.actionClear_Active_Mods.setObjectName(u"actionClear_Active_Mods")
        self.actionShow_mod_information = QAction(MainWindow)
        self.actionShow_mod_information.setObjectName(u"actionShow_mod_information")
        self.actionShow_mod_information.setCheckable(True)
        self.actionShow_mod_information.setChecked(True)
        self.actionGuided_tour = QAction(MainWindow)
        self.actionGuided_tour.setObjectName(u"actionGuided_tour")
        self.actionCheck_Updates = QAction(MainWindow)
        self.actionCheck_Updates.setObjectName(u"actionCheck_Updates")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionTheme = QAction(MainWindow)
        self.actionTheme.setObjectName(u"actionTheme")
        self.actionDefault = QAction(MainWindow)
        self.actionDefault.setObjectName(u"actionDefault")
        self.actionDyslexic = QAction(MainWindow)
        self.actionDyslexic.setObjectName(u"actionDyslexic")
        self.actionOpen_game_folder = QAction(MainWindow)
        self.actionOpen_game_folder.setObjectName(u"actionOpen_game_folder")
        self.actionOpen_mods_folder = QAction(MainWindow)
        self.actionOpen_mods_folder.setObjectName(u"actionOpen_mods_folder")
        self.actionOpen_options_file = QAction(MainWindow)
        self.actionOpen_options_file.setObjectName(u"actionOpen_options_file")
        self.actionOpen_logs = QAction(MainWindow)
        self.actionOpen_logs.setObjectName(u"actionOpen_logs")
        self.action_load_order_from_code = QAction(MainWindow)
        self.action_load_order_from_code.setObjectName(u"action_load_order_from_code")
        self.action_load_order_as_code = QAction(MainWindow)
        self.action_load_order_as_code.setObjectName(u"action_load_order_as_code")
        self.action_local_mod = QAction(MainWindow)
        self.action_local_mod.setObjectName(u"action_local_mod")
        self.actionZoom_in = QAction(MainWindow)
        self.actionZoom_in.setObjectName(u"actionZoom_in")
        self.actionZoom_out = QAction(MainWindow)
        self.actionZoom_out.setObjectName(u"actionZoom_out")
        self.actionReset_zoom = QAction(MainWindow)
        self.actionReset_zoom.setObjectName(u"actionReset_zoom")
        self.actionGenerate_Help_File = QAction(MainWindow)
        self.actionGenerate_Help_File.setObjectName(u"actionGenerate_Help_File")
        self.actionLaunch_Game = QAction(MainWindow)
        self.actionLaunch_Game.setObjectName(u"actionLaunch_Game")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart))
        self.actionLaunch_Game.setIcon(icon1)
        self.actionLaunch_Game.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_main = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_main.setSpacing(8)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.horizontalLayout_main.setContentsMargins(8, 8, 8, 8)
        self.splitter_main = QSplitter(self.centralwidget)
        self.splitter_main.setObjectName(u"splitter_main")
        self.splitter_main.setOrientation(Qt.Orientation.Horizontal)
        self.splitter_main.setChildrenCollapsible(False)
        self.widget_left_panel = QWidget(self.splitter_main)
        self.widget_left_panel.setObjectName(u"widget_left_panel")
        self.widget_left_panel.setMinimumSize(QSize(250, 0))
        self.widget_left_panel.setMaximumSize(QSize(400, 16777215))
        self.verticalLayout_available_mods = QVBoxLayout(self.widget_left_panel)
        self.verticalLayout_available_mods.setSpacing(6)
        self.verticalLayout_available_mods.setObjectName(u"verticalLayout_available_mods")
        self.verticalLayout_available_mods.setContentsMargins(0, 0, 0, 0)
        self.groupBox_installed_mods = QGroupBox(self.widget_left_panel)
        self.groupBox_installed_mods.setObjectName(u"groupBox_installed_mods")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_installed_mods)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_search_available_mods = QHBoxLayout()
        self.horizontalLayout_search_available_mods.setSpacing(6)
        self.horizontalLayout_search_available_mods.setObjectName(u"horizontalLayout_search_available_mods")
        self.lineEdit_search_installed_mods = QLineEdit(self.groupBox_installed_mods)
        self.lineEdit_search_installed_mods.setObjectName(u"lineEdit_search_installed_mods")
        self.lineEdit_search_installed_mods.setClearButtonEnabled(True)

        self.horizontalLayout_search_available_mods.addWidget(self.lineEdit_search_installed_mods)

        self.pushButton_refresh_installed_mods = QPushButton(self.groupBox_installed_mods)
        self.pushButton_refresh_installed_mods.setObjectName(u"pushButton_refresh_installed_mods")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icon/refresh-line.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton_refresh_installed_mods.setIcon(icon2)

        self.horizontalLayout_search_available_mods.addWidget(self.pushButton_refresh_installed_mods)


        self.verticalLayout_2.addLayout(self.horizontalLayout_search_available_mods)

        self.listWidget_installed_mods = QListWidget(self.groupBox_installed_mods)
        self.listWidget_installed_mods.setObjectName(u"listWidget_installed_mods")
        self.listWidget_installed_mods.setAcceptDrops(True)
        self.listWidget_installed_mods.setProperty(u"showDropIndicator", False)
        self.listWidget_installed_mods.setAlternatingRowColors(True)
        self.listWidget_installed_mods.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listWidget_installed_mods.setSortingEnabled(True)

        self.verticalLayout_2.addWidget(self.listWidget_installed_mods)

        self.horizontalLayout_available_mods_actions = QHBoxLayout()
        self.horizontalLayout_available_mods_actions.setObjectName(u"horizontalLayout_available_mods_actions")
        self.pushButton_activate = QPushButton(self.groupBox_installed_mods)
        self.pushButton_activate.setObjectName(u"pushButton_activate")

        self.horizontalLayout_available_mods_actions.addWidget(self.pushButton_activate)


        self.verticalLayout_2.addLayout(self.horizontalLayout_available_mods_actions)


        self.verticalLayout_available_mods.addWidget(self.groupBox_installed_mods)

        self.splitter_main.addWidget(self.widget_left_panel)
        self.widget_center_panel = QWidget(self.splitter_main)
        self.widget_center_panel.setObjectName(u"widget_center_panel")
        self.widget_center_panel.setMinimumSize(QSize(300, 0))
        self.verticalLayout_active_mods = QVBoxLayout(self.widget_center_panel)
        self.verticalLayout_active_mods.setSpacing(6)
        self.verticalLayout_active_mods.setObjectName(u"verticalLayout_active_mods")
        self.verticalLayout_active_mods.setContentsMargins(0, 0, 0, 0)
        self.groupBox_active_mods = QGroupBox(self.widget_center_panel)
        self.groupBox_active_mods.setObjectName(u"groupBox_active_mods")
        self.verticalLayout_3 = QVBoxLayout(self.groupBox_active_mods)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_search_active_mods = QHBoxLayout()
        self.horizontalLayout_search_active_mods.setSpacing(6)
        self.horizontalLayout_search_active_mods.setObjectName(u"horizontalLayout_search_active_mods")
        self.lineEdit_search_active_mods = QLineEdit(self.groupBox_active_mods)
        self.lineEdit_search_active_mods.setObjectName(u"lineEdit_search_active_mods")
        self.lineEdit_search_active_mods.setClearButtonEnabled(True)

        self.horizontalLayout_search_active_mods.addWidget(self.lineEdit_search_active_mods)

        self.lcdNumber_active_count = QLCDNumber(self.groupBox_active_mods)
        self.lcdNumber_active_count.setObjectName(u"lcdNumber_active_count")

        self.horizontalLayout_search_active_mods.addWidget(self.lcdNumber_active_count)


        self.verticalLayout_3.addLayout(self.horizontalLayout_search_active_mods)

        self.listWidget_active_mods = QListWidget(self.groupBox_active_mods)
        self.listWidget_active_mods.setObjectName(u"listWidget_active_mods")
        self.listWidget_active_mods.setProperty(u"showDropIndicator", True)
        self.listWidget_active_mods.setDragEnabled(True)
        self.listWidget_active_mods.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.listWidget_active_mods.setAlternatingRowColors(True)
        self.listWidget_active_mods.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.verticalLayout_3.addWidget(self.listWidget_active_mods)

        self.horizontalLayout_load_order_controls = QHBoxLayout()
        self.horizontalLayout_load_order_controls.setSpacing(6)
        self.horizontalLayout_load_order_controls.setObjectName(u"horizontalLayout_load_order_controls")
        self.pushButton_move_up = QPushButton(self.groupBox_active_mods)
        self.pushButton_move_up.setObjectName(u"pushButton_move_up")

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_move_up)

        self.pushButton_move_down = QPushButton(self.groupBox_active_mods)
        self.pushButton_move_down.setObjectName(u"pushButton_move_down")

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_move_down)

        self.horizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_load_order_controls.addItem(self.horizontalSpacer)

        self.pushButton_remove = QPushButton(self.groupBox_active_mods)
        self.pushButton_remove.setObjectName(u"pushButton_remove")

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_remove)

        self.pushButton_clear_all = QPushButton(self.groupBox_active_mods)
        self.pushButton_clear_all.setObjectName(u"pushButton_clear_all")

        self.horizontalLayout_load_order_controls.addWidget(self.pushButton_clear_all)


        self.verticalLayout_3.addLayout(self.horizontalLayout_load_order_controls)

        self.label_reorder_tip = QLabel(self.groupBox_active_mods)
        self.label_reorder_tip.setObjectName(u"label_reorder_tip")
        font = QFont()
        font.setItalic(True)
        self.label_reorder_tip.setFont(font)
        self.label_reorder_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_reorder_tip)


        self.verticalLayout_active_mods.addWidget(self.groupBox_active_mods)

        self.splitter_main.addWidget(self.widget_center_panel)
        self.widget_right_panel = QWidget(self.splitter_main)
        self.widget_right_panel.setObjectName(u"widget_right_panel")
        self.widget_right_panel.setMinimumSize(QSize(250, 0))
        self.widget_right_panel.setMaximumSize(QSize(350, 16777215))
        self.verticalLayout_sidebar = QVBoxLayout(self.widget_right_panel)
        self.verticalLayout_sidebar.setSpacing(6)
        self.verticalLayout_sidebar.setObjectName(u"verticalLayout_sidebar")
        self.verticalLayout_sidebar.setContentsMargins(0, 0, 0, 0)
        self.groupBox_mod_information = QGroupBox(self.widget_right_panel)
        self.groupBox_mod_information.setObjectName(u"groupBox_mod_information")
        self.groupBox_mod_information.setMinimumSize(QSize(0, 150))
        self.verticalLayout_mod_info = QVBoxLayout(self.groupBox_mod_information)
        self.verticalLayout_mod_info.setSpacing(6)
        self.verticalLayout_mod_info.setObjectName(u"verticalLayout_mod_info")
        self.label_mod_title = QLabel(self.groupBox_mod_information)
        self.label_mod_title.setObjectName(u"label_mod_title")
        font1 = QFont()
        font1.setBold(True)
        self.label_mod_title.setFont(font1)
        self.label_mod_title.setWordWrap(True)
        self.label_mod_title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout_mod_info.addWidget(self.label_mod_title)

        self.textEdit_mod_description = QTextEdit(self.groupBox_mod_information)
        self.textEdit_mod_description.setObjectName(u"textEdit_mod_description")
        self.textEdit_mod_description.setReadOnly(True)

        self.verticalLayout_mod_info.addWidget(self.textEdit_mod_description)


        self.verticalLayout_sidebar.addWidget(self.groupBox_mod_information)

        self.groupBox_presets = QGroupBox(self.widget_right_panel)
        self.groupBox_presets.setObjectName(u"groupBox_presets")
        self.groupBox_presets.setMinimumSize(QSize(0, 200))
        self.verticalLayout_presets = QVBoxLayout(self.groupBox_presets)
        self.verticalLayout_presets.setSpacing(6)
        self.verticalLayout_presets.setObjectName(u"verticalLayout_presets")
        self.comboBox_presets = QComboBox(self.groupBox_presets)
        self.comboBox_presets.addItem("")
        self.comboBox_presets.setObjectName(u"comboBox_presets")

        self.verticalLayout_presets.addWidget(self.comboBox_presets)

        self.horizontalLayout_preset_controls = QHBoxLayout()
        self.horizontalLayout_preset_controls.setSpacing(6)
        self.horizontalLayout_preset_controls.setObjectName(u"horizontalLayout_preset_controls")
        self.pushButton_load_preset = QPushButton(self.groupBox_presets)
        self.pushButton_load_preset.setObjectName(u"pushButton_load_preset")

        self.horizontalLayout_preset_controls.addWidget(self.pushButton_load_preset)

        self.pushButton_save_preset = QPushButton(self.groupBox_presets)
        self.pushButton_save_preset.setObjectName(u"pushButton_save_preset")

        self.horizontalLayout_preset_controls.addWidget(self.pushButton_save_preset)

        self.pushButton_delete_preset = QPushButton(self.groupBox_presets)
        self.pushButton_delete_preset.setObjectName(u"pushButton_delete_preset")

        self.horizontalLayout_preset_controls.addWidget(self.pushButton_delete_preset)


        self.verticalLayout_presets.addLayout(self.horizontalLayout_preset_controls)

        self.listWidget_presets = QListWidget(self.groupBox_presets)
        self.listWidget_presets.setObjectName(u"listWidget_presets")
        self.listWidget_presets.setProperty(u"showDropIndicator", False)
        self.listWidget_presets.setAlternatingRowColors(True)

        self.verticalLayout_presets.addWidget(self.listWidget_presets)


        self.verticalLayout_sidebar.addWidget(self.groupBox_presets)

        self.splitter_main.addWidget(self.widget_right_panel)

        self.horizontalLayout_main.addWidget(self.splitter_main)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1200, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuStyle = QMenu(self.menuView)
        self.menuStyle.setObjectName(u"menuStyle")
        self.menuFont = QMenu(self.menuStyle)
        self.menuFont.setObjectName(u"menuFont")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuImport = QMenu(self.menubar)
        self.menuImport.setObjectName(u"menuImport")
        self.menuExport = QMenu(self.menubar)
        self.menuExport.setObjectName(u"menuExport")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        QWidget.setTabOrder(self.lineEdit_search_installed_mods, self.pushButton_refresh_installed_mods)
        QWidget.setTabOrder(self.pushButton_refresh_installed_mods, self.listWidget_installed_mods)
        QWidget.setTabOrder(self.listWidget_installed_mods, self.pushButton_activate)
        QWidget.setTabOrder(self.pushButton_activate, self.lineEdit_search_active_mods)
        QWidget.setTabOrder(self.lineEdit_search_active_mods, self.listWidget_active_mods)
        QWidget.setTabOrder(self.listWidget_active_mods, self.pushButton_move_up)
        QWidget.setTabOrder(self.pushButton_move_up, self.pushButton_move_down)
        QWidget.setTabOrder(self.pushButton_move_down, self.pushButton_remove)
        QWidget.setTabOrder(self.pushButton_remove, self.pushButton_clear_all)
        QWidget.setTabOrder(self.pushButton_clear_all, self.comboBox_presets)
        QWidget.setTabOrder(self.comboBox_presets, self.pushButton_load_preset)
        QWidget.setTabOrder(self.pushButton_load_preset, self.pushButton_save_preset)
        QWidget.setTabOrder(self.pushButton_save_preset, self.pushButton_delete_preset)
        QWidget.setTabOrder(self.pushButton_delete_preset, self.listWidget_presets)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuImport.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionOpen_game_folder)
        self.menuFile.addAction(self.actionOpen_mods_folder)
        self.menuFile.addAction(self.actionOpen_options_file)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_logs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionSettings)
        self.menuEdit.addSeparator()
        self.menuView.addAction(self.actionRefresh)
        self.menuView.addAction(self.actionShow_mod_information)
        self.menuView.addSeparator()
        self.menuView.addAction(self.actionZoom_in)
        self.menuView.addAction(self.actionZoom_out)
        self.menuView.addAction(self.actionReset_zoom)
        self.menuView.addSeparator()
        self.menuView.addAction(self.menuStyle.menuAction())
        self.menuStyle.addAction(self.menuFont.menuAction())
        self.menuFont.addAction(self.actionDefault)
        self.menuFont.addAction(self.actionDyslexic)
        self.menuHelp.addAction(self.actionGuided_tour)
        self.menuHelp.addAction(self.actionGenerate_Help_File)
        self.menuHelp.addAction(self.actionAbout)
        self.menuImport.addAction(self.action_load_order_from_code)
        self.menuImport.addAction(self.action_local_mod)
        self.menuExport.addAction(self.action_load_order_as_code)
        self.toolBar.addAction(self.actionLaunch_Game)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.actionImport_mod.setText(QCoreApplication.translate("MainWindow", u"Import mod...", None))
#if QT_CONFIG(shortcut)
        self.actionImport_mod.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+I", None))
#endif // QT_CONFIG(shortcut)
        self.actionRefresh.setText(QCoreApplication.translate("MainWindow", u"Refresh All", None))
#if QT_CONFIG(shortcut)
        self.actionRefresh.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionSettings.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionClear_Active_Mods.setText(QCoreApplication.translate("MainWindow", u"Clear Active Mods", None))
#if QT_CONFIG(shortcut)
        self.actionClear_Active_Mods.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+C", None))
#endif // QT_CONFIG(shortcut)
        self.actionShow_mod_information.setText(QCoreApplication.translate("MainWindow", u"Show Mod Information", None))
        self.actionGuided_tour.setText(QCoreApplication.translate("MainWindow", u"Guided Tour...", None))
        self.actionCheck_Updates.setText(QCoreApplication.translate("MainWindow", u"Check for updates", None))
#if QT_CONFIG(tooltip)
        self.actionCheck_Updates.setToolTip(QCoreApplication.translate("MainWindow", u"Check for mod manager updates", None))
#endif // QT_CONFIG(tooltip)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
#if QT_CONFIG(tooltip)
        self.actionAbout.setToolTip(QCoreApplication.translate("MainWindow", u"About this mod manager", None))
#endif // QT_CONFIG(tooltip)
        self.actionTheme.setText(QCoreApplication.translate("MainWindow", u"Theme", None))
        self.actionDefault.setText(QCoreApplication.translate("MainWindow", u"Default", None))
        self.actionDyslexic.setText(QCoreApplication.translate("MainWindow", u"Dyslexic", None))
        self.actionOpen_game_folder.setText(QCoreApplication.translate("MainWindow", u"Open Game Folder", None))
        self.actionOpen_mods_folder.setText(QCoreApplication.translate("MainWindow", u"Open Mods Folder", None))
        self.actionOpen_options_file.setText(QCoreApplication.translate("MainWindow", u"Open Options File", None))
        self.actionOpen_logs.setText(QCoreApplication.translate("MainWindow", u"Open Logs", None))
        self.action_load_order_from_code.setText(QCoreApplication.translate("MainWindow", u"Load Order from Code...", None))
        self.action_load_order_as_code.setText(QCoreApplication.translate("MainWindow", u"Load Order as Code...", None))
        self.action_local_mod.setText(QCoreApplication.translate("MainWindow", u"Import Local Mod...", None))
        self.actionZoom_in.setText(QCoreApplication.translate("MainWindow", u"Zoom in", None))
        self.actionZoom_out.setText(QCoreApplication.translate("MainWindow", u"Zoom out", None))
        self.actionReset_zoom.setText(QCoreApplication.translate("MainWindow", u"Reset zoom", None))
        self.actionGenerate_Help_File.setText(QCoreApplication.translate("MainWindow", u"Generate Help File", None))
        self.actionLaunch_Game.setText(QCoreApplication.translate("MainWindow", u"Launch Game", None))
#if QT_CONFIG(tooltip)
        self.actionLaunch_Game.setToolTip(QCoreApplication.translate("MainWindow", u"Launch the game", None))
#endif // QT_CONFIG(tooltip)
        self.groupBox_installed_mods.setTitle(QCoreApplication.translate("MainWindow", u"Installed Mods", None))
        self.lineEdit_search_installed_mods.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search installed mods...", None))
#if QT_CONFIG(tooltip)
        self.pushButton_refresh_installed_mods.setToolTip(QCoreApplication.translate("MainWindow", u"Refresh installed mods", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_activate.setText(QCoreApplication.translate("MainWindow", u"Activate", None))
        self.groupBox_active_mods.setTitle(QCoreApplication.translate("MainWindow", u"Active Mods (Load Order)", None))
        self.lineEdit_search_active_mods.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search active mods...", None))
        self.pushButton_move_up.setText(QCoreApplication.translate("MainWindow", u"Move Up", None))
        self.pushButton_move_down.setText(QCoreApplication.translate("MainWindow", u"Move Down", None))
        self.pushButton_remove.setText(QCoreApplication.translate("MainWindow", u"Deactivate", None))
        self.pushButton_clear_all.setText(QCoreApplication.translate("MainWindow", u"Deactivate All", None))
        self.label_reorder_tip.setText(QCoreApplication.translate("MainWindow", u"Tip: Drag and drop to reorder active mods.", None))
        self.groupBox_mod_information.setTitle(QCoreApplication.translate("MainWindow", u"Mod Information", None))
        self.label_mod_title.setText(QCoreApplication.translate("MainWindow", u"Select a mod to view details.", None))
        self.groupBox_presets.setTitle(QCoreApplication.translate("MainWindow", u"Presets", None))
        self.comboBox_presets.setItemText(0, QCoreApplication.translate("MainWindow", u"Select or create a preset...", None))

        self.pushButton_load_preset.setText(QCoreApplication.translate("MainWindow", u"Load", None))
        self.pushButton_save_preset.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.pushButton_delete_preset.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"&Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"&View", None))
        self.menuStyle.setTitle(QCoreApplication.translate("MainWindow", u"Style", None))
        self.menuFont.setTitle(QCoreApplication.translate("MainWindow", u"Font", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menuImport.setTitle(QCoreApplication.translate("MainWindow", u"Import", None))
        self.menuExport.setTitle(QCoreApplication.translate("MainWindow", u"Export", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
        pass
    # retranslateUi

