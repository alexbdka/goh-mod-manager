# Translation sources (.ts) and compiled Qt binaries (.qm) live here.

## Expected names:

- en_US.ts
- fr_FR.ts
- ru_RU.ts
- zh_CN.ts
- de_DE.ts
- ...

Compiled binaries (generated from the `.ts` sources):

- en_US.qm
- fr_FR.qm
- ru_RU.qm
- zh_CN.qm
- de_DE.qm
- ...

## Workflow:

1) Generate or update translation source files:

   From the project root, run the translation script to scan the Python files and update the `.ts` files:
   ```bash
   uv run python scripts/build_translations.py
   ```

2) Translate with Qt Linguist:

   Open the target `.ts` file with Qt Linguist to add or modify translations.
   ```bash
   pyside6-linguist src/ui/i18n/fr_FR.ts
   ```

3) Compile to a `.qm` binary:

   The `.qm` binaries are automatically generated when you run the build script:
   ```bash
   uv run python scripts/build_translations.py
   ```
   Or you can compile a single file manually:
   ```bash
   pyside6-lrelease src/ui/i18n/fr_FR.ts
   ```

The translation system uses QTranslator and requires the `.qm` files to be present at runtime.