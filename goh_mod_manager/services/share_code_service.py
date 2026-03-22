import base64
import json
import time
import zlib
from typing import Dict, List, Tuple

from goh_mod_manager.core.mod import Mod


class ShareCodeService:
    def encode_versioned(self, mods: List[Mod]) -> str:
        payload = {
            "version": 1,
            "mods": [{"name": mod.name, "id": mod.id} for mod in mods],
            "timestamp": int(time.time()),
        }
        return self._encode_payload(payload)

    def encode_list(self, mod_data: List[Dict]) -> str:
        return self._encode_payload(mod_data)

    def encode_mods_list(self, mods: List[Mod]) -> str:
        mod_data = [{"id": str(mod.id), "name": mod.name} for mod in mods]
        return self.encode_list(mod_data)

    def decode(self, code: str) -> List[Dict]:
        payload = self._decode_payload(code)

        if isinstance(payload, dict) and "mods" in payload:
            mods = payload["mods"]
        elif isinstance(payload, list):
            mods = payload
        else:
            raise ValueError("Invalid share code structure")

        if not isinstance(mods, list):
            raise ValueError("Invalid share code payload")

        normalized = []
        for item in mods:
            if not isinstance(item, dict):
                raise ValueError("Invalid mod data structure")
            if "id" not in item and "name" not in item:
                raise ValueError("Invalid mod data structure")
            normalized.append(item)

        return normalized

    @staticmethod
    def resolve_mods(
        mod_data: List[Dict], installed_mods: List[Mod]
    ) -> Tuple[List[Mod], List[Dict]]:
        mods_by_id = {str(mod.id): mod for mod in installed_mods}
        mods_by_name = {mod.name: mod for mod in installed_mods}

        found_mods: List[Mod] = []
        missing_mods: List[Dict] = []

        for item in mod_data:
            mod = None

            mod_id = str(item.get("id", "")).strip()
            mod_name = item.get("name", "").strip()

            if mod_id and mod_id in mods_by_id:
                mod = mods_by_id[mod_id]
            elif mod_name and mod_name in mods_by_name:
                mod = mods_by_name[mod_name]

            if mod:
                found_mods.append(mod)
            else:
                missing_mods.append(
                    {"id": mod_id or "unknown", "name": mod_name or "Unknown Mod"}
                )

        return found_mods, missing_mods

    @staticmethod
    def _encode_payload(payload: Dict | List[Dict]) -> str:
        json_str = json.dumps(payload, separators=(",", ":"))
        compressed_bytes = zlib.compress(json_str.encode("utf-8"))
        return base64.b64encode(compressed_bytes).decode("utf-8")

    @staticmethod
    def _decode_payload(code: str) -> Dict | List[Dict]:
        clean_code = code.strip().replace(" ", "").replace("\n", "")
        raw_bytes = base64.b64decode(clean_code)
        try:
            # Try to decompress assuming it's a new version using zlib
            json_bytes = zlib.decompress(raw_bytes)
        except zlib.error:
            # Fallback to uncompressed (backward compatibility with old share codes)
            json_bytes = raw_bytes

        json_string = json_bytes.decode("utf-8")
        return json.loads(json_string)
