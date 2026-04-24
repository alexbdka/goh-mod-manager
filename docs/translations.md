# Translations

This project keeps Qt translation sources in `src/ui/i18n/*.ts` and generates
runtime binaries as `*.qm`. The source of truth is the `.ts` file set.

## Repository Rules

- Locale files must use names such as `en_US.ts`, `fr_FR.ts`, or `zh_CN.ts`.
- Non-default translation files must declare the matching `<TS language="...">`
  attribute.
- Runtime language selection is dynamic. A language appears in the settings UI
  when the corresponding `.qm` file exists.

Validate the tree locally with:

```bash
uv run python scripts/validate_translations.py
```

Compile runtime binaries with:

```bash
uv run python scripts/build_translations.py --no-update
```

## Maintainer Workflow

When UI text changes, update the translation sources first:

```bash
uv run python scripts/build_translations.py --no-compile
```

That refreshes all tracked `.ts` files and removes obsolete entries through
`pyside6-lupdate -no-obsolete`.

After translation changes land, rebuild the `.qm` files before shipping a
release or testing the new language locally.

## Weblate Setup

Use one Weblate component pointed at `src/ui/i18n/*.ts` with:

- File format: `Qt Linguist Translation File`
- File mask: `src/ui/i18n/*.ts`
- Monolingual base language file: `src/ui/i18n/en_US.ts`
- Template for new translations: `src/ui/i18n/en_US.ts`

This follows Weblate's documented setup for Qt `.ts` files in monolingual mode.
New translation files added in Git will be discovered by the repository and can
be validated in CI before they are merged.

## CI Expectations

CI validates translation naming and metadata, compiles `.qm` files, and then
builds the documentation and test suite. Release builds also recompile the
translations before packaging the app.
