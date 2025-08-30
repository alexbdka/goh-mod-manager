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
    """
    Main view for the Gates of Hell mod manager application.

    Handles UI interactions, mod list management, and user dialogs.
    Provides methods for updating displays and managing mod selection.
    """

    def __init__(self):
        """Initialize the main window and UI components."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Enable custom context menus for the available mods list
        self.ui.listWidget_available_mods.setContextMenuPolicy(Qt.CustomContextMenu)

    # ================== DIALOG METHODS ==================

    def ask_confirmation(
        self,
        title: str,
        text: str,
        default: QMessageBox.StandardButton = QMessageBox.StandardButton.No,
    ) -> bool:
        """
        Display a confirmation dialog with Yes/No options.

        Args:
            title: Dialog window title
            text: Message text to display
            default: Default button selection

        Returns:
            True if user clicks Yes, False otherwise
        """
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
        """
        Display a message dialog with customizable appearance.

        Args:
            title: Dialog window title
            text: Message text to display
            icon: Icon type ("information" or "warning")
            buttons: Available buttons
            default_button: Default button selection

        Returns:
            Button code of the clicked button
        """
        icon_map = {
            "information": QMessageBox.Icon.Information,
            "warning": QMessageBox.Icon.Warning,
            "error": QMessageBox.Icon.Critical,
            "question": QMessageBox.Icon.Question,
        }

        message_box = QMessageBox(self)
        message_box.setIcon(icon_map.get(icon.lower(), QMessageBox.Icon.Information))
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setStandardButtons(buttons)
        message_box.setDefaultButton(default_button)
        return message_box.exec()

    def show_error(self, title: str, text: str) -> int:
        """
        Display an error message dialog.

        Args:
            title: Dialog window title
            text: Error message text

        Returns:
            Button code of the clicked button
        """
        return self.show_message(title, text, icon="error")

    # ================== MOD LIST OPERATIONS ==================

    def clear_mod_lists(self) -> None:
        """Clear both available and active mod lists."""
        self.ui.listWidget_available_mods.clear()
        self.ui.listWidget_active_mods.clear()

    def populate_mod_lists(
        self, available_mods: List[Mod], active_mods: List[Mod]
    ) -> None:
        """
        Populate both mod lists with provided data.

        Args:
            available_mods: List of all available/installed mods
            active_mods: List of currently active mods in load order
        """
        self.clear_mod_lists()

        # Add available mods (highlight manually installed ones)
        for mod in available_mods:
            self._add_mod_to_available(mod)

        # Add active mods in order
        for mod in active_mods:
            self._add_mod_to_active(mod)

    def refresh_available_mods(self, available_mods: List[Mod]) -> None:
        """
        Refresh only the available mods list while preserving selection.

        Args:
            available_mods: Updated list of available mods
        """
        current_selection = self.get_selected_available_mod_ids()

        self.ui.listWidget_available_mods.clear()
        for mod in available_mods:
            self._add_mod_to_available(mod)

        # Restore selection if possible
        self._restore_available_selection(current_selection)

    def refresh_active_mods(self, active_mods: List[Mod]) -> None:
        """
        Refresh only the active mods list while preserving selection.

        Args:
            active_mods: Updated list of active mods
        """
        current_selection = self.get_selected_active_mod_ids()

        self.ui.listWidget_active_mods.clear()
        for mod in active_mods:
            self._add_mod_to_active(mod)

        # Restore selection if possible
        self._restore_active_selection(current_selection)

    # ================== ACTIVE MOD MANAGEMENT ==================

    def get_active_mods_order(self) -> List[Mod]:
        """
        Get the current order of active mods from the UI list.

        Returns:
            List of mods in their current display order
        """
        mods = []
        for i in range(self.ui.listWidget_active_mods.count()):
            item = self.ui.listWidget_active_mods.item(i)
            mod = item.data(Qt.UserRole)
            if mod:
                mods.append(mod)
        return mods

    def move_active_mod_up(self) -> bool:
        """
        Move the selected active mod up one position.

        Returns:
            True if mod was moved successfully
        """
        return self._move_active_mod(-1)

    def move_active_mod_down(self) -> bool:
        """
        Move the selected active mod down one position.

        Returns:
            True if mod was moved successfully
        """
        return self._move_active_mod(1)

    def can_move_active_mod_up(self) -> bool:
        """Check if the selected active mod can be moved up."""
        current_item = self.ui.listWidget_active_mods.currentItem()
        if not current_item:
            return False
        return self.ui.listWidget_active_mods.row(current_item) > 0

    def can_move_active_mod_down(self) -> bool:
        """Check if the selected active mod can be moved down."""
        current_item = self.ui.listWidget_active_mods.currentItem()
        if not current_item:
            return False
        current_row = self.ui.listWidget_active_mods.row(current_item)
        return current_row < self.ui.listWidget_active_mods.count() - 1

    # ================== SELECTION MANAGEMENT ==================

    def get_current_active_mod(self) -> List[QListWidgetItem]:
        """Get currently selected active mod items."""
        return self.ui.listWidget_active_mods.selectedItems()

    def get_current_available_mod(self) -> List[QListWidgetItem]:
        """Get currently selected available mod items."""
        return self.ui.listWidget_available_mods.selectedItems()

    def get_selected_available_mod_ids(self) -> List[str]:
        """Get IDs of currently selected available mods."""
        selected_ids = []
        for item in self.ui.listWidget_available_mods.selectedItems():
            mod = item.data(Qt.UserRole)
            if mod:
                selected_ids.append(mod.id)
        return selected_ids

    def get_selected_active_mod_ids(self) -> List[str]:
        """Get IDs of currently selected active mods."""
        selected_ids = []
        for item in self.ui.listWidget_active_mods.selectedItems():
            mod = item.data(Qt.UserRole)
            if mod:
                selected_ids.append(mod.id)
        return selected_ids

    def clear_selections(self) -> None:
        """Clear selections from both mod lists."""
        self.ui.listWidget_available_mods.clearSelection()
        self.ui.listWidget_active_mods.clearSelection()

    # ================== UI UPDATE METHODS ==================

    def update_active_mods_count(self, count: int) -> None:
        """
        Update the active mods count display label.

        Args:
            count: Number of active mods
        """
        if count <= 0:
            self.ui.label_mod_count.setText("No active mods")
        elif count == 1:
            self.ui.label_mod_count.setText("1 active mod")
        else:
            self.ui.label_mod_count.setText(f"{count} active mods")

    def update_mod_details(self, mod: Optional[Mod]) -> None:
        """
        Update the mod details panel with information from the selected mod.

        Args:
            mod: The mod to display details for, None to clear display
        """
        if mod:
            # Display mod name with ID and enable rich text formatting
            self.ui.label_mod_name.setTextFormat(Qt.RichText)
            formatted_name = self.parse_formatted_text(mod.name)
            self.ui.label_mod_name.setText(f"{formatted_name} [{mod.id}]")

            # Display mod description with formatting
            formatted_desc = self.parse_formatted_text(mod.desc)
            self.ui.textEdit_mod_description.setHtml(formatted_desc)
        else:
            # Clear display and switch to plain text
            self.ui.label_mod_name.setTextFormat(Qt.PlainText)
            self.ui.label_mod_name.setText("No mod selected")
            self.ui.textEdit_mod_description.clear()

    def update_window_title(self, title: str) -> None:
        """
        Update the main window title.

        Args:
            title: New window title
        """
        self.setWindowTitle(title)

    # ================== PRESET MANAGEMENT ==================

    def get_current_preset_name(self) -> str:
        """
        Get the name of the currently selected preset.

        Returns:
            Name of the selected preset, empty string if none selected
        """
        return self.ui.comboBox_presets.currentText()

    def update_presets(
        self, preset_names: List[str], current_selection: str = ""
    ) -> None:
        """
        Update the presets dropdown with available preset names.

        Args:
            preset_names: List of available preset names
            current_selection: Name of preset to select after update
        """
        # Store current selection if none specified
        if not current_selection:
            current_selection = self.ui.comboBox_presets.currentText()

        # Clear and repopulate with sorted names
        self.ui.comboBox_presets.clear()
        sorted_names = sorted(preset_names)
        self.ui.comboBox_presets.addItems(sorted_names)

        # Restore selection if it exists
        if current_selection and current_selection in sorted_names:
            index = self.ui.comboBox_presets.findText(current_selection)
            if index >= 0:
                self.ui.comboBox_presets.setCurrentIndex(index)

    def clear_preset_selection(self) -> None:
        """Clear the current preset selection."""
        self.ui.comboBox_presets.setCurrentIndex(-1)

    # ================== STATIC UTILITY METHODS ==================

    @staticmethod
    def set_application_font(font: QFont) -> None:
        """
        Set the application-wide font.

        Args:
            font: Font to apply to the entire application
        """
        QApplication.setFont(font)

    @staticmethod
    def parse_formatted_text(text: str) -> str:
        """
        Convert custom formatted text to HTML for display.

        Handles custom color tags and unicode escape sequences.

        Args:
            text: Text with custom formatting tags

        Returns:
            HTML-formatted text suitable for rich text display
        """
        if not text:
            return ""

        # Convert custom color tags to HTML spans
        # Handles both closed tags <c(RRGGBB)>text</c> and unclosed <c(RRGGBB)>text
        text = re.sub(
            r"<c\(([0-9A-Fa-f]{6})\)>(.*?)</c>|<c\(([0-9A-Fa-f]{6})\)>(.*)",
            lambda m: (
                f'<span style="color:#{m.group(1)}">{m.group(2)}</span>'
                if m.group(1) and m.group(2) is not None
                else f'<span style="color:#{m.group(3)}">{m.group(4)}</span>'
            ),
            text,
        )

        # Handle unicode escape sequences and line breaks
        if re.search(r"(\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|\\n)", text):
            try:
                text = bytes(text, "utf-8").decode("unicode_escape")
            except (UnicodeDecodeError, UnicodeError):
                # If decoding fails, keep original text
                pass

        # Convert line breaks to HTML
        text = text.replace("\n", "<br>")
        return text

    @staticmethod
    def parse_clear_text(text: str) -> str:
        """
        Remove custom formatting tags and return clean plain text.

        Args:
            text: Text with custom formatting tags

        Returns:
            Plain text with formatting tags removed
        """
        if not text:
            return ""

        # Remove closed color tags and keep content
        text = re.sub(
            r"<c\([0-9A-Fa-f]{6}\)>(.*?)</c>",
            r"\1",
            text,
        )

        # Remove unclosed color tags
        text = re.sub(
            r"<c\([0-9A-Fa-f]{6}\)>",
            "",
            text,
        )

        # Handle unicode escape sequences
        if re.search(r"(\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|\\n)", text):
            try:
                text = bytes(text, "utf-8").decode("unicode_escape")
            except (UnicodeDecodeError, UnicodeError):
                # If decoding fails, keep original text
                pass

        return text

    # ================== PRIVATE HELPER METHODS ==================

    def _move_active_mod(self, direction: int) -> bool:
        """
        Move the selected active mod in the specified direction.

        Args:
            direction: -1 for up, 1 for down

        Returns:
            True if mod was moved successfully
        """
        current_item = self.ui.listWidget_active_mods.currentItem()
        if not current_item:
            return False

        current_row = self.ui.listWidget_active_mods.row(current_item)
        new_row = current_row + direction

        # Check bounds
        if new_row < 0 or new_row >= self.ui.listWidget_active_mods.count():
            return False

        # Remove item from current position
        taken_item = self.ui.listWidget_active_mods.takeItem(current_row)

        # Insert at new position and maintain selection
        self.ui.listWidget_active_mods.insertItem(new_row, taken_item)
        self.ui.listWidget_active_mods.setCurrentItem(taken_item)

        return True

    def _add_mod_to_active(self, mod: Mod) -> None:
        """
        Add a mod to the active mods list.

        Args:
            mod: The mod to add to the active list
        """
        self._add_mod_to_list(self.ui.listWidget_active_mods, mod)

    def _add_mod_to_available(self, mod: Mod) -> None:
        """
        Add a mod to the available mods list.

        Args:
            mod: The mod to add to the available list
        """
        # Highlight manually installed mods with bold text
        self._add_mod_to_list(
            self.ui.listWidget_available_mods, mod, bold=mod.manualInstall
        )

    def _add_mod_to_list(self, list_widget, mod: Mod, bold: bool = False) -> None:
        """
        Add a mod to the specified list widget.

        Args:
            list_widget: The QListWidget to add the mod to
            mod: The mod to add
            bold: Whether to display the mod name in bold
        """
        # Get clean text without formatting for display
        clear_name = self.parse_clear_text(mod.name)

        # Create list item and store mod data
        item = QListWidgetItem(clear_name)
        item.setData(Qt.UserRole, mod)

        # Apply bold formatting if requested
        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        list_widget.addItem(item)

    def _restore_available_selection(self, mod_ids: List[str]) -> None:
        """
        Restore selection in available mods list by mod IDs.

        Args:
            mod_ids: List of mod IDs to select
        """
        if not mod_ids:
            return

        for i in range(self.ui.listWidget_available_mods.count()):
            item = self.ui.listWidget_available_mods.item(i)
            mod = item.data(Qt.UserRole)
            if mod and mod.id in mod_ids:
                item.setSelected(True)

    def _restore_active_selection(self, mod_ids: List[str]) -> None:
        """
        Restore selection in active mods list by mod IDs.

        Args:
            mod_ids: List of mod IDs to select
        """
        if not mod_ids:
            return

        for i in range(self.ui.listWidget_active_mods.count()):
            item = self.ui.listWidget_active_mods.item(i)
            mod = item.data(Qt.UserRole)
            if mod and mod.id in mod_ids:
                item.setSelected(True)
