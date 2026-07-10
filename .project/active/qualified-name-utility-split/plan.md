# Implementation Plan: Qualified-Name Utility Split

**Status:** Implemented - awaiting audit
**Created:** 2026-07-08
**Last Updated:** 2026-07-08
**Branch:** `push-down-item1-expression` full PUSH-DOWN epic branch

## Source Documents

- **Spec:** `.project/active/qualified-name-utility-split/spec.md`
- **Spec Review:** `.project/active/qualified-name-utility-split/spec-review.md` - Approved
- **Design:** `.project/active/qualified-name-utility-split/design.md`
- **Design Review:** `.project/active/qualified-name-utility-split/design-review.md` - Approved
- **Epic:** `.project/backlog/epic_push_down.md`

See `design.md#next-stage-handoff` for the fixed implementation contract. This plan does not
include item-level PR steps; the full PUSH-DOWN PR happens after Items 1-4 are implemented and
audited.

## Implementation Strategy

**Phasing Rationale:**
Land the agentic-mbse shared API first, because sysml-codegen's compatibility shim needs a stable
target and the import direction must stay one-way. Close the checking-profile loop before changing
codegen callers, so `ITEM-SYNC-C8` is not lost during the move. Then switch sysml-codegen to the
shared implementation and prove byte identity.

**Critical Path:**
agentic-mbse shared module and exports -> agentic-mbse tests/profile disposition -> sysml-codegen
shim and local builder tests -> both repo validation and `tests/fixtures` byte-identity proof.

**First Proof Point:**
`agentic_mbse.sysml.qualified_names` exposes the exact six helpers, passes moved INV-5 tests, and
agentic-mbse still has no `sysml_codegen` import.

**Overall Validation Approach:**
- Start each phase by writing the targeted tests or disposition check.
- Validate each repo at the narrowest useful surface before running full suites.
- Treat any `tests/fixtures` diff in sysml-codegen as a failed invariant until classified.
- Record baseline caveats separately from item failures.

---

## Phase 1: agentic-mbse Shared API and Pure Tests

### Goal

Create the shared qualified-name implementation and public exports in agentic-mbse before any
sysml-codegen shim work. This proves the dependency direction and gives sysml-codegen a real shared
module to import.

### Assumption Under Test

The six moved helpers are pure SysML name utilities and can run in agentic-mbse with only standard
library dependencies.

### Test Stencil (Write This First)

```python
def test_sanitize_name_inv5_guarantees():
    for raw in ["", None, "$$$", "2nd stage", "class", "'Margin Part'"]:
        result = sanitize_name(raw)
        assert result
        assert result.isidentifier()
        assert not keyword.iskeyword(result)


def test_sanitize_qualified_name_is_apply_once_boundary():
    assert sanitize_qualified_name("Lib::'Margin Part'") == "Lib__Margin_Part"
    assert sanitize_qualified_name("Lib__Margin_Part") == "Lib_Margin_Part"
```

### Changes Required

**See `design.md` for:**
- Shared API and export contract -> `design.md#architecture`
- Exact signatures -> `design.md#implementation-notes`
- INV-5 and apply-once invariants -> `design.md#required-invariants`
- Test placement -> `design.md#test-placement`

**Specific file changes:**

#### 1. agentic-mbse tests

**File:** `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_qualified_names.py` (NEW - write first)

- [x] Add pure tests for `sanitize_name`, `build_element_qualified_name`, QN separator helpers,
      `sanitize_qualified_name`, and `extract_simple_name`.
- [x] Include the non-reentrant `sanitize_qualified_name` test requested by design review.
- [x] Move only pure INV-5/no-churn table coverage that does not import sysml-codegen.

#### 2. agentic-mbse shared module

**File:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py` (NEW)

- [x] Add the six public helpers and private owner-chain helper from `design.md#component-overview`.
- [x] Keep `__all__` explicit and limited to the six public helpers.
- [x] Preserve the current `sanitize_qualified_name` doc contract from `design.md#required-invariants`.

#### 3. agentic-mbse package exports

**File:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`

- [x] Re-export the six helpers and add them to `__all__`, matching the Item 1 expression export pattern.

### Validation

**Automated:**

- [x] `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_qualified_names.py`
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/qualified_names.py src/agentic_mbse/sysml/__init__.py tests/test_sysml/test_qualified_names.py`
- [x] `cd /home/reid/1cfe/agentic-mbse && grep -R -n "sysml_codegen" src tests` -> no hits introduced by this phase.

**Manual:**

- [x] Confirm the public API is exactly the six helpers in `design.md#key-decisions`.
- [x] Confirm any fixture-corpus scan left in sysml-codegen is still local because it needs sysml-codegen machinery.

**What We Know Works After This Phase:**

agentic-mbse owns a reusable qualified-name module with the intended public surface, and the move has
not inverted the repo dependency.

---

## Phase 2: agentic-mbse Name-Profile Close-Out and `ITEM-SYNC-C8`

### Goal

Close the checking-profile loop required by the spec before sysml-codegen switches to the shim.
The implementation must either land the non-injective-name WARN or update the existing
`ITEM-SYNC-C8` backlog row with the shared-sanitizer dependency removed.

### Assumption Under Test

Level 6 can either collect sibling names cheaply enough to warn on same-scope sanitizer collisions,
or the remaining collector work is bounded and can stay filed in the existing backlog row.

### Test Stencil (Write This First if the WARN Lands)

```python
def test_two_sibling_names_with_one_identifier_warns():
    issues = check_qualified_names(model_with_siblings("a b", "a-b"))
    assert one_issue(issues, code=ValidationCode.L6_NAME_SANITIZATION_COLLISION)
    assert collision_issue.severity == Severity.WARNING


def test_same_sanitized_name_in_different_namespaces_does_not_warn():
    issues = check_qualified_names(model_with_unrelated_namespaces("a b", "a-b"))
    assert no_issue(issues, code=ValidationCode.L6_NAME_SANITIZATION_COLLISION)
```

### Changes Required

**See `design.md` for:**
- Conditional C8 decision -> `design.md#key-decisions`
- Helper-by-helper disposition table -> `design.md#checking-profile-disposition`
- Risk around collector scope -> `design.md#potential-risks`

**Specific file changes:**

#### 1. agentic-mbse validation tests or backlog disposition

**Files:**
- `/home/reid/1cfe/agentic-mbse/tests/test_validation/test_item12_checks.py`
- `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md`

- [x] First assess whether sibling-scope collection is small and local to Level 6.
- [x] If it is small, write the positive and unrelated-namespace negative tests before code.
- [x] If it is not small, update the existing `ITEM-SYNC-C8` row only. Do not file a duplicate.

#### 2. agentic-mbse validation code, only if WARN lands

**Files:**
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/types.py`
- `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`

- [x] Add a validation code only if the WARN is implemented.
- [x] Scope comparisons to siblings under the same owning namespace.
- [x] Use `agentic_mbse.sysml.qualified_names.sanitize_name`; do not duplicate sanitizer logic.

#### 3. Plan implementation note

**File:** `.project/active/qualified-name-utility-split/plan.md`

- [x] Record exactly one outcome in Phase 2 notes: `NEW RULE` with fixtures, or `FILED` with the updated `ITEM-SYNC-C8` text.

### Validation

**Automated:**

- [x] If WARN lands: `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_validation/test_item12_checks.py -k "qualified_name or collision or c8"`
- [x] If validation surfaces change: `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml tests/test_quality_gate.py tests/test_check.py`
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/qualified_names.py src/agentic_mbse/sysml/__init__.py src/agentic_mbse/sysml/types.py src/agentic_mbse/validation/level6_architecture.py tests/test_sysml/test_qualified_names.py tests/test_validation/test_item12_checks.py`

**Manual:**

- [x] Verify the helper-by-helper disposition in `design.md#checking-profile-disposition` has a matching implementation note.
- [x] Verify `ITEM-SYNC-C8` is updated, superseded, discharged, or kept with a concrete reason.
- [x] Verify no new backlog row duplicates the existing two-names-one-identifier hazard.

**What We Know Works After This Phase:**

The shared sanitizer has a profile disposition in agentic-mbse, and the existing C8 tracking thread
is current.

---

## Phase 3: sysml-codegen Compatibility Shim and Local Builder Coverage

### Goal

Switch sysml-codegen to import shared helpers from agentic-mbse while preserving permanent
sysml-codegen import paths and keeping ADR-003 builders local.

### Assumption Under Test

Existing sysml-codegen callers can keep importing from `sysml_codegen.core.qualified_names` and
receive the same helper objects and generated names.

### Test Stencil (Write This First)

```python
def test_moved_helpers_are_shared_objects():
    assert shim.sanitize_name is shared.sanitize_name
    assert shim.sanitize_qualified_name is shared.sanitize_qualified_name


def test_codegen_builders_remain_local():
    assert shim.get_channel_name("A__b", "out") == "A__b__out"
    assert not hasattr(shared, "get_channel_name")
```

### Changes Required

**See `design.md` for:**
- Shim shape -> `design.md#architecture`
- Compatibility exports -> `design.md#test-placement`
- Package-level `sanitize_qualified_name` decision -> `design.md#next-stage-handoff`

**Specific file changes:**

#### 1. sysml-codegen shim tests

**File:** `tests/unit/test_qualified_names_shim.py` (NEW - write first)

- [x] Pin object identity for all six moved helpers against `agentic_mbse.sysml.qualified_names`.
- [x] Pin that shared agentic-mbse does not expose the four codegen-owned helpers.
- [x] Pin current `sysml_codegen.core` package exports; if `sanitize_qualified_name` is added there, make that explicit.

#### 2. sysml-codegen compatibility module

**File:** `src/sysml_codegen/core/qualified_names.py`

- [x] Import and re-export the six shared helpers from agentic-mbse.
- [x] Keep `build_parameter_qualified_name`, `get_module_name`, `get_channel_name`, and `owning_part_leaf` local.
- [x] Keep `__all__` explicit and reviewable.

#### 3. sysml-codegen core package exports

**File:** `src/sysml_codegen/core/__init__.py`

- [x] Preserve existing package-level exports.
- [x] Add `sanitize_qualified_name` only if the implementation chooses that compatibility expansion and pins it in tests.

#### 4. sysml-codegen conformance tests

**Files:**
- `tests/conformance/test_naming_conventions.py`
- `tests/conformance/test_sanitize_invariance.py`

- [x] Remove or redirect moved pure helper tests so behavior coverage lives in agentic-mbse.
- [x] Keep codegen-only builder tests for parameters, modules, channels, key formats, registry collision behavior, and `owning_part_leaf`.
- [x] Keep fixture-corpus no-churn scans local when they need snapshot/context machinery.

### Validation

**Automated:**

- [x] `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/unit/test_qualified_names_shim.py`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/conformance/test_naming_conventions.py tests/conformance/test_sanitize_invariance.py`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/sysml_codegen/core/qualified_names.py src/sysml_codegen/core/__init__.py tests/unit/test_qualified_names_shim.py tests/conformance/test_naming_conventions.py tests/conformance/test_sanitize_invariance.py`

**Manual:**

- [x] Confirm the shim has no copied sanitizer implementation.
- [x] Confirm shared-helper object identity proves the permanent compatibility path.
- [x] Confirm no codegen-only helper leaked into `agentic_mbse.sysml.qualified_names`.

**What We Know Works After This Phase:**

sysml-codegen still supports old import paths, codegen-owned builders remain local, and shared
helper calls resolve to agentic-mbse.

---

## Phase 4: Cross-Repo Gates and Byte-Identity Proof

### Goal

Run the full relevant gates in both repositories, prove sysml-codegen fixtures did not change, and
record known baseline caveats without treating them as Item 2 failures.

### Assumption Under Test

The split is behavior-preserving for generation and does not introduce import, lint, or type errors
beyond existing baselines.

### Test Stencil (Write This First)

```bash
# Before final validation, capture the expected byte-identity gate.
git diff -- tests/fixtures
# Expected: no output
```

### Changes Required

**See `design.md` for:**
- Validation approach -> `design.md#validation-approach`
- Byte-identity profile -> `design.md#validation-approach`
- Known move risks -> `design.md#potential-risks`

**Specific file changes:**

#### 1. Implementation notes

**File:** `.project/active/qualified-name-utility-split/plan.md`

- [x] Fill Phase 1-4 completion notes with actual changes, validation outcomes, issues, and deviations.
- [x] Record the final `ITEM-SYNC-C8` outcome and package-level `sanitize_qualified_name` decision.
- [x] Record fixture byte-identity proof.

### Validation

**agentic-mbse automated gates:**

- [x] `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml/test_qualified_names.py`
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/test_sysml tests/test_quality_gate.py tests/test_check.py`
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/`
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run ruff check src/agentic_mbse/sysml/qualified_names.py src/agentic_mbse/sysml/__init__.py src/agentic_mbse/sysml/types.py src/agentic_mbse/validation/level6_architecture.py tests/test_sysml/test_qualified_names.py tests/test_validation/test_item12_checks.py`
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run mypy src/`
- [x] `cd /home/reid/1cfe/agentic-mbse && grep -R -n "sysml_codegen" src tests` -> no hits.

**sysml-codegen automated gates:**

- [x] `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/unit/test_qualified_names_shim.py`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/conformance/test_naming_conventions.py tests/conformance/test_sanitize_invariance.py`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/snapshot tests/conformance`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run pytest tests/`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run ruff check src/sysml_codegen/core/qualified_names.py src/sysml_codegen/core/__init__.py tests/unit/test_qualified_names_shim.py tests/conformance/test_naming_conventions.py tests/conformance/test_sanitize_invariance.py`
- [x] `cd /home/reid/1cfe/sysml-codegen && uv run mypy src/`
- [x] `cd /home/reid/1cfe/sysml-codegen && git diff -- tests/fixtures` -> no output.

**Known baseline caveats to record, not hide:**

- agentic-mbse `uv run mypy src/` may retain the existing project baseline count from Item 1; moved-helper import/type errors are item failures.
- sysml-codegen `uv run mypy src/` may retain the existing project baseline count from Item 1; moved-helper import/type errors are item failures.
- sysml-codegen project-wide `ruff check .` may retain unrelated baseline findings. `ruff check src/` and touched-file ruff must be clean for this item.
- Any sysml-codegen `tests/fixtures` diff is not a baseline caveat. Stop and classify it before accepting any snapshot change.

**Manual:**

- [x] Confirm both repos are on the full PUSH-DOWN epic branch state that includes certified Item 1.
- [x] Confirm no item-level PR body, PR command, or closeout step was added.
- [x] Confirm `git status --short` in both repos separates Item 2 changes from unrelated existing project artifacts.

**What We Know Works After This Phase:**

The split is validated in both repos, the old sysml-codegen import paths still work, and generated
fixture baselines are byte-identical.

---

## Environment Setup

See each repo's `CLAUDE.md` for full environment rules.

Expected local dependency shape:

- agentic-mbse work happens in `/home/reid/1cfe/agentic-mbse`.
- sysml-codegen work happens in `/home/reid/1cfe/sysml-codegen`.
- sysml-codegen should use the local editable agentic-mbse dependency from the same full epic branch.

If sysml-codegen cannot import the new shared helper after Phase 1, refresh the editable dependency
before changing shims:

```bash
cd /home/reid/1cfe/sysml-codegen
uv pip install -e /home/reid/1cfe/agentic-mbse
```

## Risk Management

See `design.md#potential-risks` for detailed risk analysis.

**Phase-Specific Mitigations:**

- **Phase 1:** Keep the new agentic-mbse module standard-library-only and run `rg -n "sysml_codegen" src tests`.
- **Phase 2:** Scope any collision rule to sibling names only; otherwise update the existing C8 backlog row with the remaining collector work.
- **Phase 3:** Use object-identity tests so sysml-codegen cannot accidentally keep a copied sanitizer.
- **Phase 4:** Treat fixture churn as a failed invariant unless proven unrelated to this item.

## Implementation Notes

Fill these during implementation. Do not wait until the end of the item.

### Phase 1 Completion

**Completed:** 2026-07-08
**Actual Changes:** Added `agentic_mbse.sysml.qualified_names` with the six shared helpers, exported them from `agentic_mbse.sysml`, and added pure tests for sanitization, owner-chain QNs, separator conversion, non-reentrant `sanitize_qualified_name`, leaf extraction, exact `__all__`, and package exports.
**Validation:** `uv run pytest tests/test_sysml/test_qualified_names.py` -> 21 passed. Focused ruff on the new module, package export, and tests -> all checks passed. `grep -R -n "sysml_codegen" src tests` -> no hits.
**Issues:** Initial local implementation had a quote-strip typo and an underscore-strip regression; both were fixed before the phase was marked complete.
**Deviations:** None. Fixture-corpus no-churn coverage stayed in sysml-codegen because it depends on codegen fixtures/context.

### Phase 2 Completion

**Completed:** 2026-07-08
**Actual Changes:** Updated the existing agentic-mbse `ITEM-SYNC-C8` backlog row. The row now says the shared sanitizer has landed, while the remaining sibling-scope collector and Level-6 warning still need implementation.
**Validation:** No validation-surface code changed. Focused ruff remained clean for the touched shared module/export/test set. The agentic-mbse full suite later passed with 1268 passed, 1 skipped, 33 deselected.
**Issues:** Level 6 does not currently expose a small, general sibling-name collector. Implementing one here would add new traversal policy outside the utility split.
**Deviations:** The WARN did not land in this item. The spec allowed updating the existing row when the collector work was not small and local.
**C8 Outcome:** FILED/UPDATED. Existing `ITEM-SYNC-C8` now tracks only the remaining sibling-scope collision collector and warning. It keeps the two sibling names that sanitize to one identifier as the positive fixture shape, the unrelated-owner negative, WARNING severity, and the duplicate-path codegen backstop rationale.

### Phase 3 Completion

**Completed:** 2026-07-08
**Actual Changes:** Changed `sysml_codegen.core.qualified_names` into a compatibility shim that imports the six shared helpers from agentic-mbse and keeps the four codegen-owned builders local. Added `tests/unit/test_qualified_names_shim.py` to pin shared-helper object identity, local builder ownership, and package-level export behavior. Removed the unused `OutputRegistry` import surfaced by ruff in `tests/conformance/test_naming_conventions.py`.
**Validation:** Targeted sysml-codegen run `uv run pytest tests/unit/test_qualified_names_shim.py tests/conformance/test_naming_conventions.py tests/conformance/test_sanitize_invariance.py` -> 52 passed. Focused ruff on touched sysml-codegen files -> all checks passed.
**Issues:** None after ruff removed the stale test import.
**Deviations:** None.
**Package Export Decision:** `sysml_codegen.core` did not add `sanitize_qualified_name`; the package-level export surface was preserved. The compatibility path for that helper is `sysml_codegen.core.qualified_names.sanitize_qualified_name`.

### Phase 4 Completion

**Completed:** 2026-07-08
**Actual Changes:** Ran cross-repo targeted and full validation, recorded baseline caveats, and confirmed no item-level PR artifact was added.
**Validation:** agentic-mbse `uv run pytest tests/` -> 1268 passed, 1 skipped, 33 deselected. sysml-codegen `uv run pytest tests/` -> 2122 passed, 4 skipped. sysml-codegen `uv run ruff check src/` -> all checks passed. Focused ruff in both repos -> all checks passed. Targeted sysml-codegen naming/sanitizer run -> 52 passed. Targeted agentic qualified-name run -> 21 passed.
**Issues:** Full mypy remains baseline-dirty in both repos: agentic-mbse `uv run mypy src/` -> 107 errors in 22 files, with no `qualified_names.py` errors; sysml-codegen `uv run mypy src/` -> 98 errors in 22 files, with no `core/qualified_names.py` errors.
**Deviations:** `tests/snapshot tests/conformance` was covered by the full sysml-codegen suite instead of run separately. `rg` was unavailable in the environment, so import-direction checks used `grep -R -n`.
**Byte-Identity Proof:** `git diff -- tests/fixtures` produced no output.
**Baseline Caveats:** agentic-mbse mypy retains 107 existing errors. sysml-codegen mypy retains 98 existing errors. sysml-codegen project-wide `ruff check .` was not required; `ruff check src/` and touched-file ruff passed.

---

**Status:** Complete - awaiting audit
