from typing import List

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from src.core.mod import ModInfo
from src.utils import markup_parser


class CatalogueWidget(QWidget):
    """
    Widget displaying the catalogue of available mods (Local + Workshop).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_mods: List[ModInfo] = []
        self._active_mod_ids: set[str] = set()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.title_label = QLabel(self.tr("Catalogue (Available Mods)"))
        layout.addWidget(self.title_label)

        # Search Filter and View Toggle
        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self.tr("Search mods..."))
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._apply_filters)
        search_layout.addWidget(self.search_bar)

        self.btn_toggle_view = QPushButton(self.tr("Thumbnails"))
        self.btn_toggle_view.setCheckable(True)
        self.btn_toggle_view.setChecked(True)
        self.btn_toggle_view.toggled.connect(self._on_toggle_view)
        search_layout.addWidget(self.btn_toggle_view)

        layout.addLayout(search_layout)

        # Tabs (using QTabBar as a filter selector)
        self.tab_bar = QTabBar()
        self.tab_bar.addTab(self.tr("All"))
        self.tab_bar.addTab(self.tr("Workshop"))
        self.tab_bar.addTab(self.tr("Local"))
        self.tab_bar.currentChanged.connect(self._apply_filters)
        layout.addWidget(self.tab_bar)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.setIconSize(QSize(64, 64))
        layout.addWidget(self.list_widget)

    def _on_toggle_view(self, checked: bool):
        if checked:
            self.list_widget.setIconSize(QSize(64, 64))
            self.list_widget.setWordWrap(True)
        else:
            self.list_widget.setIconSize(QSize())
            self.list_widget.setWordWrap(False)
        self._apply_filters()

    def populate(self, mods: List[ModInfo]):
        """
        Saves the provided mods and applies current filters to populate the list.
        """
        self._all_mods = sorted(
            mods, key=lambda m: markup_parser.strip_markup(m.name).lower()
        )
        self._apply_filters()

    def set_active_mod_ids(self, mod_ids: List[str]):
        self._active_mod_ids = set(mod_ids)
        self._apply_filters()

    def _apply_filters(self):
        self.list_widget.clear()
        search_text = self.search_bar.text().lower()
        current_tab = self.tab_bar.currentIndex()

        for mod in self._all_mods:
            # Tab filter: 0 = All, 1 = Workshop, 2 = Local
            if current_tab == 1 and mod.isLocal:
                continue
            if current_tab == 2 and not mod.isLocal:
                continue

            # Search filter
            if search_text and search_text not in mod.name.lower():
                continue

            # We can display the name but store the mod ID in the item's UserRole
            # so we can easily retrieve it when the user clicks on it.
            clean_name = markup_parser.strip_markup(mod.name)
            display_text = f"{clean_name}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, mod.id)

            if self.btn_toggle_view.isChecked() and mod.image_path:
                pixmap = QPixmap(mod.image_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        64,
                        64,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    item.setIcon(QIcon(scaled))

            if mod.isLocal:
                item.setToolTip(self.tr("Local Mod"))
            else:
                item.setToolTip(self.tr("Workshop Mod"))

            if mod.id in self._active_mod_ids:
                disabled_text = self.palette().color(
                    QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.Text,
                )
                item.setForeground(QBrush(disabled_text))
                item.setToolTip(
                    self.tr("{0}\nAlready active in the load order.").format(
                        item.toolTip()
                    )
                )

            self.list_widget.addItem(item)

    def get_selected_mod_id(self) -> str | None:
        """
        Returns the ID of the currently selected mod, or None if nothing is selected.
        """
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

    def get_selected_mod_ids(self) -> List[str]:
        """
        Returns a list of IDs for all currently selected mods.
        """
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list_widget.selectedItems()
        ]
