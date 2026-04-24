import qtawesome as qta
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QPushButton, QToolBar, QWidget
from src.ui.appearance_manager import AppearanceManager
from src.ui.language_change_mixin import LanguageChangeMixin


class MainToolBar(LanguageChangeMixin, QToolBar):
    """
    Main toolbar of the application, containing global actions like 'Launch Game'.
    """

    play_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setIconSize(QSize(32, 32))
        self.setMovable(False)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        # Spacer to push the play button to the right
        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Expanding
        )
        self.addWidget(spacer)

        # Play Button
        self.btn_play = QPushButton()
        self.btn_play.setMinimumWidth(170)
        self.addWidget(self.btn_play)
        self.refresh_icons()

        self.btn_play.clicked.connect(self.play_requested.emit)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Main Toolbar"))
        self.btn_play.setText(self.tr("Launch Game"))

    def refresh_icons(self):
        self.btn_play.setIcon(
            qta.icon("fa5s.play", **AppearanceManager.get_icon_colors())
        )
