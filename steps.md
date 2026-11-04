1. `uv init .` - intialize project
2. `uv lock`   - create and update the uv.lock file
3. `uv add "fastapi[standard]"`
4. `uv add sqlalchemy`
5. `uv sync` from other pc

6. `Ruff` is extermly fast Python linter and code formatter (isort Black Flake)


7. To check run command `uv run ruff check` or if you want to check specific directory use like `uv run ruff check src/`

8. To fix errors we need to format them `uv run ruff format src/`


9. `mypy` is Python static type checker

10. Use it like `uv run mypy src/`

11. Install pre-commit install `uv add --dev pre-commit`

12. install `pre-commit` -> `uv run pre-commit install`


