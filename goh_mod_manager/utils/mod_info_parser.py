import re
from pathlib import Path
from typing import Dict, Any, Optional

from goh_mod_manager.models.mod import Mod
from goh_mod_manager.utils.mod_manager_logger import logger


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
        r'\{\s*(name|desc|minGameVersion|maxGameVersion)\s+"?([^"}]+)"?\s*}',
        re.IGNORECASE,
    )

    # Default values for mod properties (tout en str maintenant)
    DEFAULT_VALUES = {
        "name": "Unknown Mod",
        "desc": "No description available",
        "minGameVersion": "0.0",
        "maxGameVersion": "any",  # Plus flexible que 999.0
    }

    # Mapping from lowercase field names to camelCase
    FIELD_NAME_MAPPING = {
        "name": "name",
        "desc": "desc",
        "mingameversion": "minGameVersion",
        "maxgameversion": "maxGameVersion",
    }

    # Plus besoin de FIELD_TYPES car tout est str

    def __init__(self, file_path: str):
        """
        Initialize the parser with a mod info file path.

        Args:
            file_path: Path to the mod info file
        """
        self.file_path = Path(file_path)
        self.lines: list[str] = []
        self._raw_content = ""
        self._parsed_data: Dict[str, str] = {}  # Spécifie que c'est Dict[str, str]
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

                    # Clean up the value - plus simple maintenant
                    cleaned_value = value.strip().strip("\"'")
                    result[proper_key] = cleaned_value
                    found_fields.add(proper_key)
                else:
                    logger.warning(f"Unknown field '{key}' found on line {line_num}")

        # Log missing fields
        missing_fields = set(self.DEFAULT_VALUES.keys()) - found_fields
        if missing_fields:
            logger.info(f"Using default values for missing fields: {missing_fields}")

        return result

    def _validate_parsed_data(self, data: Dict[str, str]) -> bool:
        """
        Validate the parsed data for basic consistency.
        Simplifié car plus de conversion de type nécessaire.

        Args:
            data: Dictionary with parsed field values

        Returns:
            bool: True if data appears valid
        """
        is_valid = True

        # Check for empty critical fields
        if not data.get("name", "").strip():
            logger.warning("Mod name is empty or missing")
            is_valid = False

        # Validation basique des versions (optionnel)
        for version_field in ["minGameVersion", "maxGameVersion"]:
            version_str = data.get(version_field, "").strip()
            if version_str and not self._is_valid_version_format(version_str):
                logger.info(
                    f"Non-standard version format for {version_field}: '{version_str}'"
                )
                # Ne pas marquer comme invalide, juste informer

        return is_valid

    def _is_valid_version_format(self, version: str) -> bool:
        """
        Check if version string has a reasonable format.
        Accepte différents formats de version.

        Args:
            version: Version string to validate

        Returns:
            bool: True if format looks reasonable
        """
        if not version:
            return False

        version_lower = version.lower()

        # Accepter "any" comme version valide
        if version_lower == "any":
            return True

        # Pattern flexible pour versions (1.0, 1.054.00, 2.1.3-beta, etc.)
        version_pattern = re.compile(r"^\d+(\.\d+)*(-\w+)?$")
        return bool(version_pattern.match(version))

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
            # Parse field data - plus simple maintenant
            parsed_data = self._parse_fields()
            self._parsed_data = parsed_data

            # Validate parsed data (optionnel maintenant)
            if not self._validate_parsed_data(parsed_data):
                logger.info(
                    f"Some validation issues in {self.file_path}, but continuing..."
                )

            # Create mod object - plus de risque d'exception de type
            mod = Mod(
                id=self._get_mod_id(),
                name=parsed_data["name"],
                desc=parsed_data["desc"],
                minGameVersion=parsed_data["minGameVersion"],
                maxGameVersion=parsed_data["maxGameVersion"],
                folderPath=str(self.file_path.parent),
                manualInstall=self._detect_manual_installation(),
            )

            return mod

        except Exception as e:
            logger.error(f"Error parsing mod info from {self.file_path}: {e}")
            return None

    # Méthodes utilitaires pour la comparaison de versions (optionnel)
    @staticmethod
    def compare_versions(version1: str, version2: str) -> int:
        """
        Compare two version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            int: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        # Gestion du cas "any"
        if version1.lower() == "any" or version2.lower() == "any":
            return 0  # "any" est compatible avec tout

        try:
            # Conversion basique pour comparaison
            v1_parts = [int(x) for x in version1.split(".") if x.isdigit()]
            v2_parts = [int(x) for x in version2.split(".") if x.isdigit()]

            # Égaliser les longueurs
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1
            return 0

        except (ValueError, AttributeError):
            # Si impossible de comparer, considérer comme égales
            return 0

    def get_raw_content(self) -> str:
        """Get the raw file content as a string."""
        return self._raw_content

    def get_parsed_fields(self) -> Dict[str, str]:
        """Get the last parsed field data."""
        return self._parsed_data.copy()

    def validate_file_format(self) -> bool:
        """
        Validate that the file appears to be a valid mod info file.

        Returns:
            bool: True if file format appears valid
        """
        if not self.lines:
            logger.warning("File is empty or not loaded")
            return False

        # Check for at least one recognizable field
        content = self._raw_content
        has_valid_fields = bool(self.FIELD_PATTERN.search(content))

        if not has_valid_fields:
            logger.warning("No valid mod info fields found in file")
            return False

        # Check for basic file structure
        if len(content.strip()) < 10:
            logger.warning("File content appears too short to be valid")
            return False

        return True

    def get_file_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the mod info file.

        Returns:
            Dict[str, Any]: File statistics and parsed field information
        """
        stats = {
            "file_exists": self.file_path.exists(),
            "file_size_bytes": (
                self.file_path.stat().st_size if self.file_path.exists() else 0
            ),
            "total_lines": len(self.lines),
            "is_valid_format": self.validate_file_format(),
            "is_manual_install": self._detect_manual_installation(),
            "mod_id": self._get_mod_id(),
        }

        # Add field-specific stats
        if self.lines:
            field_matches = self.FIELD_PATTERN.findall(self._raw_content)
            stats.update(
                {
                    "fields_found": len(field_matches),
                    "field_names": [match[0].lower() for match in field_matches],
                    "has_all_required_fields": all(
                        field in [match[0].lower() for match in field_matches]
                        for field in ["name", "desc"]
                    ),
                }
            )

        return stats

    def reload(self) -> bool:
        """
        Reload the file from disk.

        Returns:
            bool: True if reload was successful
        """
        self._parsed_data = {}
        return self._load_file()

    def __str__(self) -> str:
        """String representation showing basic mod info."""
        if self._parsed_data:
            name = self._parsed_data.get("name", "Unknown")
            mod_id = self._get_mod_id()
            return f"ModInfoParser({name}, ID: {mod_id})"
        else:
            return f"ModInfoParser({self.file_path.name}, not parsed)"

    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (
            f"ModInfoParser(file_path='{self.file_path}', "
            f"loaded={len(self.lines)} lines, "
            f"parsed_fields={len(self._parsed_data)})"
        )
