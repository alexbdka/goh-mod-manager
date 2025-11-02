import re
from pathlib import Path
from typing import Dict, Optional

from goh_mod_manager.model.mod import Mod
from goh_mod_manager.util.mod_manager_logger import logger


class ModInfoParser:
    """
    Parser for mod info files that contain mod metadata.

    Parses files with format like:
    ```
    {name "Mod Name"}
    {desc "Mod description"}
    {minGameVersion "1.054.00"}
    {maxGameVersion "2.1.3"}
    ```

    Also detects manual installation based on presence of .imported_by_mod_manager file.
    """

    # Constants for parsing
    IMPORTED_FLAG_FILE = ".imported_by_mod_manager"

    # Regex patterns for different field types
    FIELD_PATTERN = re.compile(
        r'\{\s*(name|desc|minGameVersion|maxGameVersion|require)\s+"?([^"}]+)"?\s*}',
        re.IGNORECASE,
    )

    # Default values for mod properties
    DEFAULT_VALUES = {
        "name": "Unknown Mod",
        "desc": "No description available",
        "minGameVersion": "any",
        "maxGameVersion": "any",
        "require": "",
    }

    # Mapping from lowercase field names to camelCase
    FIELD_NAME_MAPPING = {
        "name": "name",
        "desc": "desc",
        "mingameversion": "minGameVersion",
        "maxgameversion": "maxGameVersion",
        "require": "require",
    }

    def __init__(self, file_path: str):
        """
        Initialize the parser with a mod info file path.

        Args:
            file_path: Path to the mod info file
        """
        self.file_path = Path(file_path)
        self.lines: list[str] = []
        self._raw_content = ""
        self._parsed_data: Dict[str, str] = {}
        self._load_file()

    def _load_file(self) -> bool:
        """
        Load the mod info file content into memory.

        Returns:
            bool: True if file was loaded successfully
        """
        if not self.file_path.exists():
            logger.warning(f"Mod info file does not exist: {self.file_path}")
            return False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.lines = f.readlines()
                self._raw_content = "".join(self.lines)

            return True

        except Exception as e:
            logger.error(f"Error loading mod info file {self.file_path}: {e}")
            self.lines = []
            self._raw_content = ""
            return False

    def _parse_fields(self) -> Dict[str, str]:
        """
        Parse all fields from the file content.

        Returns:
            Dict[str, str]: Dictionary with parsed field values
        """
        result = self.DEFAULT_VALUES.copy()
        found_fields = set()

        for line_num, line in enumerate(self.lines, 1):
            matches = self.FIELD_PATTERN.finditer(line)

            for match in matches:
                key, value = match.groups()
                key_lower = key.lower()  # Normalize case for lookup

                # Map lowercase key to proper camelCase key
                if key_lower in self.FIELD_NAME_MAPPING:
                    proper_key = self.FIELD_NAME_MAPPING[key_lower]

                    # Clean up the value
                    cleaned_value = value.strip().strip("\"'")
                    result[proper_key] = cleaned_value
                    found_fields.add(proper_key)
                else:
                    logger.warning(f"Unknown field '{key}' found on line {line_num}")

        # Log missing fields
        missing_fields = set(self.DEFAULT_VALUES.keys()) - found_fields
        if missing_fields and missing_fields != {"require"}:
            logger.info(f"Using default values for missing fields: {missing_fields}")

        return result

    def _detect_manual_installation(self) -> bool:
        """
        Detect if this is a manually installed mod.

        Returns:
            bool: True if mod was manually installed (has .imported_by_mod_manager flag)
        """
        mod_dir = self.file_path.parent
        imported_flag = mod_dir / self.IMPORTED_FLAG_FILE
        return imported_flag.exists()

    def _get_mod_id(self) -> str:
        """
        Get the mod ID from the parent directory name.

        Returns:
            str: Mod ID (parent directory name)
        """
        return self.file_path.parent.name

    def parse(self) -> Optional[Mod]:
        """
        Parse the mod info file and create a Mod object.

        Returns:
            Optional[Mod]: Parsed Mod object, or None if parsing failed
        """
        if not self.lines:
            logger.error(f"Cannot parse: no content loaded from {self.file_path}")
            return None

        try:
            # Parse field data
            parsed_data = self._parse_fields()
            self._parsed_data = parsed_data

            # Create mod object
            mod = Mod(
                id=self._get_mod_id(),
                name=parsed_data["name"],
                desc=parsed_data["desc"],
                minGameVersion=parsed_data["minGameVersion"],
                maxGameVersion=parsed_data["maxGameVersion"],
                folderPath=str(self.file_path.parent),
                manualInstall=self._detect_manual_installation(),
                require=" ".join(
                    [r.replace("mod_", "") for r in parsed_data["require"].split()]
                ),
            )

            return mod

        except Exception as e:
            logger.error(f"Error parsing mod info from {self.file_path}: {e}")
            return None
