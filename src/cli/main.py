import argparse
from collections.abc import Iterable
from typing import Protocol

from src.application.state import (
    ActiveModsState,
    CatalogueState,
    PresetsState,
    SettingsState,
    ShareCodeExportResult,
)


class ManagerView(Protocol):
    def get_settings_state(self) -> SettingsState: ...
    def get_catalogue_state(self) -> CatalogueState: ...
    def get_active_mods_state(self) -> ActiveModsState: ...
    def get_presets_state(self) -> PresetsState: ...
    def build_share_code_export(self) -> ShareCodeExportResult: ...


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="goh-mod-manager-cli",
        description="Minimal CLI for validating the application architecture.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show configuration and initialization state.")
    subparsers.add_parser("catalogue", help="List catalogue mods.")
    subparsers.add_parser("active", help="List active mods.")
    subparsers.add_parser("presets", help="List saved presets.")
    subparsers.add_parser(
        "share-code", help="Export the current load order as a share code."
    )

    return parser


def _print_lines(lines: Iterable[str]) -> int:
    for line in lines:
        print(line)
    return 0


def _status_lines(manager: ManagerView, initialized: bool) -> list[str]:
    settings = manager.get_settings_state()
    catalogue = manager.get_catalogue_state()
    active = manager.get_active_mods_state()
    presets = manager.get_presets_state()

    return [
        f"initialized: {initialized}",
        f"game_path: {settings.game_path or '-'}",
        f"workshop_path: {settings.workshop_path or '-'}",
        f"profile_path: {settings.profile_path or '-'}",
        f"language: {settings.language}",
        f"theme: {settings.theme}",
        f"font: {settings.font}",
        f"catalogue_count: {len(catalogue.items)}",
        f"active_count: {len(active.items)}",
        f"preset_count: {len(presets.preset_names)}",
    ]


def _catalogue_lines(manager: ManagerView) -> list[str]:
    catalogue = manager.get_catalogue_state()
    if not catalogue.items:
        return ["No catalogue mods found."]

    lines = []
    for mod in catalogue.items:
        source = "Local" if mod.is_local else "Workshop"
        flags = []
        if mod.is_active:
            flags.append("active")
        if mod.missing_dependencies:
            flags.append("missing-deps")
        suffix = f" [{' '.join(flags)}]" if flags else ""
        lines.append(f"{mod.id}: {mod.name} ({source}){suffix}")
    return lines


def _active_lines(manager: ManagerView) -> list[str]:
    active = manager.get_active_mods_state()
    if not active.items:
        return ["No active mods."]

    lines = []
    for mod in active.items:
        order = mod.load_order if mod.load_order is not None else "?"
        source = "Local" if mod.is_local else "Workshop"
        lines.append(f"{order}. {mod.name} ({mod.id}) [{source}]")
    return lines


def _preset_lines(manager: ManagerView) -> list[str]:
    presets = manager.get_presets_state()
    if not presets.preset_names:
        return ["No presets saved."]

    lines = []
    for name in presets.preset_names:
        marker = " [current]" if presets.current_preset_name == name else ""
        lines.append(f"{name}{marker}")
    if presets.current_preset_name is None and presets.is_unsaved:
        lines.append("-- custom load order -- [unsaved]")
    return lines


def _share_code_lines(manager: ManagerView) -> list[str]:
    result = manager.build_share_code_export()
    if not result.has_active_mods:
        return ["No active mods to export."]
    return [result.code]


def main() -> int:
    from src.core.manager import ModManager

    parser = _build_parser()
    args = parser.parse_args()

    manager = ModManager()
    initialized = manager.initialize()

    if args.command == "status":
        return _print_lines(_status_lines(manager, initialized))
    if args.command == "catalogue":
        return _print_lines(_catalogue_lines(manager))
    if args.command == "active":
        return _print_lines(_active_lines(manager))
    if args.command == "presets":
        return _print_lines(_preset_lines(manager))
    if args.command == "share-code":
        return _print_lines(_share_code_lines(manager))

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
