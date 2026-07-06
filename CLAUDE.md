# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sysml-codegen transforms SysML v2 models into executable Python code for TEAx-style simulation frameworks. It extracts calculation definitions from SysML, builds a computation graph, and generates Pydantic schemas, TEAx module wrappers, implementation stencils, and pipeline YAML.

## Commands

```bash
# Install (requires agentic-mbse dependency)
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/

# Run single test
uv run pytest tests/unit/test_extractor.py -k test_name

# Type check
uv run mypy src/

# Lint
uv run ruff check src/

# Run code generation (live extraction; needs the syside license)
uv run sysml-codegen generate --models path/to/models --output path/to/output --package-name my_package

# Run code generation from a captured snapshot (license-free; mutually exclusive with --models)
uv run sysml-codegen generate --from-snapshot path/to/snapshot --output path/to/output --package-name my_package
```

## Architecture

### Processing Pipeline

1. **Extraction** (`extraction/`) - Parse SysML models via `agentic_mbse.sysml.syside_adapter.SysideAdapter`. `SysMLDataExtractor` produces `CalculationDefinitionData` and `PartDefinitionData` with input/output attributes, constraints, and source locations.

2. **Analysis** (`analysis/`) - `DependencyBacktracker` traces calculation dependencies and resolves bindings. `ParameterGroupDeriver` classifies entry points into parameter groups for JSON input files.

3. **Resolution** (`resolution/`) - `graph_builder.build_computation_graph()` converts backtracking results into a `ComputationGraph` (Pydantic model) - the single source of truth for pipeline structure.

4. **Generation** (`generation/`) - Jinja2 templates render the ComputationGraph into:
   - TEAx module wrappers (`modules/`)
   - Implementation stencils (`handwritten/`)
   - Pipeline YAML (`pipelines/`)
   - Parameter group schemas and JSON templates (`schemas/`, `inputs/`)
   - Module registry (`__init__.py`)

5. **Snapshot** (`snapshot/`) - Serialized extraction snapshots decouple generation from
   the syside license: `generate --from-snapshot` rebuilds the pipeline context from a
   captured snapshot (versioned format with `snapshot_format_version`; CalcUsage
   auto-implementation preserved via serialized `compilation_results`). See
   `docs/architecture/reference/27-snapshot-generation.md`.

### Key Data Models

- `CalculationDefinitionData` - Extracted calc def with inputs/outputs
- `CalcUsageData` - Calculation usage instance with bindings
- `BacktrackingResult` - Resolved dependencies and entry points
- `ComputationGraph` - Pipeline modules with inputs wired to upstream outputs or entry points
- `PipelineModule` - Single calculation in the pipeline with `ModuleInput`/`ModuleOutput`

### Naming Conventions (ADR-003)

- **Qualified names**: Use `__` separator (e.g., `Namespace__Part__calc_usage`)
- **Module names**: Lowercase EQN (execution qualified name)
- **Channel names**: PQN format (`usage_qn__output_name`)
- **Module types**: PascalCase derived from calc def qualified name

### Entry Point Classification (ADR-001)

Three types of entry points that become JSON inputs:
- `LIBRARY_DEFAULT`: Unbound parameter using calc def default
- `DESIGN_ATTRIBUTE`: Literal from design part definition
- `USAGE_LITERAL`: Literal in calc usage binding

## Dependencies

- `agentic-mbse`: SysIDE adapter and shared data models (installed from `../agentic-mbse`)
- `jinja2`: Template rendering for code generation
- `pydantic`: Data validation and schema models
