from typing import List

from PySide6.QtCore import Qt, Signal
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

from src.core.mod import ModInfo
from src.ui.widgets.preset_selector_widget import PresetSelectorWidget
from src.utils import markup_parser


class InternalTree(QTreeWidget):
    order_dropped = Signal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.order_dropped.emit()


class ActiveModsWidget(QWidget):
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
        self._current_mods: List[ModInfo] = []
        self._setup_ui()
        self._connect_signals()
        self.retranslate_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel()
        layout.addWidget(self.title_label)

        self.preset_selector = PresetSelectorWidget()
        layout.addWidget(self.preset_selector)

        self.list_widget = InternalTree(self)
        self.list_widget.setColumnCount(2)
        self.list_widget.setHeaderLabels(["", ""])
        self.list_widget.header().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.list_widget.header().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.list_widget.setRootIsDecorated(False)
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()
        self.btn_up = QPushButton()
        self.btn_down = QPushButton()
        self.btn_clear = QPushButton()
        buttons_layout.addWidget(self.btn_up)
        buttons_layout.addWidget(self.btn_down)
        buttons_layout.addWidget(self.btn_clear)
        layout.addLayout(buttons_layout)

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

    def populate(self, mods: List[ModInfo]):
        """
        Clears the current list and populates it with the provided active mods.
        The order of the list matters.
        """
        self._current_mods = list(mods)
        self.list_widget.clear()

        for i, mod in enumerate(mods):
            clean_name = markup_parser.strip_markup(mod.name)
            item = QTreeWidgetItem([str(i + 1), clean_name])
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
            item.setData(0, Qt.ItemDataRole.UserRole, mod.id)
            if mod.isLocal:
                item.setToolTip(1, self.tr("Local Mod"))
            else:
                item.setToolTip(1, self.tr("Workshop Mod"))

            self.list_widget.addTopLevelItem(item)

    def get_selected_mod_id(self) -> str | None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(0, Qt.ItemDataRole.UserRole)

    def get_mod_id_at(self, pos) -> str | None:
        item = self.list_widget.itemAt(pos)
        if item is None:
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    def clear_selection(self):
        self.list_widget.clearSelection()

    def block_list_signals(self, block: bool):
        return self.list_widget.blockSignals(block)

    def map_list_pos_to_global(self, pos):
        return self.list_widget.viewport().mapToGlobal(pos)

    def _on_move_up(self):
        mod_id = self.get_selected_mod_id()
        if mod_id:
            self.move_up_requested.emit(mod_id)

    def _on_move_down(self):
        mod_id = self.get_selected_mod_id()
        if mod_id:
            self.move_down_requested.emit(mod_id)

    def _on_clear(self):
        self.clear_requested.emit()

    def _on_item_double_clicked(self, item, _column):
        mod_id = item.data(0, Qt.ItemDataRole.UserRole)
        if mod_id:
            self.mod_double_clicked.emit(mod_id)

    def _on_reorder(self):
        new_order = []
        for i in range(self.list_widget.topLevelItemCount()):
            item = self.list_widget.topLevelItem(i)
            item.setText(0, str(i + 1))
            mod_id = item.data(0, Qt.ItemDataRole.UserRole)
            if mod_id:
                new_order.append(mod_id)
        self.order_changed.emit(new_order)

    def retranslate_ui(self):
        self.title_label.setText(self.tr("Load Order (Active Mods)"))
        self.list_widget.setHeaderLabels([self.tr("Order"), self.tr("Mod Name")])
        self.btn_up.setText(self.tr("Move Up"))
        self.btn_down.setText(self.tr("Move Down"))
        self.btn_clear.setText(self.tr("Clear"))
        self.preset_selector.retranslate_ui()
        if self._current_mods:
            self.populate(self._current_mods)
