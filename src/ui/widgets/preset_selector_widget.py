from typing import List

import qtawesome as qta
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from src.ui.appearance_manager import AppearanceManager


class PresetSelectorWidget(QWidget):
    """
    Widget allowing the user to select, save, and delete load order presets.
    Sits above the active mods list.
    """

    # Signals emitted to the parent/controller
    preset_applied = Signal(str)
    save_requested = Signal(str)  # Passes the name of the preset to overwrite
    save_as_requested = Signal()  # Emitted when creating a new preset
    delete_requested = Signal(str)  # Passes the name of the preset to delete

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_unsaved = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)  # Add a little bottom margin

        self.label = QLabel(self.tr("Preset:"))
        layout.addWidget(self.label)

        self.combo = QComboBox()
        self.combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        layout.addWidget(self.combo, stretch=1)

        # Action Buttons
        self.btn_save = QPushButton()
        self.btn_save.setToolTip(self.tr("Save current load order to this preset"))
        self.btn_save.setFixedWidth(30)
        layout.addWidget(self.btn_save)

        self.btn_save_as = QPushButton()
        self.btn_save_as.setToolTip(self.tr("Save as new preset"))
        self.btn_save_as.setFixedWidth(30)
        layout.addWidget(self.btn_save_as)

        self.btn_delete = QPushButton()
        self.btn_delete.setToolTip(self.tr("Delete this preset"))
        self.btn_delete.setFixedWidth(30)
        layout.addWidget(self.btn_delete)
        self.refresh_icons()

    def _connect_signals(self):
        # We use 'activated' rather than 'currentIndexChanged' so it only fires
        # on user interaction, not when we programmatically populate the combobox.
        self.combo.activated.connect(self._on_preset_selected)

        self.btn_save.clicked.connect(self._on_save_clicked)
        self.btn_save_as.clicked.connect(self.save_as_requested.emit)
        self.btn_delete.clicked.connect(self._on_delete_clicked)

    def set_unsaved_state(self, is_unsaved: bool):
        """
        Visually updates the save button to indicate unsaved changes.
        """
        self._is_unsaved = is_unsaved
        if is_unsaved:
            self.btn_save.setToolTip(
                self.tr("Save current load order to this preset (Unsaved changes)")
            )
        else:
            self.btn_save.setToolTip(self.tr("Save current load order to this preset"))
        self.refresh_icons()

    def refresh_icons(self):
        icon_colors = AppearanceManager.get_icon_colors(self)
        if self._is_unsaved:
            self.btn_save.setIcon(qta.icon("fa5s.save", color="#e67e22"))
        else:
            self.btn_save.setIcon(qta.icon("fa5s.save", **icon_colors))
        self.btn_save_as.setIcon(qta.icon("fa5s.plus", **icon_colors))
        self.btn_delete.setIcon(qta.icon("fa5s.trash", **icon_colors))

    def populate(self, preset_names: List[str], current: str = ""):
        """
        Populates the combobox with available presets.
        """
        self.combo.blockSignals(True)
        self.combo.clear()

        # Always provide a fallback "Unsaved / Custom" entry at index 0
        self.combo.addItem(self.tr("-- Custom Load Order --"))
        self.combo.addItems(preset_names)

        if current:
            self.set_current_preset(current)
        else:
            self.combo.setCurrentIndex(0)

        self.combo.blockSignals(False)
        self._update_buttons()

    def set_current_preset(self, name: str):
        """
        Visually sets the combobox to a specific preset name.
        """
        self.combo.blockSignals(True)
        index = self.combo.findText(name)
        if index >= 0:
            self.combo.setCurrentIndex(index)
        else:
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
        self._update_buttons()

    def _on_preset_selected(self, index: int):
        self._update_buttons()
        if index > 0:
            preset_name = self.combo.itemText(index)
            self.preset_applied.emit(preset_name)

    def _on_save_clicked(self):
        if self.combo.currentIndex() > 0:
            self.save_requested.emit(self.combo.currentText())

    def _on_delete_clicked(self):
        if self.combo.currentIndex() > 0:
            self.delete_requested.emit(self.combo.currentText())

    def _update_buttons(self):
        """
        Disables Save and Delete buttons if the user is on the "-- Custom --" fallback item.
        """
        is_preset = self.combo.currentIndex() > 0
        self.btn_save.setEnabled(is_preset)
        self.btn_delete.setEnabled(is_preset)
        if not is_preset:
            self.set_unsaved_state(False)
