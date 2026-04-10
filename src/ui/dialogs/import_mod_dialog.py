import os

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


class DropZoneWidget(QWidget):
    """
    A custom widget that accepts drag and drop events for files and folders.
    """

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

    def retranslate_ui(self):
        self.label.setText(self.tr("Drag & Drop a Mod Archive or Folder here"))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Highlight border
            self.label.setProperty("dragHover", True)
            self.label.style().unpolish(self.label)
            self.label.style().polish(self.label)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        # Restore normal border
        self.label.setProperty("dragHover", False)
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)

    def dropEvent(self, event):
        self.label.setProperty("dragHover", False)
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.exists(path):
                self.file_dropped.emit(path)
                # Only handle the first dropped item for simplicity
                break
        event.acceptProposedAction()


class ImportModDialog(QDialog):
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
        self.btn_archive.clicked.connect(self._on_select_archive)

        self.btn_folder = QPushButton()
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
        self.drop_zone.retranslate_ui()
        self.btn_archive.setText(self.tr("Select Archive..."))
        self.btn_archive.setToolTip(self.tr("Import from .zip, .rar, .7z, etc."))
        self.btn_folder.setText(self.tr("Select Folder..."))
        self.btn_folder.setToolTip(self.tr("Import an uncompressed mod folder"))
