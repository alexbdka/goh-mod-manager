import qtawesome as qta
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QPushButton, QToolBar, QWidget

from src.ui.appearance_manager import AppearanceManager


class MainToolBar(QToolBar):
    """
    Main toolbar of the application, containing global actions like 'Launch Game'.
    """

    play_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(self.tr("Main Toolbar"), parent)
        self.setIconSize(QSize(32, 32))
        self.setMovable(False)
        self._setup_ui()

    def _setup_ui(self):
        # Spacer to push the play button to the right
        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Expanding
        )
        self.addWidget(spacer)

        # Play Button
        self.btn_play = QPushButton(self.tr("Launch Game"))
        self.btn_play.setMinimumWidth(170)
        self.addWidget(self.btn_play)
        self.refresh_icons()

        self.btn_play.clicked.connect(self.play_requested.emit)

    def refresh_icons(self):
        self.btn_play.setIcon(
            qta.icon("fa5s.play", **AppearanceManager.get_icon_colors())
        )
