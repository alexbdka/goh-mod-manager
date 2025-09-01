import re
from pathlib import Path
from typing import List, Optional, Tuple

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.utils.mod_manager_logger import logger


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

    def get_mods_detailed(self) -> List[Tuple[str, bool]]:
        """
        Get all mods from the mods section with format information.

        Returns:
            List[Tuple[str, bool]]: List of (mod_id, is_manual_install) tuples
                                   is_manual_install is True for "NUMBER:0" format,
                                   False for "mod_NUMBER:0" format
        """
        if not self.is_mod_section_present():
            return []

        mods = []
        for line in self.lines:
            # Check for workshop mod format (mod_NUMBER:0)
            workshop_match = self.WORKSHOP_MOD_PATTERN.match(line)
            if workshop_match:
                mods.append((workshop_match.group(1), False))  # Workshop mod
                continue

            # Check for manual mod format (NUMBER:0)
            manual_match = self.MANUAL_MOD_PATTERN.match(line)
            if manual_match:
                mods.append((manual_match.group(1), True))  # Manual mod

        return mods

    def get_mod_ids(self) -> List[str]:
        """
        Get only the mod IDs without format information (alias for get_mods for clarity).

        Returns:
            List[str]: List of mod IDs as strings
        """
        return self.get_mods()

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
        original_count = len(self.lines)
        self.lines = [
            line for line in self.lines if not self.MOD_ENTRY_PATTERN.match(line)
        ]

        removed_count = original_count - len(self.lines)

        return self.save()

    def add_mod(self, mod: Mod) -> bool:
        """
        Add a single mod to the mods section.

        Args:
            mod: The mod object to add

        Returns:
            bool: True if mod was added successfully
        """
        if not self.is_mod_section_present():
            logger.error("Cannot add mod: mods section does not exist")
            return False

        # Check if mod already exists
        existing_mod_ids = self.get_mods()
        if mod.id in existing_mod_ids:
            logger.warning(f"Mod {mod.id} already exists in the mods section")
            return True  # Consider this a success since the mod is already there

        # Find insertion point (after mods section start)
        bounds = self._find_mods_section_bounds()
        if bounds is None:
            logger.error("Could not find mods section bounds")
            return False

        start_idx, _ = bounds
        insert_idx = start_idx + 1

        # Format the mod entry based on installation type
        if mod.manualInstall:
            mod_entry = f'\t\t"{mod.id}:0"\n'
        else:
            mod_entry = f'\t\t"mod_{mod.id}:0"\n'

        self.lines.insert(insert_idx, mod_entry)

        return self.save()

    def remove_mod(self, mod_id: str) -> bool:
        """
        Remove a mod from the mods section by its ID.

        Args:
            mod_id: The ID of the mod to remove

        Returns:
            bool: True if mod was removed successfully or didn't exist
        """
        if not self.is_mod_section_present():
            logger.warning("Cannot remove mod: mods section does not exist")
            return False

        original_count = len(self.lines)

        # Remove lines matching either format for this mod ID
        self.lines = [
            line
            for line in self.lines
            if not (line == f'\t\t"mod_{mod_id}:0"\n' or line == f'\t\t"{mod_id}:0"\n')
        ]

        removed_count = original_count - len(self.lines)
        if removed_count > 0:
            logger.info(f"Removed mod {mod_id}")
        else:
            logger.info(f"Mod {mod_id} was not found in the mods section")

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

    def has_mod(self, mod_id: str) -> bool:
        """
        Check if a specific mod is present in the mods section.

        Args:
            mod_id: The ID of the mod to check for

        Returns:
            bool: True if the mod is present in either format
        """
        mod_ids = self.get_mods()
        return mod_id in mod_ids

    def get_mod_count(self) -> int:
        """
        Get the total number of mods in the mods section.

        Returns:
            int: Number of mods present
        """
        return len(self.get_mods())

    def validate_file_format(self) -> bool:
        """
        Validate that the file has the expected structure.

        Returns:
            bool: True if file format appears valid
        """
        if not self.lines:
            logger.warning("File is empty or could not be loaded")
            return False

        # Check for basic structure - at minimum should have some content
        non_empty_lines = [line.strip() for line in self.lines if line.strip()]
        if len(non_empty_lines) < 1:
            logger.warning("File appears to be empty or contains only whitespace")
            return False

        # If mods section exists, validate its structure
        bounds = self._find_mods_section_bounds()
        if bounds is not None:
            start_idx, end_idx = bounds

            # Check that all lines between start and end are valid mod entries
            for i in range(start_idx + 1, end_idx):
                line = self.lines[i]
                if line.strip() and not self.MOD_ENTRY_PATTERN.match(line):
                    logger.warning(f"Invalid mod entry found: {line.strip()}")
                    return False

        return True

    def get_file_stats(self) -> dict:
        """
        Get statistics about the current file state.

        Returns:
            dict: Statistics including line count, mod count, etc.
        """
        stats = {
            "file_exists": self.file_path.exists(),
            "total_lines": len(self.lines),
            "has_mods_section": self._find_mods_section_bounds() is not None,
            "mod_count": self.get_mod_count(),
            "file_size_bytes": (
                self.file_path.stat().st_size if self.file_path.exists() else 0
            ),
        }

        if stats["has_mods_section"]:
            mods_detailed = self.get_mods_detailed()
            workshop_mods = [
                mod_id for mod_id, is_manual in mods_detailed if not is_manual
            ]
            manual_mods = [mod_id for mod_id, is_manual in mods_detailed if is_manual]

            stats.update(
                {
                    "workshop_mod_count": len(workshop_mods),
                    "manual_mod_count": len(manual_mods),
                }
            )

        return stats

    def __str__(self) -> str:
        """String representation showing basic file info."""
        stats = self.get_file_stats()
        return (
            f"OptionsSetParser({self.file_path.name}, "
            f"mods: {stats['mod_count']}, "
            f"lines: {stats['total_lines']})"
        )

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return f"OptionsSetParser(file_path='{self.file_path}', loaded={len(self.lines)} lines)"
