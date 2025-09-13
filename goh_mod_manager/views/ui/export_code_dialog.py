# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'export_code_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout


class Ui_ExportCodeDialog(object):
    def setupUi(self, ExportCodeDialog):
        if not ExportCodeDialog.objectName():
            ExportCodeDialog.setObjectName("ExportCodeDialog")
        ExportCodeDialog.resize(350, 120)
        self.verticalLayout = QVBoxLayout(ExportCodeDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(ExportCodeDialog)
        self.label.setObjectName("label")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit_code = QLineEdit(ExportCodeDialog)
        self.lineEdit_code.setObjectName("lineEdit_code")

        self.horizontalLayout.addWidget(self.lineEdit_code)

        self.pushButton_copy = QPushButton(ExportCodeDialog)
        self.pushButton_copy.setObjectName("pushButton_copy")

        self.horizontalLayout.addWidget(self.pushButton_copy)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ExportCodeDialog)

        QMetaObject.connectSlotsByName(ExportCodeDialog)

    # setupUi

    def retranslateUi(self, ExportCodeDialog):
        ExportCodeDialog.setWindowTitle(
            QCoreApplication.translate("ExportCodeDialog", "Code", None)
        )
        self.label.setText(
            QCoreApplication.translate("ExportCodeDialog", "Export", None)
        )
        self.lineEdit_code.setText("")
        self.lineEdit_code.setPlaceholderText(
            QCoreApplication.translate("ExportCodeDialog", "Wait for code...", None)
        )
        self.pushButton_copy.setText(
            QCoreApplication.translate("ExportCodeDialog", "Copy", None)
        )

    # retranslateUi
