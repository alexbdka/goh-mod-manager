# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'import_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_ImportDialog(object):
    def setupUi(self, ImportDialog):
        if not ImportDialog.objectName():
            ImportDialog.setObjectName("ImportDialog")
        ImportDialog.resize(261, 243)
        ImportDialog.setModal(True)
        self.main_layout = QVBoxLayout(ImportDialog)
        self.main_layout.setSpacing(15)
        self.main_layout.setObjectName("main_layout")
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.source_group = QGroupBox(ImportDialog)
        self.source_group.setObjectName("source_group")
        self.source_layout = QVBoxLayout(self.source_group)
        self.source_layout.setSpacing(8)
        self.source_layout.setObjectName("source_layout")
        self.path_input = QLineEdit(self.source_group)
        self.path_input.setObjectName("path_input")
        self.path_input.setMinimumSize(QSize(0, 30))

        self.source_layout.addWidget(self.path_input)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.setObjectName("button_layout")
        self.archive_button = QPushButton(self.source_group)
        self.archive_button.setObjectName("archive_button")
        self.archive_button.setMinimumSize(QSize(0, 35))

        self.button_layout.addWidget(self.archive_button)

        self.folder_button = QPushButton(self.source_group)
        self.folder_button.setObjectName("folder_button")
        self.folder_button.setMinimumSize(QSize(0, 35))

        self.button_layout.addWidget(self.folder_button)

        self.source_layout.addLayout(self.button_layout)

        self.main_layout.addWidget(self.source_group)

        self.vertical_spacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.main_layout.addItem(self.vertical_spacer)

        self.line = QFrame(ImportDialog)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.main_layout.addWidget(self.line)

        self.action_layout = QHBoxLayout()
        self.action_layout.setObjectName("action_layout")
        self.horizontal_spacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.action_layout.addItem(self.horizontal_spacer)

        self.import_button = QPushButton(ImportDialog)
        self.import_button.setObjectName("import_button")
        self.import_button.setMinimumSize(QSize(80, 35))

        self.action_layout.addWidget(self.import_button)

        self.cancel_button = QPushButton(ImportDialog)
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setMinimumSize(QSize(80, 35))

        self.action_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(self.action_layout)

        self.retranslateUi(ImportDialog)

        self.import_button.setDefault(True)

        QMetaObject.connectSlotsByName(ImportDialog)

    # setupUi

    def retranslateUi(self, ImportDialog):
        ImportDialog.setWindowTitle(
            QCoreApplication.translate("ImportDialog", "Import Mod", None)
        )
        self.source_group.setTitle(
            QCoreApplication.translate("ImportDialog", "Mod Source", None)
        )
        self.path_input.setPlaceholderText(
            QCoreApplication.translate(
                "ImportDialog",
                "Select a mod archive (.zip, .tar, .7z...) or folder",
                None,
            )
        )
        self.archive_button.setText(
            QCoreApplication.translate("ImportDialog", "Browse Archive...", None)
        )
        self.folder_button.setText(
            QCoreApplication.translate("ImportDialog", "Browse Folder...", None)
        )
        self.import_button.setText(
            QCoreApplication.translate("ImportDialog", "Import", None)
        )
        self.cancel_button.setText(
            QCoreApplication.translate("ImportDialog", "Cancel", None)
        )

    # retranslateUi
