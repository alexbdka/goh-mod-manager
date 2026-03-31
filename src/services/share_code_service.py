import base64
import json
import logging
import time
import zlib
from typing import Dict, List, Tuple

from src.core.exceptions import InvalidShareCodeError
from src.core.mod import ModInfo

logger = logging.getLogger(__name__)


class ShareCodeService:
    """
    Handles the encoding and decoding of mod lists into highly compressed
    Base64 strings (Share Codes) that can be easily copy-pasted.
    """

    def __init__(self):
        # We include a version number in our payload to allow future
        # changes to the share code format without breaking old codes.
        self.CURRENT_VERSION = 1

    def encode(self, mods: List[ModInfo]) -> str:
        """
        Encodes a list of active mods into a shareable Base64 string.
        Includes both ID and Name to help identify missing mods on the recipient's end.
        """
        # Minimal payload to keep the code short
        payload = {
            "v": self.CURRENT_VERSION,
            "m": [{"i": mod.id, "n": mod.name} for mod in mods],
            "t": int(time.time()),
        }

        try:
            # separators=(",", ":") removes spaces to reduce size
            json_str = json.dumps(payload, separators=(",", ":"))
            compressed_bytes = zlib.compress(json_str.encode("utf-8"))
            return base64.b64encode(compressed_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode share code: {e}")
            return ""

    def decode(self, code: str) -> List[Dict[str, str]]:
        """
        Decodes a share code back into a list of basic dictionaries
        containing 'id' and 'name' of the mods.
        """
        if not code:
            return []

        try:
            # Clean up the string just in case it was copied with weird spaces or newlines
            clean_code = code.strip().replace(" ", "").replace("\n", "")
            raw_bytes = base64.b64decode(clean_code)

            # Decompress
            json_bytes = zlib.decompress(raw_bytes)
            json_string = json_bytes.decode("utf-8")
            payload = json.loads(json_string)

            # Support for the format we just generated
            if isinstance(payload, dict) and "m" in payload:
                # Map our minified keys back to readable ones
                return [
                    {"id": m.get("i", ""), "name": m.get("n", "")} for m in payload["m"]
                ]

            # Support for the legacy format (from your old project)
            if isinstance(payload, dict) and "mods" in payload:
                return payload["mods"]

            # Super legacy (just a raw list)
            if isinstance(payload, list):
                return payload

            raise InvalidShareCodeError("Unrecognized payload structure.")

        except Exception as e:
            logger.error(f"Failed to decode share code: {e}")
            raise InvalidShareCodeError(f"Invalid share code: {e}") from e

    def resolve_mods(
        self, decoded_mods_data: List[Dict[str, str]], catalogue_mods: List[ModInfo]
    ) -> Tuple[List[ModInfo], List[Dict[str, str]]]:
        """
        Takes the decoded list of IDs/Names and matches them against the
        local catalogue to return actual ModInfo objects.

        Returns:
            A tuple of two lists: (Found Mods, Missing Mods Data)
        """
        mods_by_id = {mod.id: mod for mod in catalogue_mods}

        found_mods: List[ModInfo] = []
        missing_mods: List[Dict[str, str]] = []

        for item in decoded_mods_data:
            mod_id = item.get("id", "").strip()
            mod_name = item.get("name", "Unknown Mod").strip()

            if mod_id and mod_id in mods_by_id:
                found_mods.append(mods_by_id[mod_id])
            else:
                # If we can't find it by ID, it's missing on this user's machine
                missing_mods.append({"id": mod_id, "name": mod_name})

        return found_mods, missing_mods
