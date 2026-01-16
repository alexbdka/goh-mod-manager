# Translation files go here as Qt .qm binaries.

## Expected names:

- goh_mod_manager_en.qm
- goh_mod_manager_fr.qm
- goh_mod_manager_ru.qm
- goh_mod_manager_zh.qm
- goh_mod_manager_de.qm
- ...

## Workflow:

1) `scripts/qt/update_translations.ps1`
2) `pyside6-linguist goh_mod_manager/i18n/goh_mod_manager_fr.ts`
3) `pyside6-lrelease goh_mod_manager/i18n/goh_mod_manager_fr.ts`
