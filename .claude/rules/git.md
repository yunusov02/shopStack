# Git rules

- `main` is protected: no direct commits; changes land only through PRs with green CI.
- Branch name format: `<type>/<stage>-<short-name>`. Examples: `chore/0-tooling`, `feat/0-app-factory`, `fix/1-otp-cooldown`.
- Commits follow **Conventional Commits**, in English, with the module name as scope. Examples:
  - `feat(catalog): add barcode lookup`
  - `fix(sales): ...`
  - `chore: ...`, `test: ...`, `refactor: ...`, `ci: ...`
  - `docs(adr): ...`
- One PR covers one roadmap task (or a logical part of it). Smaller PRs get better reviews.
- The user commits and pushes; Claude does not.
