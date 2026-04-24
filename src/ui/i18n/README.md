# Translation sources (`.ts`) and compiled Qt binaries (`.qm`) live here.

## Naming

Use locale-based file names:

- `en_US.ts`
- `fr_FR.ts`
- `ru_RU.ts`
- `zh_CN.ts`
- `de_DE.ts`

The same naming applies to compiled runtime files:

- `en_US.qm`
- `fr_FR.qm`
- `ru_RU.qm`
- `zh_CN.qm`
- `de_DE.qm`

Invalid names are rejected by `scripts/validate_translations.py`.

## Workflow

1. Update the source catalog from Python code:

   ```bash
   uv run python scripts/build_translations.py --no-compile
   ```

2. Translate the `.ts` files in Qt Linguist or Weblate.

3. Validate translation metadata and naming:

   ```bash
   uv run python scripts/validate_translations.py
   ```

4. Compile runtime `.qm` files:

   ```bash
   uv run python scripts/build_translations.py --no-update
   ```

The application discovers selectable languages dynamically from the compiled
runtime files, so a language becomes available in the settings UI as soon as
its `.qm` file exists.
