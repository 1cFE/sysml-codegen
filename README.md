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

The real-TEAx execution lane (`pytest tests/execution/ -m execution`) requires TEAx commit `ca5d490` or a successor carrying its evidence schema v3 numeric-publication fix. Numeric ExitPoint values must reach study evidence under their existing exit keys, whether a generated calculation returns a single numeric wrapper or multiple scalar fields. Boolean and structured constraint outputs are excluded from numeric evidence. The mixed-output acceptance test checks distinct calculated values before and after an input change, including a dependent single-output calculation and a reopened study store.

Bind execution dependencies with `CODEGEN_EXECUTION_PROVENANCE` and `TEAX_SIMKIT_PATH` as required by [the execution provenance fixture](tests/execution/conftest.py). Live generation also needs `SYSIDE_LICENSE_KEY`. Evidence schema v3 starts a new study lineage; old stores remain historical and cannot recover omitted values by querying them again. This runtime fix requires no generated-package representation change.

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
