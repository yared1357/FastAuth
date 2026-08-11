# Contributing to FastAuth

First off, **thank you** for considering contributing to FastAuth! 🎉

Every contribution matters — whether it's a bug fix, a new feature, better documentation, or even a typo correction.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Please report unacceptable behavior to the maintainers.

## Getting Started

### Types of Contributions

| Type | Label | Description |
|---|---|---|
| 🐛 Bug Fix | `bug` | Fix a reported issue |
| ✨ Feature | `feature` | Add new functionality |
| 📝 Documentation | `docs` | Improve or add documentation |
| 🧪 Tests | `tests` | Add or improve test coverage |
| ♻️ Refactor | `refactor` | Code improvements without changing behavior |
| 🏷️ Good First Issue | `good first issue` | Great for newcomers! |

### Finding Something to Work On

- Browse [open issues](https://github.com/fastauth/fastauth/issues)
- Look for the [`good first issue`](https://github.com/fastauth/fastauth/labels/good%20first%20issue) label if you're new
- Check the [roadmap](https://github.com/fastauth/fastauth/issues?q=label%3Aroadmap) for planned features

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git

### Setup Steps

1. **Fork & clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/fastauth.git
   cd fastauth
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install in development mode**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (optional but recommended)

   ```bash
   pre-commit install
   ```

5. **Verify your setup**

   ```bash
   pytest tests/ -v
   ruff check src/ tests/
   mypy src/fastauth/
   ```

## Making Changes

### Branch Naming

Create a descriptive branch from `main`:

```bash
git checkout -b feature/add-oauth2-google    # New feature
git checkout -b fix/jwt-token-expiry          # Bug fix
git checkout -b docs/improve-quickstart       # Documentation
```

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add OAuth2 Google provider
fix: handle expired refresh tokens gracefully
docs: add cookie transport configuration guide
test: add tests for password reset flow
refactor: simplify authentication backend interface
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=fastauth --cov-report=term-missing

# Run a specific test file
pytest tests/test_authentication.py -v

# Run a specific test
pytest tests/test_authentication.py::test_jwt_token_generation -v
```

### Test Requirements

- All new features **must** include tests
- Bug fixes **should** include a regression test
- Maintain **80%+ code coverage**

## Code Style

We use **Ruff** for linting and formatting, and **mypy** for type checking.

```bash
# Lint
ruff check src/ tests/

# Auto-fix lint issues
ruff check src/ tests/ --fix

# Format
ruff format src/ tests/

# Type check
mypy src/fastauth/
```

### Style Guidelines

- All public functions and classes **must** have docstrings (Google style)
- All functions **must** have type annotations
- Use `async`/`await` for all I/O operations
- Keep functions focused — one function, one responsibility
- Prefer composition over inheritance

## Pull Request Process

1. **Update your branch** with the latest `main`:

   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Ensure all checks pass**:

   ```bash
   pytest tests/ -v --cov=fastauth
   ruff check src/ tests/
   mypy src/fastauth/
   ```

3. **Update documentation** if you've changed or added functionality

4. **Update CHANGELOG.md** under the `[Unreleased]` section

5. **Submit your PR** with:
   - A clear title following conventional commits
   - A description of what changed and why
   - Reference to any related issues (e.g., `Closes #42`)

6. **Address review feedback** — maintainers may request changes

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted (`ruff format`)
- [ ] Linting passes (`ruff check`)
- [ ] Type checking passes (`mypy`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or clearly documented if unavoidable)

## Issue Guidelines

### Reporting Bugs

Use the [bug report template](https://github.com/fastauth/fastauth/issues/new?template=bug_report.md) and include:

- FastAuth version
- Python version
- FastAPI version
- Steps to reproduce
- Expected vs. actual behavior
- Error traceback (if applicable)

### Requesting Features

Use the [feature request template](https://github.com/fastauth/fastauth/issues/new?template=feature_request.md) and include:

- Problem description
- Proposed solution
- Alternatives considered
- Willingness to implement

---

## Questions?

Feel free to open a [discussion](https://github.com/fastauth/fastauth/discussions) or reach out in the issues. We're happy to help! 💬
