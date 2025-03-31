import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, 
                            QFileDialog, QHBoxLayout, QLabel, QMessageBox,
                            QInputDialog, QComboBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt
from utils import (load_options_set, scan_mods_folder, save_config, load_config, 
                  update_mods_section, save_preset, load_preset, delete_preset,
                  get_all_presets, get_config_path)

class ModManagerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gates of Hell - Mod Manager")
        self.setGeometry(100, 100, 800, 600)
        self.config_file = get_config_path()
        
        self.setup_ui()
        self.check_config()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.main_layout = QVBoxLayout()
        
        # Main section with mod lists
        self.mod_section = QHBoxLayout()
        
        # Installed mods section
        self.left_layout = QVBoxLayout()
        self.installed_label = QLabel("Installed Mods")
        self.installed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.installed_list = QListWidget()
        self.installed_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.installed_list.itemDoubleClicked.connect(self.activate_mod)
        
        self.left_layout.addWidget(self.installed_label)
        self.left_layout.addWidget(self.installed_list)
        
        # Control section
        self.center_layout = QVBoxLayout()
        self.activate_button = QPushButton("Activate →")
        self.activate_button.clicked.connect(self.activate_selected)
        self.deactivate_button = QPushButton("← Deactivate")
        self.deactivate_button.clicked.connect(self.deactivate_selected)
        self.move_up_button = QPushButton("Move Up ↑")
        self.move_up_button.clicked.connect(self.move_mod_up)
        self.move_down_button = QPushButton("Move Down ↓")
        self.move_down_button.clicked.connect(self.move_mod_down)
        
        # Add spacing for alignment
        self.center_layout.addStretch()
        self.center_layout.addWidget(self.activate_button)
        self.center_layout.addWidget(self.deactivate_button)
        self.center_layout.addWidget(self.move_up_button)
        self.center_layout.addWidget(self.move_down_button)
        self.center_layout.addStretch()
        
        # Activated mods section
        self.right_layout = QVBoxLayout()
        self.activated_label = QLabel("Activated Mods")
        self.activated_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activated_list = QListWidget()
        self.activated_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.activated_list.setAcceptDrops(True)
        self.activated_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.activated_list.itemDoubleClicked.connect(self.deactivate_mod)
        
        self.right_layout.addWidget(self.activated_label)
        self.right_layout.addWidget(self.activated_list)
        
        # Assemble the mod section layout
        self.mod_section.addLayout(self.left_layout)
        self.mod_section.addLayout(self.center_layout)
        self.mod_section.addLayout(self.right_layout)
        
        # Presets section
        self.presets_group = QGroupBox("Presets")
        self.presets_layout = QGridLayout()
        
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)
        
        self.load_preset_button = QPushButton("Load")
        self.load_preset_button.clicked.connect(self.load_selected_preset)
        
        self.save_preset_button = QPushButton("Save Current")
        self.save_preset_button.clicked.connect(self.save_current_preset)
        
        self.delete_preset_button = QPushButton("Delete")
        self.delete_preset_button.clicked.connect(self.delete_selected_preset)
        
        self.presets_layout.addWidget(QLabel("Preset:"), 0, 0)
        self.presets_layout.addWidget(self.preset_combo, 0, 1)
        self.presets_layout.addWidget(self.load_preset_button, 0, 2)
        self.presets_layout.addWidget(self.save_preset_button, 0, 3)
        self.presets_layout.addWidget(self.delete_preset_button, 0, 4)
        
        self.presets_group.setLayout(self.presets_layout)
        
        # Bottom buttons
        self.bottom_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.save_mods_order)
        self.change_paths_button = QPushButton("Change Paths")
        self.change_paths_button.clicked.connect(self.ask_for_paths)
        self.bottom_layout.addWidget(self.apply_button)
        self.bottom_layout.addWidget(self.change_paths_button)
        
        # Assemble the main layout
        self.main_layout.addLayout(self.mod_section)
        self.main_layout.addWidget(self.presets_group)
        self.main_layout.addLayout(self.bottom_layout)
        
        self.setLayout(self.main_layout)
    
    def check_config(self):
        """Check if configuration exists, otherwise ask for paths"""
        config = load_config(self.config_file)
        if "mods_path" not in config or "options_set_path" not in config:
            self.ask_for_paths()
        else:
            self.load_mods()
            self.update_preset_list()
    
    def ask_for_paths(self):
        """Ask the user to select the necessary paths"""
        mods_path = QFileDialog.getExistingDirectory(self, "Select Mods Folder")
        if not mods_path:
            QMessageBox.critical(self, "Error", "Mods folder must be selected!")
            return
            
        options_set_path = QFileDialog.getOpenFileName(self, "Select options.set File", "", "SET Files (*.set)")[0]
        if not options_set_path:
            QMessageBox.critical(self, "Error", "options.set file must be selected!")
            return
        
        config = {"mods_path": mods_path, "options_set_path": options_set_path}
        save_config(self.config_file, config)
        self.load_mods()
        self.update_preset_list()
    
    def load_mods(self):
        """Load installed and activated mods"""
        config = load_config(self.config_file)
        if not config:
            return
            
        installed_mods = scan_mods_folder(config["mods_path"])
        active_mods = load_options_set(config["options_set_path"])
        
        self.installed_list.clear()
        self.activated_list.clear()
        
        # Sort mods by name for better readability
        sorted_mods = sorted(installed_mods.items(), key=lambda x: x[1])
        
        for mod_id, mod_name in sorted_mods:
            item_text = f"{mod_name} ({mod_id})"
            if mod_id in active_mods:
                self.activated_list.addItem(item_text)
            else:
                self.installed_list.addItem(item_text)
    
    def activate_mod(self, item):
        """Activate a mod (double-click)"""
        self.installed_list.takeItem(self.installed_list.row(item))
        self.activated_list.addItem(item.text())
    
    def deactivate_mod(self, item):
        """Deactivate a mod (double-click)"""
        self.activated_list.takeItem(self.activated_list.row(item))
        self.installed_list.addItem(item.text())
    
    def activate_selected(self):
        """Activate selected mod (button)"""
        selected_items = self.installed_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            self.activate_mod(item)
    
    def deactivate_selected(self):
        """Deactivate selected mod (button)"""
        selected_items = self.activated_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            self.deactivate_mod(item)
    
    def move_mod_up(self):
        """Move selected mod up"""
        current_row = self.activated_list.currentRow()
        if current_row > 0:
            item = self.activated_list.takeItem(current_row)
            self.activated_list.insertItem(current_row - 1, item)
            self.activated_list.setCurrentRow(current_row - 1)
    
    def move_mod_down(self):
        """Move selected mod down"""
        current_row = self.activated_list.currentRow()
        if current_row < self.activated_list.count() - 1 and current_row >= 0:
            item = self.activated_list.takeItem(current_row)
            self.activated_list.insertItem(current_row + 1, item)
            self.activated_list.setCurrentRow(current_row + 1)
    
    def extract_mod_id(self, item_text):
        """Extract mod ID from item text"""
        return item_text.split('(')[-1].rstrip(')')
    
    def save_mods_order(self):
        """Save the order of active mods"""
        config = load_config(self.config_file)
        options_set_path = config.get("options_set_path")
        
        if not options_set_path:
            QMessageBox.critical(self, "Error", "options.set file path not found!")
            return
        
        # Get active mod IDs
        active_mods = []
        for i in range(self.activated_list.count()):
            item_text = self.activated_list.item(i).text()
            mod_id = self.extract_mod_id(item_text)
            active_mods.append(mod_id)
        
        # Update mods section
        if update_mods_section(options_set_path, active_mods):
            QMessageBox.information(self, "Success", "Changes saved successfully!")
        else:
            QMessageBox.warning(self, "Warning", "Could not update mods section. Check the format of the options.set file.")
    
    def update_preset_list(self):
        """Update the list of presets in the combobox"""
        self.preset_combo.clear()
        presets = get_all_presets(self.config_file)
        if presets:
            self.preset_combo.addItems(presets)
            self.load_preset_button.setEnabled(True)
            self.delete_preset_button.setEnabled(True)
        else:
            self.preset_combo.addItem("No presets available")
            self.load_preset_button.setEnabled(False)
            self.delete_preset_button.setEnabled(False)
    
    def save_current_preset(self):
        """Save the current mod configuration as a preset"""
        # Get active mod IDs
        active_mods = []
        for i in range(self.activated_list.count()):
            item_text = self.activated_list.item(i).text()
            mod_id = self.extract_mod_id(item_text)
            active_mods.append(mod_id)
        
        if not active_mods:
            QMessageBox.warning(self, "Warning", "No mods are currently activated.")
            return
        
        # Ask for preset name
        preset_name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        if ok and preset_name:
            # Check if preset already exists
            existing_presets = get_all_presets(self.config_file)
            if preset_name in existing_presets:
                reply = QMessageBox.question(self, "Confirm Replace", 
                                            f"Preset '{preset_name}' already exists. Replace it?",
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Save the preset
            if save_preset(self.config_file, preset_name, active_mods):
                QMessageBox.information(self, "Success", f"Preset '{preset_name}' saved successfully!")
                self.update_preset_list()
                # Select the newly created preset
                index = self.preset_combo.findText(preset_name)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
            else:
                QMessageBox.warning(self, "Error", "Failed to save preset.")
    
    def load_selected_preset(self):
        """Load the selected preset"""
        if self.preset_combo.count() == 0 or self.preset_combo.currentText() == "No presets available":
            return
        
        preset_name = self.preset_combo.currentText()
        mod_ids = load_preset(self.config_file, preset_name)
        
        if not mod_ids:
            QMessageBox.warning(self, "Error", f"Could not load preset '{preset_name}'.")
            return
        
        # Get mod names for all mods
        config = load_config(self.config_file)
        installed_mods = scan_mods_folder(config["mods_path"])
        
        # First, make a full list of all mods (both installed and activated)
        all_mods = []
        
        # Add all mods from installed list
        for i in range(self.installed_list.count()):
            item_text = self.installed_list.item(i).text()
            mod_id = self.extract_mod_id(item_text)
            all_mods.append((mod_id, item_text))
        
        # Add all mods from activated list
        for i in range(self.activated_list.count()):
            item_text = self.activated_list.item(i).text()
            mod_id = self.extract_mod_id(item_text)
            all_mods.append((mod_id, item_text))
        
        # Clear both lists
        self.installed_list.clear()
        self.activated_list.clear()
        
        # Create sets for quick lookup
        preset_mod_ids = set(mod_ids)
        
        # Add mods to either activated or installed based on preset
        for mod_id, item_text in all_mods:
            if mod_id in preset_mod_ids:
                # Skip for now, we'll add them in order later
                pass
            else:
                # Add to installed list
                self.installed_list.addItem(item_text)
        
        # Now add activated mods in the exact order from preset
        for mod_id in mod_ids:
            # Find this mod in our all_mods list
            found = False
            for m_id, item_text in all_mods:
                if m_id == mod_id:
                    self.activated_list.addItem(item_text)
                    found = True
                    break
            
            # If not found in our lists but exists in installed mods directory
            if not found and mod_id in installed_mods:
                mod_name = installed_mods[mod_id]
                self.activated_list.addItem(f"{mod_name} ({mod_id})")
        
        QMessageBox.information(self, "Success", f"Preset '{preset_name}' loaded successfully!")
    
    def delete_selected_preset(self):
        """Delete the selected preset"""
        if self.preset_combo.count() == 0 or self.preset_combo.currentText() == "No presets available":
            return
        
        preset_name = self.preset_combo.currentText()
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete preset '{preset_name}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if delete_preset(self.config_file, preset_name):
                QMessageBox.information(self, "Success", f"Preset '{preset_name}' deleted successfully!")
                self.update_preset_list()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete preset '{preset_name}'.")