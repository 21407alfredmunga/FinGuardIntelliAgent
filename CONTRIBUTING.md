# Contributing to FinGuard IntelliAgent

Thank you for your interest in FinGuard IntelliAgent! This is an ADK capstone project, but feedback and suggestions are always welcome.

## Project Status

**Current Milestone:** Milestone 1 (Project Setup & Scaffolding)  
**Next Milestone:** Milestone 2 (Core Implementation)

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:

1. Check if the issue already exists in GitHub Issues
2. If not, create a new issue with:
   - Clear description of the problem/suggestion
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment details (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please:

1. Open an issue with the "enhancement" label
2. Describe the feature and its use case
3. Explain how it benefits Kenyan SMEs
4. Consider implementation complexity

### Code Contributions

As this is a capstone project, direct code contributions are not currently accepted. However, you can:

- Fork the repository for your own experiments
- Share your modifications as suggestions
- Provide feedback on the implementation approach

## Development Setup

See the main [README.md](README.md) for setup instructions.

## Code Standards

### Python Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for all functions/classes
- Keep functions focused and modular

### Formatting Tools

```bash
# Format code
black .

# Sort imports
isort .

# Check linting
flake8 .

# Type checking
mypy .
```

### Testing

```bash
# Run tests (Milestone 2+)
pytest

# With coverage
pytest --cov=backend --cov=agent --cov=tools
```

## Commit Messages

Use clear, descriptive commit messages:

```
[Component] Brief description

Detailed explanation if needed.
- Bullet points for specific changes
- Reference issues: Fixes #123
```

Examples:
```
[Backend] Add health check endpoint

[Tools] Implement SMS parser placeholder

[Docs] Update README with setup instructions
```

## Project Structure

See [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) for detailed architecture information.

## Questions?

Open an issue with the "question" label or reach out via GitHub.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for your interest in FinGuard IntelliAgent!** 🚀
