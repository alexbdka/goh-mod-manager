import qtawesome as qta
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from src.application.state import ActiveModsState, ModState
from src.core.mod_reference import to_reference_key
from src.ui.appearance_manager import AppearanceManager
from src.ui.language_change_mixin import LanguageChangeMixin
from src.ui.widgets.active_mods_item_delegate import (
    ROLE_MOD_ID,
    ROLE_MOD_REF,
    ROLE_ORDER,
    ROLE_SOURCE,
    ROLE_TITLE,
    ActiveModsItemDelegate,
)
from src.ui.widgets.preset_selector_widget import PresetSelectorWidget
from src.utils import markup_parser


class InternalTree(QTreeWidget):
    order_dropped = Signal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.order_dropped.emit()


class ActiveModsWidget(LanguageChangeMixin, QWidget):
    """
    Widget displaying the currently active mods and their load order.
    It emits signals when the user wants to reorder or remove a mod.
    """

    move_up_requested = Signal(str)
    move_down_requested = Signal(str)
    clear_requested = Signal()
    order_changed = Signal(list)
    selection_changed = Signal()
    context_menu_requested = Signal(object)
    mod_double_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_mods: list[ModState] = []
        self._setup_ui()
        self._connect_signals()
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

        self.preset_selector = PresetSelectorWidget()
        layout.addWidget(self.preset_selector)

        self.list_widget = InternalTree(self)
        self.list_widget.setColumnCount(1)
        self.list_widget.setHeaderHidden(True)
        self.list_widget.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setAlternatingRowColors(False)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.setItemDelegate(ActiveModsItemDelegate(self.list_widget))
        self.list_widget.setAccessibleName("activeModsList")
        layout.addWidget(self.list_widget)

        self.empty_label = QLabel(self.list_widget.viewport())
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setProperty("uiRole", "emptyState")
        self.empty_label.hide()

        buttons_layout = QHBoxLayout()
        self.btn_up = QPushButton()
        self.btn_down = QPushButton()
        self.btn_clear = QPushButton()
        self.btn_up.setProperty("uiRole", "compactAction")
        self.btn_down.setProperty("uiRole", "compactAction")
        self.btn_clear.setProperty("uiRole", "compactAction")
        self.btn_up.setAccessibleName("activeModsMoveUp")
        self.btn_down.setAccessibleName("activeModsMoveDown")
        self.btn_clear.setAccessibleName("activeModsClear")
        buttons_layout.addWidget(self.btn_up)
        buttons_layout.addWidget(self.btn_down)
        buttons_layout.addWidget(self.btn_clear)
        layout.addLayout(buttons_layout)
        self.refresh_icons()

    def _connect_signals(self):
        self.btn_up.clicked.connect(self._on_move_up)
        self.btn_down.clicked.connect(self._on_move_down)
        self.btn_clear.clicked.connect(self._on_clear)
        self.list_widget.order_dropped.connect(self._on_reorder)
        self.list_widget.itemSelectionChanged.connect(self.selection_changed.emit)
        self.list_widget.customContextMenuRequested.connect(
            self.context_menu_requested.emit
        )
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

    def populate(self, active_mods_state: ActiveModsState):
        """
        Clears the current list and populates it with the provided active mods state.
        The order of the list matters.
        """
        self._current_mods = list(active_mods_state.items)
        self.list_widget.clear()

        for i, mod in enumerate(self._current_mods):
            clean_name = markup_parser.strip_markup(mod.name)
            order_text = str(mod.load_order if mod.load_order is not None else i + 1)
            item = QTreeWidgetItem([clean_name])
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            source_text = (
                self.tr("Local Mod") if mod.is_local else self.tr("Workshop Mod")
            )
            item.setData(0, ROLE_MOD_ID, mod.id)
            item.setData(0, ROLE_MOD_REF, to_reference_key(mod.id, mod.is_local))
            item.setData(0, ROLE_ORDER, order_text)
            item.setData(0, ROLE_TITLE, clean_name)
            item.setData(0, ROLE_SOURCE, source_text)
            item.setToolTip(0, source_text)

            self.list_widget.addTopLevelItem(item)

        self._update_header()
        self._update_empty_state()

    def get_selected_mod_id(self) -> str | None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(0, ROLE_MOD_ID)

    def get_mod_id_at(self, pos) -> str | None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return None
        return item.data(0, ROLE_MOD_ID)

    def get_mod_ref_at(self, pos) -> str | None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return None
        return item.data(0, ROLE_MOD_REF)

    def get_selected_mod_ref(self) -> str | None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(0, ROLE_MOD_REF)

    def clear_selection(self):
        self.list_widget.clearSelection()

    def block_list_signals(self, block: bool):
        return self.list_widget.blockSignals(block)

    def map_list_pos_to_global(self, pos):
        return self.list_widget.viewport().mapToGlobal(pos)

    def _on_move_up(self):
        mod_ref = self.get_selected_mod_ref()
        if mod_ref:
            self.move_up_requested.emit(mod_ref)

    def _on_move_down(self):
        mod_ref = self.get_selected_mod_ref()
        if mod_ref:
            self.move_down_requested.emit(mod_ref)

    def _on_clear(self):
        self.clear_requested.emit()

    def _on_item_double_clicked(self, item, _column):
        mod_ref = item.data(0, ROLE_MOD_REF)
        if mod_ref:
            self.mod_double_clicked.emit(mod_ref)

    def _on_reorder(self):
        new_order = []
        for i in range(self.list_widget.topLevelItemCount()):
            item = self.list_widget.topLevelItem(i)
            if item is None:
                continue
            item.setData(0, ROLE_ORDER, str(i + 1))
            mod_ref = item.data(0, ROLE_MOD_REF)
            if mod_ref:
                new_order.append(mod_ref)
        self.order_changed.emit(new_order)

    def retranslate_ui(self):
        self.title_label.setText(self.tr("Load Order (Active Mods)"))
        self.btn_up.setToolTip(self.tr("Move selected mod up"))
        self.btn_down.setToolTip(self.tr("Move selected mod down"))
        self.btn_clear.setToolTip(self.tr("Clear active load order"))
        self.btn_up.setAccessibleDescription(self.tr("Move the selected mod up."))
        self.btn_down.setAccessibleDescription(self.tr("Move the selected mod down."))
        self.btn_clear.setAccessibleDescription(self.tr("Remove all active mods."))
        self.list_widget.setAccessibleDescription(
            self.tr("List of active mods in load order.")
        )
        self._update_header()
        self._update_empty_state()
        if self._current_mods:
            self.populate(ActiveModsState(items=self._current_mods))

    def _update_header(self):
        self.count_label.setText(self.tr("{0} active").format(len(self._current_mods)))

    def _update_empty_state(self):
        is_empty = len(self._current_mods) == 0
        self.empty_label.setVisible(is_empty)
        if is_empty:
            self.empty_label.raise_()
        self.empty_label.setText(
            self.tr(
                "No active mods yet. Add mods from the catalogue to build a load order."
            )
        )
        self._position_empty_label()
        self.btn_up.setEnabled(not is_empty)
        self.btn_down.setEnabled(not is_empty)
        self.btn_clear.setEnabled(not is_empty)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_empty_label()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._position_empty_label)

    def _position_empty_label(self):
        self.empty_label.setGeometry(self.list_widget.viewport().rect())

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors(self)
        self.btn_up.setIcon(qta.icon("fa5s.arrow-up", **icon_colors))
        self.btn_down.setIcon(qta.icon("fa5s.arrow-down", **icon_colors))
        self.btn_clear.setIcon(qta.icon("fa5s.trash", **icon_colors))
