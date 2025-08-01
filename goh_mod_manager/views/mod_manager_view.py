from typing import List, Optional

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMainWindow, QListWidgetItem, QApplication

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.views.ui.main_window import Ui_MainWindow


class ModManagerView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def clear_mod_lists(self):
        self.ui.listWidget_available_mods.clear()
        self.ui.listWidget_active_mods.clear()

    def populate_mod_lists(self, available_mods: List[Mod], active_mods: List[Mod]):
        self.clear_mod_lists()

        for mod in available_mods:
            self._add_mod_to_available(mod)

        for mod in active_mods:
            self._add_mod_to_active(mod)

    def _add_mod_to_available(self, mod: Mod):
        item = QListWidgetItem(str(mod))
        item.setData(256, mod)

        if mod.manualInstall:
            font = item.font()
            font.setItalic(True)
            item.setFont(font)

        self.ui.listWidget_available_mods.addItem(item)

    def _add_mod_to_active(self, mod: Mod):
        item = QListWidgetItem(str(mod))
        item.setData(256, mod)
        self.ui.listWidget_active_mods.addItem(item)

    def update_active_mods_count(self, count: int):
        self.ui.label_mod_count.setText(f"{count} mods")

    def update_mod_details(self, mod: Optional[Mod]):
        if mod:
            self.ui.label_mod_name.setText(mod.name)
            self.ui.textEdit_mod_description.setText(mod.desc)
        else:
            self.ui.label_mod_name.setText("No mod selected")
            self.ui.textEdit_mod_description.clear()

    def update_presets(self, preset_names: List[str], current_selection: str = ""):
        self.ui.comboBox_presets.clear()

        sorted_names = sorted(preset_names)
        for name in sorted_names:
            self.ui.comboBox_presets.addItem(name)

        if current_selection in sorted_names:
            index = self.ui.comboBox_presets.findText(current_selection)
            if index >= 0:
                self.ui.comboBox_presets.setCurrentIndex(index)

    def get_current_available_mod(self) -> List[QListWidgetItem]:
        return self.ui.listWidget_available_mods.selectedItems()

    def get_current_active_mod(self) -> List[QListWidgetItem]:
        return self.ui.listWidget_active_mods.selectedItems()

    def get_current_preset_name(self) -> str:
        return self.ui.comboBox_presets.currentText()

    def get_active_mods_order(self) -> List[Mod]:
        mods = []
        for i in range(self.ui.listWidget_active_mods.count()):
            item = self.ui.listWidget_active_mods.item(i)
            mod = item.data(256)
            if mod:
                mods.append(mod)
        return mods

    def move_active_mod_up(self) -> bool:
        item = self.ui.listWidget_active_mods.currentItem()
        if not item:
            return False

        row = self.ui.listWidget_active_mods.row(item)
        if row <= 0:
            return False

        self.ui.listWidget_active_mods.takeItem(row)
        self.ui.listWidget_active_mods.insertItem(row - 1, item)
        self.ui.listWidget_active_mods.setCurrentItem(item)
        return True

    def move_active_mod_down(self) -> bool:
        item = self.ui.listWidget_active_mods.currentItem()
        if not item:
            return False

        row = self.ui.listWidget_active_mods.row(item)
        if row >= self.ui.listWidget_active_mods.count() - 1:
            return False

        self.ui.listWidget_active_mods.takeItem(row)
        self.ui.listWidget_active_mods.insertItem(row + 1, item)
        self.ui.listWidget_active_mods.setCurrentItem(item)
        return True

    @staticmethod
    def set_font(font: QFont):
        QApplication.setFont(font)
