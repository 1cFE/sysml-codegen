# sysml-codegen

SysML v2 to Python code generation framework.

## Overview

This package transforms SysML v2 models into executable Python code for TEAx-style simulation frameworks.

## Installation

### Using uv (recommended)

```bash
cd ~/sysml-codegen
uv venv
source .venv/bin/activate
uv pip install -e ~/agentic-mbse   # install dependency first
uv pip install -e .                 # install this package
```

### Using pip

```bash
pip install -e ~/agentic-mbse   # install dependency first
pip install -e .                 # install this package
```

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/

# Type check
uv run mypy src/

# Lint
uv run ruff check src/
```

## Usage

```bash
sysml-codegen --models path/to/models --output path/to/output --package-name my_package
```

Or with uv:

```bash
uv run sysml-codegen --models path/to/models --output path/to/output --package-name my_package
```

## Dependencies

- agentic-mbse: Shared data models and SysIDE adapter
- jinja2: Template rendering
- pydantic: Data validation
- pyyaml: YAML configuration

## License

MIT
