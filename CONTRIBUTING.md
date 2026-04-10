# Contributing to FreeDF

Thank you for your interest in contributing to FreeDF! This guide will help you get started.

## Prerequisites

- Python 3.11 or higher
- Git

## Development Setup

1. Fork and clone the repository:

```bash
git clone https://github.com/<your-username>/FreeDF.git
cd FreeDF
```

2. Install in development mode:

```bash
pip install -e ".[dev]"
```

3. Verify the setup:

```bash
ruff check src/ tests/
mypy src/
pytest
```

## Running Tests

```bash
# Run all non-UI tests (no display required)
pytest -m "not ui"

# Run all tests (requires display or xvfb)
pytest

# Run with coverage
pytest --cov
```

## Linting and Formatting

```bash
# Check for lint errors
ruff check src/ tests/

# Check formatting
ruff format --check src/ tests/

# Auto-fix lint errors
ruff check --fix src/ tests/

# Auto-format code
ruff format src/ tests/
```

## Type Checking

```bash
mypy src/
```

## Code Style

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.
- Line length: 88 characters.
- All configuration is in `pyproject.toml`.

## Architecture Rules

**The most important rule**: `core/`, `commands/`, `rendering/`, and `io/` must **never** import Qt or PySide6. Only `ui/` knows about Qt. This ensures the core logic is testable without a display server.

## Git Workflow

1. Create a branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```

2. Make your changes and commit using [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` — new feature
   - `fix:` — bug fix
   - `docs:` — documentation only
   - `refactor:` — code change that neither fixes a bug nor adds a feature
   - `test:` — adding or updating tests
   - `chore:` — maintenance tasks

3. Push and open a Pull Request against `main`.

## Pull Request Checklist

- [ ] My code passes `ruff check` and `ruff format --check`
- [ ] My code passes `mypy src/`
- [ ] I have added or updated tests for my changes
- [ ] All tests pass locally (`pytest`)
- [ ] I have linked the relevant issue (if applicable)

## Reporting Bugs

Please use the [Bug Report template](https://github.com/FreeDF/FreeDF/issues/new?template=bug_report.yml) and include:
- FreeDF version
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
