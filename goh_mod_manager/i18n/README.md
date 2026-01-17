# Translation sources (.ts) and compiled Qt binaries (.qm) live here.

## Expected names:

- goh_mod_manager_en.ts
- goh_mod_manager_fr.ts
- goh_mod_manager_ru.ts
- goh_mod_manager_zh.ts
- goh_mod_manager_de.ts
- ...

Compiled binaries (generated from the `.ts` sources):

- goh_mod_manager_en.qm
- goh_mod_manager_fr.qm
- goh_mod_manager_ru.qm
- goh_mod_manager_zh.qm
- goh_mod_manager_de.qm
- ...

## Workflow:

1) Generate or update a translation source file:

    - Create a new language file:
      `.\scripts\qt\update_translations.ps1 -Language fr`
    - Update all existing `.ts` files in this folder:
      `.\scripts\qt\update_translations.ps1`

2) Translate with Qt Linguist:
   `pyside6-linguist goh_mod_manager/i18n/goh_mod_manager_fr.ts`

3) Compile to a `.qm` binary for local testing:
   `pyside6-lrelease goh_mod_manager/i18n/goh_mod_manager_fr.ts`

The CI build compiles `.qm` files automatically from the committed `.ts` sources.
