# Contributing

Contributions are welcome.

## Translations

The app UI is translated through Weblate:

- Weblate: https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/
- Source files: `src/ui/i18n/*.ts`
- Runtime files: `src/ui/i18n/*.qm`
- Translation workflow and rules: [src/ui/i18n/TRANSLATIONS.md](src/ui/i18n/TRANSLATIONS.md)

## Development

Set up the project with uv:

```bash
uv sync --group dev --group docs
```

Common checks:

```bash
uv run pre-commit validate-config
uv run python -m compileall -q src tests scripts
uv run python scripts/validate_translations.py
uv run python scripts/build_translations.py --no-update
uv run deptry .
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run pytest -q
```

Run the app locally:

```bash
uv run python -m src.main
```

Run the CLI status command:

```bash
uv run python -m src.cli.main status
```

The project also includes a docs build flow:

```bash
uv run --group docs zensical build
```
