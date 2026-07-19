# Implementation Plan: GAP-CLOSE Item 3 — Model and Seal Boundary Guards

**Status:** In Progress
**Created:** 2026-07-18
**Last Updated:** 2026-07-18
**Scope:** GAP-CLOSE Item 3 only; no implementation in this stage

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Epic:** [epic_gap_close.md](../../backlog/epic_gap_close.md), Item 3
- **Verified findings:**
  [final gap review](../../research/20260718-123558_constraint-expression-final-gap-review.md),
  F6 and F9; [independent verification](../../research/20260718_gap-review-verification.md),
  F6 and F9
- **Design:** deliberately omitted by the recorded pipeline decision in
  [spec.md#open-questions--deferred-to-design](spec.md#open-questions--deferred-to-design). The
  localized mechanisms and interfaces are specified; this plan re-derives file-level execution
  details from current code.

## Implementation Strategy

### Phasing Rationale

Freeze one source-isolated test input and capture the four required historical RED nodes before
editing production code. Correct the model lifetime guard next because its failure can leave a live
object invalid. Correct directory-symlink detection independently after that, including the emitted
verifier route. Finish with optimized, broader, full, static, diff, and fixture gates over the
combined Item 3 patch.

### Critical Path

Pinned pre-fix RED → initialization-state assignment guard → explicit directory-symlink diagnostic
→ isolated candidate GREEN → repository and scope-preservation gates.

### First Proof Point

An unchanged, hashed overlay runs in fresh processes against clean detached HEAD
`6db321225a5c8568db0287b67ed1d04c03079cc2`. Two model nodes fail only because rejected assignments
mutate or unserialize a default-omission `ConcreteConstraint`; two verifier nodes fail only because
internal and escaping directory symlinks return `ok=True` or lack a fatal diagnostic at the symlink
path. Import, setup, collection, and unrelated failures do not count as RED.

### Re-Derived Feasibility and Risks

- No premise conflict was found. The current model guard at
  `src/sysml_codegen/resolution/models.py:24` still prevalidates only fields in
  `__pydantic_fields_set__`; `eligible` and `exclusion` are defaults on `ConcreteConstraint`.
- The verifier at `src/sysml_codegen/contracts/verify.py:263` still collects `rglob("*")` entries
  and skips every non-file. `Path.rglob` exposes a directory-symlink entry but does not descend
  through it, so the link can be diagnosed directly without following it.
- The main model risk is confusing initialization writes with later assignment. Mitigation: use an
  explicit initialized-instance state check, prevalidate every post-init model-field candidate, and
  continue delegating initialization, private/internal attributes, and accepted assignments to
  Pydantic.
- The main verifier risk is changing regular-file or recorded-file-symlink semantics. Mitigation:
  detect directory symlinks as a separate fatal case alongside the existing extra-artifact walk,
  reuse the existing path-specific integrity diagnostic surface, and pin existing behavior.

### Scope Firewall

- Production changes are limited to `src/sysml_codegen/resolution/models.py` and
  `src/sysml_codegen/contracts/verify.py`.
- Kept tests are limited to `tests/unit/test_concrete_constraint_model.py`,
  `tests/unit/test_verify_package.py`, and `tests/conformance/test_seal_step9.py`, plus Item 3
  evidence under this feature directory.
- Preserve the existing Item 2 hunk in `tests/unit/test_concrete_constraint_model.py` and every
  Item 1–2 or unrelated dirty path. Record pre-item hashes for dirty paths; do not format, revert,
  stage, or absorb them into the Item 3 patch.
- Do not freeze models, change fields or serialization, follow symlinks, change package/seal
  formats, add dependencies, recapture fixtures, or refactor either boundary.
- If a correct guard requires a model lifecycle redesign, a new verifier interface/diagnostic
  schema, fixture changes, or edits outside the allowlist, stop and surface the premise conflict.

### Overall Validation Approach

- Every behavior phase begins with kept tests and an observed defect-specific failure.
- The historical overlay stays byte-identical between baseline and candidate. Both runs use clean
  source roots, fresh processes, disabled user-site imports and bytecode writes, and recorded
  resolved module paths.
- Rejected mutations compare the complete pre/post model, then prove JSON serialization and
  validate-from-JSON equality. Accepted deliberate mutation gets a positive regression.
- Directory-symlink tests cover internal and escaping targets, assert `ok is False`, fatal kind,
  and exact package-relative `path`; regular directories and current file checks remain pinned.
- Hash all 179 current files under `tests/fixtures/` before work and require the same manifest at
  completion.

---

## Phase 1: Pin Isolated Pre-Fix RED

### Goal

Write the kept regressions and a compact external overlay first, then capture reproducible F6/F9
RED at exact clean HEAD without importing code from the dirty editable checkout.

### Assumption Under Test

The four failures reproduce for the verified reasons against the pinned revision, and the same
public model/verifier surfaces can prove candidate GREEN without changing the overlay.

### Test Stencil (Write This First)

```python
def test_default_omission_assignment_is_transactional(make_default_eligible):
    model = make_default_eligible()  # omit eligible and exclusion
    before = model.model_dump(mode="python")
    with pytest.raises(ValueError):
        model.eligible = False
    assert model.model_dump(mode="python") == before
    assert type(model).model_validate_json(model.model_dump_json()) == model
```

```python
@pytest.mark.parametrize("target", ["internal", "escaping"])
def test_directory_symlink_is_fatal(tmp_path, target):
    package, link = sealed_package_with_directory_symlink(tmp_path, target)
    result = verify_package(package, "pkg")
    assert not result.ok
    assert any(d.path == link.relative_to(package).as_posix() for d in result.diagnostics)
```

### Changes Required

- [x] `tests/unit/test_concrete_constraint_model.py`: add separate default-omission regressions for
  rejected `eligible = False` and rejected exclusion installation. Capture complete state before
  each assignment and assert unchanged state plus JSON round trip after rejection.
- [x] `tests/unit/test_verify_package.py`: add internal-target and escaping-target directory-symlink
  regressions with exact link-path diagnostics. Keep a matching real-directory assertion and the
  existing recorded file-symlink test intact.
- [x] `.project/active/gap-boundary-guards/evidence/test_gap_boundary_guards_overlay.py` (new):
  encode the same four independently selectable nodes without depending on dirty test helpers.
- [x] `.project/active/gap-boundary-guards/evidence.md` (new during implementation): record the
  revision, clean tree identity, exact commands, Python/Pydantic versions, resolved source paths,
  overlay SHA-256, fixture manifest hash, exit status, and defect-specific output.
- [x] Create clean baseline and candidate source trees beneath separate `mktemp -d` roots. Keep the
  overlay outside both. Do not stash, clean, reset, or checkout files in the shared dirty worktree.

### Validation

**Automated:**

- [x] Run each overlay node separately at pinned HEAD with baseline `src` first on `PYTHONPATH`,
  `PYTHONNOUSERSITE=1`, and `PYTHONDONTWRITEBYTECODE=1`.
- [x] Require both F6 nodes to fail only on the unchanged/serializable assertions after the expected
  validation error. Require both F9 nodes to fail only because verification stays successful or
  omits the exact fatal link-path diagnostic.
- [x] Record a complete sorted SHA-256 manifest for `tests/fixtures/` and pre-item hashes/status for
  all existing dirty files, especially `tests/unit/test_concrete_constraint_model.py`.

**Evidence review:**

- [x] Confirm the overlay hash and resolved imports are identical across all baseline nodes, and no
  collection, environment, or unrelated failure is labeled RED.

**What We Know Works After This Phase:**

Both boundary gaps are independently reproducible at the required revision from a frozen input,
and the byte/scope baselines needed to protect Items 1–2 and fixtures are recorded.

---

## Phase 2: Guard Every Post-Initialization Model Assignment

### Goal

Replace fields-set membership with initialization-state gating so every post-init model-field
assignment is validated against a complete candidate before live mutation, while valid deliberate
mutation remains supported.

### Assumption Under Test

Pydantic initialization can be distinguished from an initialized model's assignments without
using field explicitness, and candidate validation can preserve the current mutable lifecycle.

### Test Stencil (Write This First)

```python
def assert_rejected_assignment_is_transactional(model, field, value):
    before = model.model_dump(mode="python")
    before_json = model.model_dump_json()
    with pytest.raises(ValueError):
        setattr(model, field, value)
    assert model.model_dump(mode="python") == before
    assert type(model).model_validate_json(before_json) == model
```

### Changes Required

- [x] `tests/unit/test_concrete_constraint_model.py`: complete the matrix with the inverse
  eligible/excluded eligibility mutation, rejected exclusion mutation, and the existing
  `ConstraintCatalogEntry` polarity rejection. Make every case assert complete unchanged state and
  JSON round-trip equality. Add one accepted assignment to a deliberately mutable field and prove
  its serialized value changes normally.
- [x] `src/sysml_codegen/resolution/models.py:24`: change `_TransactionalAssignmentModel.__setattr__`
  to bypass candidate prevalidation only while the instance is not initialized or the target is
  not a declared model field. For every initialized model-field assignment, dump the complete
  candidate, replace the proposed field, validate a new instance, then delegate the real write to
  Pydantic only after success.
- [x] Keep `ConcreteConstraint` and `ConstraintCatalogEntry` fields, validators, configuration, and
  serialized shapes unchanged. Do not add freezing or caller-side mutation workarounds.

### Validation

**Automated:**

- [x] Run the model test file normally and with `PYTHONOPTIMIZE=1`; all default-omission, inverse,
  catalog, serialization, and accepted-mutation nodes pass.
- [x] Run targeted mypy and Ruff/format checks on the model production/test files.

**Code review:**

- [x] Confirm the guard does not use `__pydantic_fields_set__` as initialization state, does not
  prevalidate private/internal writes, and never writes the proposed value before candidate
  validation succeeds.

**What We Know Works After This Phase:**

Every tested post-init model-field assignment is transactional regardless of constructor
explicitness; rejected objects remain unchanged and serializable, and valid mutation still works.

---

## Phase 3: Reject Directory Symlinks in Canonical and Emitted Verifiers

### Goal

Detect every encountered directory symlink beneath the package root and return a fatal diagnostic
at its package-relative path before or alongside normal extra-artifact classification.

### Assumption Under Test

The existing non-following `rglob` traversal yields internal and escaping directory-link entries,
so a direct `is_symlink`/directory classification closes F9 without following targets or changing
the seal format.

### Test Stencil (Write This First)

```python
def test_emitted_verifier_rejects_internal_directory_symlink(tmp_path):
    output = generate_snapshot_package(tmp_path)
    (output / "alias_modules").symlink_to(output / "modules", target_is_directory=True)
    emitted_verify = load_emitted_verifier(output / "contracts" / "verify.py")
    result = emitted_verify.verify_package(output, "chain_spike")
    assert not result.ok
    assert any(d.path == "alias_modules" for d in result.diagnostics)
```

### Changes Required

- [x] `src/sysml_codegen/contracts/verify.py:263`: classify directory symlinks explicitly while
  processing the collected walk entries. Emit an existing fatal integrity kind with the exact
  package-relative link path, regardless of whether the resolved target is internal or escaping.
  Do not descend through the link or read target contents.
- [x] `tests/unit/test_verify_package.py`: finish the two-case matrix and pin that each diagnostic is
  fatal and path-specific. Retain tests for a normal sealed package, regular extra files, recorded
  escaping file symlinks, and walk/read failures.
- [x] `tests/conformance/test_seal_step9.py`: load the verifier emitted into a generated package and
  prove it enforces the directory-symlink rule. Keep the existing canonical/emitted byte-identity
  assertion as the drift guard.
- [x] Keep `verify.py` standard-library-only, its public call signatures unchanged, and its emitted
  copy verbatim.

### Validation

**Automated:**

- [x] Run `tests/unit/test_verify_package.py` and the focused emitted-verifier conformance node in
  normal and optimized modes.
- [x] Run the verifier import scan and canonical/emitted byte-identity test.

**Diagnostic review:**

- [x] Confirm both target classes produce the same policy result at their link paths, no traversal
  follows either link, and ordinary directory/file behavior has not changed.

**What We Know Works After This Phase:**

The canonical and generated-package verifier reject internal and escaping directory symlinks with
fatal path-specific diagnostics while preserving existing file and seal behavior.

---

## Phase 4: Isolated GREEN, Repository Gates, and Scope Proof

### Goal

Prove the exact Item 3 production patch closes all four historical nodes and passes focused through
full validation without changing fixtures or absorbing Items 1–2.

### Assumption Under Test

The two localized guards compose without wider model, catalog, generation, or package regressions.

### Test Stencil (Write This First)

```python
def test_item3_scope_and_fixture_firewall():
    assert changed_production_paths() == {"resolution/models.py", "contracts/verify.py"}
    assert fixture_manifest() == baseline_fixture_manifest
    assert inherited_dirty_path_hashes() == pre_item_hashes
```

### Changes Required

- [x] Apply only the two-file production patch to the clean detached candidate tree. Record its
  path allowlist and binary diff SHA-256 before running the unchanged Phase 1 overlay.
- [x] Update `evidence.md` with candidate commands, source paths, overlay/patch hashes, outputs, gate
  counts, license state, mypy comparison, and fixture/scope results.
- [x] Add implementation completion notes to this plan as phases finish; do not mark work complete
  before every applicable gate is recorded.

### Validation

**Isolated candidate:**

- [x] Run all four unchanged overlay nodes in fresh candidate processes and require GREEN with the
  same overlay hash and environment controls as baseline.

**Focused and optimized:**

- [x] `uv run pytest -q tests/unit/test_concrete_constraint_model.py tests/unit/test_verify_package.py`
- [x] Repeat the focused command with `PYTHONOPTIMIZE=1`; record that normal mode remains the primary
  assertion evidence.

**Broader and full:**

- [x] `uv run pytest -q tests/unit/test_contract_models.py tests/unit/test_constraint_graph_extension.py tests/unit/test_constraint_emission.py tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py`
- [x] `uv run pytest tests/`; record exact pass/skip/fail/error counts and license state. Classify
  known license-dependent failures accurately rather than calling them green.

**Static, diff, and fixture:**

- [x] `uv run ruff check` on both touched production files and all touched Item 3 test/evidence
  Python files.
- [x] `uv run ruff format --check` on the same paths; do not format inherited dirty files wholesale.
- [x] `uv run mypy src/`; require no new or changed errors relative to the recorded 76-error project
  baseline. Also run targeted mypy on both touched production files and record exact results.
- [x] Run `git diff --check` on the Item 3 patch/artifact paths. Review any whole-tree report by path
  rather than rewriting unrelated dirty files.
- [x] Require the complete `tests/fixtures/` manifest and `git diff -- tests/fixtures` to match the
  Phase 1 baseline exactly.
- [x] Review `git diff --name-only`, the production allowlist, and inherited dirty-path hashes.
  Confirm no Item 1–2 byte was reverted or absorbed and no model/schema/seal/archive/generated-layout
  change entered Item 3.

**What We Know Works After This Phase:**

The source-isolated candidate closes both F6 default-omission failures and both F9 directory-link
cases, retains mutable valid models and catalog behavior, keeps canonical/emitted verification in
sync, preserves fixtures and prior work, and has complete repository gate evidence.

---

## Implementation Notes

Fill this section during implementation. Record actual changes, commands/results, issues, and any
deviation under the corresponding phase. A deviation that crosses the scope firewall is a premise
conflict, not an implementation convenience.

### Phase 1 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added two default-omission transactional model regressions, the two-case
directory-symlink matrix, the real-directory pin, emitted-verifier regression, and the frozen
four-node overlay. Captured the 179-file fixture manifest and inherited dirty-file hashes before
production edits.
**Validation:** Exact HEAD `6db321225a5c8568db0287b67ed1d04c03079cc2`; overlay SHA-256
`b1cf09fbc3588ef23029b90b829a8a9b1049d2ac3b7bded41d920821fc426fa6`. Each node ran separately
with baseline `src` first, user site disabled, and bytecode disabled. All four exited 1 for the
defect-specific assertion: both defaulted assignments mutated the object after the expected
validation error; both directory symlinks returned `ok=True` with no diagnostics.
**Issues / Deviations:** Used `git archive` into a fresh `mktemp` source root instead of registering
a detached worktree. This preserves the required exact clean tree while avoiding any mutation of
the shared repository's `.git` state. The overlay remained outside the clean source root.

### Phase 2 Completion

**Completed:** 2026-07-18
**Actual Changes:** `_TransactionalAssignmentModel` now treats the presence of Pydantic's
post-initialization state, rather than constructor fields-set membership, as the candidate-validation
boundary. Every declared field assignment validates a complete dumped candidate before delegating
the real write. Added unchanged-state, byte-identical JSON, validate-from-JSON, inverse mutation,
catalog polarity, and accepted `tracking_key` assignment coverage.
**Validation:** Model suite: 28 passed normally and 28 passed under `PYTHONOPTIMIZE=1`. Touched Ruff
and format checks passed. Targeted mypy reported only imported project-baseline errors and none in
the touched model/verifier files.
**Issues / Deviations:** None.

### Phase 3 Completion

**Completed:** 2026-07-18
**Actual Changes:** The canonical extra-artifact walk now detects a directory symlink before its
non-file skip and emits fatal `INVALID_PATH` at the package-relative link path. It neither follows
the entry nor changes recorded file-symlink or real-directory handling. Added internal, escaping,
real-directory, and emitted-verifier coverage.
**Validation:** Verifier unit suite: 29 passed normally and 29 passed optimized. The two
emitted-verifier nodes passed normally and optimized; the canonical/emitted bytes remain identical.
The stdlib-only import scan passed in the verifier suite. Ruff and format checks passed.
**Issues / Deviations:** The first emitted test expected a lowercase diagnostic spelling; the
canonical public value is uppercase `INVALID_PATH`. The test was corrected to the existing
interface, then passed.

### Phase 4 Completion

**Completed:** 2026-07-18
**Actual Changes:** Materialized an exact clean candidate from pinned HEAD, copied only the two
allowed production files, and ran the unchanged overlay from outside that source root. Completed
focused, optimized, broader, default-full, static, diff, fixture, and dirty-scope gates. Updated
the evidence, spec status, plan, and current-work record.
**Validation:** Overlay 4/4 GREEN with unchanged SHA-256
`b1cf09fbc3588ef23029b90b829a8a9b1049d2ac3b7bded41d920821fc426fa6`; two-file patch SHA-256
`ce1944fd824e945349f51d6779402845842fad05730519430822ba6792847447`. Focused: 57 passed;
optimized focused: 57 passed; broader: 53 passed. Default full: 2,213 passed, 205 skipped, 9
deselected, 23 failed, 96 errors; all failures/errors are the known unlicensed SysIDE families,
matching the recorded pre-item 23/96 shape. Touched Ruff/format and scoped diff checks passed.
Project mypy remained at the 76-error baseline with no touched-file error. All 179 fixture hashes
matched and `git diff -- tests/fixtures` was empty.
**Issues / Deviations:** A SysIDE license was unavailable, so the licensed full-suite leg is
accurately unclaimed. The default full command was still run and classified. Fresh `git archive`
trees were used in place of registered worktrees as recorded in Phase 1. Every inherited dirty-file
hash remained unchanged except `tests/unit/test_concrete_constraint_model.py`, the one pre-dirty
file explicitly extended by Item 3; its Item 2 hunk remained byte-for-byte present.

---

**Status:** Complete
