# Design: Codegen Runtime Gap Fixes

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-01T22:17:00Z
**Branch:** 1cfe_dev

## Overview

Fix three codegen runtime gaps that prevent generated output from executing as a TEAx pipeline, plus add comprehensive test coverage. Changes span 6 source files (1 deleted), 2 new test files, and 1 updated test file, plus a new test fixture.

## Related Artifacts

- **Spec:** `.project/active/codegen-runtime-gap-fixes/spec.md`
- **Research:** `/home/reid/1cfe/fusion-tea/.project/reports/codegen-runtime-gaps-2026-02-01-2047.md`
- **Root Cause:** `/home/reid/1cfe/fusion-tea/.project/research/20260201-210000_codegen-runtime-gaps-root-cause.md`
- **Gap 1 Findings:** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/findings.md`
- **Gap 1 Fix Plan:** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/fix-plan.md`
- **Epic:** `/home/reid/1cfe/fusion-tea/.project/backlog/epic-end-to-end-pipeline-derisking.md`

## Research Findings

### Gap 1: Empty design_params.json

**Root cause chain (confirmed by diagnostic scripts):**

1. `extract_design_attributes()` at `parameter_groups.py:87-127` defaults `design_path_filter="models/designs"` (line 89)
2. `build_pipeline_context()` at `initialization.py:140` calls `extract_design_attributes(extractor.model)` — no filter override passed
3. The chain spike model lives at `models/tests/codegen_chain_spike/design.sysml` — doesn't contain `"models/designs"`
4. Result: 0 design attributes extracted → empty `design_attr_by_qname` in graph builder → empty JSON

**Secondary issue:** When the path filter is broadened, library output attributes (e.g., `out attribute area : Real = length * width`) are also traversed. Their `OperatorExpression` values reference features, causing `evaluate_true_static_expression()` at `parameter_groups.py:188` to raise `ValueError`.

**Safety net mechanism:** The actual default resolution happens via `_group_entry_points_via_deriver()` in `graph_builder.py:326-336`, which calls `ParameterGroupDeriver.get_default_value()`. This performs a fuzzy match by simple name. The path filter fix enables this safety net by ensuring design attributes are extracted and indexed.

### Gap 2: Missing RootModel[float] Handler

**Root cause:**

1. `_build_exit_points()` at `pipeline.py:196-227` generates `RootModel[float]` type strings for single-output modules (line 218)
2. `generate_registry_function()` at `registry.py:30-74` only receives `entry_point_groups` — no exit point type info
3. Template at `registry_function.py.jinja2:38-47` renders `CUSTOM_SCHEMA_TYPES` from `parameter_groups` only
4. The generated `__init__.py` registers `DesignParams` but not `Float`/`RootModel[float]`
5. TEAx's output router has no handler → `PipelineValidationError`

**Key observation:** `_generate_primitives()` at `cli/__init__.py:99-113` already generates `primitives.py` containing `Float = RootModel[float]`. The fix needs to import and register this `Float` type.

### Gap 3: Static FusionParams Template

**Root cause:**

1. `_generate_schemas()` at `cli/__init__.py:127-161` unconditionally copies `templates/schemas_ref.py` to `{package_name}_schemas.py` (lines 138-143)
2. `schemas_ref.py` contains hardcoded `FusionParams` with 8 fusion-specific fields
3. This file is never referenced by any generated module, pipeline YAML, or registry

### Existing Test Patterns

- Tests at `tests/integration/test_full_pipeline.py` use `run_codegen()` with `GenerationConfig` and `sample_model_path` fixture
- `conftest.py` provides `sample_model_path` → `tests/fixtures/sample_model/`
- `test_generates_schemas()` (line 256-276) currently asserts either `ref_schema.exists()` or multioutput schemas — this must be updated
- Tests use `tmp_path` for output directories
- Some tests skip gracefully if SysML models can't load (`sample_extractor` fixture)

### Exit Point Type Collection

From `ComputationGraph.modules`, each `PipelineModule` has `outputs: list[ModuleOutput]`. Each `ModuleOutput` has:
- `field_name`: `"root"` for single-output, attribute name for multi-output
- `python_type`: e.g., `"float"`, `"int"`

The exit point types needed for registration are:
- Single-output: `RootModel[{python_type}]` → maps to `Float`, `Int`, etc. from `primitives.py`
- Multi-output: the generated BaseModel schema class (already in `schemas/`)

The `_map_output_type()` helper at `registry.py:159-179` already maps SysML types to primitive wrapper names (`"Real"` → `"Float"`). This can be reused.

---

## Proposed Design

### Component 1: Gap 1 — Design Path Filter Fix

#### 1a. Change default in `parameter_groups.py`

**File:** `src/sysml_codegen/analysis/parameter_groups.py`
**Line 89:** Change `design_path_filter: str = "models/designs"` → `design_path_filter: str = ""`

When `design_path_filter` is empty string, the filter check at lines 108-111 is skipped (`if design_path_filter:` is falsy for `""`), so all files are included. This is the existing behavior for an empty filter — no code change needed beyond the default value.

#### 1b. Wire `design_path_filter` through `build_pipeline_context()`

**File:** `src/sysml_codegen/generation/initialization.py`

Add `design_path_filter: str = ""` parameter to `build_pipeline_context()` signature (line 82-86). Pass it to `extract_design_attributes()` call at line 140:

```python
def build_pipeline_context(
    model_paths: list[Path],
    targets: list[str] | None = None,
    include_all: bool = True,
    design_path_filter: str = "",
) -> PipelineContext:
```

Line 140:
```python
design_attrs = extract_design_attributes(extractor.model, design_path_filter=design_path_filter)
```

#### 1c. Add `design_path_filter` to `GenerationConfig` and CLI

**File:** `src/sysml_codegen/cli/__init__.py`

Add field to `GenerationConfig` dataclass (after line 59):
```python
design_path_filter: str = ""
```

Add CLI argument to `gen_parser` (after `--verbose`, around line 553):
```python
gen_parser.add_argument(
    "--design-path-filter",
    type=str,
    default="",
    help="Substring filter for design file paths (default: accept all files)"
)
```

Wire in `cmd_generate()` at line 442-451:
```python
config = GenerationConfig(
    ...
    design_path_filter=args.design_path_filter,
)
```

Wire in `run_codegen()` at line 610:
```python
ctx = build_pipeline_context(
    [config.models_path],
    design_path_filter=config.design_path_filter,
)
```

#### 1d. Add crash guard for OperatorExpression

**File:** `src/sysml_codegen/analysis/parameter_groups.py`
**Lines 186-189:** Wrap the `evaluate_true_static_expression()` call:

```python
elif SysideAdapter.is_instance(expr, "OperatorExpression"):
    try:
        result = evaluate_true_static_expression(expr)
        return str(result)
    except (ValueError, TypeError):
        return None
```

This handles non-static expressions (e.g., `length * width` that reference features) by returning `None` instead of crashing. The `_parse_default_value()` method at line 703-712 already handles `None` gracefully.

---

### Component 2: Gap 2 — Exit Point Type Registration

#### 2a. Collect exit point types from ComputationGraph

**File:** `src/sysml_codegen/generation/registry.py`

Add a new parameter `exit_point_types` to `generate_registry_function()` and a helper to collect them:

```python
def _collect_exit_point_primitive_types(
    modules: list,
) -> list[str]:
    """Collect unique primitive wrapper type names needed for exit points.

    For single-output modules (field_name="root"), returns the wrapper type
    name from primitives.py (e.g., "Float" for python_type="float").

    Multi-output modules use BaseModel schemas which are already registered
    via entry_point_groups or schema generation.
    """
    TYPE_MAP = {
        "float": "Float",
        "int": "Int",
        "str": "String",
        "bool": "Bool",
    }
    types = set()
    for module in modules:
        for out in module.outputs:
            if out.field_name == "root":
                wrapper = TYPE_MAP.get(out.python_type)
                if wrapper:
                    types.add(wrapper)
    return sorted(types)
```

Update `generate_registry_function()` signature to accept `modules` from ComputationGraph:

```python
def generate_registry_function(
    calc_defs: list[CalculationDefinitionData],
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
    entry_point_groups: "list[ModelParameterGroup]",
    exit_point_primitive_types: list[str] | None = None,
) -> str:
```

Build context with both entry point groups and exit point types:

```python
context = {
    ...
    "parameter_groups": group_names,
    "exit_point_types": exit_point_primitive_types or [],
}
```

#### 2b. Update the Jinja2 template

**File:** `src/sysml_codegen/templates/registry_function.py.jinja2`

Add a primitives import when exit point types are present, and include them in `CUSTOM_SCHEMA_TYPES`:

```jinja2
{% for import_line in imports %}
{{ import_line }}
{% endfor %}

{# Parameter group schema imports #}
{% if schema_imports %}
{% for import_line in schema_imports %}
{{ import_line }}
{% endfor %}
{% endif %}

{# Primitive type imports for exit point registration #}
{% if exit_point_types %}
from {{ package_name }}.primitives import {{ exit_point_types | join(", ") }}
{% endif %}


def {{ function_name }}() -> PipelineModuleRegistry:
    ...


{% if parameter_groups or exit_point_types %}
# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [
{%- for schema_name in parameter_groups %}
    {{ schema_name }},
{%- endfor %}
{%- for type_name in exit_point_types %}
    {{ type_name }},
{%- endfor %}
]
{% endif %}
```

Note: The trailing comma on every item (including last) is valid Python and avoids the need for `loop.last` logic, simplifying the template.

#### 2c. Wire through CLI orchestrator

**File:** `src/sysml_codegen/cli/__init__.py`

In `_generate_registry()` (lines 317-343), collect exit point types and pass them:

```python
def _generate_registry(ctx, config, template_env):
    from sysml_codegen.generation import generate_registry_function
    from sysml_codegen.generation.registry import _collect_exit_point_primitive_types

    output_path = config.output_path / "__init__.py"
    calc_defs_with_outputs = [cd for cd in ctx.calc_defs if cd.output_attributes]

    exit_point_types = _collect_exit_point_primitive_types(ctx.computation_graph.modules)

    code = generate_registry_function(
        calc_defs=calc_defs_with_outputs,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
        entry_point_groups=ctx.computation_graph.entry_point_groups,
        exit_point_primitive_types=exit_point_types,
    )
    ...
```

The template also needs `package_name` in context for the primitives import. Add it:

```python
context = {
    ...
    "package_name": package_name,
    "exit_point_types": exit_point_primitive_types or [],
}
```

---

### Component 3: Gap 3 — Remove Static FusionParams Template

#### 3a. Delete the template file

**Action:** Delete `src/sysml_codegen/templates/schemas_ref.py`

#### 3b. Remove the copy operation

**File:** `src/sysml_codegen/cli/__init__.py`

In `_generate_schemas()` (lines 127-161), remove lines 137-143:

```python
# DELETE these lines:
ref_schema = Path(__file__).parent.parent / "templates" / "schemas_ref.py"
if ref_schema.exists():
    dest = config.output_path / f"{config.package_name}_schemas.py"
    shutil.copy(ref_schema, dest)
    logger.debug(f"Copied reference schema to {dest}")
```

The function retains the multi-output schema generation logic (lines 145-161) which is dynamically generated from model content.

---

### Component 4: Test Fixture

#### 4a. Copy chain spike model to test fixtures

**Action:** Copy the chain spike SysML model from `fusion-tea` into `sysml-codegen/tests/fixtures/`:

```
tests/fixtures/chain_spike_model/
├── library.sysml    (from fusion-tea/models/tests/codegen_chain_spike/library.sysml)
└── design.sysml     (from fusion-tea/models/tests/codegen_chain_spike/design.sysml)
```

#### 4b. Add conftest fixture

**File:** `tests/conftest.py`

Add fixture:
```python
@pytest.fixture
def chain_spike_model_path(fixtures_path: Path) -> Path:
    """Return path to chain spike SysML model directory."""
    return fixtures_path / "chain_spike_model"
```

---

### Component 5: Unit Tests

#### 5a. Gap 1 unit tests

**File:** `tests/unit/test_parameter_groups.py` (new)

Tests that exercise `extract_design_attributes()` and `_extract_default_value()` directly. These require a loaded SysML model, so they use the `chain_spike_model_path` fixture.

```python
"""Unit tests for parameter group extraction — Gap 1 fixes."""
import pytest
from pathlib import Path


class TestExtractDesignAttributes:
    """Tests for extract_design_attributes() path filter behavior."""

    def test_default_filter_includes_test_models(self, chain_spike_model_path: Path):
        """Default filter (empty string) should include models in tests/ directory.

        FR-1: design_path_filter default must be "" (accept all).
        AC-1: Chain spike model produces 3 design attributes.
        """
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        attrs_by_file = extract_design_attributes(extractor.model)
        all_attrs = [a for attrs in attrs_by_file.values() for a in attrs]

        # Should find design attributes (length, width, rate)
        assert len(all_attrs) >= 3, (
            f"Expected at least 3 design attributes, got {len(all_attrs)}"
        )

        # Verify non-None defaults
        for attr in all_attrs:
            if attr.name in ("length", "width", "rate"):
                assert attr.default_value is not None, (
                    f"Attribute '{attr.name}' should have a default value"
                )

    def test_restrictive_filter_excludes_test_models(self, chain_spike_model_path: Path):
        """A restrictive filter like 'models/designs' should exclude test models."""
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        attrs_by_file = extract_design_attributes(
            extractor.model, design_path_filter="models/designs"
        )
        all_attrs = [a for attrs in attrs_by_file.values() for a in attrs]
        assert len(all_attrs) == 0, "Restrictive filter should exclude test models"

    def test_explicit_filter_narrows_results(self, chain_spike_model_path: Path):
        """An explicit filter should only include matching files."""
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        attrs = extract_design_attributes(
            extractor.model, design_path_filter="design.sysml"
        )
        all_attrs = [a for alist in attrs.values() for a in alist]
        assert len(all_attrs) >= 3


class TestExtractDefaultValueCrashGuard:
    """Tests for OperatorExpression crash guard in _extract_default_value().

    FR-3: Must not crash on OperatorExpressions with feature references.
    AC-2: Non-extractable values are None.
    """

    def test_operator_expression_does_not_crash(self, chain_spike_model_path: Path):
        """Broadening filter to include library should not crash."""
        from sysml_codegen.extraction.extractor import SysMLDataExtractor
        from sysml_codegen.analysis.parameter_groups import extract_design_attributes

        extractor = SysMLDataExtractor([chain_spike_model_path])
        if not extractor.load_models():
            pytest.skip("Could not load chain spike SysML models")

        # Empty filter includes library files with OperatorExpressions
        # (e.g., area = length * width). This should not crash.
        attrs_by_file = extract_design_attributes(extractor.model, design_path_filter="")
        # If we get here without exception, the crash guard works
        assert attrs_by_file is not None


class TestBuildPipelineContextDefaults:
    """Tests for build_pipeline_context() producing populated entry points.

    AC-1: Chain spike model produces design_params.json with 3 entries.
    """

    def test_entry_points_have_defaults(self, chain_spike_model_path: Path):
        """Entry points from chain spike model should have non-None default values."""
        from sysml_codegen.generation.initialization import build_pipeline_context

        try:
            ctx = build_pipeline_context([chain_spike_model_path])
        except Exception:
            pytest.skip("Could not build pipeline context for chain spike model")

        # Check that entry point groups exist and have parameters with defaults
        assert len(ctx.computation_graph.entry_point_groups) > 0, (
            "Should have at least one entry point group"
        )
        all_params = [
            ep for group in ctx.computation_graph.entry_point_groups
            for ep in group.parameters
        ]
        params_with_defaults = [ep for ep in all_params if ep.default_value is not None]
        assert len(params_with_defaults) >= 3, (
            f"Expected at least 3 params with defaults, got {len(params_with_defaults)}"
        )
```

#### 5b. Gap 2 unit tests

**File:** `tests/unit/test_registry_generation.py` (new)

Tests that verify exit point type collection and template rendering.

```python
"""Unit tests for registry generation — Gap 2 fixes."""
import pytest


class TestCollectExitPointTypes:
    """Tests for _collect_exit_point_primitive_types()."""

    def test_single_output_modules_produce_float(self):
        """Single-output modules with python_type='float' should produce 'Float'."""
        from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
        from sysml_codegen.resolution.models import PipelineModule, ModuleOutput, ModuleInput

        modules = [
            PipelineModule(
                name="test_module",
                module_type="TestModule",
                inputs=[],
                outputs=[
                    ModuleOutput(field_name="root", python_type="float", channel_name="test__result")
                ],
                execution_order=0,
            )
        ]

        types = _collect_exit_point_primitive_types(modules)
        assert "Float" in types

    def test_multi_output_modules_excluded(self):
        """Multi-output modules (field_name != 'root') should not add primitive types."""
        from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
        from sysml_codegen.resolution.models import PipelineModule, ModuleOutput

        modules = [
            PipelineModule(
                name="test_module",
                module_type="TestModule",
                inputs=[],
                outputs=[
                    ModuleOutput(field_name="area", python_type="float", channel_name="test__area"),
                    ModuleOutput(field_name="cost", python_type="float", channel_name="test__cost"),
                ],
                execution_order=0,
            )
        ]

        types = _collect_exit_point_primitive_types(modules)
        assert len(types) == 0

    def test_deduplication(self):
        """Multiple single-output float modules should produce only one 'Float'."""
        from sysml_codegen.generation.registry import _collect_exit_point_primitive_types
        from sysml_codegen.resolution.models import PipelineModule, ModuleOutput

        modules = [
            PipelineModule(
                name=f"mod_{i}",
                module_type=f"Mod{i}Module",
                inputs=[],
                outputs=[
                    ModuleOutput(field_name="root", python_type="float", channel_name=f"mod{i}__out")
                ],
                execution_order=i,
            )
            for i in range(3)
        ]

        types = _collect_exit_point_primitive_types(modules)
        assert types == ["Float"]  # sorted, deduplicated


class TestRegistryTemplateRendering:
    """Tests for registry template rendering with exit point types."""

    def test_custom_schema_types_includes_exit_point_types(self):
        """CUSTOM_SCHEMA_TYPES should include both entry point and exit point types.

        FR-6: Template must render exit point types alongside entry point schemas.
        AC-3: Generated __init__.py includes Float in CUSTOM_SCHEMA_TYPES.
        """
        import jinja2
        from pathlib import Path

        template_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("registry_function.py.jinja2")
        rendered = template.render(
            function_name="create_test_registry",
            all_modules=[],
            imports=["from simkit.core.registry_builder import create_registry",
                     "from simkit.core.pipeline_registry import PipelineModuleRegistry"],
            schema_imports=["from test_pkg.schemas.design_params import DesignParams as DesignParams"],
            parameter_groups=["DesignParams"],
            exit_point_types=["Float"],
            package_name="test_pkg",
        )

        assert "CUSTOM_SCHEMA_TYPES" in rendered
        assert "DesignParams" in rendered
        assert "Float" in rendered
        assert "from test_pkg.primitives import Float" in rendered

    def test_no_exit_point_types_still_renders(self):
        """Template should render correctly without exit point types."""
        import jinja2
        from pathlib import Path

        template_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        template = env.get_template("registry_function.py.jinja2")
        rendered = template.render(
            function_name="create_test_registry",
            all_modules=[],
            imports=["from simkit.core.registry_builder import create_registry",
                     "from simkit.core.pipeline_registry import PipelineModuleRegistry"],
            schema_imports=[],
            parameter_groups=[],
            exit_point_types=[],
            package_name="test_pkg",
        )

        assert "CUSTOM_SCHEMA_TYPES" not in rendered
        assert "primitives" not in rendered
```

---

### Component 6: Integration Tests

#### 6a. Update existing schema test

**File:** `tests/integration/test_full_pipeline.py`

Update `test_generates_schemas()` (lines 256-276) to assert the static schema file is NOT generated:

```python
def test_generates_schemas(self, tmp_path: Path, sample_model_path: Path):
    """Verify schema files are generated (Phase 2) — no static FusionParams."""
    from sysml_codegen.cli import run_codegen, GenerationConfig

    output = tmp_path / "generated"
    config = GenerationConfig(
        models_path=sample_model_path,
        output_path=output,
        package_name="test_pkg",
    )

    run_codegen(config)

    # FR-10/AC-5: No static FusionParams schema should be generated
    ref_schema = output / "test_pkg_schemas.py"
    assert not ref_schema.exists(), (
        "Static FusionParams schema should NOT be generated"
    )

    # Multi-output schemas may or may not exist depending on model
    schemas_dir = output / "schemas"
    assert schemas_dir.exists(), "schemas/ directory should exist"
```

#### 6b. Add end-to-end codegen verification test

Add a new test class to `tests/integration/test_full_pipeline.py`:

```python
class TestCodegenRuntimeGapFixes:
    """Integration tests verifying all three runtime gap fixes.

    These tests run full codegen on the chain spike model and verify
    the output is correct without manual intervention.
    """

    def test_design_params_json_populated(self, tmp_path: Path, chain_spike_model_path: Path):
        """AC-1: design_params.json should contain correct default values."""
        import json
        from sysml_codegen.cli import run_codegen, GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=output,
            package_name="chain_spike",
        )

        success = run_codegen(config)
        assert success, "Codegen should succeed on chain spike model"

        # Find JSON files in inputs/
        json_files = list((output / "inputs").glob("*.json"))
        assert len(json_files) > 0, "Should generate at least one JSON input file"

        # Check that at least one JSON file has populated values
        has_populated_json = False
        for jf in json_files:
            data = json.loads(jf.read_text())
            if data:  # non-empty
                has_populated_json = True
                # Verify numeric values are present
                for key, value in data.items():
                    assert isinstance(value, (int, float)), (
                        f"JSON value for '{key}' should be numeric, got {type(value)}"
                    )
        assert has_populated_json, "At least one JSON file should have populated values"

    def test_custom_schema_types_includes_exit_point_types(
        self, tmp_path: Path, chain_spike_model_path: Path
    ):
        """AC-3: Generated __init__.py should include Float in CUSTOM_SCHEMA_TYPES."""
        from sysml_codegen.cli import run_codegen, GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=output,
            package_name="chain_spike",
        )

        success = run_codegen(config)
        assert success, "Codegen should succeed on chain spike model"

        init_content = (output / "__init__.py").read_text()
        assert "CUSTOM_SCHEMA_TYPES" in init_content, (
            "Generated __init__.py should have CUSTOM_SCHEMA_TYPES"
        )
        assert "Float" in init_content, (
            "CUSTOM_SCHEMA_TYPES should include Float for RootModel[float] exit points"
        )
        assert "from chain_spike.primitives import" in init_content, (
            "Should import Float from primitives"
        )

    def test_no_fusion_params_schema(self, tmp_path: Path, chain_spike_model_path: Path):
        """AC-5/AC-6: No FusionParams schema should exist in generated output."""
        from sysml_codegen.cli import run_codegen, GenerationConfig

        output = tmp_path / "generated"
        config = GenerationConfig(
            models_path=chain_spike_model_path,
            output_path=output,
            package_name="chain_spike",
        )

        success = run_codegen(config)
        assert success, "Codegen should succeed"

        # No {package}_schemas.py file should exist
        schemas_file = output / "chain_spike_schemas.py"
        assert not schemas_file.exists(), (
            "Static FusionParams schema should not be generated"
        )

        # Double-check: no FusionParams anywhere in generated code
        for py_file in output.rglob("*.py"):
            content = py_file.read_text()
            assert "FusionParams" not in content, (
                f"FusionParams found in {py_file.name} — static template was not removed"
            )

    def test_design_path_filter_cli_flag(self):
        """FR-4: CLI should expose --design-path-filter flag."""
        import io
        import sys
        from contextlib import redirect_stdout
        from unittest.mock import patch
        from sysml_codegen.cli import main

        help_text = ""
        with patch.object(sys, "argv", ["sysml-codegen", "generate", "--help"]):
            try:
                with redirect_stdout(io.StringIO()) as f:
                    main()
            except SystemExit:
                pass
            help_text = f.getvalue()

        assert "--design-path-filter" in help_text, (
            "CLI should have --design-path-filter option"
        )

    def test_generation_config_has_design_path_filter(self):
        """FR-4: GenerationConfig should have design_path_filter field."""
        from sysml_codegen.cli import GenerationConfig

        config = GenerationConfig(
            models_path=Path("/tmp/models"),
            output_path=Path("/tmp/output"),
        )
        assert hasattr(config, "design_path_filter")
        assert config.design_path_filter == ""
```

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Broadening path filter includes unexpected elements | Low | Medium | The `feature_value_expression` check at line 103-106 already filters to only `AttributeUsage` elements with values. The crash guard (Component 1d) handles non-static expressions. |
| Template rendering change breaks existing codegen | Low | High | Existing tests run codegen on sample models. The template change is additive (new `exit_point_types` variable defaults to empty list). |
| Chain spike model requires syside runtime | Medium | Medium | Tests use `pytest.skip()` when model loading fails, matching the existing pattern in `conftest.py:sample_extractor`. |
| Removing `schemas_ref.py` breaks downstream consumers | Very Low | Low | The file is unused by any generated code — `CUSTOM_SCHEMA_TYPES` only references dynamically generated schema classes. Verified by grep in the gap analysis. |

---

## Integration Strategy

### Execution Order

1. **Gap 3 first** — Delete `schemas_ref.py` and remove copy. Zero risk, simplest change.
2. **Gap 1 second** — Path filter default + crash guard + CLI flag wiring.
3. **Gap 2 third** — Exit point type collection + template update + CLI wiring.
4. **Tests last** — Copy fixture, add unit tests, update integration tests.

This order minimizes risk: each gap fix is independently testable, and Gap 3 is the simplest possible change to start with.

### Backward Compatibility

- `design_path_filter=""` is more permissive than the old `"models/designs"` default. Any model that worked before will continue to work. Models under `models/designs/` are still included (empty filter accepts everything).
- `exit_point_primitive_types=None` defaults to empty list, so existing callers of `generate_registry_function()` without the new parameter get unchanged behavior.
- The `CUSTOM_SCHEMA_TYPES` list in the template now always uses trailing commas, which is valid Python and avoids the `loop.last` logic issue.

---

## Validation Approach

### Automated Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run only gap-fix tests
uv run pytest tests/unit/test_parameter_groups.py tests/unit/test_registry_generation.py tests/integration/test_full_pipeline.py::TestCodegenRuntimeGapFixes -v

# Type check
uv run mypy src/

# Lint
uv run ruff check src/
```

### Manual Verification

After implementation, run codegen on the chain spike model and verify output:

```bash
cd /home/reid/1cfe/fusion-tea

uv run sysml-codegen generate \
    --models models/tests/codegen_chain_spike/ \
    --output generated/codegen_chain_spike/ \
    --package-name chain_spike

# Verify JSON is populated
python -c "
import json
data = json.load(open('generated/codegen_chain_spike/inputs/design_params.json'))
assert len(data) >= 3
print('JSON populated:', data)
"

# Verify Float in CUSTOM_SCHEMA_TYPES
grep -n "Float" generated/codegen_chain_spike/__init__.py

# Verify no FusionParams
grep -rn "FusionParams" generated/codegen_chain_spike/ || echo "No FusionParams found (correct)"
```

### Acceptance Criteria Mapping

| AC | Verified By |
|----|-------------|
| AC-1 (populated JSON) | `test_design_params_json_populated` + manual |
| AC-2 (no crash on OperatorExpression) | `test_operator_expression_does_not_crash` |
| AC-3 (Float in CUSTOM_SCHEMA_TYPES) | `test_custom_schema_types_includes_exit_point_types` |
| AC-4 (execute_pipeline works) | Manual verification on fusion-tea |
| AC-5 (no FusionParams) | `test_no_fusion_params_schema` |
| AC-6 (schemas_ref.py deleted) | Git status / file absence |
| AC-7 (existing tests pass) | `uv run pytest tests/` |
| AC-8 (new unit tests) | `test_parameter_groups.py`, `test_registry_generation.py` |
| AC-9 (integration test) | `TestCodegenRuntimeGapFixes` class |
| AC-10 (mypy passes) | `uv run mypy src/` |
| AC-11 (ruff passes) | `uv run ruff check src/` |

---

**Next Step:** After approval → `/_my_implement` or `/_my_plan`
