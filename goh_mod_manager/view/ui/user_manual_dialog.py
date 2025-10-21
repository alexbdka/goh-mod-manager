# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'user_manual_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_UserManualDialog(object):
    def setupUi(self, UserManualDialog):
        if not UserManualDialog.objectName():
            UserManualDialog.setObjectName("UserManualDialog")
        UserManualDialog.resize(800, 600)
        UserManualDialog.setMinimumSize(QSize(800, 600))
        UserManualDialog.setMaximumSize(QSize(800, 600))
        UserManualDialog.setModal(True)
        self.main_layout = QVBoxLayout(UserManualDialog)
        self.main_layout.setSpacing(20)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.title_label = QLabel(UserManualDialog)
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.title_label)

        self.tab_widget = QTabWidget(UserManualDialog)
        self.tab_widget.setObjectName("tab_widget")
        self.setup_tab = QWidget()
        self.setup_tab.setObjectName("setup_tab")
        self.setup_tab_layout = QVBoxLayout(self.setup_tab)
        self.setup_tab_layout.setObjectName("setup_tab_layout")
        self.setup_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_content = QTextEdit(self.setup_tab)
        self.setup_content.setObjectName("setup_content")
        self.setup_content.setReadOnly(True)

        self.setup_tab_layout.addWidget(self.setup_content)

        self.tab_widget.addTab(self.setup_tab, "")
        self.interface_tab = QWidget()
        self.interface_tab.setObjectName("interface_tab")
        self.interface_tab_layout = QVBoxLayout(self.interface_tab)
        self.interface_tab_layout.setObjectName("interface_tab_layout")
        self.interface_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.interface_content = QTextEdit(self.interface_tab)
        self.interface_content.setObjectName("interface_content")
        self.interface_content.setReadOnly(True)

        self.interface_tab_layout.addWidget(self.interface_content)

        self.tab_widget.addTab(self.interface_tab, "")
        self.managing_tab = QWidget()
        self.managing_tab.setObjectName("managing_tab")
        self.managing_tab_layout = QVBoxLayout(self.managing_tab)
        self.managing_tab_layout.setObjectName("managing_tab_layout")
        self.managing_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.managing_content = QTextEdit(self.managing_tab)
        self.managing_content.setObjectName("managing_content")
        self.managing_content.setReadOnly(True)

        self.managing_tab_layout.addWidget(self.managing_content)

        self.tab_widget.addTab(self.managing_tab, "")
        self.presets_tab = QWidget()
        self.presets_tab.setObjectName("presets_tab")
        self.presets_tab_layout = QVBoxLayout(self.presets_tab)
        self.presets_tab_layout.setObjectName("presets_tab_layout")
        self.presets_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.presets_content = QTextEdit(self.presets_tab)
        self.presets_content.setObjectName("presets_content")
        self.presets_content.setReadOnly(True)

        self.presets_tab_layout.addWidget(self.presets_content)

        self.tab_widget.addTab(self.presets_tab, "")
        self.support_tab = QWidget()
        self.support_tab.setObjectName("support_tab")
        self.support_tab_layout = QVBoxLayout(self.support_tab)
        self.support_tab_layout.setObjectName("support_tab_layout")
        self.support_tab_layout.setContentsMargins(0, 0, 0, 0)
        self.support_content = QTextEdit(self.support_tab)
        self.support_content.setObjectName("support_content")
        self.support_content.setReadOnly(True)

        self.support_tab_layout.addWidget(self.support_content)

        self.tab_widget.addTab(self.support_tab, "")

        self.main_layout.addWidget(self.tab_widget)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName("button_layout")
        self.horizontal_spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.button_layout.addItem(self.horizontal_spacer)

        self.ok_button = QPushButton(UserManualDialog)
        self.ok_button.setObjectName("ok_button")

        self.button_layout.addWidget(self.ok_button)

        self.main_layout.addLayout(self.button_layout)

        self.retranslateUi(UserManualDialog)

        self.tab_widget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(UserManualDialog)

    # setupUi

    def retranslateUi(self, UserManualDialog):
        UserManualDialog.setWindowTitle(
            QCoreApplication.translate("UserManualDialog", "User Manual", None)
        )
        self.title_label.setText(
            QCoreApplication.translate("UserManualDialog", "User Guide", None)
        )
        self.setup_content.setHtml(
            QCoreApplication.translate(
                "UserManualDialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Initial Setup</span></h2>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">On first launch, you\'ll need to configure two important paths:</span></p>\n'
                '<h4 style=" margin-top'
                ':12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">1. Mods Directory</span></h4>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">This is where Steam Workshop mods are stored. The path is typically:</span></p>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Courier New,courier\'; font-size:8.25pt;">DRIVE/STEAM_FOLDER/steamapps/workshop/content/400750</span></p>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Examples:</span></p>\n'
                '<ul style="margin-top: 0px; margin-bottom: 0'
                'px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Courier New,courier\';">C:/Program Files (x86)/Steam/steamapps/workshop/content/400750</span></li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Courier New,courier\';">D:/Steam/steamapps/workshop/content/400750</span></li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Courier New,courier\';">C:/Steam/steamapps/workshop/content/400750</span></li></ul>\n'
                '<h4 style=" margin-top:12px; margin-bottom:12px; marg'
                'in-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">2. Options.set File</span></h4>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">This file can be found in one of two locations:</span></p>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Location 1 (Most Common):</span></p>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Courier New,courier\'; font-size:8.25pt;">C:/Users/YOUR_USERNAME/Documents/My Games/gates of hell/profiles/STEAM_USER_ID/options.set</span></p>\n'
                '<p style=" margin-top:12px; margin-botto'
                'm:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Location 2 (Alternative):</span></p>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'Courier New,courier\'; font-size:8.25pt;">C:/Users/YOUR_USERNAME/AppData/Local/digitalmindsoft/gates of hell/profiles/STEAM_USER_ID/options.set</span></p></body></html>',
                None,
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.setup_tab),
            QCoreApplication.translate("UserManualDialog", "Setup", None),
        )
        self.interface_content.setHtml(
            QCoreApplication.translate(
                "UserManualDialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Interface Layout</span></h2>\n'
                '<h4 style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Left Panel: Installed Mods</span></h4>\n'
                '<p style=" margin-top:12px; margin-b'
                'ottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Shows all mods available in your mods directory</span></p>\n'
                '<h4 style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Right Panel: Active Mods</span></h4>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Shows currently enabled mods that will load in-game</span></p>\n'
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Mod Information Panel</span></h2>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px;'
                ' margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Click any mod to view its details automatically. This can be disabled in the menu if preferred.</span></p></body></html>',
                None,
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.interface_tab),
            QCoreApplication.translate("UserManualDialog", "Interface", None),
        )
        self.managing_content.setHtml(
            QCoreApplication.translate(
                "UserManualDialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Managing Mods</span></h2>\n'
                '<h4 style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Activating Mods</span></h4>\n'
                '<ul style="margin-top: 0px; margin-bottom: 0px; ma'
                'rgin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Double-click</span> any installed mod to activate it</li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Select multiple mods</span> (Ctrl+click) and use &quot;Add Selected&quot;</li></ul>\n'
                '<h4 style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Deactivating Mods</span></h4>\n'
                '<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">\n'
                "<li style=\" font-family:'MS"
                ' Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Double-click</span> any active mod to remove it</li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">Select multiple mods</span> and click &quot;Remove&quot;</li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">&quot;Clear All&quot;</span> removes all active mods at once</li></ul></body></html>',
                None,
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.managing_tab),
            QCoreApplication.translate("UserManualDialog", "Managing Mods", None),
        )
        self.presets_content.setHtml(
            QCoreApplication.translate(
                "UserManualDialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Preset System</span></h2>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Save and load different mod configurations:</span></p>\n'
                '<ul style="margin-top: 0px; margin-bottom'
                ': 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">&quot;Save&quot;</span> - Create a preset from current active mods</li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">&quot;Load&quot;</span> - Apply a saved preset</li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">&quot;Delete&quot;</span> - Remove a preset permanently</li></ul>\n'
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; '
                'text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Sharing Configurations</span></h2>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Share your mod setups with other players:</span></p>\n'
                '<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;">\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">&quot;Export&quot;</span> - Generate a shareable code in the text field</li>\n'
                '<li style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;" style=" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600;">&quot;Import&q'
                "uot;</span> - Load a configuration from a shared code</li></ul></body></html>",
                None,
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.presets_tab),
            QCoreApplication.translate("UserManualDialog", "Presets && Sharing", None),
        )
        self.support_content.setHtml(
            QCoreApplication.translate(
                "UserManualDialog",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "hr { height: 1px; border-width: 0; }\n"
                'li.unchecked::marker { content: "\\2610"; }\n'
                'li.checked::marker { content: "\\2612"; }\n'
                "</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
                '<h2 style=" margin-top:16px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:600;">Support</span></h2>\n'
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">Found a bug or have suggestions? The interface is designed to be user-friendly - feel free to experiment an'
                "d provide feedback for improvements.</span></p>\n"
                '<p style=" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt;">You can report issues or suggest improvements through the appropriate channels.</span></p></body></html>',
                None,
            )
        )
        self.tab_widget.setTabText(
            self.tab_widget.indexOf(self.support_tab),
            QCoreApplication.translate("UserManualDialog", "Support", None),
        )
        self.ok_button.setText(
            QCoreApplication.translate("UserManualDialog", "OK", None)
        )

    # retranslateUi
