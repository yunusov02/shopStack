# Git rules

- `main` is protected: no direct commits; changes land only through PRs (with green CI once CI exists, slice 12).
- Branch name format: `<type>/<slice>-<short-name>`, slice number with two digits. Examples: `feat/01-sell-by-barcode`, `feat/02-stock-ledger`, `fix/13-otp-cooldown`.
- Commits follow **Conventional Commits**, in English, with the module name as scope. Examples:
  - `feat(catalog): add barcode lookup`
  - `fix(sales): ...`
  - `chore: ...`, `test: ...`, `refactor: ...`, `ci: ...`
  - `docs(adr): ...`
- One PR covers one slice checklist item or spec step (or a logical part of it). Smaller PRs get better reviews.
- The user commits and pushes; Claude does not.
