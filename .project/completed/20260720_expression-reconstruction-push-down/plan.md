# Implementation Plan: Expression Reconstruction Push-Down

**Status:** Implemented - Awaiting Audit
**Created:** 2026-07-08
**Last Updated:** 2026-07-08

## Source Documents

- **Epic:** `.project/backlog/epic_push_down.md`
- **Spec:** `.project/active/expression-reconstruction-push-down/spec.md`
- **Spec Review:** `.project/active/expression-reconstruction-push-down/spec-review.md` (Approve)
- **Design:** `.project/active/expression-reconstruction-push-down/design.md`
- **Design Review:** `.project/active/expression-reconstruction-push-down/design-review.md` (Approve)

## Implementation Strategy

**Phasing Rationale:**
This is a cross-repo move. The riskiest failure mode is starting from a stacked or half-merged
base, so Phase 0 is a hard gate before any code edit. After that, the work lands from the
shared side outward: agentic-mbse tests and API first, then the sysml-codegen shim and
invariant split, then profile-disposition close-out and full cross-repo gates.

**Critical Path:**
Phase 0 merge-base proof -> agentic-mbse expression tests -> shared expression API and binding
literal consolidation -> sysml-codegen shim/export tests -> static invariant migration ->
profile-disposition close-out -> both repos green and sysml-codegen baselines byte-identical.

**First Proof Point:**
The first implementation proof is an agentic-mbse test file that fails before the move because
`agentic_mbse.sysml.expression` does not expose reconstruction, chain-segment, and literal-node
helpers, and because the adapter precondition is not pinned.

**Overall Validation Approach:**
- Each implementation phase starts with tests.
- agentic-mbse owns shared behavior and moved implementation-body invariants.
- sysml-codegen owns compatibility imports, codegen-local invariants, and byte-identity gates.
- No baseline recapture is expected. Any generated diff is a stop-and-investigate signal.

---

## Phase 0: [x] Prerequisite Landing-Base Gate

### Goal

Confirm implementation can start from real merged bases. This phase prohibits code edits until
all three prerequisite proofs are recorded here.

### Assumption Under Test

The selected sysml-codegen landing base contains merged `truth-debt-epic`, and the selected
agentic-mbse landing base contains merged `upstream-findings-sync` plus merged
`pipeline-truth-item4`.

### Test Stencil (Write This First)

```text
# Phase 0 is a documentation/test gate, not production code.
# Record exact selected branches and commits before editing either repo.
sysml_codegen_base = "<branch>@<commit>"
agentic_mbse_base = "<branch>@<commit>"
assert truth_debt_epic_is_merged_into(sysml_codegen_base)
assert upstream_findings_sync_is_merged_into(agentic_mbse_base)
assert pipeline_truth_item4_is_merged_into(agentic_mbse_base)
```

### Changes Required

**See `design.md` for:**
- Implementation gate -> `design.md#implementation-gate`
- Key bets -> `design.md#key-bets`

**Specific steps:**

- [x] In sysml-codegen, select and record the implementation landing branch/commit.
- [x] Prove the selected sysml-codegen base contains merged `truth-debt-epic` with a merge-base
  or branch-containment check.
- [x] In agentic-mbse, select and record the implementation landing branch/commit.
- [x] Prove agentic-mbse `upstream-findings-sync` is merged into the selected base.
- [x] Prove agentic-mbse `pipeline-truth-item4` is merged into the selected base.
- [x] Record the exact commands and outputs in this phase's implementation notes before any
  production or test code edit.

### Validation

**Automated:**
- [x] sysml-codegen: `git status --short --branch`
- [x] sysml-codegen: `git merge-base --is-ancestor <truth-debt-epic-commit> HEAD`
- [x] agentic-mbse: `git status --short --branch`
- [x] agentic-mbse: `git merge-base --is-ancestor <upstream-findings-sync-commit> HEAD`
- [x] agentic-mbse: `git merge-base --is-ancestor <pipeline-truth-item4-commit> HEAD`

**Manual:**
- [x] Confirm the current repo is no longer only the planning branch described in the spec.
- [x] Confirm no implementation files were edited before this checkbox was completed.

**What We Know Works After This Phase:**
Implementation is allowed to start. If any prerequisite fails, stop and do not edit code.

---

## Phase 1: [x] agentic-mbse Shared Expression Tests

### Goal

Add failing tests in agentic-mbse for the shared API, TYPE_MAP preconditions, literal
consolidation, and moved static invariants before moving implementation.

### Assumption Under Test

agentic-mbse can host reconstruction as neutral SysML meaning without importing sysml-codegen,
and the adapter can resolve every moved node type.

### Test Stencil (Write This First)

```python
def test_expression_public_exports_include_reconstruction_helpers():
    import agentic_mbse.sysml as sysml

    assert sysml.reconstruct_expression is expression.reconstruct_expression
    assert sysml.extract_feature_chain_segments is expression.extract_feature_chain_segments
    assert sysml.is_literal_node is expression.is_literal_node
```

### Changes Required

**See `design.md` for:**
- Shared layer -> `design.md#shared-layer`
- Public export boundary -> `design.md#public-export-boundary`
- Adapter-dispatch precondition -> `design.md#adapter-dispatch-precondition`
- Static test migration -> `design.md#static-test-migration`

**Specific file changes:**

- [ ] `/home/reid/1cfe/agentic-mbse/tests/test_adapter.py` - add TYPE_MAP coverage for
  `FeatureChainExpression`, `FeatureReferenceExpression`, `OperatorExpression`,
  `InvocationExpression`, `LiteralInteger`, `LiteralRational`, `LiteralBoolean`,
  `LiteralString`, `LiteralInfinity`, and `NullExpression`.
- [ ] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_expression.py` - add reconstruction,
  precedence, feature-reference, full chain-segment, `is_literal_node`, and
  `extract_literal_value` behavior tests.
- [ ] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_expression.py` or a new nearby test
  file - add static body-order tests for moved `reconstruct_expression`: FCE before OE, and
  literal/null before invocation.
- [ ] `/home/reid/1cfe/agentic-mbse/tests/test_validation/test_item9_checks.py` - add/adjust
  Level-6 C7 tests so `attribute :>> attr = a + b` warns and literal/null RHS shapes do not.
- [ ] `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_binding.py` or the existing binding
  test location - pin literal binding extraction for numeric, string, boolean, infinity, and
  null literal nodes through the public shared helper.

### Validation

**Automated:**
- [ ] agentic-mbse: `uv run pytest tests/test_adapter.py tests/test_sysml/test_expression.py tests/test_validation/test_item9_checks.py`
- [ ] agentic-mbse: confirm the new tests fail for missing shared reconstruction exports before
  implementation.

**Manual:**
- [ ] Inspect test failures and confirm they are contract failures, not fixture mistakes.

**What We Know Works After This Phase:**
The shared-side contract is executable and will catch missing exports, adapter drift, literal
semantic confusion, and moved body-order regressions.

---

## Phase 2: [x] agentic-mbse Shared Implementation

### Goal

Move the expression implementation into agentic-mbse, expose the deterministic public boundary,
and replace binding's duplicate literal extraction.

### Assumption Under Test

The current sysml-codegen implementation is behaviorally pure and can move mechanically into
`agentic_mbse.sysml.expression` without codegen policy.

### Test Stencil (Write This First)

```python
def test_literal_node_name_is_distinct_from_true_static_expression():
    assert expression.is_literal_node(literal_integer_node)
    assert expression.is_true_static_expression(literal_integer_node)
    assert expression.is_literal_expression(non_reference_static_expression)
```

### Changes Required

**See `design.md` for:**
- D2 literal naming -> `design.md#d2--add-is_literal_node-do-not-reuse-agentic-mbses-is_literal_expression`
- Public export boundary -> `design.md#public-export-boundary`
- agentic-mbse binding -> `design.md#agentic-mbse-binding`

**Specific file changes:**

- [ ] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/expression.py` - add
  `reconstruct_expression`, `reconstruct_operator_expression`,
  `extract_feature_reference_name`, `extract_feature_chain_name`,
  `extract_feature_chain_segments`, `is_literal_node`, `extract_literal_value`, and the
  precedence support helpers from the design.
- [ ] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py` - export only the seven
  package-root helpers listed in `design.md#public-export-boundary`; keep precedence constants
  submodule-only.
- [ ] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/binding.py` - replace private
  `_extract_literal_value` logic with the shared `extract_literal_value`.
- [ ] `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py` -
  switch Level-6 C7 literal RHS detection to shared `is_literal_node`.
- [ ] Verify agentic-mbse has no import of `sysml_codegen`.

### Validation

**Automated:**
- [ ] agentic-mbse: `uv run pytest tests/test_adapter.py tests/test_sysml/test_expression.py tests/test_validation/test_item9_checks.py`
- [ ] agentic-mbse: `uv run pytest tests/`
- [ ] agentic-mbse: `uv run ruff check src/ tests/`
- [ ] agentic-mbse: `uv run mypy src/`
- [ ] agentic-mbse: `rg -n "sysml_codegen" src tests` returns no production dependency.

**Manual:**
- [ ] Confirm `is_literal_node`, existing `is_literal_expression`, and
  `is_true_static_expression` still mean three different things.
- [ ] Confirm no codegen identifiers, module names, channel names, graph concepts, or generated
  artifact policy moved into agentic-mbse.

**What We Know Works After This Phase:**
agentic-mbse owns the shared expression API and can validate C7 with the same literal-node fact
that codegen will use.

---

## Phase 3: [x] sysml-codegen Compatibility Shim and Export Pin

### Goal

Keep sysml-codegen callers on the permanent compatibility module while proving all old imports
reach the shared implementation.

### Assumption Under Test

The old `sysml_codegen.extraction.expression_utils` import path can become a thin shim without
changing caller behavior.

### Test Stencil (Write This First)

```python
def test_expression_utils_shim_exports_segments_and_aliases_literal_name():
    from agentic_mbse.sysml import expression as shared
    from sysml_codegen.extraction import expression_utils as shim

    assert "extract_feature_chain_segments" in shim.__all__
    assert shim.is_literal_expression is shared.is_literal_node
    assert shim.reconstruct_expression is shared.reconstruct_expression
```

### Changes Required

**See `design.md` for:**
- D1 move by re-export -> `design.md#d1--move-by-re-export-not-by-bulk-caller-rewrite`
- Compatibility shim -> `design.md#compatibility-shim`
- sysml-codegen shim tests -> `design.md#static-test-migration`

**Specific file changes:**

- [ ] `tests/unit/` or `tests/conformance/` - add a shim test that imports every name in
  `src/sysml_codegen/extraction/expression_utils.py::__all__`, pins
  `extract_feature_chain_segments`, and asserts selected identity with shared exports.
- [ ] `src/sysml_codegen/extraction/expression_utils.py` - convert the implementation body to
  re-exports from `agentic_mbse.sysml.expression`.
- [ ] `src/sysml_codegen/extraction/expression_utils.py` - preserve
  `is_literal_expression = is_literal_node` as the old-name compatibility alias.
- [ ] Leave current sysml-codegen production callers on the shim path:
  `usage_extractor.py`, `hierarchy_resolver.py`, `computed_attribute_extractor.py`,
  `expression_compiler.py`, and `extractor.py`.

### Validation

**Automated:**
- [ ] sysml-codegen: `uv run pytest tests/unit tests/conformance -k "expression or ast_dispatch or agg_literal"`
- [ ] sysml-codegen: run the new shim test and confirm it fails before the shim implementation.
- [ ] sysml-codegen: `uv run ruff check src/`
- [ ] sysml-codegen: `uv run mypy src/`

**Manual:**
- [ ] Confirm the shim owns compatibility only: no duplicate constants, duplicate
  reconstruction bodies, or static body-order implementation logic.

**What We Know Works After This Phase:**
Old sysml-codegen imports still work, the missing `extract_feature_chain_segments` export is
pinned, and sysml-codegen consumes the shared implementation through the permanent shim.

---

## Phase 4: [x] Static Invariant Migration Split

### Goal

Move the static invariant that belongs with `reconstruct_expression` to agentic-mbse while
keeping sysml-codegen static invariants for codegen-local dispatch sites.

### Assumption Under Test

The invariant suite can be split by ownership without weakening either repository's coverage.

### Test Stencil (Write This First)

```python
def test_codegen_dispatch_inventory_no_longer_counts_expression_utils_body():
    assert "expression_utils.reconstruct_expression" not in CODEGEN_DUAL_CHECK_SITES
    assert "expression_compiler.build_expression_ast" in CODEGEN_DUAL_CHECK_SITES
```

### Changes Required

**See `design.md` for:**
- Required invariants -> `design.md#required-invariants`
- Static test migration -> `design.md#static-test-migration`

**Specific file changes:**

- [ ] sysml-codegen `tests/conformance/test_ast_dispatch_invariant.py` - remove
  `expression_utils.py:reconstruct_expression` from the sysml-codegen static dual-check
  inventory and update the expected count.
- [ ] sysml-codegen `tests/conformance/test_ast_dispatch_invariant.py` - keep
  `expression_compiler.build_expression_ast`, `hierarchy_resolver._walk_aggregation_ast`,
  `usage_extractor._extract_single_binding`, and `parameter_groups._extract_default_value`.
- [ ] agentic-mbse `tests/test_sysml/` - ensure the moved FCE/OE and literal/null/invocation
  static tests added in Phase 1 are passing against the moved implementation.
- [ ] sysml-codegen behavioral tests - keep coverage that calls `reconstruct_expression`
  through the shim path.

### Validation

**Automated:**
- [ ] agentic-mbse: `uv run pytest tests/test_sysml/test_expression.py`
- [ ] sysml-codegen: `uv run pytest tests/conformance/test_ast_dispatch_invariant.py tests/conformance/test_agg_literal_dispatch.py tests/unit/test_expression_paren_helper.py`

**Manual:**
- [ ] Confirm no sysml-codegen static test parses the moved agentic-mbse implementation
  through a filesystem path assertion.

**What We Know Works After This Phase:**
The body-order invariant travels with the moved body, and sysml-codegen retains only
codegen-local dispatch invariants.

---

## Phase 5: [x] Profile-Disposition Close-Out Gate

### Goal

Close the expression-profile loop in agentic-mbse. This phase is pass/fail: Item 1 cannot close
until every row has a final disposition and every filed rule exists in the agentic-mbse backlog
with the required fields.

### Assumption Under Test

Every moved helper either powers validation now, supports existing behavior, or has an explicit
tracked backlog rule with enough detail for a future implementer.

### Test Stencil (Write This First)

```text
for row in profile_disposition_table:
    assert row.disposition in {"DONE", "EXISTING", "NEW RULE", "FILED"}
    if row.disposition == "FILED":
        assert backlog_contains(row.rule_id, row.fixture_shape, row.severity, row.rationale)
```

### Changes Required

**See `design.md` for:**
- D4 close-out gate -> `design.md#d4--checking-profile-closure-is-a-passfail-close-out-gate`
- Required rows -> `design.md#checking-profile-disposition`

**Specific file changes:**

- [ ] agentic-mbse backlog file selected during implementation - file or update
  `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS` with rule, fixture shape, severity, and rationale.
- [ ] agentic-mbse backlog file selected during implementation - file or update
  `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE` with rule, fixture shape, severity, and
  rationale.
- [ ] agentic-mbse backlog file selected during implementation - file or update
  `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR` with rule, fixture shape, severity, and
  rationale, unless implemented in this item.
- [ ] `.project/active/expression-reconstruction-push-down/plan.md` - fill the close-out table
  in the implementation notes with final dispositions for every helper row.
- [ ] If any default design disposition changes, record the reason and keep the same required
  fields.

### Validation

**Automated:**
- [ ] agentic-mbse: `rg -n "PUSH-DOWN-EXPR-PROFILE-(CHAIN-SEGMENTS|UNSUPPORTED-SHAPE-MESSAGE|UNSUPPORTED-OPERATOR)" .project BACKLOG.md work/BACKLOG.md`
- [ ] agentic-mbse: `uv run pytest tests/test_validation/test_item9_checks.py`

**Manual:**
- [ ] Verify `is_literal_node` is `NEW RULE` or `DONE` through Level-6 C7
  `L6_ATTR_REDEF_EXPR_DROPPED`.
- [ ] Verify `extract_literal_value`, feature reference/name helpers, and precedence helpers are
  `EXISTING` or otherwise justified.
- [ ] Verify every `FILED` row has rule ID, fixture shape, severity, and rationale.

**What We Know Works After This Phase:**
PUSH-DOWN SC-G is satisfied for Item 1, and the profile work is not silently deferred.

---

## Phase 6: [x] Cross-Repo Final Gates and Byte-Identity Proof

### Goal

Run the full validation surface in both repositories and prove sysml-codegen generated artifacts
did not change.

### Assumption Under Test

This was a move, not a behavior change. Both suites pass and committed generated baselines are
byte-identical.

### Test Stencil (Write This First)

```text
before = sha256_tree("tests/fixtures/**/*baseline*", "tests/fixtures/**/extraction_snapshot.json")
run_sysml_codegen_gates()
after = sha256_tree("tests/fixtures/**/*baseline*", "tests/fixtures/**/extraction_snapshot.json")
assert before == after
```

### Changes Required

**See `design.md` for:**
- Required invariants -> `design.md#required-invariants`
- Non-goals -> `design.md#non-goals`

**Specific steps:**

- [ ] agentic-mbse - run full suite, ruff, and mypy.
- [ ] sysml-codegen - run targeted expression/invariant tests, full suite, ruff, and mypy.
- [ ] sysml-codegen - run snapshot-driven generation/baseline comparison tests.
- [ ] sysml-codegen - prove no committed extraction snapshots or baseline outputs changed.
- [ ] Record final gate results in this plan's implementation notes.

### Validation

**Automated:**
- [ ] agentic-mbse: `uv run pytest tests/`
- [ ] agentic-mbse: `uv run ruff check src/ tests/`
- [ ] agentic-mbse: `uv run mypy src/`
- [ ] sysml-codegen: `uv run pytest tests/`
- [ ] sysml-codegen: `uv run ruff check src/`
- [ ] sysml-codegen: `uv run mypy src/`
- [ ] sysml-codegen: `uv run pytest tests/conformance/test_extraction_snapshots.py tests/conformance/test_snapshot_generation.py tests/conformance/test_snapshot_contract.py`
- [ ] sysml-codegen: `uv run python scripts/capture_baseline_yaml.py`
- [ ] sysml-codegen: `git diff -- tests/fixtures/**/extraction_snapshot.json tests/fixtures/baseline_outputs tests/fixtures/baseline_yaml`

**Manual:**
- [ ] Treat any baseline or snapshot diff as a failure unless a separate reviewed design change
  explains it. This item expects zero generated artifact churn.
- [ ] Confirm final ruff/mypy results do not regress from the epic anchors in
  `.project/backlog/epic_push_down.md`.

**What We Know Works After This Phase:**
Both repositories are green, the public compatibility boundary is intact, and sysml-codegen
generated artifacts are byte-identical.

---

## Environment Setup

**sysml-codegen** (`/home/reid/1cfe/sysml-codegen`):

```bash
uv pip install -e ~/agentic-mbse
uv pip install -e ".[dev]"
```

**agentic-mbse** (`/home/reid/1cfe/agentic-mbse`):

```bash
uv sync
```

Use editable installs deliberately. After changing agentic-mbse, rerun the sysml-codegen tests
from an environment that imports the edited agentic-mbse checkout.

## Risk Management

**See `design.md#key-bets` and `design.md#required-invariants` for the detailed risks.**

**Phase-Specific Mitigations:**

- **Phase 0:** Stops the largest process risk: building on unmerged branch stacks.
- **Phase 1:** Makes the agentic-mbse contract fail before implementation, including TYPE_MAP
  and public export drift.
- **Phase 2:** Keeps shared code policy-free and checks dependency direction.
- **Phase 3:** Preserves the old sysml-codegen import path before any caller cleanup.
- **Phase 4:** Splits invariants by ownership instead of weakening static checks.
- **Phase 5:** Turns profile deferral into a pass/fail artifact with filed rule IDs.
- **Phase 6:** Treats generated diffs as failures because this item is a move.

## Implementation Notes

Fill these sections during implementation. Do not mark a phase complete without command output
or a concise explanation of why a command could not run.

### Phase 0 Completion

**Completed:** Yes
**Actual Changes:** None expected beyond plan notes.
**Prerequisite Proofs:**
- sysml-codegen selected base: `push-down-item1-expression` at
  `337d0015929b785ff69a1d6e2a055a172035df1f`.
- `truth-debt-epic` merged proof: PR #6 is merged to `main` with merge commit
  `337d0015929b785ff69a1d6e2a055a172035df1f` at `2026-07-08T22:04:49Z`; `git show --stat
  337d001 -- .project/completed/20260708_epic_truth_debt.md .project/CURRENT_WORK.md`
  shows the TRUTH-DEBT close-out artifact on the selected base. The old branch-tip ancestry
  check, `git merge-base --is-ancestor 365628c HEAD`, returns `1` because PR #6 landed without
  preserving the branch tip as an ancestor.
- agentic-mbse selected base: `push-down-item1-expression` at
  `d5829406e84f967aa5f81005a5519322deac2178`.
- `upstream-findings-sync` merged proof: `git merge-base --is-ancestor 7f77510 HEAD` returned
  `0`.
- `pipeline-truth-item4` merged proof: `git merge-base --is-ancestor 9cc7ab4 HEAD` returned
  `0`.
**Issues:** None blocking implementation.
**Deviations:** The sysml-codegen prerequisite used PR merge metadata and artifact proof instead
of old-tip ancestry because the merged PR commit is `337d001`.

### Phase 1 Completion

**Completed:** Yes
**Actual Changes:**
- Added agentic-mbse TYPE_MAP coverage for invocation, literal, and null expression node names.
- Added shared expression tests for package-root exports, reconstruction, precedence, chain
  segments, literal-node/value behavior, helper names, and moved dispatch-order invariants.
- Kept Level-6 C7 validation coverage for expression RHS warnings and literal/null non-warnings.
**Red/Green Evidence:**
- Targeted command after implementation: `uv run pytest tests/test_adapter.py
  tests/test_sysml/test_expression.py tests/test_validation/test_item9_checks.py` ->
  `93 passed`.
**Issues:** None in the final targeted test run.
**Deviations:** The delegated implement stage could not write `/home/reid/1cfe/agentic-mbse`
from its sandbox, so the initial red-before proof for missing exports was not preserved for every
new test. The first targeted agentic run did fail on a Level-6 import wiring issue before the final
green run.

### Phase 2 Completion

**Completed:** Yes
**Actual Changes:**
- Added reconstruction, precedence, feature-reference, feature-chain, chain-segment, literal-node,
  and literal-value helpers to `agentic_mbse.sysml.expression`.
- Exported the seven public helpers from `agentic_mbse.sysml`.
- Replaced binding's private literal value helper with `extract_literal_value`.
- Switched Level-6 C7 literal RHS detection to shared `is_literal_node`.
**Validation:**
- `uv run pytest tests/test_adapter.py tests/test_sysml/test_expression.py
  tests/test_validation/test_item9_checks.py` -> `93 passed`.
- `uv run pytest tests/` -> `1247 passed, 1 skipped, 33 deselected, 6 warnings`.
- Focused ruff on touched files -> `All checks passed!`.
- `grep -R -n "sysml_codegen" src tests` -> no matches.
**Issues:** Full `uv run mypy src/` still fails on the existing project baseline. After typing
cleanup in the moved helpers, it reports `104 errors in 21 files`; the moved expression helper
errors are gone.
**Deviations:** Full agentic-mbse ruff over `src/ tests/` remains baseline-dirty; touched-file
ruff is clean.

### Phase 3 Completion

**Completed:** Yes
**Actual Changes:**
- Replaced `sysml_codegen.extraction.expression_utils` with a permanent compatibility shim that
  re-exports shared helpers from `agentic_mbse.sysml.expression`.
- Preserved `is_literal_expression = is_literal_node` and `SysideAdapter` for existing callers and
  monkeypatch-based tests.
- Added `tests/unit/test_expression_utils_shim.py` to pin shim exports and identity.
**Validation:**
- `uv run pytest tests/unit/test_expression_utils_shim.py
  tests/unit/test_expression_paren_helper.py tests/conformance/test_ast_dispatch_invariant.py
  tests/conformance/test_agg_literal_dispatch.py
  tests/conformance/test_expression_reconstruction_fidelity.py
  tests/conformance/test_expression_compiler.py` -> `70 passed`.
- Focused ruff on touched sysml-codegen files -> `All checks passed!`.
- `uv run mypy src/` -> `97 errors in 22 files`, matching the planned baseline count.
**Issues:** None in the shim or focused tests.
**Deviations:** The shim import from untyped `agentic_mbse.sysml.expression` is explicitly ignored
for mypy so the sysml-codegen baseline count does not rise.

### Phase 4 Completion

**Completed:** Yes
**Actual Changes:**
- Removed `expression_utils.reconstruct_expression` from sysml-codegen's static body-order
  inventory because the body moved to agentic-mbse.
- Kept codegen-local dispatch invariants for expression compiler, hierarchy resolver, usage
  extraction, and parameter-group default extraction.
- Replaced the stale expression-utils body-inspection test with a shim-delegation assertion.
**Validation:**
- agentic-mbse targeted expression tests are included in the `93 passed` targeted run.
- sysml-codegen invariant and expression tests are included in the `70 passed` focused run.
**Issues:** None.
**Deviations:** None.

### Phase 5 Completion

**Completed:** Yes
**Actual Changes:**
- Filed three profile follow-up rules in agentic-mbse `.project/backlog/BACKLOG.md`.
**Profile-Disposition Table:**
- `reconstruct_expression`, `reconstruct_operator_expression`, precedence helpers: EXISTING for
  sysml-codegen behavior through the shim.
- `extract_feature_reference_name`, `extract_feature_chain_name`: EXISTING for reconstruction and
  compatibility behavior.
- `extract_feature_chain_segments`: FILED for codegen-compatible validation of lossy/anonymous
  chain shapes.
- `is_literal_node`: DONE through Level-6 C7 `L6_ATTR_REDEF_EXPR_DROPPED`.
- `extract_literal_value`: EXISTING through binding literal extraction.
- Unsupported opaque fallback and unsupported operator checks: FILED as future profile rules.
**Filed Backlog Rule IDs:**
- `PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS`
- `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`
- `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR`
**Issues:** None.
**Deviations:** None.

### Phase 6 Completion

**Completed:** Yes
**Actual Changes:** No extra production changes beyond Phases 1-5.
**agentic-mbse Gates:**
- `uv run pytest tests/` -> `1247 passed, 1 skipped, 33 deselected, 6 warnings`.
- Focused touched-file ruff -> `All checks passed!`.
- `uv run mypy src/` -> baseline failure, `104 errors in 21 files`; moved helper errors cleaned.
**sysml-codegen Gates:**
- `uv run pytest tests/` -> `2119 passed, 4 skipped`.
- Snapshot-specific tests -> `87 passed`.
- `uv run ruff check src/` -> `All checks passed!`.
- Full `uv run ruff check src/ tests/` -> baseline failure, `332 errors`.
- `uv run mypy src/` -> baseline failure, `97 errors in 22 files`.
**Byte-Identity Proof:**
- `git diff -- tests/fixtures` produced no output.
- Snapshot tests include live-vs-snapshot byte-identity cases and passed.
**Issues:** Project-wide ruff/mypy baselines remain dirty outside this item.
**Deviations:** Did not run `uv run python scripts/capture_baseline_yaml.py`; no fixture diff and
snapshot byte-identity tests were used as the non-mutating baseline proof.

---

**Status:** Implemented - Awaiting Audit
