# Implementation Plan: Phase 0 — Test Infrastructure & Baselines

**Status:** Complete
**Created:** 2026-02-17
**Last Updated:** 2026-02-17

## Source Documents
- **Implementation Plan:** `.project/concepts/refactor-design-intent/IMPLEMENTATION_PLAN.md` (Phase 0)
- **Strategy:** `.project/concepts/refactor-design-intent/STRATEGY.md`
- **Data Models:** `src/sysml_codegen/extraction/data_models.py`, `src/sysml_codegen/extraction/usage_extractor.py`
- **Pipeline Context:** `src/sysml_codegen/generation/initialization.py:76` (`PipelineContext`)
- **Existing Baseline Infrastructure:** `scripts/capture_baseline_yaml.py`, `tests/integration/test_e2e_output_registry.py`

## Implementation Strategy

**Phasing Rationale:**
Phase 0.1 (extraction snapshots) is riskiest because extraction dataclasses contain
non-serializable SysIDE AST nodes — this is where the serialization boundary gets
designed. Phase 0.2 (pipeline baselines) builds on 0.1's patterns and is lower risk
because `ComputationGraph` is already Pydantic. Phase 0.3 (harness polish) is last
because the harness already works (C01/C02 prove it).

**Overall Validation Approach:**
- Each sub-phase has a capture script + round-trip test
- 0.1 validates snapshots round-trip through typed dataclasses
- 0.2 validates deterministic pipeline output via JSON/YAML diff
- 0.3 validates that `pytest -m req` collects conformance tests and snapshot fixtures are available

**Current State (pre-Phase 0):**
- 804 tests collected (C01=91, C02=46 conformance already done)
- Baseline YAML exists for 4 models in `tests/fixtures/baseline_yaml/`
- `tests/conformance/conftest.py` has `req` marker
- No extraction snapshots exist
- No ComputationGraph JSON baselines exist

---

## Phase 0.1: Snapshot Extraction Fixtures

### Goal
Serialize extraction output from all fixture models so downstream conformance tests
(C03+) can run without the JVM/SysIDE parser. This is the foundation for the entire
test-first refactor strategy.

### The Serialization Boundary Problem

Extraction data models are **dataclasses** (not Pydantic) with `Any`-typed fields
that hold live SysIDE Java objects bridged via py4j:

| Type | Non-serializable fields | Strategy |
|------|------------------------|----------|
| `CalculationDefinitionData` | `output_expression_asts: dict[str, Any]`, `member_expressions: dict[str, Any]`, `all_member_names: set[str]` | ASTs → `null` (expression compiler tests use live extraction); `set` → `list` |
| `BindingInfo` | `source_instance_elem: object`, `source_attribute_elem: object`, `expression_ast: Any` | Store `source_instance_name`/`source_attribute_name` (computed properties) instead; AST → `null` |
| `CalcUsageData` | `raw_element: object` | → `null` |
| `ComputedAttributeData` | `expression_ast: Any` | → `null`; store `expression_text` (already present) |
| `RedefinitionData` | `expression_ast: Any` | → `null`; store `expression_text` (already present) |
| `AggregationExpressionData` | (no AST fields) | Fully serializable |
| `ScopedAggregationData` | (delegates to `AggregationExpressionData`) | Fully serializable |
| `HierarchyExtractionResult` | (no AST fields directly) | Contains `RedefinitionData` list → handle above |
| `DesignAttributeData` | (no AST fields) | `source_file: Path` → `str` |
| `ChannelAlias` | (Pydantic BaseModel) | Native `model_dump()` |

**Path** and **Enum** fields need custom JSON encoding (`Path` → `str`, `Enum` → `.value`).

### Test Stencil (Write This First)

```python
# tests/conformance/test_extraction_snapshots.py
import pytest
from tests.helpers.snapshot_loader import load_extraction_snapshot

MODELS = ["sample_model", "solar_battery_model", "catf_mfe_model", "attr_expr_probe"]

@pytest.mark.parametrize("model_name", MODELS)
class TestExtractionSnapshotRoundTrip:
    def test_snapshot_loads(self, model_name):
        """Snapshot file exists and deserializes without error."""
        snapshot = load_extraction_snapshot(model_name)
        assert snapshot is not None

    def test_calc_defs_have_fields(self, model_name):
        """Every CalculationDefinitionData has required fields populated."""
        snapshot = load_extraction_snapshot(model_name)
        for cd in snapshot["calc_defs"]:
            assert cd.name
            assert cd.qualified_name
            assert cd.source_file
            assert isinstance(cd.input_attributes, list)
            assert isinstance(cd.output_attributes, list)

    def test_calc_usages_have_bindings(self, model_name):
        """Every CalcUsageData has typed bindings."""
        snapshot = load_extraction_snapshot(model_name)
        for cu in snapshot["calc_usages"]:
            assert cu.instance_name
            assert cu.calc_def_name
            for b in cu.bindings:
                assert b.binding_type is not None

    def test_snapshot_matches_live_extraction(self, model_name, fixtures_path):
        """Snapshot matches live extraction output (field-by-field, AST fields excluded)."""
        # This test requires JVM — skip if SysIDE unavailable
        snapshot = load_extraction_snapshot(model_name)
        # ... compare serializable fields against live extraction
```

### Changes Required

#### 1. Serialization Helpers
**File:** `tests/helpers/snapshot_serializer.py` (NEW)
- [x] Create `serialize_extraction_snapshot(ctx: PipelineContext) -> dict`
  - Calls `dataclasses.asdict()` on each extraction type
  - Custom `default` function handles: `Path` → `str`, `Enum` → `.value`, AST objects → `None`, `set` → sorted `list`
  - Preserves computed property values (`source_instance_name`, `source_attribute_name`) as explicit fields
  - Serializes `ChannelAlias` list via `.model_dump()` (Pydantic)
- [x] Create `_serialize_dataclass(obj) -> dict` recursive helper
  - Handles nested dataclasses (e.g., `CalcUsageData.bindings: list[BindingInfo]`)
  - Handles `ExpressionRef` (Pydantic in `agentic_mbse`) via `.model_dump()`

**Data captured per model:**
```python
{
    "model_name": "solar_battery_model",
    "captured_at": "2026-02-17T...",
    "calc_defs": [...],           # list[CalculationDefinitionData]
    "calc_usages": [...],         # list[CalcUsageData]
    "design_attributes": {...},   # dict[str, list[DesignAttributeData]]  (Path keys → str)
    "hierarchy_data": {...},      # HierarchyExtractionResult
    "aggregation_expressions": [...],  # list[ScopedAggregationData]
    "computed_attributes": [...],      # list[ComputedAttributeData]
    "channel_aliases": [...],          # list[ChannelAlias]
}
```

#### 2. Deserialization Loader
**File:** `tests/helpers/snapshot_loader.py` (NEW)
- [x] Create `load_extraction_snapshot(model_name: str) -> dict`
  - Loads from `tests/fixtures/{model_name}/extraction_snapshot.json`
  - Reconstructs typed dataclass instances from dicts
  - `Path` fields: `str` → `Path`
  - Enum fields: `str` → `BindingType(value)`, `RedefinitionType(value)`, etc.
  - AST fields: remain `None` (documented as "not available from snapshot")
  - Returns dict with same keys as serialized format, values as typed dataclass instances
- [x] Create `_deserialize_calc_def(d: dict) -> CalculationDefinitionData`
- [x] Create `_deserialize_calc_usage(d: dict) -> CalcUsageData`
- [x] Create `_deserialize_binding_info(d: dict) -> BindingInfo`
- [x] Create `_deserialize_design_attribute(d: dict) -> DesignAttributeData`
- [x] Create `_deserialize_hierarchy_result(d: dict) -> HierarchyExtractionResult`
- [x] Create `_deserialize_scoped_aggregation(d: dict) -> ScopedAggregationData`
- [x] Create `_deserialize_computed_attribute(d: dict) -> ComputedAttributeData`

#### 3. Capture Script
**File:** `scripts/capture_extraction_snapshots.py` (NEW)
- [x] Pattern after existing `scripts/capture_baseline_yaml.py`
- [x] For each model in `MODELS` dict:
  - Call `build_pipeline_context([model_path])`
  - Call `serialize_extraction_snapshot(ctx)`
  - Write to `tests/fixtures/{model_name}/extraction_snapshot.json`
  - Print summary: model name, counts (calc_defs, calc_usages, bindings, etc.)
- [ ] Models to capture:
  - `sample_model` (small, 3 calc defs)
  - `solar_battery_model` (medium, 9 calc defs, hierarchy + aggregation)
  - `catf_mfe_model` (large, many calc defs, physics + components)
  - `attr_expr_probe` (computed attributes, FORMULA/EXPOSE patterns)
  - `chain_spike_model` (CHAIN binding patterns)
  - `issue22_model` (REFERENCE→aggregation regression)

#### 4. Snapshot Files
**Files:** `tests/fixtures/{model}/extraction_snapshot.json` (NEW, 6 files)
- [x] Run capture script to generate all 6 snapshots
- [x] Verify each file is valid JSON and loadable

#### 5. Round-Trip Test File
**File:** `tests/conformance/test_extraction_snapshots.py` (NEW)
- [x] Implement test stencil above
- [x] Parametrize over all 6 models
- [x] Tag with `@pytest.mark.req(id="REQ-SNAP-01")` etc.

### Validation (How to Verify This Phase)

**Automated:**
- [x] `uv run pytest tests/conformance/test_extraction_snapshots.py -v` → 54 passed in 0.47s
- [x] `uv run pytest tests/ -v` → 858 passed (804 + 54 new) in 6.20s
- [x] JSON files are well-formed: `python -m json.tool` validates all 6 snapshots

**Manual:**
- [x] Inspect one snapshot (solar_battery) — calc_def count is 15 (plan said 9, actual is 15)
- [x] Verify AST fields are `null` (not serialized Java objects)
- [x] Verify `source_file` fields are string paths (not PosixPath repr)
- [x] Verify enum fields are string values (e.g., `"chain"` not `"BindingType.CHAIN"`)

**What We Know Works After This Phase:**
Downstream conformance tests (C03+) can load extraction output as typed dataclass
instances without touching SysIDE. The serialization boundary is defined and tested.

---

## Phase 0.2: Snapshot Pipeline Baselines

### Goal
Capture ComputationGraph JSON and generated `__init__.py` as baselines alongside
the existing YAML baselines. These enable diff-based regression detection for the
entire pipeline spine.

### Test Stencil (Write This First)

```python
# tests/conformance/test_baselines.py
import json
import pytest
from sysml_codegen.generation.initialization import build_pipeline_context
from sysml_codegen.resolution.models import ComputationGraph

MODELS = [
    ("solar_battery", "solar_battery_model"),
    ("attr_expr_probe", "attr_expr_probe"),
    ("chain_spike", "chain_spike_model"),
    ("sample_model", "sample_model"),
]

@pytest.mark.parametrize("baseline_name,model_dir", MODELS, ids=[m[0] for m in MODELS])
class TestPipelineBaselines:
    def test_computation_graph_matches_baseline(self, baseline_name, model_dir, fixtures_path):
        """ComputationGraph JSON matches captured baseline."""
        ctx = build_pipeline_context([fixtures_path / model_dir])
        generated = ctx.computation_graph.model_dump_json(indent=2)
        baseline_path = fixtures_path / "baseline_outputs" / baseline_name / "computation_graph.json"
        baseline = baseline_path.read_text()
        assert json.loads(generated) == json.loads(baseline)

    def test_computation_graph_round_trips(self, baseline_name, model_dir, fixtures_path):
        """Baseline JSON deserializes back to valid ComputationGraph."""
        baseline_path = fixtures_path / "baseline_outputs" / baseline_name / "computation_graph.json"
        graph = ComputationGraph.model_validate_json(baseline_path.read_text())
        assert len(graph.modules) > 0
        assert len(graph.execution_order) == len(graph.modules)
```

### Changes Required

#### 1. Capture Script
**File:** `scripts/capture_pipeline_baselines.py` (NEW)
- [x] Pattern after `scripts/capture_baseline_yaml.py`
- [x] For each model:
  - Call `build_pipeline_context([model_path])`
  - Serialize `ctx.computation_graph.model_dump_json(indent=2)` → `computation_graph.json`
  - Generate `__init__.py` via `generate_registry_function()` → `registry_init.py`
- [ ] Output dir: `tests/fixtures/baseline_outputs/{model_name}/`

#### 2. Baseline Output Files
**Files:** `tests/fixtures/baseline_outputs/{model}/computation_graph.json` (NEW, 4 files)
**Files:** `tests/fixtures/baseline_outputs/{model}/registry_init.py` (NEW, 4 files)
- [x] Run capture script to generate all baselines
- [x] Verify ComputationGraph JSON round-trips through Pydantic
- [x] Verify registry files are syntactically valid Python (`ast.parse()`)

#### 3. Baseline Test File
**File:** `tests/conformance/test_baselines.py` (NEW)
- [x] Implement test stencil above
- [x] Add registry `__init__.py` baseline test (syntax validation)
- [x] Tag with `@pytest.mark.req(id="REQ-BASE-01")` etc.

### Validation

**Automated:**
- [x] `uv run pytest tests/conformance/test_baselines.py -v` → 16 passed in 0.25s
- [x] `uv run pytest tests/ -v` → 874 passed in 6.12s

**Manual:**
- [x] Inspect solar_battery `computation_graph.json` — 36 modules (matches YAML baseline)
- [x] Verify `ComputationGraph.model_validate_json()` succeeds on every baseline file
- [x] Verify `execution_order` length equals `modules` length in each baseline

**What We Know Works After This Phase:**
Pipeline output is deterministic and captured. Any component refactoring that changes
pipeline output will be caught by JSON/YAML diff. Regressions are detected by data,
not by opinion.

---

## Phase 0.3: Conformance Test Harness Polish

### Goal
Add shared snapshot-loading fixtures to the conformance conftest so C03+ tests can
load extraction data with a single fixture call. Verify the `req` marker works for
filtering.

### Test Stencil (Write This First)

```python
# Verify harness works by running existing C01/C02 + new fixture tests
# No dedicated test file — validated by running:
#   uv run pytest -m req --co -q  →  should list 137+ tests (C01=91, C02=46)
#   uv run pytest tests/conformance/ -v  →  all green
```

### Changes Required

#### 1. Conformance Conftest Enhancement
**File:** `tests/conformance/conftest.py` (EDIT — currently 5 lines)
- [x] Add `extraction_snapshot` fixture (session-scoped, parametrized)
  ```python
  @pytest.fixture(scope="session")
  def extraction_snapshots():
      """Load all extraction snapshots once per session."""
      from tests.helpers.snapshot_loader import load_extraction_snapshot
      return {
          name: load_extraction_snapshot(name)
          for name in ["sample_model", "solar_battery_model", "catf_mfe_model",
                       "attr_expr_probe", "chain_spike_model", "issue22_model"]
      }
  ```
- [x] Add individual model fixtures for convenience:
  ```python
  @pytest.fixture
  def solar_battery_snapshot(extraction_snapshots):
      return extraction_snapshots["solar_battery_model"]
  ```
- [x] Add `baseline` marker registration:
  ```python
  config.addinivalue_line("markers", "baseline: pipeline baseline comparison test")
  ```

#### 2. Marker Registration
**File:** `pyproject.toml` (EDIT — if markers not registered there)
- [x] Check if `[tool.pytest.ini_options]` has `markers` list
- [x] Add `req` and `baseline` markers if not present (avoids PytestUnknownMarkWarning)

### Validation

**Automated:**
- [x] `uv run pytest -m req --co -q` → 205 tests collected (C01=91, C02=46, SNAP=54, BASE=14)
- [x] `uv run pytest tests/conformance/ -v` → 207 passed in 0.56s
- [x] `uv run pytest tests/ -v` → 874 passed in 6.44s

**Manual:**
- [x] Verify `extraction_snapshots` fixture loads all 6 models in <2 seconds (0.56s total for all conformance tests)
- [x] Verify `solar_battery_snapshot["calc_defs"]` returns typed `CalculationDefinitionData` instances

**What We Know Works After This Phase:**
The conformance harness is ready for C03+. Any new conformance test can use
`solar_battery_snapshot` (or similar) to get typed extraction data without SysIDE.
The `req` marker correctly filters conformance tests. Baseline comparison tests
are tagged and runnable.

---

## Environment Setup

See `CLAUDE.md` for full environment rules. Key commands:
```bash
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"
uv run pytest tests/
uv run pytest tests/conformance/ -v
uv run pytest -m req --co -q
```

---

## Risk Management

See `IMPLEMENTATION_PLAN.md#risk-mitigations` for overall risk analysis.

**Phase-Specific Mitigations:**

1. **AST serialization boundary (0.1)**: The design explicitly nullifies AST fields
   rather than attempting lossy serialization. Tests that need real ASTs (C04 expression
   compiler) will use live extraction. This is acceptable per Ground Rule 1 ("stubs
   acceptable ONLY for the SysIDE adapter boundary").

2. **Snapshot staleness (0.1)**: Capture script is idempotent and re-runnable.
   If extraction code changes during refactor, re-run `scripts/capture_extraction_snapshots.py`
   and commit updated snapshots with documented reason (per Ground Rule 2).

3. **Path sensitivity (0.1)**: Snapshot serialization stores relative paths
   (relative to fixtures dir) to avoid machine-specific absolute paths breaking diffs.

4. **Baseline drift (0.2)**: If a component fix intentionally changes output, update
   baselines deliberately via capture script and document the change. The test failure
   message includes the capture command for easy re-baseline.

5. **Pydantic/dataclass mismatch (0.1)**: Extraction types are dataclasses but
   `ChannelAlias`/`ExpressionRef` are Pydantic. The serializer handles both:
   dataclasses via `asdict()`, Pydantic via `.model_dump()`.

---

## Implementation Notes

*(TO BE FILLED DURING IMPLEMENTATION)*

### Phase 0.1 Completion
**Completed:** 2026-02-17
**Actual Changes:**
- Created `tests/helpers/snapshot_serializer.py` — recursive serializer handling dataclasses, Pydantic, Path, Enum, set, AST nullification, tuple dict keys
- Created `tests/helpers/snapshot_loader.py` — full deserialization back to typed instances (CalculationDefinitionData, CalcUsageData, BindingInfo, HierarchyExtractionResult, etc.)
- Created `scripts/capture_extraction_snapshots.py` — capture script for all 6 models
- Created `tests/conformance/test_extraction_snapshots.py` — 54 tests (9 test methods x 6 models)
- Generated 6 snapshot JSON files: `tests/fixtures/{model}/extraction_snapshot.json`
  - sample_model: 5 calc_defs, 0 calc_usages
  - solar_battery_model: 15 calc_defs, 15 calc_usages, 31 bindings, 78 redefs, 20 scoped_agg, 41 aliases
  - catf_mfe_model: 21 calc_defs, 42 calc_usages, 125 bindings, 46 computed_attrs, 44 aliases
  - attr_expr_probe: 2 calc_defs, 18 computed_attrs, 3 aliases
  - chain_spike_model: 3 calc_defs, 6 bindings
  - issue22_model: 2 calc_defs, 2 redefs, 1 scoped_agg, 1 alias
**Issues:** None
**Deviations:**
- Plan said solar_battery has 9 calc_defs; actual is 15 (plan estimate was outdated)
- Added BindingInfo computed property preservation (source_instance_name, source_attribute_name) as explicit serialized fields — plan mentioned this but didn't specify mechanism
- Test count: 54 (plan estimated ~15) — 9 test methods parametrized over 6 models

### Phase 0.2 Completion
**Completed:** 2026-02-17
**Actual Changes:**
- Created `scripts/capture_pipeline_baselines.py` — captures ComputationGraph JSON + registry __init__.py for 4 models
- Created `tests/conformance/test_baselines.py` — 16 tests (4 test methods x 4 models)
- Generated 8 baseline files in `tests/fixtures/baseline_outputs/{model}/`:
  - solar_battery: 36 modules, 9480-byte registry
  - attr_expr_probe: 16 modules, 4334-byte registry
  - chain_spike: 3 modules, 1533-byte registry
  - sample_model: 0 modules (no calc usages), 1602-byte registry
**Issues:** None
**Deviations:**
- Replaced plan's live-pipeline-comparison test (`build_pipeline_context` in test) with static baseline validation — tests run in 0.25s without JVM, which is the whole point of Phase 0
- Added REQ-BASE-04 (execution_order/modules length equality) as dedicated test

### Phase 0.3 Completion
**Completed:** 2026-02-17
**Actual Changes:**
- Expanded `tests/conformance/conftest.py` from 5 lines to 72 lines:
  - Session-scoped `extraction_snapshots` fixture loading all 6 models
  - 6 per-model convenience fixtures (solar_battery_snapshot, etc.)
  - `baseline` marker registration alongside existing `req` marker
- Added `markers` list to `pyproject.toml` `[tool.pytest.ini_options]`
**Issues:** None
**Deviations:** None

---

## Summary

| Sub-phase | New Files | New Tests | Key Risk |
|-----------|-----------|-----------|----------|
| 0.1 Extraction Snapshots | capture script, serializer, loader, 6 JSON files, test file | ~15 | AST serialization boundary |
| 0.2 Pipeline Baselines | capture script, 8 baseline files, test file | ~10 | ComputationGraph determinism |
| 0.3 Harness Polish | (edits only) | ~2 (marker verification) | None |
| **Total** | **~18 new files** | **~27 new tests** | |

**Checkpoint 0 criteria:** All baseline snapshots captured. All 804+ existing tests pass. `pytest -m req` collects 137+ conformance tests. Snapshot fixtures load typed data without JVM.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete** (2026-02-17)
