from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.core.mod import ModInfo
from src.utils import markup_parser


class ModDetailsWidget(QFrame):
    """
    Widget displaying the detailed information of a selected mod.
    Parses GEM markup tags to display rich text descriptions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Mod Title
        self.title_label = QLabel(self.tr("Select a mod to view details"))
        self.title_label.setWordWrap(True)
        self.title_label.setTextFormat(Qt.TextFormat.RichText)
        # Using a very slight style here just to distinguish the title from the body
        self.title_label.setObjectName("ModTitle")
        layout.addWidget(self.title_label)

        # Meta Information (ID, Version, etc.)
        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)
        self.meta_label.setObjectName("ModMeta")
        layout.addWidget(self.meta_label)

        # Description (Rich Text)
        self.desc_browser = QTextBrowser()
        self.desc_browser.setOpenExternalLinks(True)
        # Remove border to blend better with the widget
        self.desc_browser.setFrameShape(QFrame.Shape.NoFrame)
        # Keep background transparent
        self.desc_browser.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout.addWidget(self.desc_browser)

    def display_mod(self, mod: ModInfo | None):
        """
        Updates the widget to show the details of the given mod.
        If mod is None, clears the display.
        """
        if not mod:
            self.title_label.setText(self.tr("Select a mod to view details"))
            self.meta_label.setText("")
            self.desc_browser.clear()
            return

        # Title
        html_title = markup_parser.to_html(mod.name)
        self.title_label.setText(html_title)

        # Meta Info
        meta_html = f"<b>ID:</b> {mod.id}<br>"

        if mod.minGameVersion:
            meta_html += self.tr("<b>Game Version:</b> {0}").format(mod.minGameVersion)
            if mod.maxGameVersion and mod.maxGameVersion != mod.minGameVersion:
                meta_html += f" - {mod.maxGameVersion}"
            meta_html += "<br>"

        if mod.tags:
            meta_html += self.tr("<b>Tags:</b> {0}<br>").format(", ".join(mod.tags))

        if mod.dependencies:
            meta_html += (
                self.tr("<b>Requires:</b> {0}<br>").format(", ".join(mod.dependencies))
            )

        self.meta_label.setText(meta_html)

        # Description (HTML)
        html_desc = markup_parser.to_html(mod.desc)
        if not html_desc:
            html_desc = self.tr("<i>No description available.</i>")

        self.desc_browser.setHtml(html_desc)
