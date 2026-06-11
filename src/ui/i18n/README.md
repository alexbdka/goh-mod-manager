# UI Translations

This directory is the home of the app's Qt translation files.

If you are translating the interface, this is the practical reference. The root
README only gives the short version.

## Files

- `*.ts`: Qt Linguist source files. These are the files translators and Weblate
  work with.
- `*.qm`: compiled runtime files. The app loads these files to populate the
  language selector and translate the UI.

The `.ts` files are the source of truth. The `.qm` files are generated from
them and should not be edited by hand.

## Naming Rules

Translation files use Qt/Weblate locale names:

- `en.ts`
- `fr.ts`
- `ru.ts`
- `zh_Hans.ts`
- `pt_BR.ts`

The `<TS language="...">` metadata inside a `.ts` file must match the filename.
For example:

```xml
<TS version="2.1" language="fr">
```

Invalid names or mismatched metadata are rejected by:

```bash
uv run python scripts/validate_translations.py
```

## Translator Workflow

The preferred workflow is Weblate:

1. Translate strings in the
   [hosted Weblate project](https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/).
2. Let Weblate open or update a pull request.
3. Keep review focused on wording, placeholders, and UI fit.

Local editing is also possible with Qt Linguist:

1. Open the relevant `.ts` file.
2. Translate or review strings.
3. Save the file.
4. Run validation before committing.

```bash
uv run python scripts/validate_translations.py
```

Do not edit `.qm` files directly. Rebuild them from `.ts` sources.

## Maintainer Workflow

When UI source text changes, refresh the `.ts` catalogs:

```bash
uv run python scripts/build_translations.py --no-compile
```

This updates translation sources without rebuilding runtime `.qm` files.

Before testing translated UI locally or shipping a release, compile runtime
files:

```bash
uv run python scripts/build_translations.py --no-update
```

Validate after translation or build changes:

```bash
uv run python scripts/validate_translations.py
```

For a full refresh and compile in one pass:

```bash
uv run python scripts/build_translations.py
```

## Adding A Language

1. Add a new locale file using the naming rules above.
2. Use `en.ts` as the template/base language.
3. Make sure the `<TS language="...">` metadata matches the filename.
4. Run validation.
5. Compile `.qm` files when you want the language to appear in the app.

The app discovers languages dynamically from compiled `.qm` files in this
directory. If a new language has a valid `.qm` file, it can appear in the
settings UI without hard-coding it in Python.

## Placeholders

Keep placeholders intact. Strings like `{0}`, `{name}`, `%1`, and HTML-ish Qt
markup are part of the UI contract.

Good:

```text
Could not save settings: {0}
```

Bad:

```text
Could not save settings:
```

If a placeholder looks strange, keep it and ask in the pull request.

## CI Expectations

CI validates:

- locale filenames
- `<TS language="...">` metadata
- translation compilation
- the regular Python quality checks

Release builds also recompile translations before packaging the app.
