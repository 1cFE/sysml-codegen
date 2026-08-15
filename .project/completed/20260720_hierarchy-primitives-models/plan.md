# Implementation Plan: Hierarchy Primitives and Data Models

**Status:** Complete, audited
**Created:** 2026-07-08
**Last Updated:** 2026-07-08

## Source Documents

- **Spec:** `.project/active/hierarchy-primitives-models/spec.md`
- **Spec review:** `.project/active/hierarchy-primitives-models/spec-review.md`
- **Design:** `.project/active/hierarchy-primitives-models/design.md`
- **Design review:** `.project/active/hierarchy-primitives-models/design-review.md`

Use `design.md` for API shape, ownership boundaries, dataclass fields, and compatibility strategy.
This plan only records the execution order, proof points, file-level steps, and gates.

## Implementation Strategy

**Phasing Rationale:** Land the shared primitive surface in agentic-mbse first, because every
sysml-codegen compatibility change depends on those class objects and shared functions existing.
Close the hierarchy-profile matrix before touching codegen wrappers so validation and backlog
decisions stay inside agentic-mbse. Then wire sysml-codegen to the shared API and finish with
cross-repo gates plus fixture byte-identity proof.

**Critical Path:** shared dataclasses and hierarchy API -> profile dispositions/backlog updates ->
sysml-codegen re-exports and wrappers -> full cross-repo validation.

**First Proof Point:** `agentic-mbse` can import `agentic_mbse.sysml.hierarchy`, construct the moved
dataclasses with exact field order/defaults, and classify literal/chain/expression redefinitions
without importing sysml-codegen.

**Overall Validation Approach:**

- Each phase starts with tests or a proof artifact.
- Targeted gates run before full gates.
- Snapshot and generated fixture directories must remain byte-identical.
- Known caveat: project-wide mypy baselines were already dirty before this item
  (`agentic-mbse` about 107 errors, `sysml-codegen` about 98 errors after Item 2). Run mypy if the
  local baseline allows it; otherwise record unchanged counts and do not treat unrelated baseline
  debt as this item.

---

## Phase 1: agentic-mbse Shared Dataclasses and Hierarchy API

### Goal

Move the neutral hierarchy primitive layer into agentic-mbse and prove it works without a
sysml-codegen dependency.

### Assumption Under Test

The existing redefinition classifier, owned-member redefinition scan, multiplicity scan, and three
primitive models are reusable SysML facts rather than codegen policy.

### Test Stencil (Write This First)

```python
def test_classify_redefinition_literal_chain_expression(fake_reference_usage):
    literal = classify_redefinition(fake_reference_usage(":>> cost = 7.0"), "Plant::Driver")
    chain = classify_redefinition(fake_reference_usage(":>> cost = economics.rate"), "Plant::Driver")
    expr = classify_redefinition(fake_reference_usage(":>> cost = base + fee"), "Plant::Driver")

    assert literal.redefinition_type is RedefinitionType.LITERAL
    assert chain.source_path == ["economics", "rate"]
    assert expr.expression_text == "base + fee"
```

### Changes Required

**See `design.md` for:**

- API and public helper decision -> `design.md#public-api`
- dataclass move and exact field contract -> `design.md#dataclass-move-and-re-export-strategy`
- type-map inventory scope -> `design.md#type_map-inventory-strategy`
- implementation gotchas -> `design.md#implementation-notes`

**Specific file changes:**

- [x] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_hierarchy.py` (NEW): add failing tests
  for dataclass field order/defaults, enum values, public imports, literal/chain/expression
  classification, type-only skip, non-`ReferenceUsage` skip, deep target paths, multiplicity
  extraction, singleton exclusion, and float `cached_lower_bound` integer casting.
- [x] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_hierarchy.py` (NEW): add the TYPE_MAP
  inventory test from the moved `agentic_mbse.sysml.hierarchy` source or AST.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py`: add
  `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` as standard-library dataclasses or
  enum/dataclass pairs with exact sysml-codegen field order and defaults.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py` (NEW): implement
  `classify_redefinition`, `extract_redefinitions`, and `extract_multiplicities` using only
  agentic-mbse helpers and standard-library code.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`: re-export the hierarchy API.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py`: no production change
  expected; only inspect if the TYPE_MAP proof exposes a missing direct adapter string.

### Validation

**Automated:**

- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_hierarchy.py`
  -> shared primitive tests pass.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/data_models.py src/agentic_mbse/sysml/hierarchy.py src/agentic_mbse/sysml/__init__.py tests/test_sysml/test_hierarchy.py`
  -> touched files are clean.

**Manual/proof checks:**

- [x] Verify `rg "sysml_codegen" /home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py`
  has no hits.
- [x] Verify the TYPE_MAP inventory is limited to direct adapter strings in
  `agentic_mbse.sysml.hierarchy`: `ReferenceUsage`, `FeatureChainExpression`,
  `FeatureReferenceExpression`, and `PartUsage` unless implementation adds a new direct call.
- [x] Reset or bypass `SysideAdapter._type_map` around fake-syside checks in the inventory test.
  The adapter caches the map, so the test must not depend on test order.
- [x] Do not broaden the TYPE_MAP inventory to transitive strings used by expression helpers.
  Existing expression-helper coverage owns that surface.

**What We Know Works After This Phase:**

The shared dataclasses and hierarchy primitive API exist in agentic-mbse, are importable, and pass
the behavior and TYPE_MAP proofs that sysml-codegen will rely on.

---

## Phase 2: Hierarchy-Profile Disposition Matrix and Backlog/Rule Updates

### Goal

Close the spec-required hierarchy-profile loop in agentic-mbse by implementing only rules supported
by moved primitive facts and filing the rest with exact backlog rows.

### Assumption Under Test

The profile rows split cleanly: unsupported RHS and multiplicity-shape checks can land from shared
facts, while precedence and ambiguous inherited attributes require codegen-local policy and should
be filed.

### Test Stencil (Write This First)

```python
def test_level6_warns_on_unresolved_multiplicity_count(tmp_path):
    model = tmp_path / "multiplicity_probe.sysml"
    model.write_text("part def Pack { part cell[pack_count]; }")

    issues = run_level6(model)

    assert any(issue.rule_id == "L6_HIER_MULTIPLICITY_SHAPE" for issue in issues)
```

### Changes Required

**See `design.md` for:**

- disposition table -> `design.md#checking-profile-disposition-matrix`
- test placement -> `design.md#test-placement`
- risks around overreaching rules -> `design.md#potential-risks`

**Specific file changes:**

- [x] `/home/reid/1cfe/agentic-mbse/tests/test_validation/test_item3_hierarchy_profile.py` (NEW or
  nearest existing Level-6 test file): add failing tests for each `NEW RULE` row that lands.
- [x] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`: implement
  only profile checks that can use agentic-mbse primitives without importing sysml-codegen.
- [x] `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`: add or update filed rows for
  `PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE` and
  `PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR` if implementation confirms they cannot land in this
  item.
- [x] `.project/active/hierarchy-primitives-models/plan.md`: update this phase's Implementation
  Notes with the final disposition matrix: `EXISTING`, `NEW RULE`, `FILED`, or `NO-OP`, including
  exact rule, fixture shape, severity, rationale, and backlog ID when filed.

### Validation

**Automated:**

- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_validation/test_item3_hierarchy_profile.py`
  or the exact touched Level-6 test file -> new/profile disposition tests pass.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_hierarchy.py <touched-level6-test-file>`
  -> shared primitive and profile tests pass together.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/validation/level6_architecture.py <touched-test-files>`
  -> touched files are clean.

**Manual/proof checks:**

- [x] Verify no profile code imports `sysml_codegen`.
- [x] Verify filed backlog rows include exact rule, fixture shape, severity, rationale, and backlog ID.
- [x] Verify the missing-instantiation row is recorded as `EXISTING`, not reimplemented.

**What We Know Works After This Phase:**

agentic-mbse has a closed hierarchy-profile disposition record. Rules that can run from shared
facts are tested, and rows that need codegen policy are filed without moving policy across repos.

---

## Phase 3: sysml-codegen Re-Export/Wrapper Compatibility

### Goal

Replace sysml-codegen's local primitive model/function bodies with compatibility re-exports and
wrappers that delegate to agentic-mbse while leaving hierarchy policy local.

### Assumption Under Test

Existing sysml-codegen callers can keep their import paths while using the shared class objects and
shared primitive functions.

### Test Stencil (Write This First)

```python
def test_extract_redefinitions_wrapper_delegates(monkeypatch):
    sentinel = [object()]
    part = object()

    monkeypatch.setattr(shared_hierarchy, "extract_redefinitions", lambda arg: sentinel)

    assert hierarchy_resolver.extract_redefinitions(part) is sentinel
```

### Changes Required

**See `design.md` for:**

- compatibility paths -> `design.md#compatibility-paths`
- what stays local -> `design.md#what-stays-in-sysml-codegen`
- snapshot no-churn invariant -> `design.md#required-invariants`

**Specific file changes:**

- [x] `tests/conformance/test_data_models.py`: add object-identity and exact dataclass field
  assertions through `sysml_codegen.extraction.data_models`.
- [x] `tests/unit/test_hierarchy_resolver.py`: add wrapper delegation tests for
  `extract_redefinitions` and `extract_multiplicities`.
- [x] `tests/unit/test_hierarchy_resolver.py`: add `extract_design_overrides` classifier-delegation
  tests that prove local plain-usage filtering still drops CHAIN/EXPRESSION results from plain
  usages and retains literals.
- [x] `src/sysml_codegen/extraction/data_models.py`: import and re-export
  `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` from agentic-mbse; keep
  `HierarchyExtractionResult` and codegen-only models local.
- [x] `src/sysml_codegen/extraction/hierarchy_resolver.py`: import
  `agentic_mbse.sysml.hierarchy` as the shared primitive module; replace local primitive bodies with
  wrappers and update `extract_design_overrides` to call `classify_redefinition`.
- [x] `src/sysml_codegen/snapshot/loader.py`: no behavior change expected; adjust imports only if
  the re-export changes expose a local typing/import issue.
- [x] `tests/unit/test_data_models.py`, `tests/conformance/test_hierarchy_resolver.py`,
  `tests/unit/test_hierarchy_pipeline.py`, and `tests/integration/test_hierarchy_e2e.py`: update
  only if compatibility tests expose import assumptions tied to the old local class definitions.

### Validation

**Automated:**

- [x] Run `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py`
  -> wrapper and identity tests pass.
- [x] Run a snapshot-loader or snapshot round-trip target that touches hierarchy data. Prefer an
  existing narrow command if available; otherwise run
  `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/ -k "snapshot and hierarchy"`
  and record the exact command used in Implementation Notes.
- [x] Run `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/sysml_codegen/extraction/data_models.py src/sysml_codegen/extraction/hierarchy_resolver.py src/sysml_codegen/snapshot/loader.py tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py`
  -> touched files are clean.

**Manual/proof checks:**

- [x] Verify `sysml_codegen.extraction.data_models.RedefinitionData is agentic_mbse.sysml.hierarchy.RedefinitionData`
  and the same identity holds for `RedefinitionType` and `MultiplicityData`.
- [x] Verify `extract_hierarchy_data` still owns orchestration, usage-type indexing, aggregation,
  warnings, and `HierarchyExtractionResult`.
- [x] Verify no generated fixture files changed before proceeding to full gates:
  `cd /home/reid/1cfe/sysml-codegen && git diff -- tests/fixtures`.

**What We Know Works After This Phase:**

sysml-codegen compatibility import paths still work, primitive extraction delegates to agentic-mbse,
and local hierarchy policy remains local.

---

## Phase 4: Cross-Repo Full Gates and Fixture Byte-Identity Proof

### Goal

Run the end-to-end validation needed for a cross-repo PUSH-DOWN item and prove this move did not
change serialized fixtures or generated baselines.

### Assumption Under Test

The move is behavior-preserving for code generation and validation except for intentional
agentic-mbse profile-rule/backlog changes.

### Test Stencil (Proof First)

```bash
cd /home/reid/1cfe/sysml-codegen
git diff -- tests/fixtures
# Expected: no output
```

### Changes Required

**Specific file changes:**

- [x] `.project/active/hierarchy-primitives-models/plan.md`: fill Implementation Notes for all
  phases with actual commands, results, deviations, final profile dispositions, and known baseline
  caveats.
- [x] `.project/CURRENT_WORK.md`: update only if implementation discovers context that a later
  session needs before audit.

### Validation

**agentic-mbse full gates:**

- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/` -> no regressions.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/ tests/` or at minimum touched
  files if the full ruff baseline is dirty; record the exact scope.
- [x] Run `cd /home/reid/1cfe/agentic-mbse && uv run mypy src/` if baseline permits; otherwise
  record the unchanged baseline caveat and current count.

**sysml-codegen full gates:**

- [x] Run `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/` -> no regressions.
- [x] Run `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/` -> current expected full
  source gate is clean after Item 2.
- [x] Run `cd /home/reid/1cfe/sysml-codegen && uv run mypy src/` if baseline permits; otherwise
  record the unchanged baseline caveat and current count.
- [x] Run `cd /home/reid/1cfe/sysml-codegen && git diff -- tests/fixtures` -> no output.

**Cross-repo compatibility proof:**

- [x] Confirm sysml-codegen is using the local editable `agentic-mbse` from
  `/home/reid/1cfe/agentic-mbse` via `pyproject.toml` or environment notes.
- [x] Confirm both repos are on the PUSH-DOWN branch `push-down-item1-expression`.
- [x] Confirm there is no item-level PR closeout; the full PUSH-DOWN epic closes after later items.

**What We Know Works After This Phase:**

The shared move is validated in both repos, compatibility paths are proven, and fixture byte identity
shows no snapshot or generated-output churn.

---

## Environment Setup

See each repo's `CLAUDE.md` for full commands:

- sysml-codegen: `/home/reid/1cfe/sysml-codegen/CLAUDE.md`
- agentic-mbse: `/home/reid/1cfe/agentic-mbse/CLAUDE.md`

Use `uv run` for tests, lint, and mypy. sysml-codegen's `pyproject.toml` points `agentic-mbse` at
`../agentic-mbse` as an editable local source, which is required for this cross-repo move.

## Risk Management

See `design.md#potential-risks` for full risk analysis.

- **Phase 1:** Dataclass defaults or field order can drift. Mitigation: exact ordered
  `dataclasses.fields()` assertions before implementation.
- **Phase 1:** TYPE_MAP inventory can become order-dependent. Mitigation: reset or bypass
  `SysideAdapter._type_map` in fake-syside tests.
- **Phase 1:** TYPE_MAP scope can over-expand. Mitigation: inventory only direct adapter strings in
  `agentic_mbse.sysml.hierarchy`; rely on existing expression-helper coverage for transitive calls.
- **Phase 2:** Profile rules can import codegen policy by accident. Mitigation: grep for
  `sysml_codegen` and file rows that need usage-type indexing or precedence facts.
- **Phase 3:** Compatibility wrappers can retain copied bodies. Mitigation: monkeypatch delegation
  tests for both wrappers and `extract_design_overrides` classifier usage.
- **Phase 4:** Fixture churn can hide a behavior change. Mitigation: `git diff -- tests/fixtures`
  must be empty; any diff blocks completion unless separately reviewed.

## Implementation Notes

Fill this section during implementation. Do not leave final command results only in chat.

### Phase 1 Completion

**Completed:** 2026-07-08

**Actual Changes:** Added `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` to
`agentic_mbse.sysml.data_models`; added `agentic_mbse.sysml.hierarchy`; re-exported the hierarchy
API from `agentic_mbse.sysml`; added primitive behavior, dataclass contract, package export, and
TYPE_MAP inventory tests in `tests/test_sysml/test_hierarchy.py`.

**Commands and Results:**

- `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_hierarchy.py` -> `10 passed`.
- `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/data_models.py src/agentic_mbse/sysml/hierarchy.py src/agentic_mbse/sysml/__init__.py tests/test_sysml/test_hierarchy.py` -> clean.
- `grep -R -n "sysml_codegen" src/agentic_mbse/sysml/hierarchy.py src/agentic_mbse/sysml/data_models.py src/agentic_mbse/validation tests/test_sysml/test_hierarchy.py` -> no hits.

**Issues:** None.

**Deviations:** The inventory test bypasses the adapter cache by monkeypatching `_get_type_map` and
resetting `_type_map`; this implements the design review note. The inventory is limited to direct
strings in `agentic_mbse.sysml.hierarchy`: `ReferenceUsage`, `FeatureChainExpression`,
`FeatureReferenceExpression`, and `PartUsage`.

### Phase 2 Completion

**Completed:** 2026-07-08

**Actual Changes:** Updated `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md` with filed
hierarchy-profile rows. No `level6_architecture.py` change landed because the candidate checks need
codegen-local policy or are already represented by an existing rule.

**Disposition Matrix:**

| Idiom | Disposition | Rule / Backlog ID | Severity | Fixture Shape | Rationale |
|---|---|---|---|---|---|
| Redefinition precedence | FILED | `PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE` | WARN | subtype literal, usage-level literal, and design override all target the same attribute | Needs codegen-local precedence policy and supplied-value ordering. |
| Unsupported redefinition RHS | FILED | `PUSH-DOWN-HIER-PROFILE-UNSUPPORTED-RHS` | WARN | non-literal, non-chain RHS inside `:>>` | Overlaps expression-profile policy; filed rather than duplicating a shallow hierarchy-only rule. |
| Multiplicity shapes | FILED | `PUSH-DOWN-HIER-PROFILE-MULTIPLICITY-SHAPE` | WARN | `part cell[pack_count]` or unresolved upper-bound shape | Needs model-level validation semantics beyond primitive extraction. |
| Missing instantiations | EXISTING | `L6_CALC_DEF_NO_INSTANTIATION` | WARN | reusable definition with no concrete instantiation | Existing agentic-mbse Level-6 rule owns this surface. |
| Ambiguous inherited attributes | FILED | `PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR` | WARN | multiple inherited attributes sanitize or resolve to the same generated field | Needs usage-type indexing and most-specific selection that remain in sysml-codegen. |

**Commands and Results:**

- No new profile test file was created because no `NEW RULE` row landed.
- `grep -R -n "sysml_codegen" src/agentic_mbse/sysml/hierarchy.py src/agentic_mbse/sysml/data_models.py src/agentic_mbse/validation tests/test_sysml/test_hierarchy.py` -> no hits.
- Full agentic-mbse validation in Phase 4 covered the unchanged Level-6 suite: `1278 passed, 1 skipped, 33 deselected, 6 warnings`.

**Issues:** None.

**Deviations:** The plan assumed unsupported RHS and multiplicity-shape checks might land as
`NEW RULE` rows. Implementation closed them as filed backlog rows after confirming a real rule would
either duplicate expression-profile work or require policy this item must leave out of agentic-mbse.

### Phase 3 Completion

**Completed:** 2026-07-08

**Actual Changes:** `sysml_codegen.extraction.data_models` now re-exports the shared hierarchy
model class objects at runtime while keeping typed mirrors for local mypy compatibility.
`hierarchy_resolver.py` delegates primitive redefinition and multiplicity extraction to
`agentic_mbse.sysml.hierarchy`; design override extraction stays local and calls the shared
classifier. Conformance tests now prove class identity and ordered field contracts. Wrapper tests
prove delegation and local plain-usage filtering. The AST dispatch guardrail counts the moved shared
classifier so the audited dispatch-site total remains at seven.

**Commands and Results:**

- `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py` -> `155 passed`.
- `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py tests/conformance/test_ast_dispatch_invariant.py::TestReqAst04DispatchSiteGuardrail::test_total_dispatch_function_count` -> `156 passed`.
- `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/sysml_codegen/extraction/data_models.py src/sysml_codegen/extraction/hierarchy_resolver.py tests/unit/test_hierarchy_resolver.py tests/conformance/test_data_models.py tests/conformance/test_ast_dispatch_invariant.py` -> clean.
- `cd /home/reid/1cfe/sysml-codegen && git diff -- tests/fixtures` -> no output.

**Issues:** None.

**Deviations:** `tests/snapshot` does not exist in this repo, so the requested narrow snapshot
target could not run. The full suite and conformance suite include the available snapshot-loader and
round-trip coverage, and fixture diff stayed empty.

### Phase 4 Completion

**Completed:** 2026-07-08

**Commands and Results:**

- `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/` -> `1278 passed, 1 skipped, 33 deselected, 6 warnings`.
- `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/data_models.py src/agentic_mbse/sysml/hierarchy.py src/agentic_mbse/sysml/__init__.py tests/test_sysml/test_hierarchy.py` -> clean.
- `cd /home/reid/1cfe/agentic-mbse && uv run mypy src/` -> known dirty baseline, `107 errors in 22 files`.
- `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/` -> `2127 passed, 4 skipped`.
- `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/` -> clean.
- `cd /home/reid/1cfe/sysml-codegen && uv run mypy src/` -> known dirty baseline, `98 errors in 22 files`.
- `cd /home/reid/1cfe/sysml-codegen && git diff -- tests/fixtures` -> no output.
- `git status --short --branch` in both repos -> both on `push-down-item1-expression`.

**Fixture Byte-Identity Proof:** `git diff -- tests/fixtures` was empty after implementation and
after full sysml-codegen validation. No snapshot or generated fixture file changed.

**Known Baseline Caveats:** Project-wide mypy remains dirty at the same known Item 2 baselines:
agentic-mbse `107 errors in 22 files`; sysml-codegen `98 errors in 22 files`. These are unrelated
baseline errors, not new Item 3 failures. sysml-codegen uses the local editable agentic-mbse source
from `/home/reid/1cfe/agentic-mbse`.

**Deviations:** No item-level PR closeout. The user wants the whole PUSH-DOWN epic implemented
before PR, so Item 3 proceeds to audit and commit only.

---

**Status:** Complete, audited
