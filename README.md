# sysml-codegen

Parse SysML v2 models, resolve their modeled occurrences, and emit executable Python packages for TEAx. Both live models and sealed v6 snapshots use the same exact elaboration and projection authority. Unsupported model forms refuse with diagnostics.

## Installation

From this repository, with `agentic-mbse` checked out beside it:

```bash
uv pip install -e ../agentic-mbse
uv pip install -e ".[dev]"
```

With pip, use the same relative paths: `pip install -e ../agentic-mbse` and `pip install -e ".[dev]"`. Live parsing and snapshot capture require a valid `SYSIDE_LICENSE_KEY`.

## Generation

```bash
# Live models: needs a SysIDE license.
uv run sysml-codegen generate --models path/to/models --output path/to/output --package-name my_package

# Capture once with the license, then generate without it.
uv run sysml-codegen snapshot --models path/to/models --output path/to/instance_graph_snapshot.json
uv run sysml-codegen generate --from-snapshot path/to/instance_graph_snapshot.json --output path/to/output --package-name my_package
```

The generated package includes schemas, input JSON, module wrappers, implementations, pipeline YAML, and semantic/physical contracts. Preserve completed implementations with `--overwrite --preserve-handwritten`; use `--smart-regen` for signature-aware regeneration. Units written on values remain parser facts; declaration comments are human documentation and do not supply generated units.

## Development

```bash
uv run --extra dev pytest tests/
uv run --extra dev mypy src/
uv run --extra dev ruff check src/
```

The default suite excludes the real-TEAx lane. Full licensed acceptance requires zero license skips; a green unlicensed subset is not a full validation result. See [CLAUDE.md](CLAUDE.md) for environment commands and [the architecture overview](docs/architecture/overview.md) for the generation route.

The real-TEAx lane (`pytest tests/execution/ -m execution`) needs TEAx's evidence schema v3 numeric-publication capability. Numeric single-output and multi-output values must reach study evidence under their existing exit keys, including dependent arithmetic and reopened-study checks. Boolean values retain numeric 0/1 representation; structured constraint outputs are excluded from numeric evidence.

Bind immutable dependencies with `CODEGEN_EXECUTION_PROVENANCE` and `TEAX_SIMKIT_PATH` as required by [the execution fixture](tests/execution/conftest.py). Live tests also need the license. Evidence schema v3 starts a new study lineage; querying an old store cannot restore omitted values. The runtime fix changes no generated-package representation.

## Dependencies and license

`agentic-mbse` supplies the SysIDE adapter and neutral model facts; Jinja2 renders templates; Pydantic defines schemas; PyYAML writes pipeline configuration. MIT license.
