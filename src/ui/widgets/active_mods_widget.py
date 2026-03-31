from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.core.mod import ModInfo
from src.ui.widgets.preset_selector_widget import PresetSelectorWidget
from src.utils import markup_parser


class ActiveModsWidget(QWidget):
    """
    Widget displaying the currently active mods and their load order.
    It emits signals when the user wants to reorder or remove a mod.
    """

    # Signals to communicate with the main window / controller
    move_up_requested = Signal(str)
    move_down_requested = Signal(str)
    clear_requested = Signal()
    order_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.title_label = QLabel(self.tr("Load Order (Active Mods)"))
        self.title_label.setObjectName("SectionTitle")
        layout.addWidget(self.title_label)

        # Preset Selector
        self.preset_selector = PresetSelectorWidget()
        layout.addWidget(self.preset_selector)

        # List
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.list_widget)

        # Controls
        buttons_layout = QHBoxLayout()

        self.btn_up = QPushButton(self.tr("Move Up"))
        self.btn_down = QPushButton(self.tr("Move Down"))
        self.btn_clear = QPushButton(self.tr("Clear"))

        buttons_layout.addWidget(self.btn_up)
        buttons_layout.addWidget(self.btn_down)
        buttons_layout.addWidget(self.btn_clear)

        layout.addLayout(buttons_layout)

    def _connect_signals(self):
        self.btn_up.clicked.connect(self._on_move_up)
        self.btn_down.clicked.connect(self._on_move_down)
        self.btn_clear.clicked.connect(self._on_clear)
        self.list_widget.model().rowsMoved.connect(self._on_rows_moved)

    def populate(self, mods: List[ModInfo]):
        """
        Clears the current list and populates it with the provided active mods.
        The order of the list matters.
        """
        self.list_widget.clear()

        for i, mod in enumerate(mods):
            # Display load order index + name
            clean_name = markup_parser.strip_markup(mod.name)
            display_text = f"{i + 1}. {clean_name}"
            item = QListWidgetItem(display_text)

            # Store the underlying mod ID to easily retrieve it later
            item.setData(Qt.ItemDataRole.UserRole, mod.id)
            if mod.isLocal:
                item.setToolTip(self.tr("Local Mod"))
            else:
                item.setToolTip(self.tr("Workshop Mod"))

            self.list_widget.addItem(item)

    def get_selected_mod_id(self) -> str | None:
        """
        Returns the ID of the currently selected mod, or None if nothing is selected.
        """
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return None
        return selected_items[0].data(Qt.ItemDataRole.UserRole)

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

    def _on_rows_moved(self, parent, start, end, destination, row):
        new_order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            mod_id = item.data(Qt.ItemDataRole.UserRole)
            if mod_id:
                new_order.append(mod_id)
        self.order_changed.emit(new_order)
