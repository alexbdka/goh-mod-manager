from PySide6.QtCore import Qt, QTimer, Signal
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
from src.application.state import CatalogueState, ModState
from src.core.mod_reference import to_reference_key
from src.ui.language_change_mixin import LanguageChangeMixin
from src.ui.widgets.catalogue_item_delegate import (
    ROLE_IS_ACTIVE,
    ROLE_MOD_ID,
    ROLE_MOD_REF,
    ROLE_PIXMAP,
    ROLE_STATUS_ENTRIES,
    ROLE_TITLE,
    CatalogueItemDelegate,
)
from src.utils import markup_parser


class CatalogueWidget(LanguageChangeMixin, QWidget):
    """
    Widget displaying the catalogue of available mods (Local + Workshop).
    """

    selection_changed = Signal()
    context_menu_requested = Signal(object)
    mod_double_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._catalogue_items: list[ModState] = []
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setProperty("uiRole", "sectionTitle")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        self.count_label = QLabel()
        self.count_label.setProperty("uiRole", "sectionMeta")
        header_layout.addWidget(self.count_label)
        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._apply_filters)
        self.search_bar.setAccessibleName("catalogueSearch")
        search_layout.addWidget(self.search_bar)

        self.btn_toggle_view = QPushButton()
        self.btn_toggle_view.setProperty("uiRole", "compactAction")
        self.btn_toggle_view.setCheckable(True)
        self.btn_toggle_view.setChecked(True)
        self.btn_toggle_view.toggled.connect(self._on_toggle_view)
        self.btn_toggle_view.setAccessibleName("catalogueToggleThumbnails")
        search_layout.addWidget(self.btn_toggle_view)

        layout.addLayout(search_layout)

        self.tab_bar = QTabBar()
        self.tab_bar.addTab("")
        self.tab_bar.addTab("")
        self.tab_bar.addTab("")
        self.tab_bar.currentChanged.connect(self._apply_filters)
        self.tab_bar.setAccessibleName("catalogueSourceTabs")
        layout.addWidget(self.tab_bar)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.setMouseTracking(True)
        self.list_widget.setAccessibleName("catalogueList")
        self.list_widget.itemSelectionChanged.connect(self.selection_changed.emit)
        self.list_widget.customContextMenuRequested.connect(
            self.context_menu_requested.emit
        )
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._delegate = CatalogueItemDelegate(self.list_widget, thumbnail_enabled=True)
        self.list_widget.setItemDelegate(self._delegate)
        layout.addWidget(self.list_widget)

        self.empty_label = QLabel(self.list_widget.viewport())
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setProperty("uiRole", "emptyState")
        self.empty_label.hide()

    def _on_toggle_view(self, checked: bool):
        self._delegate.set_thumbnail_enabled(checked)
        self.list_widget.doItemsLayout()
        self.list_widget.viewport().update()

    def populate(self, catalogue_state: CatalogueState):
        """
        Saves the provided catalogue state and applies current filters.
        """
        self._catalogue_items = sorted(
            catalogue_state.items,
            key=lambda m: markup_parser.strip_markup(m.name).lower(),
        )
        self._apply_filters()

    def refresh_icons(self):
        self._delegate.clear_icon_cache()
        self.list_widget.viewport().update()

    def retranslate_ui(self):
        self.title_label.setText(self.tr("Catalogue (Available Mods)"))
        self.search_bar.setPlaceholderText(self.tr("Search mods..."))
        self.search_bar.setToolTip(
            self.tr(
                "Search by name, id, tags, dependencies, or source."
                " Examples: id:123, tag:ui, dep:mod_x, source:local."
            )
        )
        self.search_bar.setAccessibleDescription(
            self.tr(
                "Search by name, id, tags, dependencies, or source."
                " Examples: id:123, tag:ui, dep:mod_x, source:local."
            )
        )
        self.btn_toggle_view.setText(self.tr("Thumbnails"))
        self.btn_toggle_view.setAccessibleDescription(
            self.tr("Toggle thumbnail previews in the catalogue list.")
        )
        self.tab_bar.setTabText(0, self.tr("All"))
        self.tab_bar.setTabText(1, self.tr("Workshop"))
        self.tab_bar.setTabText(2, self.tr("Local"))
        self.tab_bar.setAccessibleDescription(
            self.tr("Filter the catalogue by source.")
        )
        self.list_widget.setAccessibleDescription(
            self.tr("List of available mods in the catalogue.")
        )
        self._apply_filters()

    def _apply_filters(self):
        selected_mod_refs = set(self.get_selected_mod_refs())
        self.list_widget.clear()
        search_text = self.search_bar.text().lower()
        current_tab = self.tab_bar.currentIndex()
        visible_count = 0

        for mod in self._catalogue_items:
            if current_tab == 1 and mod.is_local:
                continue
            if current_tab == 2 and not mod.is_local:
                continue

            if not self._matches_search(mod, search_text):
                continue

            clean_name = markup_parser.strip_markup(mod.name)
            tooltip = self._build_tooltip(mod)
            if mod.is_active:
                tooltip = self.tr("{0}\nAlready active in the load order.").format(
                    tooltip
                )

            item = QListWidgetItem(clean_name)
            item.setToolTip(tooltip)
            item.setData(ROLE_MOD_ID, mod.id)
            item.setData(ROLE_MOD_REF, to_reference_key(mod.id, mod.is_local))
            item.setData(ROLE_TITLE, clean_name)
            item.setData(ROLE_PIXMAP, self._build_thumbnail_pixmap(mod))
            item.setData(ROLE_STATUS_ENTRIES, self._build_status_entries(mod))
            item.setData(ROLE_IS_ACTIVE, mod.is_active)
            self.list_widget.addItem(item)
            visible_count += 1

            mod_ref = item.data(ROLE_MOD_REF)
            if mod_ref in selected_mod_refs:
                item.setSelected(True)

        self._update_header(visible_count)
        self._update_empty_state(visible_count, search_text, current_tab)

    def _update_header(self, visible_count: int):
        total_count = len(self._catalogue_items)
        if visible_count == total_count:
            self.count_label.setText(self.tr("{0} mods").format(total_count))
            return
        self.count_label.setText(
            self.tr("{visible} of {total} mods").format(
                visible=visible_count,
                total=total_count,
            )
        )

    def _update_empty_state(self, visible_count: int, search_text: str, tab_index: int):
        has_filters = bool(search_text) or tab_index != 0
        is_empty = visible_count == 0
        self.empty_label.setVisible(is_empty)
        if is_empty:
            self.empty_label.raise_()
        self._position_empty_label()

        if not is_empty:
            return

        if self._catalogue_items and has_filters:
            self.empty_label.setText(self.tr("No mods match the current filters."))
            return

        self.empty_label.setText(
            self.tr("No mods found. Configure your paths, then refresh the catalogue.")
        )
        self._position_empty_label()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_empty_label()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._position_empty_label)

    def _position_empty_label(self):
        self.empty_label.setGeometry(self.list_widget.viewport().rect())

    def _build_thumbnail_pixmap(self, mod: ModState) -> QPixmap | None:
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

    def _build_tooltip(self, mod: ModState) -> str:
        tooltip_lines = [
            self.tr("Local Mod") if mod.is_local else self.tr("Workshop Mod")
        ]
        missing_dependencies = mod.missing_dependencies

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

    def _build_status_entries(self, mod: ModState) -> list[dict[str, str]]:
        if not mod.dependencies:
            return []

        missing_dependencies = mod.missing_dependencies
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

    def _matches_search(self, mod: ModState, query: str) -> bool:
        if not query:
            return True

        parsed = self._parse_search_query(query)
        source = "local" if mod.is_local else "workshop"

        if parsed["source"] and source not in parsed["source"]:
            return False

        if parsed["id"] and not all(term in mod.id.lower() for term in parsed["id"]):
            return False

        tags_lower = [tag.lower() for tag in mod.tags]
        if parsed["tag"] and not all(
            any(term in tag for tag in tags_lower) for term in parsed["tag"]
        ):
            return False

        dependencies_lower = [dep.lower() for dep in mod.dependencies]
        if parsed["dep"] and not all(
            any(term in dep for dep in dependencies_lower) for term in parsed["dep"]
        ):
            return False

        searchable = " ".join(
            [
                markup_parser.strip_markup(mod.name).lower(),
                mod.id.lower(),
                " ".join(tags_lower),
                " ".join(dependencies_lower),
                source,
            ]
        )
        return all(term in searchable for term in parsed["terms"])

    @staticmethod
    def _parse_search_query(query: str) -> dict[str, list[str]]:
        parsed: dict[str, list[str]] = {
            "terms": [],
            "id": [],
            "tag": [],
            "dep": [],
            "source": [],
        }
        for raw_token in query.split():
            token = raw_token.strip().lower()
            if not token:
                continue

            if ":" not in token:
                parsed["terms"].append(token)
                continue

            key, value = token.split(":", 1)
            if not value:
                continue
            if key in {"id", "tag", "dep", "source"}:
                parsed[key].append(value)
            else:
                parsed["terms"].append(token)
        return parsed

    def get_mod_id_at(self, pos) -> str | None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return None
        return item.data(ROLE_MOD_ID)

    def get_mod_ref_at(self, pos) -> str | None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return None
        return item.data(ROLE_MOD_REF)

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

    def get_selected_mod_ids(self) -> list[str]:
        return [item.data(ROLE_MOD_ID) for item in self.list_widget.selectedItems()]

    def get_selected_mod_ref(self) -> str | None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(ROLE_MOD_REF)

    def get_selected_mod_refs(self) -> list[str]:
        return [item.data(ROLE_MOD_REF) for item in self.list_widget.selectedItems()]

    def _on_item_double_clicked(self, _item):
        self.mod_double_clicked.emit()
