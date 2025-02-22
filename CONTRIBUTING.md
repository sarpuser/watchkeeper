# Contributing to Watchkeeper

Thank you for your interest in contributing to Watchkeeper! This document provides guidelines and workflows for contributing to the project.

## Development Environment Setup

1. Fork the repository
2. Clone your fork locally
3. Create a Python virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Code Style

- Use camelCase for variable and function names
- Use CapitalCamelCase for class names
- Write self-documenting code with descriptive names
- Include units in variable/function names when it improves readability
- Avoid nesting more than 3 levels deep
- Write tests for all new code
- Follow PEP 8 guidelines (enforced by ruff)

## Git Workflow

1. Create a new branch from `dev`:
   - For new features: `feat/feature-name`
   - For bug fixes: `fix/bug-name`

2. Make your changes, following these guidelines:
   - Each commit should be a complete, reviewable unit
   - Write clear commit messages
   - Include tests for new functionality
   - Update documentation as needed

3. Before submitting:
   - Run tests locally: `pytest`
   - Check code formatting: `ruff format --check .`
   - Run type checking: `mypy .`
   - Run security checks: `bandit -r src/`

4. Push your changes and create a pull request to the `dev` branch

## Pull Request Process

- All PRs must target the `dev` branch
- PRs must pass all automated checks:
   - Linting (ruff)
   - Type checking (mypy)
   - Security checks (bandit)
   - Code formatting (ruff)
   - Unit tests


## Notes

- Infrastructure changes (changes to `.github` directory) are not accepted from forks
- The project aims to be resource-efficient for systems like Raspberry Pi Zero W
- Core functionality should remain lightweight and modular

## Getting Help

If you need help or have questions:

1. Check existing issues and documentation
2. Open a new issue with:
   - Clear description of your question/problem
   - Steps to reproduce if applicable
   - Relevant system information
   - Any error messages or logs

Thank you for contributing to Watchkeeper!