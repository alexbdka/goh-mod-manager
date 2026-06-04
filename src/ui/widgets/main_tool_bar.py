from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QPushButton, QToolBar
from src.ui.appearance_manager import AppearanceManager
from src.ui.language_change_mixin import LanguageChangeMixin
from src.ui.qtawesome_compat import qta

SCALE_FACTOR = 1.2


class MainToolBar(LanguageChangeMixin, QToolBar):
    """
    Compact toolbar for high-frequency global actions.
    """

    import_share_code_requested = Signal()
    export_share_code_requested = Signal()
    play_requested = Signal()
    editor_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setObjectName("MainToolBar")
        self.setIconSize(QSize(18, 18))
        self.setMovable(False)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.btn_import_share_code = self._create_toolbar_button()
        self.btn_export_share_code = self._create_toolbar_button()
        self.btn_play = self._create_toolbar_button(primary=True)
        self.btn_editor = self._create_toolbar_button()

        self.addWidget(self.btn_play)
        self.addWidget(self.btn_editor)
        self.addSeparator()
        self.addWidget(self.btn_import_share_code)
        self.addWidget(self.btn_export_share_code)

        self.refresh_icons()

        self.btn_import_share_code.clicked.connect(
            self.import_share_code_requested.emit
        )
        self.btn_export_share_code.clicked.connect(
            self.export_share_code_requested.emit
        )
        self.btn_play.clicked.connect(self.play_requested.emit)
        self.btn_editor.clicked.connect(self.editor_requested.emit)

    def _create_toolbar_button(self, *, primary: bool = False) -> QPushButton:
        button = QPushButton()
        button.setProperty(
            "uiRole", "toolbarPrimaryButton" if primary else "toolbarButton"
        )
        button.setFixedSize(34, 30)
        return button

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Main Toolbar"))
        self._set_button_text(self.btn_import_share_code, self.tr("Import Share Code"))
        self._set_button_text(self.btn_export_share_code, self.tr("Export Share Code"))
        self._set_button_text(self.btn_play, self.tr("Launch Game"))
        self._set_button_text(self.btn_editor, self.tr("Launch Editor"))

    def _set_button_text(self, button: QPushButton, text: str):
        button.setText("")
        button.setToolTip(text)
        button.setStatusTip(text)
        button.setAccessibleName(text)

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors()
        self.btn_import_share_code.setIcon(
            qta.icon("mdi6.import", **icon_colors, scale_factor=SCALE_FACTOR)
        )
        self.btn_export_share_code.setIcon(
            qta.icon("mdi6.export", **icon_colors, scale_factor=SCALE_FACTOR)
        )
        self.btn_play.setIcon(
            qta.icon("mdi6.play", **icon_colors, scale_factor=SCALE_FACTOR)
        )
        self.btn_editor.setIcon(
            qta.icon("mdi6.puzzle", **icon_colors, scale_factor=SCALE_FACTOR)
        )
