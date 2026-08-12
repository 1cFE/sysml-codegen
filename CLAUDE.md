# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sysml-codegen transforms SysML v2 models into executable Python code for TEAx-style simulation frameworks. It extracts calculation definitions from SysML, builds a computation graph, and generates Pydantic schemas, TEAx module wrappers, implementation stencils, and pipeline YAML.

## Commands

```bash
# Install (requires the agentic-mbse companion checkout beside this one)
uv pip install -e ../agentic-mbse && uv pip install -e ".[dev]"

# Run tests (dev is an optional extra, so it must be named)
uv run --extra dev pytest tests/

# Run single test
uv run --extra dev pytest tests/unit/test_extractor.py -k test_name

# Type check
uv run --extra dev mypy src/

# Lint
uv run --extra dev ruff check src/

# Run code generation (live extraction; needs the syside license)
uv run sysml-codegen generate --models path/to/models --output path/to/output --package-name my_package

# Capture a v6 instance-graph snapshot (needs the syside license)
uv run sysml-codegen snapshot --models path/to/models --output path/to/instance_graph_snapshot.json

# Run code generation from that snapshot (license-free; mutually exclusive with --models)
uv run sysml-codegen generate --from-snapshot path/to/snapshot --output path/to/output --package-name my_package
```

The licensed suite needs `SYSIDE_LICENSE_KEY`, which lives in the companion checkout's `.env`
(`set -a; source ../agentic-mbse/.env; set +a`). Without it the license-gated tests skip rather
than fail, so a green run with no key is not a full run.

## Architecture

### Processing Pipeline

`run_codegen` (`cli/__init__.py`) is the single public generation entry point and constructs
exactly one way. `--models` and `--from-snapshot` are two *sources* for the same authority, not
two implementations.

1. **Extraction** (`extraction/`) - Parse SysML models via `agentic_mbse.sysml.syside_adapter.SysideAdapter`. `SysMLDataExtractor` loads the model and extracts `CalculationDefinitionData`. This is the only step that needs the syside license.

2. **Elaboration** (`elaboration/`) - `elaborate()` turns the loaded model into an `InstanceGraph`: one attribute node per modelled value occurrence, with consumers holding typed node references. References resolve against node identity — occurrence enumeration, never qualified-name string matching. A model that does not elaborate cleanly is refused (`ElaborationError` for readiness findings, `ElaborationDiagnosticError` for validation diagnostics).

3. **Projection** (`elaboration/project.py`) - `project()` renders the resolved graph onto a `ComputationGraph` (Pydantic model, `resolution/models.py`) - the single source of truth for pipeline structure. It renders identifiers, classifies sources elaboration already resolved, and orders the modules. Semantics are complete before it runs.

   The graph is reached through an `ExactPipelineContext` (`orchestration/exact_pipeline_context.py`), which holds the sealed instance-graph bytes plus a receipt: it cannot be mutated, and every read re-decodes, re-projects, and refuses a graph the receipt disagrees with.

4. **Generation** (`generation/`) - Jinja2 templates render the ComputationGraph into:
   - TEAx module wrappers (`modules/`)
   - Implementation stencils (`handwritten/`)
   - Pipeline YAML (`pipelines/`)
   - Parameter group schemas and JSON templates (`schemas/`, `inputs/`)
   - Module registry (`__init__.py`)

   Four preflight checks run before any output is written or cleared: constraint name safety,
   duplicate output paths, params coverage (V11), and registry class-name collisions.

5. **Sealing** (`contracts/`) - A semantic `ModelContract` over the graph and a physical `PackageContract` over the final on-disk bytes, on the live and from-snapshot paths alike.

6. **Snapshot** (`snapshot/`) - The **v6 instance-graph snapshot** decouples generation from the
   syside license. `sysml-codegen snapshot` admits the sources, elaborates them once, and seals
   the graph into an envelope; `generate --from-snapshot` loads that envelope license-free. A v5
   extraction snapshot is refused at load, by name. The envelope's digest is unkeyed, so it
   proves coherence and not authenticity; pass `source_roots` when provenance matters. See
   `docs/architecture/reference/27-snapshot-generation.md`.

### Retired — read before trusting a document

The legacy string-resolution stack is **gone from the tree**, deleted by the cutover
recovery's four retirement steps (2026-08-12, `19072ad` / `82c7951` / `882fc8d` / `3071fba`):
`orchestration/pipeline_builder.py`, `orchestration/snapshot_context.py`, `analysis/`'s
backtracker, parameter groups and constraint lowering, `resolution/graph_builder.py`,
`resolution/producer_resolution.py`, `resolution/producer_completeness.py`,
`core/output_registry.py`, the v5 `snapshot/{loader,serializer,graph_rebuild}.py`,
`elaboration/diff.py`, both v5 capture scripts, and every committed
`extraction_snapshot.json` fixture. The exact route is the only authority left, and the
v5 exports it kept are gone too — `snapshot/__init__.py` re-exports nothing.

`tests/conformance/test_public_authority_switch.py` and
`tests/unit/test_elaboration_import_boundaries.py` now pin the **absence**: the modules do
not exist, and the CLI names none of them. `orchestration/pipeline_context.py` survives as
the `SysMLParsingError` / `CodeGenerationError` re-export point and carries no
`PipelineContext`.

Reference documents 03, 04, 05, 07, 10, 11, 12, 13, 17, 24, and 25 describe that stack and
open with a retiring banner; document 09 is mixed and says which models are which. Their
rewrite is a separate authorship pass that has not run. **Do not read them as descriptions
of what the product does.**

### Key Data Models

- `InstanceGraph` - The elaborated model: `AttrNode`, `CalcNode`, `ConstraintNode`, occurrences
- `CalculationDefinitionData` - Extracted calc def with inputs/outputs
- `ComputationGraph` - Pipeline modules with inputs wired to upstream outputs or entry points
- `PipelineModule` - Single calculation in the pipeline with `ModuleInput`/`ModuleOutput`
- `ExactPipelineContext` / `ProjectionReceipt` - The sealed graph and what it promises

### Naming Conventions (ADR-003)

- **Qualified names**: Use `__` separator (e.g., `Namespace__Part__calc_usage`)
- **Module names**: Lowercase EQN (execution qualified name)
- **Channel names**: PQN format (`usage_qn__output_name`)
- **Module types**: PascalCase derived from calc def qualified name

### Entry Point Classification (ADR-001)

Three types of entry points that become JSON inputs:
- `LIBRARY_DEFAULT`: Unbound formal falling back to its calc def default
- `DESIGN_ATTRIBUTE`: Supplied by a modelled attribute
- `USAGE_LITERAL`: Literal written in a calc usage binding

The type is decided where projection mints the entry point, not by a later classification pass.
Two rules govern the public keys, and both show up in the shipped JSON:

- A `DESIGN_ATTRIBUTE` keys by the **supplying attribute's** display path, so two calculations
  reading one modelled value share one key. The other two key by `{consumer}__{formal}`.
- The key carries the occurrence index for an arrayed child
  (`…__battery_pack[0]__capacity_kwh`). The generated schema declares a sanitized field name
  and keeps the exact key as its `alias`.

A group is named after the file that **declares** the owner node, not the file that uses it.

## Dependencies

- `agentic-mbse`: SysIDE adapter and shared data models (installed from `../agentic-mbse`)
- `jinja2`: Template rendering for code generation
- `pydantic`: Data validation and schema models
