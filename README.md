# GoH Mod Manager

GoH Mod Manager is a PySide6 desktop app for managing
[Call to Arms - Gates of Hell](https://www.barbed-wire.eu/we-are-barbedwire-studios/our-game-development/)
mods, load order, presets, and local/Steam Workshop content without editing
`options.set` by hand.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

- Translations: Weblate project for the Qt UI
  https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/
- Translation workflow and rules: [src/ui/i18n/TRANSLATIONS.md](src/ui/i18n/TRANSLATIONS.md)
- Development setup and quality checks: [CONTRIBUTING.md](CONTRIBUTING.md)

## Build

Requirements:

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
uv run python -m src.main
uv run python -m src.cli.main status
```

Docs build:

```bash
uv run --group docs zensical build
```

Release-style build:

```bash
uv run python scripts/build_app.py
```

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md)
for the project license and [licenses/CREDITS.md](licenses/CREDITS.md) for
third-party credits and notices.
