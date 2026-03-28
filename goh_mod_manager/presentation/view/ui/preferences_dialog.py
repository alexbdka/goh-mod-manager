# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(500, 324)
        PreferencesDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pathGroupBox = QGroupBox(PreferencesDialog)
        self.pathGroupBox.setObjectName(u"pathGroupBox")
        self.gridLayout = QGridLayout(self.pathGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.modsFolderLineEdit = QLineEdit(self.pathGroupBox)
        self.modsFolderLineEdit.setObjectName(u"modsFolderLineEdit")
        self.modsFolderLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.modsFolderLineEdit, 1, 1, 1, 1)

        self.settingsFileButton = QPushButton(self.pathGroupBox)
        self.settingsFileButton.setObjectName(u"settingsFileButton")

        self.gridLayout.addWidget(self.settingsFileButton, 2, 2, 1, 1)

        self.settingsFileLineEdit = QLineEdit(self.pathGroupBox)
        self.settingsFileLineEdit.setObjectName(u"settingsFileLineEdit")
        self.settingsFileLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.settingsFileLineEdit, 2, 1, 1, 1)

        self.settingsFileLabel = QLabel(self.pathGroupBox)
        self.settingsFileLabel.setObjectName(u"settingsFileLabel")
        self.settingsFileLabel.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.settingsFileLabel, 2, 0, 1, 1)

        self.modsFolderLabel = QLabel(self.pathGroupBox)
        self.modsFolderLabel.setObjectName(u"modsFolderLabel")
        self.modsFolderLabel.setMinimumSize(QSize(80, 0))

        self.gridLayout.addWidget(self.modsFolderLabel, 1, 0, 1, 1)

        self.modsFolderButton = QPushButton(self.pathGroupBox)
        self.modsFolderButton.setObjectName(u"modsFolderButton")

        self.gridLayout.addWidget(self.modsFolderButton, 1, 2, 1, 1)

        self.gameFolderLineEdit = QLineEdit(self.pathGroupBox)
        self.gameFolderLineEdit.setObjectName(u"gameFolderLineEdit")
        self.gameFolderLineEdit.setReadOnly(True)

        self.gridLayout.addWidget(self.gameFolderLineEdit, 0, 1, 1, 1)

        self.gameFolderLabel = QLabel(self.pathGroupBox)
        self.gameFolderLabel.setObjectName(u"gameFolderLabel")

        self.gridLayout.addWidget(self.gameFolderLabel, 0, 0, 1, 1)

        self.gameFolderButton = QPushButton(self.pathGroupBox)
        self.gameFolderButton.setObjectName(u"gameFolderButton")

        self.gridLayout.addWidget(self.gameFolderButton, 0, 2, 1, 1)


        self.verticalLayout.addWidget(self.pathGroupBox)

        self.guidedTourGroupBox = QGroupBox(PreferencesDialog)
        self.guidedTourGroupBox.setObjectName(u"guidedTourGroupBox")
        self.guidedTourLayout = QHBoxLayout(self.guidedTourGroupBox)
        self.guidedTourLayout.setObjectName(u"guidedTourLayout")
        self.checkBox_show_guided_tour = QCheckBox(self.guidedTourGroupBox)
        self.checkBox_show_guided_tour.setObjectName(u"checkBox_show_guided_tour")

        self.guidedTourLayout.addWidget(self.checkBox_show_guided_tour)

        self.guidedTourSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.guidedTourLayout.addItem(self.guidedTourSpacer)

        self.pushButton_start_guided_tour = QPushButton(self.guidedTourGroupBox)
        self.pushButton_start_guided_tour.setObjectName(u"pushButton_start_guided_tour")

        self.guidedTourLayout.addWidget(self.pushButton_start_guided_tour)


        self.verticalLayout.addWidget(self.guidedTourGroupBox)

        self.languageGroupBox = QGroupBox(PreferencesDialog)
        self.languageGroupBox.setObjectName(u"languageGroupBox")
        self.languageLayout = QHBoxLayout(self.languageGroupBox)
        self.languageLayout.setObjectName(u"languageLayout")
        self.languageLabel = QLabel(self.languageGroupBox)
        self.languageLabel.setObjectName(u"languageLabel")

        self.languageLayout.addWidget(self.languageLabel)

        self.comboBox_language = QComboBox(self.languageGroupBox)
        self.comboBox_language.setObjectName(u"comboBox_language")

        self.languageLayout.addWidget(self.comboBox_language)

        self.languageSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.languageLayout.addItem(self.languageSpacer)


        self.verticalLayout.addWidget(self.languageGroupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.pathGroupBox.setTitle(QCoreApplication.translate("PreferencesDialog", u"Required paths", None))
        self.modsFolderLineEdit.setPlaceholderText(QCoreApplication.translate("PreferencesDialog", u"Select the mods folder...", None))
        self.settingsFileButton.setText(QCoreApplication.translate("PreferencesDialog", u"Browse...", None))
        self.settingsFileLineEdit.setPlaceholderText(QCoreApplication.translate("PreferencesDialog", u"Select the options.set file...", None))
        self.settingsFileLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Options.set file", None))
        self.modsFolderLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Mods folder", None))
        self.modsFolderButton.setText(QCoreApplication.translate("PreferencesDialog", u"Browse...", None))
        self.gameFolderLineEdit.setPlaceholderText(QCoreApplication.translate("PreferencesDialog", u"Select the game folder...", None))
        self.gameFolderLabel.setText(QCoreApplication.translate("PreferencesDialog", u"Game folder", None))
        self.gameFolderButton.setText(QCoreApplication.translate("PreferencesDialog", u"Browse...", None))
        self.guidedTourGroupBox.setTitle(QCoreApplication.translate("PreferencesDialog", u"Guided tour", None))
        self.checkBox_show_guided_tour.setText(QCoreApplication.translate("PreferencesDialog", u"Show guided tour on startup", None))
        self.pushButton_start_guided_tour.setText(QCoreApplication.translate("PreferencesDialog", u"Start guided tour", None))
        self.languageGroupBox.setTitle(QCoreApplication.translate("PreferencesDialog", u"Language", None))
        self.languageLabel.setText(QCoreApplication.translate("PreferencesDialog", u"App language", None))
    # retranslateUi

