# GoH Mod Manager

GoH Mod Manager is a PySide6 desktop app for managing
[Call to Arms - Gates of Hell](https://www.barbed-wire.eu/we-are-barbedwire-studios/our-game-development/)
mods, load order, presets, and local/Steam Workshop content.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).  
For translations, **Weblate** kindly hosts our translation platform at [goh-mod-manager/qt-ui](https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/).

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
for the project license and [licenses/README.md](licenses/README.md) for
third-party credits and notices.
