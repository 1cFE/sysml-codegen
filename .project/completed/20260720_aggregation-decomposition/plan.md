# Implementation Plan: Aggregation Decomposition and Compatibility Gates

**Status:** Certified
**Created:** 2026-07-08
**Last Updated:** 2026-07-08

## Source Documents

- **Spec:** `.project/active/aggregation-decomposition/spec.md`
- **Spec review:** `.project/active/aggregation-decomposition/spec-review.md` (Approved after revision)
- **Design:** `.project/active/aggregation-decomposition/design.md`
- **Design review:** `.project/active/aggregation-decomposition/design-review.md` (Approved after revision)
- **Epic:** `.project/backlog/epic_push_down.md`
- **Current context:** `.project/CURRENT_WORK.md`
- **Prior certified item:** `.project/active/hierarchy-primitives-models/audit.md`

Use `design.md` for API shape, ownership boundaries, neutral node contracts, and compatibility
details. This plan records execution order, proof points, file-level changes, and gates.

## Implementation Strategy

**Phasing Rationale:** Build and prove the shared neutral decomposition surface in agentic-mbse
before switching sysml-codegen. Close the profile/backlog loop while still inside agentic-mbse.
Then replace sysml-codegen's mixed walker with a local adapter around the shared result and run
consumer gates that prove fixture byte identity and no behavior drift.

**Critical Path:** shared term classes and neutral decomposer -> combined TYPE_MAP proof ->
profile disposition/backlog updates -> sysml-codegen term re-exports and local adapter -> downstream
compatibility gates -> full cross-repo gates.

**First Proof Point:** `agentic-mbse` can decompose sum, singleton, local, wrapper, literal,
unsupported-node, and unsupported-operator shapes into neutral facts with no Python source,
codegen identifiers, `input_channels`, `entry_points`, aliases, or sysml-codegen containers.

**Overall Validation Approach:**

- Each phase starts with tests or a proof artifact.
- The riskiest proofs run early: neutral decomposition, direct builder field compatibility, and
  combined TYPE_MAP inventory.
- sysml-codegen fixture identity is checked with `git diff -- tests/fixtures` after targeted gates
  and again after the full suite.
- Known caveat: project-wide mypy baselines are already dirty from prior certified items
  (`agentic-mbse` about 107 errors, `sysml-codegen` about 98 errors after Item 3). Run mypy if the
  current baseline allows it; otherwise record unchanged counts and do not treat unrelated baseline
  debt as this item.
- No item-level PR closeout. This item can be implemented, audited, and committed, but PR
  preparation waits until all PUSH-DOWN epic items are complete.

---

## Phase 1: agentic-mbse Shared Aggregation Surface

### Goal

Add the shared term classes and neutral aggregation decomposer in agentic-mbse, then prove the moved
logic is reusable SysML understanding rather than codegen policy.

### Assumption Under Test

The aggregation walker can classify terms, wrappers, literals, operators, and unsupported shapes
without returning Python spelling, pipeline identifiers, aliases, or sysml-codegen containers.

### Test Stencil (Write This First)

```python
def test_decompose_sum_singleton_local_and_literal_without_codegen_leaks(fake_exprs):
    result = decompose_aggregation_expression(
        fake_exprs.operator("+", [fake_exprs.sum("module.cost"), fake_exprs.literal("5.0")])
    )

    assert result.sum_terms == [SumTerm("module", "cost", None, None)]
    assert result.root.operator == "+"
    assert not result.has_unsupported
    assert_no_codegen_fields(result)
```

### Changes Required

**See `design.md` for:**

- Architecture and data flow -> `design.md#architecture`
- Shared API shape and neutral node contracts -> `design.md#shared-api-shape`
- Required invariants -> `design.md#required-invariants`
- TYPE_MAP inventory strategy -> `design.md#type_map-inventory-strategy`

**Specific file changes:**

- [x] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py` (NEW): add failing
  tests for `SumTerm`, `SingletonTerm`, and `LocalTerm` field order/defaults and import identity
  through `agentic_mbse.sysml.data_models`, `agentic_mbse.sysml.aggregation`, and
  `agentic_mbse.sysml`.
- [x] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py` (NEW): add neutral
  decomposition tests for sum, singleton child reference, local attribute reference, wrappers,
  literals, unsupported nodes, unsupported operators, term order, no-leak payload assertions, and
  wrapper facts including permissive `sum(filter(module.cost))`.
- [x] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py` (NEW): add dispatch-order
  tests proving feature-chain handling runs before operator handling and literal/null handling runs
  before invocation handling in the shared walker.
- [x] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_aggregation.py` (NEW): add the combined
  source-inventory TYPE_MAP proof over `agentic_mbse.sysml.aggregation` plus imported
  `agentic_mbse.sysml.expression` helper source. Reset or bypass `SysideAdapter._type_map` so the
  test is independent of test order.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`: move/add
  `SumTerm`, `SingletonTerm`, and `LocalTerm` as standard-library dataclasses with exact current
  field names, order, and defaults.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py` (NEW): implement
  `decompose_aggregation_expression`, neutral result/node dataclasses, wrapper facts, diagnostics,
  and term collection using only agentic-mbse and stdlib imports.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`: re-export the aggregation
  API and moved term classes.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`: no production change
  expected; update only if the source inventory proves a direct or helper adapter string is missing.

### Validation

**Automated:**

- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_aggregation.py`
  -> shared aggregation tests pass.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_expression.py tests/test_sysml/test_hierarchy.py tests/test_sysml/test_aggregation.py`
  -> expression/helper, hierarchy, and aggregation shared surfaces pass together.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/data_models.py src/agentic_mbse/sysml/aggregation.py src/agentic_mbse/sysml/__init__.py tests/test_sysml/test_aggregation.py`
  -> touched files are clean.

**Manual/proof checks:**

- [x] Verify `rg "sysml_codegen" /home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/aggregation.py`
  has no hits.
- [x] Verify the shared result does not expose Python source strings, sanitized identifiers,
  `input_channels`, `entry_points`, aliases, or `AggregationExpressionData`.
- [x] Verify the TYPE_MAP proof inventories `FeatureChainExpression`, `OperatorExpression`, and
  `FeatureReferenceExpression` from aggregation plus helper strings from expression helpers,
  including `InvocationExpression`, literal types, and `NullExpression` when present in helper
  source.

**What We Know Works After This Phase:**

agentic-mbse owns the neutral aggregation decomposition surface and all direct/helper adapter type
strings used by that surface are proven present without relying on cached TYPE_MAP state.

---

## Phase 2: Aggregation-Profile Disposition and Backlog Updates

### Goal

Close the spec-required aggregation-profile loop without adding shallow duplicate Level-6 rules.

### Assumption Under Test

The approved design's profile dispositions are enough to close this item: filed rows become exact
agentic-mbse backlog entries, and existing rows cite the owning expression-profile rules.

### Test Stencil (Write This First)

```python
def test_aggregation_profile_disposition_rows_are_recorded():
    backlog = Path(".project/backlog/BACKLOG.md").read_text()

    assert "PUSH-DOWN-AGG-PROFILE-SUM-SHAPE" in backlog
    assert "PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE" in backlog
    assert "PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE" in backlog
```

### Changes Required

**See `design.md` for:**

- Exact disposition table -> `design.md#aggregation-profile-disposition-strategy`
- Risks around duplicate diagnostics -> `design.md#potential-risks`

**Approved disposition table to preserve exactly unless implementation proves a better existing rule:**

| Shape | Disposition | Exact rule | Fixture shape | Severity | Rationale | Backlog ID |
| --- | --- | --- | --- | --- | --- | --- |
| Sum aggregation | FILED | Warn when a codegen-targeted aggregation expression uses `sum(...)` on an operand that cannot decompose to a supported child feature chain or local reference, unless existing expression/hierarchy profile checks already cover the rejected operand shape. | `:>> total = sum(module.cost)` is clean; an unsupported operand shape warns only if not already covered elsewhere. | WARNING | Aggregation-specific unsupported sum operand diagnostics need profile integration over shared aggregation facts. Avoid a shallow rule in this behavior-preserving move. | `PUSH-DOWN-AGG-PROFILE-SUM-SHAPE` |
| Singleton child reference | EXISTING | Existing expression-profile chain-segment coverage reports lossy or anonymous chain segments. | `:>> total = allocation_model.total_allocation` is clean; anonymous or lossy chain segment shapes are covered by `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`. | WARNING | Singleton aggregation controls still need local codegen tests, but early profile diagnostics for malformed chains already belong to the expression-profile row. | N/A |
| Local attribute reference | EXISTING | Existing unsupported-shape message coverage reports opaque feature reference shapes that cannot be explained by shared expression facts. | `:>> total = misc_hardware_cost` is clean; missing referent/name or opaque local reference shape is covered by `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`. | WARNING | Supported bare feature references are clean/no-op for profile purposes. Opaque references are a general expression-shape diagnostic, not aggregation-specific policy. | N/A |
| Invocation wrapper | FILED | Preserve current generation behavior for wrapper unwrapping. Any profile-only warning for unsupported wrappers must be explicitly separated from this item's behavior-preserving implementation. | `sum(Evaluation(module.cost))`, `sum(collect(Evaluation(module.cost)))`, `Evaluation(allocation.total)`, and current permissive `sum(filter(module.cost))` behavior are controls. A future stricter wrapper warning is filed rather than implemented here. | WARNING | Current generation is permissive inside `sum(...)`; stricter profile warning is future profile work, not this behavior-preserving move. | `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE` |
| Literal operand | FILED | Warn when a literal appears where codegen aggregation decomposition cannot use it as a term, while preserving supported literal rendering inside otherwise valid operator expressions. | `:>> total = sum(module.cost) + 5.0` keeps the literal in neutral operator facts; `sum(5.0)` is the filed aggregation-specific incompatible shape. | WARNING | `sum(5.0)` is aggregation-specific and should not be mixed with general literal expression support. | `PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE` |
| Unsupported AST node | EXISTING | Existing expression-profile unsupported-shape message coverage reports AST nodes that cannot be classified into supported shared expression facts. | Unknown expression node inside `:>> total = <unknown>` is covered by `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`; feature chain, reference, literal, operator, and supported invocation controls stay clean. | WARNING | The shared aggregation diagnostic can reuse the same expression-profile unsupported-shape policy instead of adding duplicate aggregation warnings. | N/A |
| Operator shape | EXISTING | Existing expression-profile unsupported-operator coverage reports operators outside the supported expression operator set. | Supported `+`, `-`, `*`, `/`, comparisons, logical operators, and `^` controls are covered; unknown operators are covered by `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR`. | WARNING | Operator compatibility is already expressed as a shared expression-profile rule. Python spelling remains local in sysml-codegen. | N/A |

**Specific file changes:**

- [x] `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`: add or update exact filed rows
  for `PUSH-DOWN-AGG-PROFILE-SUM-SHAPE`, `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE`, and
  `PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE`.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`: no
  production rule expected for filed/existing rows; inspect only if implementation discovers a
  better tested `NEW RULE` candidate.
- [x] `/home/reid/1cfe/agentic-mbse/tests/test_validation/`: add or update tests only for any row
  that changes to `NEW RULE`; otherwise rely on backlog proof plus existing expression-profile
  tests.
- [x] `.project/active/aggregation-decomposition/plan.md`: update this phase's Implementation
  Notes with final disposition evidence and backlog line references during implementation.

### Validation

**Automated:**

- [x] No Level-6 code changed, so no `tests/test_validation/<touched-test-file>.py` profile test
  run was required.
- [x] No Level-6 validation or validation-test file changed, so no touched-file ruff run for those
  paths was required.

**Manual/proof checks:**

- [x] Verify no agentic-mbse validation code imports `sysml_codegen`.
- [x] Verify each filed backlog row includes exact rule, fixture shape, severity, rationale, and
  backlog ID from the approved design.
- [x] Verify existing rows cite the owning expression-profile rows and do not add duplicate
  aggregation warnings.

**What We Know Works After This Phase:**

The aggregation-profile loop is closed for Item 4, with future profile work filed exactly and
existing expression-profile ownership preserved.

---

## Phase 3: sysml-codegen Local Adapter Compatibility

### Goal

Switch sysml-codegen to shared term classes and shared neutral decomposition while keeping
`build_aggregation_expression` as the local Python/pipeline adapter.

### Assumption Under Test

The shared neutral result carries enough structure for sysml-codegen to reproduce
`AggregationExpressionData` field values, unsupported behavior, wrapper behavior, and missing
multiplicity behavior exactly.

### Test Stencil (Write This First)

```python
def test_build_aggregation_expression_field_level_compatibility():
    result = build_aggregation_expression(redef_expr("sum(module.cost) + misc"), mults(), part())

    assert result.owning_part_name == "cost_model"
    assert result.transformed_expression == "(module_count * module.cost) + misc"
    assert result.sum_terms == [SumTerm("module", "cost", "module_count", 4)]
    assert result.local_terms == [LocalTerm("misc")]
    assert result.aliases == []
```

### Changes Required

**See `design.md` for:**

- Local adapter responsibilities -> `design.md#local-adapter-responsibilities`
- Required invariants -> `design.md#required-invariants`
- Implementation notes -> `design.md#implementation-notes`
- Validation approach -> `design.md#validation-approach`

**Specific file changes:**

- [x] `tests/conformance/test_data_models.py`: add object-identity tests proving `SumTerm`,
  `SingletonTerm`, and `LocalTerm` are the same runtime class objects through
  `agentic_mbse.sysml.data_models`, `agentic_mbse.sysml.aggregation`, `agentic_mbse.sysml`, and
  `sysml_codegen.extraction.data_models`; keep `AggregationExpressionData` local.
- [x] `tests/conformance/test_data_models.py`: update source-file expectations so the three moved
  term classes point at `agentic_mbse/sysml/data_models.py` and `AggregationExpressionData` still
  points at `sysml_codegen/extraction/data_models.py`.
- [x] `tests/unit/test_hierarchy_resolver.py`: add/extend direct builder field-level tests for
  `owning_part_qn`, sanitized `owning_part_name`, `attribute_name`, `raw_expression_text`,
  `transformed_expression`, all three term lists, `input_channels`, `entry_points`,
  `compilability`, `has_unsupported_nodes`, default-empty `aliases`, and source metadata defaults.
- [x] `tests/unit/test_hierarchy_resolver.py`: add/extend compatibility tests for non-`EXPRESSION`
  redefinitions returning `None`, `EXPRESSION` redefinitions with no AST returning `None`, missing
  multiplicity producing an unresolved `SumTerm`, known wrappers, and permissive
  `sum(filter(module.cost))`.
- [x] `tests/unit/test_hierarchy_resolver.py`: add unsupported local rendering tests proving
  unsupported invocations set unsupported, still walk operands, and render a local call expression;
  unsupported operators set unsupported and render the raw operator with current spacing.
- [x] `src/sysml_codegen/extraction/data_models.py`: import and re-export shared `SumTerm`,
  `SingletonTerm`, and `LocalTerm`; keep `AggregationExpressionData`, `HierarchyExtractionResult`,
  and `ScopedAggregationData` local.
- [x] `src/sysml_codegen/extraction/hierarchy_resolver.py`: call
  `agentic_mbse.sysml.aggregation.decompose_aggregation_expression` from
  `build_aggregation_expression`, add local rendering over neutral nodes, apply multiplicity by
  creating new local/shared `SumTerm` objects rather than mutating the neutral result, and keep
  alias collection after builder return.

### Validation

**Automated:**

- [x] Run `uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py`
  -> local builder and identity tests pass.
- [x] Run `uv run ruff check src/sysml_codegen/extraction/data_models.py src/sysml_codegen/extraction/hierarchy_resolver.py tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py`
  -> touched files are clean.

**Manual/proof checks:**

- [x] Verify `AggregationExpressionData`, `HierarchyExtractionResult`, and `ScopedAggregationData`
  remain defined in sysml-codegen.
- [x] Verify the local adapter does not re-walk raw SysIDE nodes except through the shared neutral
  result and local multiplicity/naming policy.
- [x] Verify `aliases=[]` before hierarchy orchestration enrichment.

**What We Know Works After This Phase:**

sysml-codegen preserves the public builder and data-model import paths while using shared neutral
decomposition and shared term class objects.

---

## Phase 4: sysml-codegen Probe and Consumer Compatibility Gates

### Goal

Prove the adapter change did not alter committed fixture behavior or downstream consumers of local
`AggregationExpressionData`.

### Assumption Under Test

Fixture probes, dispatch invariants, scoping, input resolution, graph assembly, and alias enrichment
continue to observe byte-identical behavior after the shared decomposition move.

### Test Stencil (Write This First)

```python
def test_agg_literal_probe_keeps_literal_supported(snapshot_result):
    agg = snapshot_result("agg_literal_probe").aggregation("total")

    assert "+ 5.0" in agg.transformed_expression
    assert not agg.has_unsupported_nodes
    assert agg.input_channels
```

### Changes Required

**See `design.md` for:**

- sysml-codegen validation list -> `design.md#validation-approach`
- downstream ownership -> `design.md#local-adapter-responsibilities`
- fixture no-churn rule -> `design.md#required-invariants`

**Specific file changes:**

- [x] `tests/conformance/test_agg_literal_dispatch.py`: keep or extend `agg_literal_probe` coverage
  so literal operands do not trip unsupported invocation behavior and the fixture remains unchanged.
- [x] `tests/unit/test_hierarchy_resolver.py` and/or `tests/conformance/test_hierarchy_resolver.py`:
  keep or extend `alias_agg_probe` and dotted-leaf alias coverage, including orchestration alias
  enrichment around aggregation expressions.
- [x] `tests/conformance/test_ast_dispatch_invariant.py`: update dispatch invariant coverage to
  include the moved shared aggregation walker, not only local expression reconstruction.
- [x] `tests/conformance/test_aggregation_scoping.py`: run and update only if import path or source
  expectations need adjustment.
- [x] `tests/conformance/test_input_resolver.py`: run and update only if term class source/identity
  assumptions need adjustment.
- [x] `tests/conformance/test_factory_aggregation.py`: run and update only if local aggregation
  fields surface through factory/graph behavior.
- [x] `tests/unit/test_output_registry_construction.py` and graph builder aggregation tests: run and
  update only if local container construction assumptions need shared class identity adjustments.
- [x] `tests/fixtures/agg_literal_probe/**` and `tests/fixtures/alias_agg_probe/**`: do not
  recapture or edit. Any diff is a failure unless a separate reviewed behavior-change item exists.

### Validation

**Automated:**

- [x] Run `uv run pytest tests/conformance/test_agg_literal_dispatch.py`
  -> `agg_literal_probe` remains compatible.
- [x] Run `uv run pytest tests/unit/test_hierarchy_resolver.py -k "alias or aggregation or wrapper or unsupported or literal"`
  -> focused local aggregation pins pass.
- [x] Run `uv run pytest tests/conformance/test_hierarchy_resolver.py tests/conformance/test_ast_dispatch_invariant.py tests/conformance/test_aggregation_scoping.py tests/conformance/test_input_resolver.py tests/conformance/test_factory_aggregation.py tests/unit/test_output_registry_construction.py`
  -> orchestration, dispatch, scoping, resolver, graph/factory, and registry consumers pass.
- [x] Run `git diff -- tests/fixtures` -> no fixture diff.
- [x] Run `uv run ruff check src/` -> sysml-codegen source remains clean.

**Manual/proof checks:**

- [x] Verify unsupported invocation/operator assertions cover rendered text and
  `has_unsupported_nodes`, not only the diagnostic flag.
- [x] Verify `sum(filter(module.cost))` remains permissive and does not become an unsupported
  wrapper warning in generation.
- [x] Verify `agg_literal_probe` and `alias_agg_probe` remain committed fixture controls, not new
  generated artifacts.

**What We Know Works After This Phase:**

The shared decomposition move is invisible to sysml-codegen's committed fixtures and downstream
consumers of `AggregationExpressionData`.

---

## Phase 5: Cross-Repo Landing Gates and Documentation State

### Goal

Run the full required gates, record known baseline caveats, and leave the PUSH-DOWN epic ready for
audit of Item 4 without item-level PR closeout.

### Assumption Under Test

Both repos are green at the item landing point, and any type-check caveat is unchanged baseline debt
rather than an Item 4 regression.

### Test Stencil (Write This First)

```python
def test_cross_repo_import_identity():
    from agentic_mbse.sysml.data_models import SumTerm as SharedSumTerm
    from sysml_codegen.extraction.data_models import SumTerm as CodegenSumTerm

    assert CodegenSumTerm is SharedSumTerm
```

### Changes Required

**See `design.md` for:**

- Integration strategy -> `design.md#integration-strategy`
- Validation approach -> `design.md#validation-approach`
- Non-goals and PR closeout rule -> `design.md#non-goals`

**Specific file changes:**

- [x] `.project/active/aggregation-decomposition/plan.md`: fill Implementation Notes with actual
  changes, validation evidence, fixture diff evidence, profile disposition evidence, and any
  unchanged mypy baseline counts.
- [x] `.project/active/aggregation-decomposition/spec.md`: mark success criteria complete only after
  implementation evidence exists.
- [x] `.project/backlog/epic_push_down.md`: mark Item 4 criteria complete only after audit or as
  directed by the audit stage; do not mark the whole epic ready for PR from this item alone.
- [x] `.project/CURRENT_WORK.md`: update Item 4 status and validation summary if implementation
  completes in this session; otherwise leave a precise resume note.
- [x] `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`: ensure filed aggregation-profile
  rows are present and not duplicated.

### Validation

**Automated:**

- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_aggregation.py`
  -> focused shared aggregation suite passes.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest`
  -> full agentic-mbse suite passes.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run ruff check <touched-src-and-test-files>`
  -> touched agentic-mbse files are clean.
- [x] Run `uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py tests/conformance/test_agg_literal_dispatch.py tests/conformance/test_hierarchy_resolver.py tests/conformance/test_ast_dispatch_invariant.py tests/conformance/test_aggregation_scoping.py tests/conformance/test_input_resolver.py tests/conformance/test_factory_aggregation.py tests/unit/test_output_registry_construction.py`
  -> targeted sysml-codegen compatibility set passes.
- [x] Run `uv run pytest tests/`
  -> full sysml-codegen suite passes.
- [x] Run `uv run ruff check src/`
  -> sysml-codegen source is clean.
- [x] Run `git diff -- tests/fixtures`
  -> no fixture diff after full suite.
- [x] Run mypy in each repo only if the current baseline allows it:
  `cd /home/reid/1cfe/agentic-mbse && uv run mypy src/` and `uv run mypy src/`. If dirty, record
  unchanged baseline counts and representative pre-existing errors in Implementation Notes.

**Manual/proof checks:**

- [x] Verify full-repo searches show no `sysml_codegen` imports under
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml` or validation code touched by this item.
- [x] Verify shared aggregation API exports no local codegen identifiers or containers.
- [x] Verify no item-level PR closeout is performed. The full PUSH-DOWN epic PR waits until all
  items are complete.

**What We Know Works After This Phase:**

Item 4 has a complete validation record for audit: shared decomposition, local adapter
compatibility, profile disposition/backlog updates, fixture byte identity, and full cross-repo gates.

---

## Environment Setup

Use `CLAUDE.md` for sysml-codegen commands. The cross-repo editable install pattern from prior
items still applies:

- `uv pip install -e /home/reid/1cfe/agentic-mbse && uv pip install -e ".[dev]"` from sysml-codegen when the
  editable dependency needs refresh.
- Run agentic-mbse commands from `/home/reid/1cfe/agentic-mbse`.
- Run sysml-codegen commands from `/home/reid/1cfe/sysml-codegen`.
- Snapshot/conformance gates should not require a SysIDE license because this item must not
  recapture fixtures.

## Risk Management

**See `design.md#potential-risks` for the detailed risk list.**

**Phase-Specific Mitigations:**

- **Phase 1:** Neutral API may miss a rendering fact. Mitigate with explicit literal, invocation,
  operator, unsupported, wrapper, and term-order tests before production code.
- **Phase 2:** Profile work may duplicate existing expression diagnostics. Mitigate by preserving
  the approved filed/existing disposition table unless a better tested rule is proven.
- **Phase 3:** Local adapter may mutate shared decomposition output or leak codegen policy into
  agentic-mbse. Mitigate with no-leak tests, object identity tests, and assertions that local
  multiplicity creates new `SumTerm` instances.
- **Phase 4:** Fixture identity may drift silently. Mitigate with `agg_literal_probe`,
  `alias_agg_probe`, downstream consumer tests, and `git diff -- tests/fixtures` before and after
  the full suite.
- **Phase 5:** Cross-repo editable state may be half-migrated. Mitigate by running both focused and
  full gates before stopping and recording exact baseline caveats.

## Implementation Notes

Item 4 implementation is complete and ready for audit. Spec and epic success criteria remain for
the audit stage to verify and mark.

### Phase 1 Completion

**Completed:** 2026-07-08
**Actual Changes:** Added `SumTerm`, `SingletonTerm`, and `LocalTerm` to
`agentic_mbse.sysml.data_models`; added `agentic_mbse.sysml.aggregation` with neutral
decomposition nodes, diagnostics, wrapper facts, and `decompose_aggregation_expression`; exported
the API from `agentic_mbse.sysml`. Added `tests/test_sysml/test_aggregation.py` with 12 tests for
term contracts, no codegen leakage, wrappers, unsupported shapes/operators, dispatch ordering,
null handling, and combined TYPE_MAP inventory over aggregation plus expression helpers.
**Issues:** Initial aggregation tests exposed duplicate term collection inside `sum(...)`; fixed by
rendering sum operands with term collection disabled. Ruff also caught duplicate term re-exports in
`__init__.py`; fixed by exporting through the aggregation module.
**Deviations:** The combined TYPE_MAP inventory does not require `InvocationExpression` from the
expression helper source because that helper source does not currently call
`SysideAdapter.is_instance(..., "InvocationExpression")`.

Validation: `uv run pytest tests/test_sysml/test_aggregation.py` -> `12 passed`;
`uv run pytest tests/test_sysml/test_expression.py tests/test_sysml/test_hierarchy.py tests/test_sysml/test_aggregation.py`
-> `93 passed`; touched-file ruff -> clean; `grep -R -n sysml_codegen src/agentic_mbse/sysml src/agentic_mbse/validation`
-> no hits.

### Phase 2 Completion

**Completed:** 2026-07-08
**Actual Changes:** Added three filed aggregation-profile backlog rows in
`/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`:
`PUSH-DOWN-AGG-PROFILE-SUM-SHAPE`, `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE`, and
`PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE`.
**Issues:** No Level-6 code was changed because the approved design classified the rows as FILED
or EXISTING, not NEW RULE.
**Deviations:** None.

Final disposition: sum aggregation FILED; singleton child reference EXISTING via
`PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`; local attribute reference EXISTING via
`PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`; invocation wrapper FILED; literal operand
FILED; unsupported AST node EXISTING via `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`;
operator shape EXISTING via `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR`.

### Phase 3 Completion

**Completed:** 2026-07-08
**Actual Changes:** sysml-codegen now imports and re-exports the shared term class objects while
keeping `AggregationExpressionData`, `HierarchyExtractionResult`, and `ScopedAggregationData`
local. `build_aggregation_expression` still returns the local container, but the raw aggregation
walk is now delegated through `agentic_mbse.sysml.aggregation.decompose_aggregation_expression`.
The local adapter renders neutral nodes, applies multiplicity by creating new `SumTerm` instances,
keeps missing multiplicity behavior, and preserves unsupported invocation/operator rendering.
Added object-identity/source-file conformance tests and direct builder compatibility tests.
**Issues:** Mypy initially rose by one due an unused ignore on the new aggregation import; fixed the
import/ignore placement and restored the prior sysml-codegen baseline.
**Deviations:** `_walk_aggregation_ast` remains as a compatibility shim for existing tests and
callers, but it no longer owns raw SysIDE dispatch.

Validation: `uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py`
-> `166 passed`; touched-file ruff -> clean.

### Phase 4 Completion

**Completed:** 2026-07-08
**Actual Changes:** Updated dispatch invariant tests to inspect the moved shared aggregation
walker. Added compatibility tests for non-expression redefinitions, empty ASTs, missing
multiplicity, unsupported local rendering, field defaults, permissive `sum(filter(...))`, and
alias/literal controls.
**Issues:** The dispatch invariant expected local `_walk_aggregation_ast` to be a raw multi-type
dispatch site. That moved into `agentic_mbse.sysml.aggregation._decompose_node`, so the invariant
now audits the shared function explicitly.
**Deviations:** The audited multi-type dispatch count is now 6 instead of 7 because local
aggregation raw dispatch moved to agentic-mbse.

Validation: `uv run pytest tests/conformance/test_agg_literal_dispatch.py` -> `1 passed`;
`uv run pytest tests/unit/test_hierarchy_resolver.py -k "alias or aggregation or wrapper or unsupported or literal"`
-> `28 passed, 39 deselected`;
`uv run pytest tests/conformance/test_hierarchy_resolver.py tests/conformance/test_ast_dispatch_invariant.py tests/conformance/test_aggregation_scoping.py tests/conformance/test_input_resolver.py tests/conformance/test_factory_aggregation.py tests/unit/test_output_registry_construction.py`
-> `202 passed, 1 skipped`; `git diff -- tests/fixtures` -> empty.

### Phase 5 Completion

**Completed:** 2026-07-08
**Actual Changes:** Full cross-repo gates were run after the implementation and local mypy cleanup.
No fixture recaptures or item-level PR closeout were performed.
**Issues:** Both repos still have pre-existing mypy debt. agentic-mbse remains at `107` errors.
sysml-codegen remains at `98` errors after the import cleanup.
**Deviations:** None.

Validation: agentic-mbse full suite -> `1290 passed, 1 skipped, 33 deselected, 6 warnings`;
sysml-codegen full suite -> `2138 passed, 4 skipped`; sysml-codegen `uv run ruff check src/` ->
clean; `git diff -- tests/fixtures` -> empty; agentic-mbse touched-file ruff -> clean; sysml-codegen
touched-file ruff after import cleanup -> clean.

---

**Status:** Draft -> In Progress -> Implemented -> Certified
