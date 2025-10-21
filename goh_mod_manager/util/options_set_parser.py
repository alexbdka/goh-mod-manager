import re
from pathlib import Path
from typing import List, Optional, Tuple

from goh_mod_manager.model.mod import Mod
from goh_mod_manager.util.mod_manager_logger import logger


class OptionsSetParser:
    """
    Parser for game options/settings files that handles mod configurations.

    Manages mods in two formats:
    - Workshop mods: "mod_NUMBER:0"
    - Manual mods: "NUMBER:0"

    The file structure expected:
    ```
    some_config_line
    {mods
        "mod_123:0"
        "456:0"
    }
    other_config_line
    ```
    """

    # Constants for better maintainability
    MODS_SECTION_START = "\t{mods\n"
    MODS_SECTION_END = "\t}\n"
    MOD_ENTRY_PATTERN = re.compile(r'^\t\t"(mod_)?(\d+):0"\n$')
    WORKSHOP_MOD_PATTERN = re.compile(r'^\t\t"mod_(\d+):0"\n$')
    MANUAL_MOD_PATTERN = re.compile(r'^\t\t"(\d+):0"\n$')

    def __init__(self, file_path: str):
        """
        Initialize the parser with a file path.

        Args:
            file_path: Path to the options/settings file
        """
        self.file_path = Path(file_path)
        self.lines: List[str] = []
        self._load_file()

    def _load_file(self) -> None:
        """Load the file content into memory."""
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.lines = f.readlines()
            except Exception as e:
                logger.error(f"Error loading {self.file_path}: {e}")
                self.lines = []
        else:
            logger.warning(f"File {self.file_path} does not exist")
            self.lines = []

    def save(self) -> bool:
        """
        Save the current content back to the file.

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.writelines(self.lines)
            return True
        except Exception as e:
            logger.error(f"Error saving {self.file_path}: {e}")
            return False

    def _find_mods_section_bounds(self) -> Optional[Tuple[int, int]]:
        """
        Find the start and end indices of the mods section.

        Returns:
            Optional[Tuple[int, int]]: (start_index, end_index) or None if not found
        """
        start_idx = None
        end_idx = None

        for i, line in enumerate(self.lines):
            if line == self.MODS_SECTION_START:
                start_idx = i
            elif line == self.MODS_SECTION_END and start_idx is not None:
                end_idx = i
                break

        if start_idx is not None and end_idx is not None:
            return start_idx, end_idx
        return None

    def is_mod_section_present(self) -> bool:
        """
        Check if the mods section exists in the file.

        Returns:
            bool: True if mods section exists or was successfully created
        """
        if self._find_mods_section_bounds() is not None:
            return True

        logger.warning(f"No mods section found in {self.file_path}")
        return self._create_mods_section()

    def _create_mods_section(self) -> bool:
        """
        Create a new mods section at the end of the file.

        Returns:
            bool: True if section was created and saved successfully
        """
        logger.info("Creating mods section...")

        if not self.lines:
            # Empty file, create basic structure
            self.lines = [self.MODS_SECTION_START, self.MODS_SECTION_END]
        else:
            # Insert before the last line (assuming it's a closing brace or similar)
            insert_pos = len(self.lines) - 1 if self.lines else 0
            self.lines.insert(insert_pos, self.MODS_SECTION_START)
            self.lines.insert(insert_pos + 1, self.MODS_SECTION_END)

        return self.save()

    def get_mods(self) -> List[str]:
        """
        Get all mod IDs from the mods section (maintains original signature for compatibility).

        Returns:
            List[str]: List of mod IDs as strings
        """
        if not self.is_mod_section_present():
            return []

        mods = []
        for line in self.lines:
            # Check for workshop mod format (mod_NUMBER:0)
            workshop_match = self.WORKSHOP_MOD_PATTERN.match(line)
            if workshop_match:
                mods.append(workshop_match.group(1))
                continue

            # Check for manual mod format (NUMBER:0)
            manual_match = self.MANUAL_MOD_PATTERN.match(line)
            if manual_match:
                mods.append(manual_match.group(1))

        return mods

    def clear_mods_section(self) -> bool:
        """
        Remove all mod entries from the mods section while preserving the section structure.

        Returns:
            bool: True if clearing was successful and saved
        """
        if not self.is_mod_section_present():
            logger.warning("Cannot clear mods section: section does not exist")
            return False

        # Remove all lines matching mod patterns
        self.lines = [
            line
            for line in self.lines
            if not self.MOD_ENTRY_PATTERN.match(line)
            and line.strip() != '"mod_template:0"'
        ]

        return self.save()

    def set_mods(self, mods: List[Mod]) -> bool:
        """
        Replace all mods in the section with the provided list.

        Args:
            mods: List of mod objects to set

        Returns:
            bool: True if mods were set successfully
        """
        if not self.is_mod_section_present():
            logger.error("Cannot set mods: mods section does not exist")
            return False

        # Clear existing mods
        if not self.clear_mods_section():
            return False

        if not mods:
            return True

        # Find insertion point
        bounds = self._find_mods_section_bounds()
        if bounds is None:
            logger.error("Could not find mods section bounds after clearing")
            return False

        start_idx, _ = bounds
        insert_idx = start_idx + 1

        # Insert all mods
        for i, mod in enumerate(mods):
            if mod.manualInstall:
                mod_entry = f'\t\t"{mod.id}:0"\n'
            else:
                mod_entry = f'\t\t"mod_{mod.id}:0"\n'

            self.lines.insert(insert_idx + i, mod_entry)

        return self.save()
