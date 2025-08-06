import re
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.views.ui.main_window import Ui_MainWindow


class ModManagerView(QMainWindow):
    """Main view for the mod manager application."""

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.listWidget_available_mods.setContextMenuPolicy(Qt.CustomContextMenu)

    # Dialog methods
    def ask_confirmation(
        self,
        title: str,
        text: str,
        default: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
    ) -> bool:
        """Show a confirmation dialog and return True if Yes is selected."""
        result = QMessageBox.question(
            self,
            title,
            text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            default,
        )
        return result == QMessageBox.StandardButton.Yes

    def show_message(
        self,
        title: str,
        text: str,
        icon: str = "information",
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
        default_button: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> int:
        """Show a message dialog with the specified parameters."""
        icon_map = {
            "information": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
        }

        message_box = QMessageBox(self)
        message_box.setIcon(icon_map.get(icon.lower(), QMessageBox.Icon.Information))
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setStandardButtons(buttons)
        message_box.setDefaultButton(default_button)
        return message_box.exec()

    # Mod list operations
    def clear_mod_lists(self):
        """Clear both available and active mod lists."""
        self.ui.listWidget_available_mods.clear()
        self.ui.listWidget_active_mods.clear()

    def populate_mod_lists(self, available_mods: List[Mod], active_mods: List[Mod]):
        """Populate both mod lists with the provided data."""
        self.clear_mod_lists()

        for mod in available_mods:
            self._add_mod_to_available(mod)

        for mod in active_mods:
            self._add_mod_to_active(mod)

    # Active mod management
    def get_active_mods_order(self) -> List[Mod]:
        """Get the current order of active mods."""
        mods = []
        for i in range(self.ui.listWidget_active_mods.count()):
            item = self.ui.listWidget_active_mods.item(i)
            mod = item.data(Qt.UserRole)
            if mod:
                mods.append(mod)
        return mods

    def move_active_mod_up(self) -> bool:
        """Move the selected active mod up in the list."""
        return self._move_active_mod(-1)

    def move_active_mod_down(self) -> bool:
        """Move the selected active mod down in the list."""
        return self._move_active_mod(1)

    # Selection getters
    def get_current_active_mod(self) -> List[QListWidgetItem]:
        """Get currently selected active mod items."""
        return self.ui.listWidget_active_mods.selectedItems()

    def get_current_available_mod(self) -> List[QListWidgetItem]:
        """Get currently selected available mod items."""
        return self.ui.listWidget_available_mods.selectedItems()

    # UI update methods
    def update_active_mods_count(self, count: int):
        """Update the active mods count label."""
        self.ui.label_mod_count.setText(f"{count} mods")

    def update_mod_details(self, mod: Optional[Mod]):
        """Update the mod details display."""
        if mod:
            self.ui.label_mod_name.setTextFormat(Qt.RichText)
            self.ui.label_mod_name.setText(
                self.parse_formatted_text(mod.name) + " [" + mod.id + "]"
            )
            self.ui.textEdit_mod_description.setText(
                self.parse_formatted_text(mod.desc)
            )
        else:
            self.ui.label_mod_name.setTextFormat(Qt.PlainText)
            self.ui.label_mod_name.setText("No mod selected")
            self.ui.textEdit_mod_description.clear()

    # Preset management
    def get_current_preset_name(self) -> str:
        """Get the currently selected preset name."""
        return self.ui.comboBox_presets.currentText()

    def update_presets(self, preset_names: List[str], current_selection: str = ""):
        """Update the presets combobox with sorted names."""
        self.ui.comboBox_presets.clear()

        sorted_names = sorted(preset_names)
        self.ui.comboBox_presets.addItems(sorted_names)

        if current_selection and current_selection in sorted_names:
            index = self.ui.comboBox_presets.findText(current_selection)
            if index >= 0:
                self.ui.comboBox_presets.setCurrentIndex(index)

    # Static utility methods
    @staticmethod
    def set_font(font: QFont):
        """Set the application font."""
        QApplication.setFont(font)

    @staticmethod
    def parse_formatted_text(text: str) -> str:
        """Parse custom formatted text to HTML."""

        # Convert custom color tags to HTML spans
        text = re.sub(
            r"<c\(([0-9A-Fa-f]{6})\)>(.*?)</c>|<c\(([0-9A-Fa-f]{6})\)>(.*)",
            lambda m: (
                f'<span style="color:#{m.group(1)}">{m.group(2)}</span>'
                if m.group(1)
                else f'<span style="color:#{m.group(3)}">{m.group(4)}</span>'
            ),
            text,
        )

        # Handle unicode escape sequences and line breaks
        if re.search(r"(\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|\\n)", text):
            try:
                text = bytes(text, "utf-8").decode("unicode_escape")
            except Exception:
                pass

        text = text.replace("\n", "<br>")
        return text

    @staticmethod
    def parse_clear_text(text: str) -> str:
        """Remove custom formatting tags and return plain text."""

        text = re.sub(
            r"<c\([0-9A-Fa-f]{6}\)>(.*?)</c>",
            r"\1",
            text,
        )

        text = re.sub(
            r"<c\([0-9A-Fa-f]{6}\)>",
            "",
            text,
        )

        if re.search(r"(\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|\\n)", text):
            try:
                text = bytes(text, "utf-8").decode("unicode_escape")
            except Exception:
                pass

        return text

    # Private helper methods
    def _move_active_mod(self, direction: int) -> bool:
        """Move the selected active mod in the specified direction (-1 for up, 1 for down)."""
        item = self.ui.listWidget_active_mods.currentItem()
        if not item:
            return False

        row = self.ui.listWidget_active_mods.row(item)
        new_row = row + direction

        # Check bounds
        if new_row < 0 or new_row >= self.ui.listWidget_active_mods.count():
            return False

        # Move item
        self.ui.listWidget_active_mods.takeItem(row)
        self.ui.listWidget_active_mods.insertItem(new_row, item)
        self.ui.listWidget_active_mods.setCurrentItem(item)
        return True

    def _add_mod_to_active(self, mod: Mod):
        """Add a mod to the active mods list."""
        self._add_mod_to_list(self.ui.listWidget_active_mods, mod)

    def _add_mod_to_available(self, mod: Mod):
        """Add a mod to the available mods list."""
        self._add_mod_to_list(self.ui.listWidget_available_mods, mod, mod.manualInstall)

    def _add_mod_to_list(self, list_widget, mod: Mod, bold: bool = False):
        clear_name = self.parse_clear_text(mod.name)

        item = QListWidgetItem(clear_name)
        item.setData(Qt.UserRole, mod)

        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        list_widget.addItem(item)
