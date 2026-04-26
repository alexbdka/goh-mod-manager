from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from src.application.state import ModState
from src.ui.language_change_mixin import LanguageChangeMixin
from src.utils import markup_parser


class ModDetailsWidget(LanguageChangeMixin, QFrame):
    """
    Widget displaying the detailed information of a selected mod.
    Parses GEM markup tags to display rich text descriptions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mod: ModState | None = None
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._current_pixmap = None
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.addStretch(1)
        self.empty_label = QLabel()
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setProperty("uiRole", "emptyState")
        empty_layout.addWidget(self.empty_label)
        empty_layout.addStretch(1)
        self.stack.addWidget(self.empty_widget)

        self.details_widget = QWidget()
        details_layout = QVBoxLayout(self.details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        left_column = QVBoxLayout()
        left_column.setSpacing(6)

        self.title_label = QLabel()
        self.title_label.setProperty("uiRole", "detailsTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        left_column.addWidget(self.title_label)

        self.meta_label = QLabel("")
        self.meta_label.setProperty("uiRole", "detailsMeta")
        self.meta_label.setWordWrap(True)
        self.meta_label.setTextFormat(Qt.TextFormat.RichText)
        self.meta_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        left_column.addWidget(self.meta_label)
        left_column.addStretch()

        header_layout.addLayout(left_column, stretch=1)

        self.image_label = QLabel()
        self.image_label.setObjectName("ModDetailsImage")
        self.image_label.setFixedSize(150, 150)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.hide()
        header_layout.addWidget(self.image_label)

        details_layout.addLayout(header_layout)

        self.desc_browser = QTextBrowser()
        self.desc_browser.setObjectName("ModDetailsDescription")
        self.desc_browser.setOpenExternalLinks(True)
        self.desc_browser.setFrameShape(QFrame.Shape.NoFrame)
        details_layout.addWidget(self.desc_browser)

        self.stack.addWidget(self.details_widget)

    def display_mod(self, mod: ModState | None):
        """
        Updates the widget to show the details of the given mod.
        If mod is None, clears the display.
        """
        self._current_mod = mod
        if not mod:
            self._current_pixmap = None
            self._update_image()
            self.empty_label.setText(self.tr("Select a mod to view details"))
            self.meta_label.setText("")
            self.desc_browser.clear()
            self.stack.setCurrentWidget(self.empty_widget)
            return

        self.stack.setCurrentWidget(self.details_widget)

        # Image
        self._current_pixmap = None
        if mod.image_path:
            pixmap = QPixmap(mod.image_path)
            if not pixmap.isNull():
                self._current_pixmap = pixmap

        self._update_image()

        # Title
        html_title = markup_parser.to_html(mod.name)
        self.title_label.setText(html_title)

        # Meta Info
        meta_lines = [self.tr("<b>ID:</b> {0}").format(mod.id)]

        if mod.min_game_version:
            version_text = self.tr("<b>Game Version:</b> {0}").format(
                mod.min_game_version
            )
            if mod.max_game_version and mod.max_game_version != mod.min_game_version:
                version_text += f" - {mod.max_game_version}"
            meta_lines.append(version_text)

        if mod.tags:
            meta_lines.append(self.tr("<b>Tags:</b> {0}").format(", ".join(mod.tags)))

        if mod.dependencies:
            meta_lines.append(
                self.tr("<b>Requires:</b> {0}").format(", ".join(mod.dependencies))
            )

        self.meta_label.setText("<br>".join(meta_lines))

        # Description (HTML)
        html_desc = markup_parser.to_html(mod.description)
        if not html_desc:
            html_desc = self.tr("<i>No description available.</i>")

        self.desc_browser.setHtml(html_desc)

    def retranslate_ui(self):
        self.display_mod(self._current_mod)

    def _update_image(self):
        if self._current_pixmap is not None:
            # Scale to a fixed, reasonable thumbnail size (e.g. 150x150 max)
            scaled_pixmap = self._current_pixmap.scaled(
                150,
                150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.show()
        else:
            self.image_label.hide()
