# Contributing to LiteDocs

Thank you for your interest in contributing to LiteDocs! We welcome contributions of all kinds — bug reports, feature requests, documentation improvements, and code changes.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/litedocs.git
   cd litedocs
   ```
3. **Install** development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. **Run tests** to verify everything works:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Add or update tests as needed
4. Run the full test suite:
   ```bash
   pytest tests/ -v --tb=short
   ```
5. Commit your changes with a clear message:
   ```bash
   git commit -m "feat: add support for custom theme colors"
   ```
6. Push to your fork and open a Pull Request

## Commit Message Convention

We follow a simplified [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `test:` — Adding or updating tests
- `refactor:` — Code refactoring (no feature or fix)
- `chore:` — Build, CI, or tooling changes

## Code Style

- All code, comments, and documentation are written in **English**
- Follow existing code patterns and conventions
- Use type hints for all function signatures
- Keep functions focused and small
- Add docstrings to public functions and classes

## Testing

- Every new feature must include tests
- Every bug fix should include a regression test
- Tests are located in the `tests/` directory
- We use `pytest` with `pytest-asyncio` for async tests
- Run the full suite before submitting:
  ```bash
  pytest tests/ -v
  ```

## Pull Request Guidelines

- Keep PRs focused — one feature or fix per PR
- Include a clear description of what changed and why
- Reference any related issues (e.g., "Fixes #123")
- Ensure all tests pass
- Update documentation if your change affects user-facing behavior
- Update `CHANGELOG.md` for notable changes

## Reporting Bugs

When filing a bug report, please include:

- Python version (`python --version`)
- Operating system (macOS, Linux, Windows)
- Steps to reproduce the issue
- Expected vs. actual behavior
- Relevant log output or error messages

## Requesting Features

Feature requests are welcome! Please include:

- A clear description of the feature
- The use case or problem it solves
- Any suggestions for implementation (optional)

## Project Structure

See the [README](README.md#project-structure) for an overview of the codebase.

Key documents for contributors:
- `docs/DESIGN.md` — Architecture and product design
- `docs/CONVENTIONS.md` — Format specifications
- `docs/TASKS.md` — Task breakdown and roadmap

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

By contributing to LiteDocs, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

Questions? Open an issue or reach out at [Litestartup](https://www.litestartup.com).
