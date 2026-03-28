# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(450, 240)
        AboutDialog.setMinimumSize(QSize(450, 240))
        AboutDialog.setMaximumSize(QSize(450, 240))
        AboutDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.thankYouLabel = QLabel(AboutDialog)
        self.thankYouLabel.setObjectName(u"thankYouLabel")
        self.thankYouLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.thankYouLabel)

        self.descriptionLabel = QLabel(AboutDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.creditsLabel = QLabel(AboutDialog)
        self.creditsLabel.setObjectName(u"creditsLabel")
        self.creditsLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.creditsLabel)

        self.versionLabel = QLabel(AboutDialog)
        self.versionLabel.setObjectName(u"versionLabel")
        self.versionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.versionLabel)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)
        self.buttonBox.setCenterButtons(True)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.rejected.connect(AboutDialog.reject)
        self.buttonBox.accepted.connect(AboutDialog.accept)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About", None))
        self.thankYouLabel.setText(QCoreApplication.translate("AboutDialog", u"Thank you for using the mod manager!", None))
        self.descriptionLabel.setText(QCoreApplication.translate("AboutDialog", u"This application helps you manage Gates of Hell mods. Built with Python and PySide6.\n"
"                        ", None))
        self.creditsLabel.setText(QCoreApplication.translate("AboutDialog", u"Credits:\n"
"                            Interface: Qt for Python (PySide6)\n"
"                            Icons: Remix Icon, awasde\n"
"                            Developer: alex6\n"
"                        ", None))
        self.versionLabel.setText(QCoreApplication.translate("AboutDialog", u"Version: {VERSION_PLACEHOLDER}", None))
    # retranslateUi

