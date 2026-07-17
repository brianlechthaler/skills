# AGENTS.md

## Cursor Cloud specific instructions

This repo is a **Python Agent Skills library + cross-platform installer** (`install.py`). There is no web app, server, or database — development is fully offline and consists of the pytest suite, ruff lint, a README-count sync check, and running the `install.py` CLI.

### Running tooling
- Dev dependencies (`pytest`, `pytest-cov`, `ruff`) are installed with `pip --user`, so their console scripts land in `~/.local/bin`, which is **not on `PATH`**. Invoke them as modules instead: `python3 -m pytest`, `python3 -m ruff ...`. (`python3 scripts/...` and `python3 install.py ...` work directly.)
- The pytest config enforces **100% coverage on `install.py`** (`--cov-fail-under=100`); a change that adds an untested branch in `install.py` will fail the suite even if all assertions pass.

### Standard commands (already documented in CI — see `.github/workflows/test.yml` and `lint.yml`)
- Tests: `python3 -m pytest`
- Lint: `python3 -m ruff check install.py skill_categories.py skill_validate.py scripts/ tests/`
- Format check: `python3 -m ruff format --check install.py skill_categories.py skill_validate.py scripts/ tests/`
- README skill count sync: `python3 scripts/sync_readme_skill_count.py --check`

### Installer CLI (the product; see `README.md` / `USAGE.md`)
- Discover: `python3 install.py --list` / `--list-agents` / `--list-by-category`
- Install a skill into a project: `python3 install.py -s <skill> -a <agent> [--copy|--as-rule] -y` (defaults to symlink; use `--copy` in throwaway/temp dirs).
- Uninstall: `python3 install.py -s <skill> -a <agent> --uninstall -y`
- Prefer running installer smoke tests against a temporary directory so you don't create `.cursor/`, `.claude/`, etc. artifacts in the repo root.
