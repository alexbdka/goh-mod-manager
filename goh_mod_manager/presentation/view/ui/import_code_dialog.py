# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'import_code_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

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
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit_code = QLineEdit(ImportCodeDialog)
        self.lineEdit_code.setObjectName(u"lineEdit_code")
        self.lineEdit_code.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.lineEdit_code)

        self.pushButton_import = QPushButton(ImportCodeDialog)
        self.pushButton_import.setObjectName(u"pushButton_import")

        self.horizontalLayout.addWidget(self.pushButton_import)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(ImportCodeDialog)

        QMetaObject.connectSlotsByName(ImportCodeDialog)
    # setupUi

    def retranslateUi(self, ImportCodeDialog):
        ImportCodeDialog.setWindowTitle(QCoreApplication.translate("ImportCodeDialog", u"Load Order Code", None))
        self.label.setText(QCoreApplication.translate("ImportCodeDialog", u"Import Load Order", None))
        self.lineEdit_code.setPlaceholderText(QCoreApplication.translate("ImportCodeDialog", u"Paste code...", None))
        self.pushButton_import.setText(QCoreApplication.translate("ImportCodeDialog", u"Import", None))
    # retranslateUi

