from dataclasses import dataclass

from src.core import constants

LOCAL_PREFIX = "local::"
WORKSHOP_PREFIX = "workshop::"


@dataclass(frozen=True)
class ModReference:
    id: str
    is_local: bool


def to_reference_key(mod_id: str, is_local: bool) -> str:
    prefix = LOCAL_PREFIX if is_local else WORKSHOP_PREFIX
    return f"{prefix}{mod_id}"


def parse_reference_key(value: str) -> ModReference | None:
    if value.startswith(LOCAL_PREFIX):
        return ModReference(id=value[len(LOCAL_PREFIX) :], is_local=True)
    if value.startswith(WORKSHOP_PREFIX):
        return ModReference(id=value[len(WORKSHOP_PREFIX) :], is_local=False)
    return None


def to_profile_mod_token(reference: ModReference) -> str:
    if reference.is_local:
        return reference.id
    return f"{constants.MOD_PREFIX}{reference.id}"


def from_profile_mod_token(token: str) -> ModReference:
    if token.startswith(constants.MOD_PREFIX):
        return ModReference(id=token[len(constants.MOD_PREFIX) :], is_local=False)
    return ModReference(id=token, is_local=True)
