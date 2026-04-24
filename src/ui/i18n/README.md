# Translation Files

This directory stores Qt translation source files (`.ts`) and compiled runtime
files (`.qm`).

## Naming Convention

Translation files must use locale-based names such as:

- `en_US.ts`
- `fr_FR.ts`
- `zh_CN.ts`

Compiled runtime files follow the same convention:

- `en_US.qm`
- `fr_FR.qm`
- `zh_CN.qm`

Invalid names or inconsistent metadata are rejected by
`scripts/validate_translations.py`.

## Workflow

1. Update the translation source catalog:

   ```bash
   uv run python scripts/build_translations.py --no-compile
   ```

2. Translate through **Weblate** or edit the `.ts` files with Qt Linguist.

3. Validate the translation tree:

   ```bash
   uv run python scripts/validate_translations.py
   ```

4. Compile runtime `.qm` files:

   ```bash
   uv run python scripts/build_translations.py --no-update
   ```

## Runtime Behavior

The application discovers selectable languages dynamically from the compiled
`.qm` files present in this directory. A new language becomes selectable in the
settings UI as soon as its runtime file exists and passes validation.
