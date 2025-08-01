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
        PreferencesDialog.resize(500, 208)
        PreferencesDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setContentsMargins(20, 20, 20, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pathGroupBox = QGroupBox(PreferencesDialog)
        self.pathGroupBox.setObjectName("pathGroupBox")
        self.gridLayout = QGridLayout(self.pathGroupBox)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setContentsMargins(15, 15, 15, 15)
        self.gridLayout.setObjectName("gridLayout")
        self.folderLabel = QLabel(self.pathGroupBox)
        self.folderLabel.setObjectName("folderLabel")
        self.folderLabel.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.folderLabel, 0, 0, 1, 1)

        self.folderLineEdit = QLineEdit(self.pathGroupBox)
        self.folderLineEdit.setObjectName("folderLineEdit")
        self.folderLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.folderLineEdit, 0, 1, 1, 1)

        self.folderBrowseButton = QPushButton(self.pathGroupBox)
        self.folderBrowseButton.setObjectName("folderBrowseButton")
        self.folderBrowseButton.setMaximumSize(QSize(100, 16777215))

        self.gridLayout.addWidget(self.folderBrowseButton, 0, 2, 1, 1)

        self.fileLabel = QLabel(self.pathGroupBox)
        self.fileLabel.setObjectName("fileLabel")
        self.fileLabel.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.fileLabel, 1, 0, 1, 1)

        self.fileLineEdit = QLineEdit(self.pathGroupBox)
        self.fileLineEdit.setObjectName("fileLineEdit")
        self.fileLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.fileLineEdit, 1, 1, 1, 1)

        self.fileBrowseButton = QPushButton(self.pathGroupBox)
        self.fileBrowseButton.setObjectName("fileBrowseButton")
        self.fileBrowseButton.setMaximumSize(QSize(100, 16777215))

        self.gridLayout.addWidget(self.fileBrowseButton, 1, 2, 1, 1)

        self.verticalLayout.addWidget(self.pathGroupBox)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.buttonLayout.addItem(self.horizontalSpacer)

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
        self.folderLabel.setText(
            QCoreApplication.translate("PreferencesDialog", "Mods folder :", None)
        )
        self.folderLineEdit.setPlaceholderText(
            QCoreApplication.translate("PreferencesDialog", "Select a folder...", None)
        )
        self.folderBrowseButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Browse...", None)
        )
        self.fileLabel.setText(
            QCoreApplication.translate("PreferencesDialog", "options.set", None)
        )
        self.fileLineEdit.setPlaceholderText(
            QCoreApplication.translate(
                "PreferencesDialog", "Select the options.set file", None
            )
        )
        self.fileBrowseButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Browse...", None)
        )
        self.okButton.setText(
            QCoreApplication.translate("PreferencesDialog", "OK", None)
        )
        self.cancelButton.setText(
            QCoreApplication.translate("PreferencesDialog", "Cancel", None)
        )

    # retranslateUi
