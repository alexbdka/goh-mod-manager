# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'import_code_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QVBoxLayout)

class Ui_ImportCodeDialog(object):
    def setupUi(self, ImportCodeDialog):
        if not ImportCodeDialog.objectName():
            ImportCodeDialog.setObjectName(u"ImportCodeDialog")
        ImportCodeDialog.resize(350, 120)
        self.verticalLayout = QVBoxLayout(ImportCodeDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(ImportCodeDialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_code = QLineEdit(ImportCodeDialog)
        self.lineEdit_code.setObjectName(u"lineEdit_code")

        self.horizontalLayout.addWidget(self.lineEdit_code)

        self.pushButton_import = QPushButton(ImportCodeDialog)
        self.pushButton_import.setObjectName(u"pushButton_import")

        self.horizontalLayout.addWidget(self.pushButton_import)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(ImportCodeDialog)

        QMetaObject.connectSlotsByName(ImportCodeDialog)
    # setupUi

    def retranslateUi(self, ImportCodeDialog):
        ImportCodeDialog.setWindowTitle(QCoreApplication.translate("ImportCodeDialog", u"Code", None))
        self.label.setText(QCoreApplication.translate("ImportCodeDialog", u"Import", None))
        self.lineEdit_code.setPlaceholderText(QCoreApplication.translate("ImportCodeDialog", u"Enter code...", None))
        self.pushButton_import.setText(QCoreApplication.translate("ImportCodeDialog", u"Import", None))
    # retranslateUi

