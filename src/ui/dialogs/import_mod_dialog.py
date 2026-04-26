import os

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from src.ui.appearance_manager import AppearanceManager
from src.ui.language_change_mixin import LanguageChangeMixin


class DropZoneWidget(LanguageChangeMixin, QWidget):
    """
    A custom widget that accepts drag and drop events for files and folders.
    """

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("ImportDropZone")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMinimumHeight(180)
        self.setProperty("dragHover", False)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.icon_label)

        self.title_label = QLabel()
        self.title_label.setProperty("uiRole", "dropZoneTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setProperty("uiRole", "dropZoneSubtitle")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)
        layout.addStretch()
        self.refresh_icons()

    def retranslate_ui(self):
        self.title_label.setText(self.tr("Drop a mod archive or folder here"))
        self.subtitle_label.setText(
            self.tr("Supported archives: .zip, .rar, .7z, .tar, .gz")
        )

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors(self)
        icon = qta.icon("fa5s.upload", **icon_colors)
        self.icon_label.setPixmap(icon.pixmap(32, 32))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._set_drag_hover(True)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._set_drag_hover(False)

    def dropEvent(self, event):
        self._set_drag_hover(False)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):
                self.file_dropped.emit(path)
                # Only handle the first dropped item for simplicity
                break
        event.acceptProposedAction()

    def _set_drag_hover(self, active: bool):
        self.setProperty("dragHover", active)
        self.style().unpolish(self)
        self.style().polish(self)


class ImportModDialog(LanguageChangeMixin, QDialog):
    """
    Dialog allowing users to import a mod via Drag & Drop or file/folder browsers.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(520, 320)
        self.selected_path = None
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Drop Zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self._on_item_dropped)
        layout.addWidget(self.drop_zone, stretch=1)

        # Fallback Buttons
        buttons_layout = QHBoxLayout()

        self.btn_archive = QPushButton()
        self.btn_archive.setProperty("uiRole", "compactAction")
        self.btn_archive.clicked.connect(self._on_select_archive)

        self.btn_folder = QPushButton()
        self.btn_folder.setProperty("uiRole", "compactAction")
        self.btn_folder.clicked.connect(self._on_select_folder)

        buttons_layout.addWidget(self.btn_archive)
        buttons_layout.addWidget(self.btn_folder)

        layout.addLayout(buttons_layout)

    def _on_item_dropped(self, path: str):
        self.selected_path = path
        self.accept()

    def _on_select_archive(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Mod Archive"),
            "",
            self.tr("Archives (*.zip *.rar *.7z *.tar *.gz);;All Files (*)"),
        )
        if file_path:
            self.selected_path = file_path
            self.accept()

    def _on_select_folder(self):
        dir_path = QFileDialog.getExistingDirectory(
            self, self.tr("Select Mod Directory")
        )
        if dir_path:
            self.selected_path = dir_path
            self.accept()

    def get_path(self) -> str | None:
        return self.selected_path

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Import Mod"))
        self.btn_archive.setText(self.tr("Select Archive..."))
        self.btn_archive.setToolTip(self.tr("Import from .zip, .rar, .7z, etc."))
        self.btn_folder.setText(self.tr("Select Folder..."))
        self.btn_folder.setToolTip(self.tr("Import an uncompressed mod folder"))
        self.refresh_icons()

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors(self)
        self.drop_zone.refresh_icons()
        self.btn_archive.setIcon(qta.icon("fa5s.file-archive", **icon_colors))
        self.btn_folder.setIcon(qta.icon("fa5s.folder-open", **icon_colors))
