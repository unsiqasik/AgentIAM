# Contributing to AgentIAM

First off, thank you for considering contributing to AgentIAM! It's people like you who make AgentIAM such a great tool.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs
- Use the **Bug Report** issue template.
- Provide a clear description and reproduction steps.
- Check if the bug has already been reported.

### Suggesting Enhancements
- Use the **Feature Request** issue template.
- Explain why this enhancement would be useful.

### Pull Requests
1. **Fork** the repository and create your branch from `main`.
2. **Setup** your development environment following [DEVELOPMENT.md](DEVELOPMENT.md).
3. **Commit** your changes. Use [Conventional Commits](https://www.conventionalcommits.org/) if possible.
4. **Test** your changes. Add new tests for new features.
5. **Lint & Type Check** your code. We use Ruff, Black, and MyPy.
6. **Submit** the PR using the provided template.

## PR Validation & Branch Protection

To maintain high code quality, we have strict automated checks:
- **Linting**: Ruff and Black must pass.
- **Type Checking**: MyPy must pass.
- **Security**: Bandit and Safety scans must be clean.
- **Tests**: Pytest must pass on all supported Python versions (3.10 - 3.13).
- **Review**: At least one maintainer must approve the PR.

## Style Guidelines

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/).
- Use type hints for all function signatures.
- Document classes and functions using Google-style docstrings.

### Documentation
- Keep documentation up-to-date with code changes.
- Use clear and concise English.

## Maintainers

This project is maintained by @SHAURYASANYAL3.
