# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(500, 306)
        PreferencesDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pathGroupBox = QGroupBox(PreferencesDialog)
        self.pathGroupBox.setObjectName("pathGroupBox")
        self.gridLayout = QGridLayout(self.pathGroupBox)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.modsFolderLineEdit = QLineEdit(self.pathGroupBox)
        self.modsFolderLineEdit.setObjectName("modsFolderLineEdit")
        self.modsFolderLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.modsFolderLineEdit, 1, 1, 1, 1)

        self.settingsFileButton = QPushButton(self.pathGroupBox)
        self.settingsFileButton.setObjectName("settingsFileButton")
        self.settingsFileButton.setMaximumSize(QSize(100, 16777215))

        self.gridLayout.addWidget(self.settingsFileButton, 2, 2, 1, 1)

        self.settingsFileLineEdit = QLineEdit(self.pathGroupBox)
        self.settingsFileLineEdit.setObjectName("settingsFileLineEdit")
        self.settingsFileLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.settingsFileLineEdit, 2, 1, 1, 1)

        self.settingsFileLabel = QLabel(self.pathGroupBox)
        self.settingsFileLabel.setObjectName("settingsFileLabel")
        self.settingsFileLabel.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.settingsFileLabel, 2, 0, 1, 1)

        self.modsFolderLabel = QLabel(self.pathGroupBox)
        self.modsFolderLabel.setObjectName("modsFolderLabel")
        self.modsFolderLabel.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.modsFolderLabel, 1, 0, 1, 1)

        self.modsFolderButton = QPushButton(self.pathGroupBox)
        self.modsFolderButton.setObjectName("modsFolderButton")
        self.modsFolderButton.setMaximumSize(QSize(100, 16777215))

        self.gridLayout.addWidget(self.modsFolderButton, 1, 2, 1, 1)

        self.gameFolderLineEdit = QLineEdit(self.pathGroupBox)
        self.gameFolderLineEdit.setObjectName("gameFolderLineEdit")

        self.gridLayout.addWidget(self.gameFolderLineEdit, 0, 1, 1, 1)

        self.gameFolderLabel = QLabel(self.pathGroupBox)
        self.gameFolderLabel.setObjectName("gameFolderLabel")

        self.gridLayout.addWidget(self.gameFolderLabel, 0, 0, 1, 1)

        self.gameFolderButton = QPushButton(self.pathGroupBox)
        self.gameFolderButton.setObjectName("gameFolderButton")

        self.gridLayout.addWidget(self.gameFolderButton, 0, 2, 1, 1)

        self.verticalLayout.addWidget(self.pathGroupBox)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.okButton = QPushButton(PreferencesDialog)
        self.okButton.setObjectName("okButton")
        self.okButton.setMinimumSize(QSize(80, 30))

        self.buttonLayout.addWidget(self.okButton)

        self.cancelButton = QPushButton(PreferencesDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.setMinimumSize(QSize(80, 30))

        self.buttonLayout.addWidget(self.cancelButton)

        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(PreferencesDialog)
        self.okButton.clicked.connect(PreferencesDialog.accept)
        self.cancelButton.clicked.connect(PreferencesDialog.reject)

        self.okButton.setDefault(True)

        QMetaObject.connectSlotsByName(PreferencesDialog)

    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(
            QCoreApplication.translate("PreferencesDialog", "Preferences", None)
        )
        self.pathGroupBox.setTitle(
            QCoreApplication.translate("PreferencesDialog", "Required Paths", None)
        )
        self.modsFolderLineEdit.setPlaceholderText(
            QCoreApplication.translate(
                "PreferencesDialog", "Select the mods folder...", None
            )
        )
        self.settingsFileButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Browse...", None)
        )
        self.settingsFileLineEdit.setPlaceholderText(
            QCoreApplication.translate(
                "PreferencesDialog", "Select the options.set file...", None
            )
        )
        self.settingsFileLabel.setText(
            QCoreApplication.translate("PreferencesDialog", "Settings file", None)
        )
        self.modsFolderLabel.setText(
            QCoreApplication.translate("PreferencesDialog", "Mods folder :", None)
        )
        self.modsFolderButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Browse...", None)
        )
        self.gameFolderLineEdit.setPlaceholderText(
            QCoreApplication.translate(
                "PreferencesDialog", "Select the game folder...", None
            )
        )
        self.gameFolderLabel.setText(
            QCoreApplication.translate("PreferencesDialog", "Game folder", None)
        )
        self.gameFolderButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Browse...", None)
        )
        self.okButton.setText(
            QCoreApplication.translate("PreferencesDialog", "OK", None)
        )
        self.cancelButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Cancel", None)
        )

    # retranslateUi
