# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(400, 200)
        AboutDialog.setMinimumSize(QSize(400, 200))
        AboutDialog.setMaximumSize(QSize(400, 200))
        AboutDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(20, 15, 20, 15)
        self.thankYouLabel = QLabel(AboutDialog)
        self.thankYouLabel.setObjectName("thankYouLabel")
        self.thankYouLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.thankYouLabel)

        self.descriptionLabel = QLabel(AboutDialog)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.descriptionLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.creditsLabel = QLabel(AboutDialog)
        self.creditsLabel.setObjectName("creditsLabel")
        self.creditsLabel.setTextFormat(Qt.TextFormat.RichText)
        self.creditsLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )
        self.creditsLabel.setWordWrap(True)
        self.creditsLabel.setOpenExternalLinks(True)
        self.creditsLabel.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )

        self.verticalLayout.addWidget(self.creditsLabel)

        self.versionLabel = QLabel(AboutDialog)
        self.versionLabel.setObjectName("versionLabel")
        self.versionLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.versionLabel)

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

        self.closeButton = QPushButton(AboutDialog)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setMinimumSize(QSize(80, 30))

        self.buttonLayout.addWidget(self.closeButton)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.buttonLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(AboutDialog)
        self.closeButton.clicked.connect(AboutDialog.accept)

        self.closeButton.setDefault(True)

        QMetaObject.connectSlotsByName(AboutDialog)

    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(
            QCoreApplication.translate("AboutDialog", "About", None)
        )
        self.thankYouLabel.setText(
            QCoreApplication.translate(
                "AboutDialog",
                '<html><head/><body><p align="center"><span style=" font-weight:600;">Thank you for using this Mod Manager!</span></p></body></html>',
                None,
            )
        )
        self.descriptionLabel.setText(
            QCoreApplication.translate(
                "AboutDialog",
                "This application is a friendly mod manager designed to make your life easier.\n"
                "Built with \u2764\ufe0f using Python and PySide6.",
                None,
            )
        )
        self.creditsLabel.setText(
            QCoreApplication.translate(
                "AboutDialog",
                '<html><head/><body><p><span style=" font-weight:600;">Credits:</span><br/>\u2022 Interface: <a href="https://doc.qt.io/qtforpython/"><span style=" text-decoration: underline; color:#0000ff;">Qt for Python (PySide6)</span></a><br/>\u2022 Icons: <a href="https://remixicon.com/"><span style=" text-decoration: underline; color:#0000ff;">Remix Icon</span></a><br/>\u2022 Developer: <a href="https://github.com/alexbdka"><span style=" text-decoration: underline; color:#0000ff;">alex6</span></a></p></body></html>',
                None,
            )
        )
        self.versionLabel.setText(
            QCoreApplication.translate(
                "AboutDialog",
                '<html><head/><body><p align="center">Version : <span style=" font-weight:600;">{VERSION_PLACEHOLDER}</span></p></body></html>',
                None,
            )
        )
        self.closeButton.setText(
            QCoreApplication.translate("AboutDialog", "Close", None)
        )

    # retranslateUi
