# Implementation Plan: GAP-CLOSE Item 1 — Runtime Evaluation Contract

**Status:** Complete — sysml-codegen leg; external TEAx P0 open
**Created:** 2026-07-18
**Last Updated:** 2026-07-18
**Scope:** sysml-codegen only; do not modify TEAx

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Spec review:** [spec-review.md](spec-review.md) — approved after revision
- **Design:** [design.md](design.md) — component details, decisions, invariants, and exact evidence protocol
- **Design review:** [design-review.md](design-review.md) — resolved and approved
- **Epic:** [epic_gap_close.md](../../backlog/epic_gap_close.md), Item 1

## Implementation Strategy

### Phasing Rationale

Capture the historical defect before touching production code. The first phase freezes one test-only
overlay and proves all three F2 collision classes fail for the intended reason at revision
`6db321225a5c8568db0287b67ed1d04c03079cc2`, with source selection and import isolation proven in
each process. The next two phases add the direct compile-seam guard and the earlier CLI preflight in
separate test-first batches. Phase 4 characterizes the already-correct F1 boundary and narrows only
the template promise. Phase 5 proves candidate behavior, byte stability, route parity where the
existing licensed route is available, and the project quality gates.

This ordering follows [design.md#next-stage-handoff](design.md#next-stage-handoff). It keeps RED
evidence independent of the implementation and makes the no-output-mutation timing testable after
the collision rule itself is known to work.

### Critical Path

Hashed overlay and isolated baseline RED → direct collision validator → pre-write CLI preflight →
F1 characterization and docstring clarification → isolated candidate evidence, byte/parity gates,
and broader validation.

### First Proof Point

The unchanged overlay runs from a detached worktree at the pinned revision and produces exactly
three F2 assertion failures, one for each collision class, because `CodeGenerationError` was not
raised. The separate impact probe passes and proves the old later-definition overwrite. Collection,
source-path, revision, environment, or import failures do not count as RED evidence.

### Overall Validation Approach

- Start every phase with the named tests or evidence probe.
- Use [design.md#appendix-a--exact-evidence-commands](design.md#appendix-a--exact-evidence-commands)
  as the command contract. Do not weaken its detached-worktree, hash, source-path, or fresh-process
  checks.
- Keep the saved overlay byte-identical between baseline and candidate. Keep production changes in
  the three-file allowlisted patch from [design.md#durable-overlay-and-source-isolation](design.md#durable-overlay-and-source-isolation).
- Treat F1 codegen tests as characterization on both revisions, never as pre-fix RED.
- Do not create a new live capture. Use the committed `plant_values` model and snapshot. If a
  SysIDE license is available, generate both routes and compare them; otherwise record the licensed
  live leg as not run, retain the committed input bytes, and complete the snapshot-based
  before/after gate without claiming live parity.
- Preserve every byte under `tests/fixtures/`. Any proposed fixture change stops implementation
  unless it has explicit approval and is recorded as an approved diff.

---

## Phase 1: Freeze the Evidence Input and Capture F2 Pre-Fix RED

### Goal

Create the durable test-only evidence inputs first, then capture reproducible defect-specific RED
for case-fold, underscore-run collapse, and quoted-hyphen collisions at the pinned revision. Also
record the passing old-impact probe and passing F1 characterization separately.

### Assumption Under Test

The pinned source has all three reachable silent-collision modes, and a standalone overlay can
demonstrate them without importing current source, a current editable install, cached bytecode, or
post-fix-only helpers. See [design.md#key-decisions](design.md#key-decisions), D5, and
[design.md#f2-behavior-and-pre-fix-red](design.md#f2-behavior-and-pre-fix-red).

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("collision_case", COLLISION_CASES, ids=COLLISION_IDS)
def test_f2_collision_rejected(collision_case):
    catalog = catalog_with_opposite_predicates(*collision_case.raw_keys)
    with pytest.raises(CodeGenerationError) as error:
        compile_shared_predicates(catalog)
    assert collision_case.expected_name in str(error.value)
    assert all(repr(key) in str(error.value) for key in sorted(collision_case.raw_keys))
```

### Changes Required

**See:** [design.md#exact-collision-contract](design.md#exact-collision-contract),
[design.md#durable-overlay-and-source-isolation](design.md#durable-overlay-and-source-isolation),
and [design.md#appendix-a--exact-evidence-commands](design.md#appendix-a--exact-evidence-commands).

- [x] `.project/active/gap-runtime-contract/evidence/test_gap_runtime_contract_overlay.py` (new):
  add the three stable F2 nodes, old later-body overwrite probe, both generation-API preservation
  probes, F1 characterization group, and import/revision/patch assertions using only public seams
  present at the baseline.
- [x] `.project/active/gap-runtime-contract/evidence/run_generated_constraint_case.py` (new):
  add the fresh-process finite/non-finite route runner with generated-package and codegen path
  assertions.
- [x] `.project/active/gap-runtime-contract/evidence/classify_generated_tree_diff.py` (new):
  add strict complete-tree comparison and approved-docstring-only classification.
- [x] `.project/active/gap-runtime-contract/evidence.md` (new): record the pinned revision, exact
  commands, Python/environment details, hashes, resolved import paths, exit status, and full output
  for each node.
- [x] Create detached baseline and candidate worktrees only under one `mktemp -d` root. Do not use
  checkout, reset, clean, or stash in the current worktree.
- [x] Save SHA-256 hashes before either behavioral run and copy the same overlay bytes into both
  worktrees.

### Validation

**Automated:**

- [x] Run each F2 node separately and the three-node group at the pinned baseline using Appendix
  A2. Each individual node exits 1 with `DID NOT RAISE CodeGenerationError`; the group has exactly
  those three failures.
- [x] Run the old-impact node at the baseline. It exits 0 while proving the shared emitted name and
  later-body overwrite.
- [x] Run the overlay F1 group at the baseline. It exits 0 and is recorded under
  “characterization,” outside the RED table.
- [x] Confirm each process asserts the baseline revision and imports `sysml_codegen` and the
  generation module from the detached worktree. Confirm user-site and bytecode writes are disabled.
- [x] Confirm the current worktree's production diff is unchanged by this phase.

**Manual record check:**

- [x] Verify `evidence.md` contains three distinct F2 RED records, not one aggregate claim, and no
  setup failure is presented as defect evidence.
- [x] Verify hashes and full command output are durable before any temporary worktree is removed.

**What We Know Works After This Phase:**

All three old F2 failure modes are reproducible at the intended revision from a frozen test input,
and F1 is honestly established as already-correct at the generated boundary.

---

## Phase 2: Reject Collisions at the Direct Compile Boundary

### Goal

Add one canonical emitted-name helper and one deterministic uniqueness validator, then enforce it
before predicate compilation for direct callers. Preserve compile-once behavior for repeated
identical definition keys.

### Assumption Under Test

Every predicate rendered into the shared module comes from the validated catalog, and validation
over distinct definition keys catches all emitted-name collisions without changing the successful
compile map. This is the design's only load-bearing bet; see [design.md#key-bets](design.md#key-bets)
and invariants I1–I3, I5–I6 in [design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
def test_collision_rejected_before_predicate_compilation(monkeypatch):
    calls = []
    monkeypatch.setattr(predicate_compiler, "compile_predicate", lambda *a, **k: calls.append(a))
    catalog = catalog_with_keys("Pkg::Foo", "Pkg::foo")
    with pytest.raises(CodeGenerationError, match="constraint_pred_pkg__foo"):
        compile_shared_predicates(catalog)
    assert calls == []
```

### Changes Required

**See:** [design.md#component-overview](design.md#component-overview),
[design.md#implementation-notes](design.md#implementation-notes), and decisions D1–D3 in
[design.md#key-decisions](design.md#key-decisions).

- [x] `tests/unit/test_constraint_emission.py:1`: add exact helper-output cases for all three
  collision classes; exact, both-key `repr` diagnostic assertions; catalog-permutation coverage;
  compiler-spy ordering; identical-key compile-once coverage; and a collision-free control.
- [x] `src/sysml_codegen/generation/modules.py:100`: extract the exact current mapping, validate
  distinct `predicate_definition_key` values, sort collision groups and keys, raise
  `CodeGenerationError` for the first complete group, and call the validator before
  `compile_predicate` or existing compile-loop work.

### Validation

**Automated:**

- [x] `uv run pytest -q tests/unit/test_constraint_emission.py`
- [x] Re-run the three focused collision nodes with different catalog orders; diagnostics are byte
  identical and name the emitted function plus both raw keys.
- [x] Run the compile-once controls; repeated identical keys still produce one function.
- [x] Run `uv run ruff check src/sysml_codegen/generation/modules.py tests/unit/test_constraint_emission.py`.

**Manual code check:**

- [x] Confirm the raw `::`-qualified key is sanitized exactly once and neither call site
  reimplements normalization.
- [x] Confirm no renderer interface, suffix allocation, general sanitizer, predicate arithmetic,
  or TEAx file changed.

**What We Know Works After This Phase:**

Direct compilation cannot silently emit two distinct raw keys as one Python function, diagnostics
are deterministic and complete, and collision-free naming remains unchanged.

---

## Phase 3: Move Rejection Ahead of Every Output Mutation

### Goal

Invoke the same validator from the shared live/snapshot CLI path before overwrite clearing or any
output creation. Prove absence of mutation for both a missing target and a populated nested tree.

### Assumption Under Test

Both generation routes converge on a catalog before the first output mutation, so one early
preflight protects the destructive `overwrite=True` path without route-specific logic. See
[design.md#architecture](design.md#architecture), I4 in
[design.md#required-invariants](design.md#required-invariants), and
[design.md#no-partial-generated-artifacts](design.md#no-partial-generated-artifacts).

### Test Stencil (Write This First)

```python
def test_collision_rejection_preserves_populated_tree(tmp_path, monkeypatch):
    output = seed_nested_tree_with_files_and_symlink(tmp_path / "out")
    before = complete_tree_manifest(output)
    monkeypatch.setattr(pipeline_builder, "build_pipeline_context", colliding_context)
    assert run_codegen(config(output, overwrite=True)) is False
    assert complete_tree_manifest(output) == before
```

### Changes Required

- [x] `tests/unit/test_cli_generation.py:1`: add a reusable full-tree manifest that records sorted
  relative paths, path kinds, regular-file bytes, and symlink targets; add absent-target and
  populated-target tests through the real `run_codegen` API with `overwrite=True`.
- [x] `.project/active/gap-runtime-contract/evidence/test_gap_runtime_contract_overlay.py`: keep
  matching no-write nodes usable in the isolated candidate worktree.
- [x] `src/sysml_codegen/cli/__init__.py:929`: call the Phase 2 validator after context construction,
  gated only on `catalog is not None`, and before `_clear_output_directory` and every setup/write.

### Validation

**Automated:**

- [x] Run the two kept no-mutation tests. The absent root remains absent; the populated tree's full
  manifest remains exactly equal.
- [x] Run Appendix A3's two overlay no-write nodes in the isolated candidate worktree.
- [x] `uv run pytest -q tests/unit/test_cli_generation.py tests/unit/test_constraint_emission.py`
- [x] `uv run pytest -q tests/unit/test_uncovered_params.py tests/unit/test_warning_reconciliation.py tests/unit/test_duplicate_path_failfast.py`

**Manual code check:**

- [x] Confirm the preflight is shared by live and snapshot routes and precedes the first possible
  output write.
- [x] Confirm an empty catalog passes and direct callers remain protected by the Phase 2 recheck.

**What We Know Works After This Phase:**

Collision rejection is transactional at the generation API boundary: neither an absent output nor
an existing output tree is changed.

---

## Phase 4: Characterize F1 and Narrow the Generated Promise

### Goal

Keep generated arithmetic unchanged while adding boundary characterization for division by zero,
`0 ** negative`, exponent overflow, and a raising expression nested beneath a supported connective.
Prove the generated wrapper propagates the original exception class and message before constructing
evidence. Narrow the template docstring by one sentence.

### Assumption Under Test

Native Python arithmetic raises before Kleene comparison or connective logic can manufacture a
verdict, and the generated wrapper constructs no `ConstraintEvaluation` on that path. See decision
D4 in [design.md#key-decisions](design.md#key-decisions) and invariants I7–I9 in
[design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("expression, values, error_type, message", RAISING_CASES)
def test_f1_unmangled_raise(expression, values, error_type, message):
    predicate, _ = compile_and_load(expression)
    with pytest.raises(error_type, match=re.escape(message)):
        predicate(**values)
```

### Changes Required

- [x] `tests/unit/test_predicate_compiler.py:116`: add the three direct arithmetic cases and the
  nested connective case; assert the supported Python exception class and exact message.
- [x] `tests/execution/test_constraint_execution.py:389`: add a production-generated wrapper case
  that invokes `run()` directly and proves the exception class/message leave unchanged and no
  evaluation/report object is produced.
- [x] `src/sysml_codegen/templates/constraint_module.py.jinja2:1`: replace only the verdict
  sentence with the approved narrow wording from D4. Record it as clarity, not behavioral repair.

### Validation

**Automated:**

- [x] `uv run pytest -q tests/unit/test_predicate_compiler.py`
- [x] Run the focused generated-wrapper node in the documented agentic-mbse/TEAx execution
  environment. This exercises generated code only and does not modify TEAx.
- [x] Re-run existing finite/violated and non-finite/indeterminate nodes in
  `tests/unit/test_predicate_compiler.py` and `tests/execution/test_constraint_execution.py`.
- [x] Run the same overlay F1 group in baseline and candidate worktrees. Both pass; neither appears
  in the F2 RED table.

**Manual code and diff check:**

- [x] Confirm no catch, guard, safe arithmetic helper, exception wrapping, fallback, evaluation
  order change, or TEAx edit exists.
- [x] Confirm the template change is exactly the approved one-line documentation clarification.

**What We Know Works After This Phase:**

Sysml-codegen preserves Python's value-versus-raise boundary for all four required shapes. Raised
arithmetic leaves generated code unchanged as an exception rather than becoming evidence. This is
not evaluator-level F1 closure.

---

## Phase 5: Candidate Evidence, Byte Stability, Route Parity, and Quality Gates

### Goal

Replay the frozen overlay against the production-only candidate patch, prove collision-free
before/after generated-byte stability, check live/snapshot parity without recapturing inputs, and
run focused and broader project gates. Finish the durable evidence record without claiming the
external TEAx work.

### Assumption Under Test

The rejected-collision change has no successful-generation byte effect beyond the approved
docstring and its transitive seals, and isolated route/revision processes cannot impersonate one
another through editable installs or `sys.modules`. See I6 and I10 in
[design.md#required-invariants](design.md#required-invariants) and
[design.md#route-parity-and-beforeafter-bytes](design.md#route-parity-and-beforeafter-bytes).

### Test Stencil (Write This First)

```python
def test_generated_tree_diff_is_approved_only(before, after):
    diff = classify_complete_tree_diff(before, after)
    assert diff.unapproved == []
    assert diff.shared_predicates_identical
    assert diff.wrapper_imports_identical
```

### Changes Required

- [x] `.project/active/gap-runtime-contract/evidence/candidate-production.patch` (new): capture
  only `modules.py`, CLI `__init__.py`, and the constraint-module template against the pinned
  revision; require a non-empty, apply-clean, hashed patch.
- [x] `.project/active/gap-runtime-contract/evidence/hashes.txt` and input/output manifests (new):
  record overlay, runner, classifier, patch, committed `plant_values` input, and generated trees.
- [x] `.project/active/gap-runtime-contract/evidence.md`: append candidate GREEN, no-mutation,
  route, before/after, fixture-preservation, focused/broader-test, Ruff, mypy, and diff-check results.
- [x] No fixture file is changed. If a diff appears under `tests/fixtures/`, stop and classify it
  before continuing; only an explicitly approved fixture change may be retained.

### Validation

**Isolated candidate and generated-byte gates:**

- [x] Apply the hashed production patch only to the detached candidate worktree and prove its
  binary diff hash matches the recorded patch before running behavior.
- [x] Run Appendix A3. The unchanged candidate F2 group and F1 characterization group both pass.
- [x] Generate the collision-free `plant_values` snapshot package in baseline and candidate
  worktrees from one hashed copied input. Run the strict classifier. Permit only the narrowed
  wrapper docstring and package contracts/seals transitively derived from those changed bytes.
- [x] Assert `modules/constraints/predicates.py`, every emitted predicate name, every wrapper import
  line, and all other generated files are byte-identical.
- [x] Confirm `git diff -- tests/fixtures` is empty and the recorded fixture manifest is unchanged.

**Route parity and behavior:**

- [x] Assert the committed `plant_values` inputs contain the shared predicates module and at least
  one importing constraint wrapper after generation.
- [x] If the existing SysIDE license is available, run Appendix A4 live and snapshot generation
  from the same committed model/snapshot with the same package name, without creating a new live
  capture. Require complete byte identity.
- [x] Run finite and non-finite behavior for each generated route in separate subprocesses. Each
  process asserts its generated-package root and candidate codegen root before verdict/margin or
  Kleene assertions.
- [x] If the license is unavailable, record the live command as skipped for that external reason;
  do not recapture, synthesize, or weaken the route gate, and do not claim fresh live parity.

**Focused and broader tests:**

- [x] `uv run pytest -q tests/unit/test_constraint_emission.py tests/unit/test_cli_generation.py tests/unit/test_predicate_compiler.py`
- [x] Run the focused execution nodes for raising-wrapper, finite/violated, and
  non-finite/indeterminate behavior in the documented execution environment.
- [x] `uv run pytest -q tests/conformance/test_snapshot_generation.py -k 'plant_values or snapshot_context_has_null_extractor_and_generates'`
- [x] `uv run pytest tests/` with the available license state recorded. Any license-gated skips are
  reported, not treated as passing live evidence.

**Static and diff gates:**

- [x] `uv run ruff check src/ tests/unit/test_constraint_emission.py tests/unit/test_cli_generation.py tests/unit/test_predicate_compiler.py tests/execution/test_constraint_execution.py`
- [x] `uv run ruff format --check` on every touched Python file.
- [x] `uv run mypy src/`; compare with the recorded 76-error project baseline and require no new
  error or changed error on the touched production files. Also run
  `uv run mypy src/sysml_codegen/generation/modules.py src/sysml_codegen/cli/__init__.py` and record
  the exact touched-file result.
- [x] `git diff --check`
- [x] Review `git diff --name-only` and the production-patch allowlist. Confirm no TEAx path,
  sanitizer implementation, arithmetic compiler behavior, snapshot format, package metadata, or
  unapproved fixture entered the change.

**What We Know Works After This Phase:**

The candidate rejects all three collision classes before writes, preserves collision-free
generated bytes except the approved documentation-derived differences, preserves finite and
non-finite behavior, and passes the relevant codegen gates. Live/snapshot parity is freshly proven
only if the existing licensed route ran; no new live capture is needed or authorized.

---

## Environment Setup

Use the project commands in `CLAUDE.md`. For execution tests and isolated evidence, use the
agentic-mbse environment and TEAx import path documented in `tests/execution/conftest.py` and the
exact environment from [design.md#appendix-a--exact-evidence-commands](design.md#appendix-a--exact-evidence-commands).
Every historical, candidate, and generated-package invocation is a fresh process.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks) and the resolved M1–M3 findings in
[design-review.md#resolutions](design-review.md#resolutions).

- **Phase 1 — false historical evidence:** hash one overlay, assert revision and source paths
  before behavior, and reject collection/import/setup failures as RED.
- **Phase 2 — validator/emitter drift:** one helper supplies both validation and emission; exact
  mapping tests cover all three classes.
- **Phase 3 — late rejection:** use the real `run_codegen(overwrite=True)` boundary and complete
  tree manifests, not sentinel survival.
- **Phase 4 — scope expansion:** characterize native raises and change one docstring sentence; do
  not change arithmetic or TEAx.
- **Phase 5 — falsely green parity or stability:** isolate processes and worktrees, hash shared
  inputs, assert source roots, compare complete trees, and preserve fixture bytes.

## Blocked External Dependency

- **`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` — BLOCKED outside this plan.** TEAx must attach the
  generated constraint module key at its serial-executor seam and prove the exact
  `EvaluationFailed` record and causal chain for both evaluators. This plan makes no TEAx source or
  test change. Sysml-codegen completion must say that its F1 boundary is characterized and that
  end-to-end GAP-CLOSE F1 remains open until the external P0 passes. See
  [spec.md#related-artifacts](spec.md#related-artifacts) and I9 in
  [design.md#required-invariants](design.md#required-invariants).

## Implementation Notes

Fill these records immediately as each phase completes. Do not pre-check a phase or replace command
output with a summary claim.

### Phase 1 Completion

**Completed:** 2026-07-18 14:09 PDT
**Actual Changes:** Added the frozen cross-revision overlay, generated-package runner, strict tree
classifier, and evidence record. Created detached baseline/candidate worktrees under
`/tmp/gap-runtime-contract-evidence.qehvkM`; current production files remained untouched.
**Evidence Commands and Results:** Final frozen overlay SHA-256
`b85fb3c9dfa526ff4a60cebea6bfff7b4940d454dd04a37e7764350f3cea7606`. Each isolated F2 node failed
at `6db321225a5c8568db0287b67ed1d04c03079cc2` with exactly `DID NOT RAISE CodeGenerationError`;
the combined run reported exactly three such failures. The old overwrite-impact probe passed, and
all four F1 raw-exception cases passed (5 tests total with impact). Source/revision gates ran before
behavior in every process.
**Issues:** The first F1 overflow assertion exposed the supported runtime's exact native message as
`(34, 'Numerical result out of range')`; the overlay was corrected, re-hashed, recopied unchanged to
both worktrees, and the complete evidence set was rerun.
**Deviations:** None. The initial pre-final-overlay trial is not counted as evidence.

### Phase 2 Completion

**Completed:** 2026-07-18 14:14 PDT
**Actual Changes:** Added one canonical raw-key-to-function-name helper and one deterministic
catalog validator in `generation/modules.py`; `compile_shared_predicates` now rejects before the
same-IR/compile loop and uses the same helper for successful emission. Added all three mapping
classes, forward/reverse catalog order, exact diagnostic, compiler-spy, collision-free, and
existing compile-once coverage.
**Validation Results:** `tests/unit/test_constraint_emission.py`: **22 passed**. Ruff passed on the
production and test files. Tests prove the same exact message in both catalog orders and that no
predicate compiler call occurs on collision.
**Issues:** One test line initially exceeded Ruff's 100-character rule; reformatted and reran all
Phase 2 gates green.
**Deviations:** None.

### Phase 3 Completion

**Completed:** 2026-07-18 14:18 PDT
**Actual Changes:** Added a shared-path CLI preflight immediately after live/snapshot context
construction and before existing output/path checks. Added kept absent-target and populated-tree
regressions using the real `run_codegen(overwrite=True)` API and a full manifest covering path
kinds, file bytes, and symlink targets.
**Validation Results:** The tests were RED before the CLI preflight: the absent root was created and
the populated tree was cleared/replaced. Post-fix: focused CLI/emission **31 passed**, adjacent CLI
safety **18 passed**, isolated candidate overlay no-write **2 passed**, and touched-file Ruff passed.
**Issues:** Ruff surfaced one unused import, three inherited local import-order issues in the now
touched test file, and one long line; all were corrected and the gate rerun green.
**Deviations:** None.

### Phase 4 Completion

**Completed:** 2026-07-18 14:29 PDT
**Actual Changes:** Added kept compiler characterization for division by zero, zero-to-negative
power, exponent overflow, and division nested under `and`. Added a production-generated wrapper
test that replaces `ConstraintEvaluation` with a fail-loud spy and proves the native exception
leaves `run()` first. Narrowed exactly one generated docstring sentence. No arithmetic production
code changed.
**Validation Results:** Full predicate compiler suite **38 passed**. Focused generated execution
covering raising wrapper, finite/violated, and non-finite/indeterminate behavior **3 passed**.
Baseline F1 overlay **4 passed** and final candidate overlay F1/F2 **7 passed**. Touched tests passed
Ruff and format checks.
**Issues:** The first wrapper-file lookup assumed constraint wrappers lived beside the shared
predicates module; production places owner-specific wrappers under `modules/<owner>/`. The test was
corrected to locate the production-emitted class recursively, then passed.
**Deviations:** None. F1 remains codegen-boundary characterization only.

### Phase 5 Completion

**Completed:** 2026-07-18 14:43 PDT
**Actual Changes:** Saved and verified the exact three-file production patch, final hashes, input
and generated-tree manifest summaries, and durable evidence. Replayed the refreshed overlay at both
revisions; generated baseline/candidate snapshot trees and candidate live/snapshot trees from one
copied input; ran route behavior in fresh processes.
**Validation Results:** Final candidate overlay **9 passed**; focused units **69 passed**; generated
execution **3 passed**; selected snapshot conformance **1 passed, 1 skipped**. The default project
full suite produced **2,169 passed, 205 skipped, 9 deselected, 23 failed, 96 errors**; every
failure/error was missing SysIDE license setup in that environment. Licensed plant_values live
generation and route parity passed separately in the companion environment. Ruff passed. Full and
targeted mypy reproduced the exact **76 errors in 17 files** baseline. `git diff --check` passed.
**Fixture and Byte-Diff Results:** `tests/fixtures` is untouched; input manifest
`5ce74869...bdefb5`. Before/after classification changed only the approved constraint-wrapper
sentence plus derived `package_contract.json`. Shared predicates/names/imports were identical.
Licensed live/snapshot complete trees were byte-identical before behavior execution.
**External Dependency Status:** `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open and external. This
item does not claim evaluator normalization or end-to-end F1 closure.
**Issues:** The first classifier assumed wrappers lived in `modules/constraints`; production
owner-specific wrappers live under their owner namespace. The classifier was narrowed to accept
only the exact approved sentence substitution in any Python wrapper and was rerun green. Whole-file
Ruff formatting of CLI would introduce 148 lines of unrelated churn; the format attempt was fully
removed. Both baseline and candidate identically report that inherited file-level format debt,
while every other touched/new Python file passes format check. Automated cleanup of detached
worktrees was denied because they contain the uncommitted evidence overlay/candidate patch; they
remain intact at `/tmp/gap-runtime-contract-evidence.qehvkM/{pre,post}`. Durable evidence does not
depend on retaining them.
**Deviations:** The full project suite ran in the default unlicensed environment, while the
available license was exercised through the documented agentic-mbse environment for live route and
focused execution gates. The conditional “license unavailable” branch is checked as handled/not
applicable because licensed evidence exists.

---

**Status:** Complete (sysml-codegen leg; external TEAx P0 remains open)
