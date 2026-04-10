from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
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
from src.ui.widgets.catalogue_item_delegate import (
    CatalogueItemDelegate,
    ROLE_IS_ACTIVE,
    ROLE_MOD_ID,
    ROLE_PIXMAP,
    ROLE_STATUS_ENTRIES,
    ROLE_TITLE,
)
from src.utils import markup_parser


class CatalogueWidget(QWidget):
    """
    Widget displaying the catalogue of available mods (Local + Workshop).
    """

    selection_changed = Signal()
    context_menu_requested = Signal(object)
    mod_double_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_mods: List[ModInfo] = []
        self._active_mod_ids: set[str] = set()
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._apply_filters)
        search_layout.addWidget(self.search_bar)

        self.btn_toggle_view = QPushButton()
        self.btn_toggle_view.setCheckable(True)
        self.btn_toggle_view.setChecked(True)
        self.btn_toggle_view.toggled.connect(self._on_toggle_view)
        search_layout.addWidget(self.btn_toggle_view)

        layout.addLayout(search_layout)

        self.tab_bar = QTabBar()
        self.tab_bar.addTab("")
        self.tab_bar.addTab("")
        self.tab_bar.addTab("")
        self.tab_bar.currentChanged.connect(self._apply_filters)
        layout.addWidget(self.tab_bar)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.setMouseTracking(True)
        self.list_widget.itemSelectionChanged.connect(self.selection_changed.emit)
        self.list_widget.customContextMenuRequested.connect(
            self.context_menu_requested.emit
        )
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._delegate = CatalogueItemDelegate(self.list_widget, thumbnail_enabled=True)
        self.list_widget.setItemDelegate(self._delegate)
        layout.addWidget(self.list_widget)

    def _on_toggle_view(self, checked: bool):
        self._delegate.set_thumbnail_enabled(checked)
        self.list_widget.doItemsLayout()
        self.list_widget.viewport().update()

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

    def refresh_icons(self):
        self._delegate.clear_icon_cache()
        self.list_widget.viewport().update()

    def retranslate_ui(self):
        self.title_label.setText(self.tr("Catalogue (Available Mods)"))
        self.search_bar.setPlaceholderText(self.tr("Search mods..."))
        self.btn_toggle_view.setText(self.tr("Thumbnails"))
        self.tab_bar.setTabText(0, self.tr("All"))
        self.tab_bar.setTabText(1, self.tr("Workshop"))
        self.tab_bar.setTabText(2, self.tr("Local"))
        if self._all_mods:
            self._apply_filters()

    def _apply_filters(self):
        selected_mod_ids = set(self.get_selected_mod_ids())
        self.list_widget.clear()
        search_text = self.search_bar.text().lower()
        current_tab = self.tab_bar.currentIndex()

        for mod in self._all_mods:
            if current_tab == 1 and mod.isLocal:
                continue
            if current_tab == 2 and not mod.isLocal:
                continue

            if search_text and search_text not in mod.name.lower():
                continue

            clean_name = markup_parser.strip_markup(mod.name)
            tooltip = self._build_tooltip(mod)
            if mod.id in self._active_mod_ids:
                tooltip = self.tr("{0}\nAlready active in the load order.").format(
                    tooltip
                )

            item = QListWidgetItem(clean_name)
            item.setToolTip(tooltip)
            item.setData(ROLE_MOD_ID, mod.id)
            item.setData(ROLE_TITLE, clean_name)
            item.setData(ROLE_PIXMAP, self._build_thumbnail_pixmap(mod))
            item.setData(ROLE_STATUS_ENTRIES, self._build_status_entries(mod))
            item.setData(ROLE_IS_ACTIVE, mod.id in self._active_mod_ids)
            self.list_widget.addItem(item)

            if mod.id in selected_mod_ids:
                item.setSelected(True)

    def _build_thumbnail_pixmap(self, mod: ModInfo) -> QPixmap | None:
        if not mod.image_path:
            return None

        pixmap = QPixmap(mod.image_path)
        if pixmap.isNull():
            return None

        return pixmap.scaled(
            32,
            32,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _build_tooltip(self, mod: ModInfo) -> str:
        tooltip_lines = [self.tr("Local Mod") if mod.isLocal else self.tr("Workshop Mod")]
        missing_dependencies = self._get_missing_dependency_ids(mod)

        if missing_dependencies:
            tooltip_lines.append(
                self.tr("Missing dependencies: {0}").format(
                    ", ".join(missing_dependencies)
                )
            )
        elif mod.dependencies:
            tooltip_lines.append(
                self.tr("Dependencies: {0}").format(", ".join(mod.dependencies))
            )

        return "\n".join(tooltip_lines)

    def _get_missing_dependency_ids(self, mod: ModInfo) -> List[str]:
        if not mod.dependencies:
            return []

        known_mod_ids = {catalogue_mod.id for catalogue_mod in self._all_mods}
        return [dep_id for dep_id in mod.dependencies if dep_id not in known_mod_ids]

    def _build_status_entries(self, mod: ModInfo) -> list[dict[str, str]]:
        if not mod.dependencies:
            return []

        missing_dependencies = self._get_missing_dependency_ids(mod)
        if missing_dependencies:
            return [
                {
                    "kind": "missing_dependencies",
                    "tooltip": self.tr("Missing dependencies: {0}").format(
                        ", ".join(missing_dependencies)
                    ),
                }
            ]

        return [
            {
                "kind": "dependencies",
                "tooltip": self.tr("Dependencies: {0}").format(
                    ", ".join(mod.dependencies)
                ),
            }
        ]

    def get_mod_id_at(self, pos) -> str | None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return None
        return item.data(ROLE_MOD_ID)

    def clear_selection(self):
        self.list_widget.clearSelection()

    def block_list_signals(self, block: bool):
        return self.list_widget.blockSignals(block)

    def map_list_pos_to_global(self, pos):
        return self.list_widget.viewport().mapToGlobal(pos)

    def get_selected_mod_id(self) -> str | None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(ROLE_MOD_ID)

    def get_selected_mod_ids(self) -> List[str]:
        return [item.data(ROLE_MOD_ID) for item in self.list_widget.selectedItems()]

    def _on_item_double_clicked(self, _item):
        self.mod_double_clicked.emit()
