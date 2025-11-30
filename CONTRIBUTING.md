# Contributing to RAGBrain MCP

Thank you for your interest in contributing to RAGBrain MCP! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributions from everyone.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ragbrain/ragbrain-mcp.git
   cd ragbrain-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"

   # Or using pip
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. Verify the setup:
   ```bash
   pytest
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ragbrain_mcp --cov-report=html

# Run specific test file
pytest tests/test_tools.py

# Run with verbose output
pytest -v
```

### Code Quality

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
ruff check src tests

# Auto-fix issues
ruff check --fix src tests

# Format code
ruff format src tests
```

We use [mypy](https://mypy.readthedocs.io/) for type checking:

```bash
mypy src
```

### Pre-commit Checks

Before submitting a PR, ensure:

1. All tests pass: `pytest`
2. Code is formatted: `ruff format src tests`
3. No linting issues: `ruff check src tests`
4. Type checks pass: `mypy src`

## Making Changes

### Branching Strategy

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

3. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues when relevant ("Fix #123: ...")

### Pull Request Guidelines

1. **Title**: Clear, concise description of the change
2. **Description**: Explain what and why (not how - the code shows that)
3. **Testing**: Describe how you tested the changes
4. **Breaking Changes**: Clearly note any breaking changes

## Project Structure

```
ragbrain-mcp/
├── src/ragbrain_mcp/
│   ├── __init__.py      # Package metadata
│   ├── config.py        # Configuration management
│   ├── client.py        # RAGBrain API client
│   ├── formatters.py    # Output formatters
│   ├── tools.py         # MCP tool definitions
│   └── server.py        # MCP server entry point
├── tests/
│   ├── conftest.py      # Test fixtures
│   ├── test_config.py   # Config tests
│   ├── test_client.py   # Client tests
│   ├── test_formatters.py
│   └── test_tools.py    # Tool handler tests
├── pyproject.toml       # Project configuration
└── README.md            # Documentation
```

## Adding New Features

### Adding a New Tool

1. Define the tool constant in `tools.py`:
   ```python
   TOOL_NEW_FEATURE = "ragbrain_new_feature"
   ```

2. Add the tool definition in `get_tool_definitions()`:
   ```python
   Tool(
       name=TOOL_NEW_FEATURE,
       description="...",
       inputSchema={...}
   )
   ```

3. Add the handler method in `ToolHandler`:
   ```python
   async def _handle_new_feature(self, arguments: dict) -> list[TextContent]:
       ...
   ```

4. Add the dispatch in `handle()`:
   ```python
   elif name == TOOL_NEW_FEATURE:
       return await self._handle_new_feature(arguments)
   ```

5. Add a formatter if needed in `formatters.py`

6. Add tests for the new tool

### Adding Configuration Options

1. Add the field in `Settings` class in `config.py`
2. Update the README with the new environment variable
3. Add tests for validation

## Reporting Issues

When reporting issues, please include:

1. Python version
2. Operating system
3. RAGBrain MCP version
4. Steps to reproduce
5. Expected vs actual behavior
6. Error messages or logs

## Questions?

Feel free to open an issue for questions or discussions about the project.

Thank you for contributing!
