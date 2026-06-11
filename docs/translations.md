# Translations

GoH Mod Manager uses Qt translation files for the desktop UI.

The recommended path is Weblate:
[GoH Mod Manager - Qt UI](https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/).
It gives translators a web interface, handles language files for us, and keeps
the contribution flow much lighter than asking people to edit Qt files by hand.

The short version:

- translators work on `.ts` files
- the app loads compiled `.qm` files
- Weblate is the preferred collaboration path for UI translations
- CI validates naming, metadata, and compilation

The detailed maintainer workflow lives next to the translation files in
`src/ui/i18n/README.md`.

## Where Files Live

```text
src/ui/i18n/
├── en.ts
├── fr.ts
├── ru.ts
├── zh_Hans.ts
├── en.qm
├── fr.qm
├── ru.qm
└── zh_Hans.qm
```

The `.ts` files are the source of truth. The `.qm` files are generated runtime
artifacts used by the app.

## Local Commands

Validate translation files:

```bash
uv run python scripts/validate_translations.py
```

Refresh `.ts` catalogs after UI text changes:

```bash
uv run python scripts/build_translations.py --no-compile
```

Compile runtime `.qm` files:

```bash
uv run python scripts/build_translations.py --no-update
```

## Weblate

Use Weblate for normal translation work:

[https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/](https://hosted.weblate.org/projects/goh-mod-manager/qt-ui/)

This is the easiest way to suggest wording, improve an existing language, or
start a new translation. It also keeps review focused on the actual UI text
instead of file formatting.

Technical setup:

- file mask: `src/ui/i18n/*.ts`
- base language: `src/ui/i18n/en.ts`
- file format: Qt Linguist Translation File

New languages should follow Qt locale naming, such as `fr.ts`, `ru.ts`, or
`zh_Hans.ts`.

## Runtime Behavior

The app discovers available languages from compiled `.qm` files. That keeps the
settings UI data-driven: adding a valid translation file and compiling it is
enough for the language to become available.
