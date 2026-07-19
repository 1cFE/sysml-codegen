# Implementation Plan: GAP-CLOSE Item 2 — Lowering Outcome Integrity

**Status:** Certified in GAP-CLOSE re-audit
**Created:** 2026-07-18
**Last Updated:** 2026-07-18 (implementation complete)
**Scope:** GAP-CLOSE Item 2 only; sysml-codegen production changes only

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Spec review:** [spec-review.md](spec-review.md) — approved after revision
- **Design:** [design.md](design.md) — architecture, decisions, invariants, and evidence protocol
- **Design review:** [design-review.md](design-review.md) — approved after revision
- **Epic:** [epic_gap_close.md](../../backlog/epic_gap_close.md), Item 2

## Implementation Strategy

### Phasing Rationale

Freeze the test input and capture isolated historical RED before any production edit. Then make the
small F4 reporting-order correction and prove that a BLOCK remains atomic. Build F5 in two batches:
first the pure source-referent and anonymous-only lowering boundary, then live/capture/replay route
threading and deterministic parity. Finish with direct byte-firewall checks, the real duplicate-ID
guard, fixture/migration preservation, and focused through full repository gates.

This order follows [design.md#integration-strategy](design.md#integration-strategy) and
[design.md#next-stage-handoff](design.md#next-stage-handoff). Historical evidence cannot be
contaminated by the candidate. F4 can close independently. F5's risky path grammar and minting are
proved before orchestration and snapshot integration widen the affected surface.

### Critical Path

Unchanged overlay + coordinated baseline RED → warning pre-pass and BLOCK atomicity → canonical
source referent + anonymous-only excluded mint → explicit live/capture/replay routes and parity →
byte, migration, duplicate, focused, broader, full, and static gates.

### First Proof Point

The unchanged overlay runs in fresh processes against clean detached worktrees at sysml-codegen
`6db321225a5c8568db0287b67ed1d04c03079cc2` and agentic-mbse
`4ed2a0728ea49298666415cd389d9a6173a81a3e`. It imports both packages from those worktrees, asserts
`PROFILE_SEMANTIC_VERSION == "executable-profile/v3"`, and records four independent defect REDs:
F4 sees `[raised]`, while each live-shaped F5 kind collides. Collection, setup, route, license,
revision, or import-source failures do not count.

### Overall Validation Approach

- Start every phase with its test stencil and observe the intended failure before production edits.
- Keep one hashed evidence overlay byte-identical between baseline and candidate. Run every evidence
  node in a fresh process with worktree-first imports and no user site or bytecode writes. See
  [design.md#isolated-test-first-redgreen-evidence](design.md#isolated-test-first-redgreen-evidence).
- Use live-shaped synthetic facts for the complete three-kind by three-source-dimension matrix.
  Use temporary licensed SysML trees only to prove the real extraction shapes and CLI atomicity.
- Compare observable identity bytes, not only behavior: IDs, warnings where applicable, canonical
  locations, excluded-record JSON, and catalog fingerprints.
- Preserve named exclusions and eligible-anonymous behavior with exact before/after pins. The
  anonymous-only boundary is the approved `[INFERRED]` design choice, not owner-originated settled
  scope.
- Hash all `tests/fixtures` bytes before work and require the same manifest afterward. Do not add,
  recapture, or edit a fixture, and do not weaken the migration guard.

### Scope Firewall

- `[ANON-ELIGIBLE-KEY]` stays open. Do not canonicalize eligible-anonymous facts, widen their
  16-hex IDs, or change their compile grouping. See [design.md#required-invariants](design.md#required-invariants),
  I3-I5.
- Do not change profile classification, warning text, catalog/schema models, agentic-mbse source,
  snapshot format version, wider lowering architecture, or any GAP-CLOSE item other than Item 2.
- Preserve all Item 1 dirty work. Do not edit, format, stage, export into the candidate patch, or
  revert current changes in `src/sysml_codegen/cli/__init__.py`,
  `src/sysml_codegen/generation/modules.py`, `src/sysml_codegen/templates/constraint_module.py.jinja2`,
  `tests/execution/test_constraint_execution.py`, `tests/unit/test_cli_generation.py`,
  `tests/unit/test_constraint_emission.py`, or `tests/unit/test_predicate_compiler.py`. Also preserve
  unrelated changes in `.project/CURRENT_WORK.md`, `.project/backlog/BACKLOG.md`, and all untracked
  Item 1 artifacts.
- If implementation requires an eligible-anonymous change, a named mint-input change, a facts-schema
  change, fixture recapture, or an Item 1 file edit, stop and surface the premise conflict.

---

## Phase 1: Freeze the Overlay and Capture Coordinated Pre-Fix RED

### Goal

Create the durable test-only overlay and evidence record first. Capture one isolated F4 RED and one
isolated F5 RED for each of `non_numerical`, `unassessed_form` (a `satisfy` usage), and
`unsupported_owner` at the exact coordinated baseline. Record fixture bytes and exact named-ID and
eligible-anonymous pins before any production edit.

### Assumption Under Test

The four defects reproduce at the approved revisions for the intended reasons, and the same
baseline public surfaces are sufficient to run an unchanged overlay after the fix. See
[design.md#key-decisions](design.md#key-decisions), D9-D10, and
[design.md#isolated-test-first-redgreen-evidence](design.md#isolated-test-first-redgreen-evidence).

### Test Stencil (Write This First)

```python
def test_f4_warns_before_block(live_shaped_mixed_facts, caplog):
    events = capture_warning_and_raise_events(live_shaped_mixed_facts, caplog)
    assert events == [warning_1, warning_2, "raised"]

@pytest.mark.parametrize("kind", EXCLUSION_KINDS)
def test_f5_anonymous_pair_is_distinct(kind, live_shaped_pair, lower_compatibly):
    assert_live_shape(live_shaped_pair, name=None, qualified_name=None)
    records = lower_compatibly(live_shaped_pair)
    assert len({record.constraint_id for record in records}) == 2
```

### Changes Required

**See:** [design.md#validation-approach](design.md#validation-approach), especially the isolated
evidence and byte/scope gates.

- [x] `.project/active/gap-lowering-integrity/evidence/test_gap_lowering_integrity_overlay.py`
  (new): add separately addressable F4, non-numerical, satisfy/unassessed-form, unsupported-owner,
  and non-blocking-warning nodes. Before behavior imports, assert both exact revisions, both clean
  statuses/tree hashes, worktree-contained `sysml_codegen` and `agentic_mbse` imports, lowering,
  constraint-facts, and executable-profile module paths, worktree-first `sys.path`, profile v3, and
  the overlay's own SHA-256.
- [x] Make every F5 node construct and assert the verified live shape: `identity.name is None`,
  `identity.qualified_name is None`, and exact non-null `LocationFact(file, line, column)`. Use
  signature inspection so baseline calls the old lowering signature and candidate supplies explicit
  live mode and roots without changing overlay bytes.
- [x] `.project/active/gap-lowering-integrity/evidence.md` (new): record commands, environment/path
  order, both revisions, clean/tree hashes, resolved import paths, profile version, overlay hash,
  exit codes, and full defect-specific outputs. Keep four independent RED records.
- [x] `.project/active/gap-lowering-integrity/evidence/hashes.txt` (new): record overlay and complete
  sorted `tests/fixtures` SHA-256 manifests plus the exact pre-fix ID values.
- [x] Create clean detached baseline/candidate codegen worktrees and a clean detached companion
  worktree under one `mktemp -d` root. Keep the overlay outside them. Do not use reset, checkout,
  clean, or stash in the current dirty worktree.
- [x] Record one exact named baseline ID for each exclusion kind and one exact eligible-anonymous ID,
  including its raw location, 16-hex suffix, and compile-grouping result. A fixture/corpus hash does
  not replace these four direct pins.

### Validation

**Automated:**

- [x] Run each overlay node separately in a fresh process with candidate-or-baseline codegen `src`
  first, pinned companion `src` second, `PYTHONNOUSERSITE=1`, and
  `PYTHONDONTWRITEBYTECODE=1`.
- [x] F4 exits RED only because the captured event list is `[raised]`, while the exception retains
  every blocking diagnostic and repair string.
- [x] Each F5 kind exits RED only because two different live-shaped records receive one ID. Both
  non-numerical warnings must already be observable; the other two kinds must emit no profile warning.
- [x] The non-blocking two-warning node passes at baseline with exactly `[warning-1, warning-2]`.
- [x] Assert `git status --short` for the current worktree has no new production or test changes from
  this evidence-only phase, apart from the planned evidence artifacts.

**Record check:**

- [x] Confirm no setup, import, license, route, or unrelated failure is labeled RED.
- [x] Confirm the four baseline records name both revisions and profile v3, and include the exact
  command and full relevant output.

**What We Know Works After This Phase:**

F4 and all three F5 kinds are reproducible at the intended coordinated baseline from one frozen,
source-isolated input. The direct byte and fixture baselines needed to enforce anonymous-only scope
are durable before implementation begins.

---

## Phase 2: Report Every Non-Numerical Warning Before BLOCK

### Goal

Move warning reporting into the read-only pre-pass, then prove exact source/profile order, exactly
once behavior, complete BLOCK diagnostics, and no returned context, catalog, package, or output-tree
mutation. This phase changes ordering only; warning values stay byte-identical.

### Assumption Under Test

The existing evaluated decisions contain all warning and blocking information before record
construction, so a reporting pass can make F4 observable without weakening the halt. See
[design.md#key-decisions](design.md#key-decisions), D1, and I1-I2 in
[design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
def test_two_warnings_precede_complete_block(caplog, mixed_facts):
    with pytest.raises(CodeGenerationError) as error:
        lower(mixed_facts)
    assert profile_warnings(caplog) == [warning_1, warning_2]
    assert_all_block_diagnostics_and_repairs(str(error.value))
    assert catalog_spy.call_count == graph_spy.call_count == 0
```

### Changes Required

- [x] `tests/conformance/test_constraint_lowering.py`: add a two-NON_NUMERICAL plus one-BLOCK test
  that asserts the exact warning list before the synchronous raise, and strengthen the non-blocking
  batch to assert the same two warnings exactly once.
- [x] Licensed mixed-model context leg disposition: external skip because no SysIDE license was
  available. The license-free mixed test asserts every warning once and all BLOCK
  diagnostics/repair text; no licensed test was added or claimed.
- [x] Licensed real-`run_codegen(overwrite=True)` atomicity leg disposition: external skip because
  no SysIDE license was available. No licensed absent/populated output-tree result is claimed.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py`: implement D1's read-only warning pre-pass
  before BLOCK aggregation and remove warning emission from the record-building loop. Preserve the
  existing warning formatting bytes and BLOCK diagnostic aggregation.

### Validation

**Automated:**

- [x] Run the new license-free F4 and non-blocking tests. Require exact event lists
  `[warning-1, warning-2, raised]` and `[warning-1, warning-2]`.
- [x] Run the focused lowering profile family:
  `uv run pytest -q tests/conformance/test_constraint_lowering.py tests/conformance/test_constraint_non_numerical.py`.
- [x] License disposition recorded for the two `run_codegen` atomicity cases: unavailable,
  external skip, and no real CLI atomicity claim.
- [x] Run `uv run ruff check src/sysml_codegen/analysis/constraint_lowering.py` and the touched F4
  tests; run `uv run ruff format --check` on those files.

**What We Know Works After This Phase:**

Every non-numerical sibling is reported once before a BLOCK, while generation still halts before
records, catalog, graph completion, output clearing, or package creation.

---

## Phase 3: Mint Portable Anonymous Excluded Identity and Keep Uniqueness Truthful

### Goal

Implement and test the canonical source referent, one authoritative excluded-index selector, the
anonymous-only excluded mint with file/line/column identity and a 32-hex suffix, and truthful
two-record duplicate diagnostics. Keep named and eligible-anonymous paths byte-for-byte unchanged.

### Assumption Under Test

Ordered roots plus lexical containment can provide a portable identity for every verified live
anonymous exclusion, and the excluded branch can consume it without reconstructing named mint
inputs or touching eligible-anonymous facts. See [design.md#key-decisions](design.md#key-decisions),
D2-D5 and D7-D8.

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("kind", EXCLUSION_KINDS)
@pytest.mark.parametrize("dimension", ["line", "column", "file"])
def test_anonymous_excluded_identity(kind, dimension, live_shaped_pair, roots):
    records = lower_live(live_shaped_pair(kind, dimension), roots)
    assert len(records) == 2
    assert len({r.constraint_id for r in records}) == 2
    assert all(len(r.constraint_id.rsplit("__", 1)[1]) == 32 for r in records)
    assert_exact_kind_warning_location_and_json(kind, records)
```

### Changes Required

**See:** [design.md#required-invariants](design.md#required-invariants), I3-I7 and I9-I10, and
[design.md#implementation-notes](design.md#implementation-notes).

- [x] `tests/unit/test_source_referent.py` (new): test directory and exact-file roots, most-specific
  match, stable root slots, duplicate roots, redundant separators, symlink spelling without
  `resolve`, RFC 3986 segment encoding, Unicode, separator injection, and every malformed replay
  grammar. Prove no-match, missing segment, `.`, `..`, absolute payload, non-canonical percent
  encoding, and encoded separators fail loud.
- [x] `tests/conformance/test_constraint_lowering_integrity.py` (new): add the complete
  three-exclusion-kind by line/column/file matrix from
  [design.md#kept-behavioral-and-route-matrix](design.md#kept-behavioral-and-route-matrix). Assert
  live-shaped facts, deterministic distinct 128-bit IDs, canonical source association, exact
  excluded-record JSON, two warnings only for `non_numerical`, and none for `unassessed_form` or
  `unsupported_owner`.
- [x] In the same conformance file, test selector/profile cardinality failure, missing anonymous
  location, unmatched live root, and explicit live-versus-snapshot route rejection. Test the
  authoritative selector against resulting excluded indices for all three kinds.
- [x] `tests/unit/test_concrete_constraint_model.py`: pin the default mint's 16-hex behavior and add
  a real adversarial duplicate test using two concrete records with different usage, source,
  owner-definition, and owner-instance identities but one forced ID. Assert the ID and both record
  descriptions, and reject `hash collision`, `broken model`, or equivalent causal blame.
- [x] `src/sysml_codegen/analysis/source_referent.py` (new): implement the two explicit pure routes
  and shared canonical grammar from D4-D5. Use lexical `abspath(normpath(...))`, never filesystem
  resolution.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py`: add the one shared excluded-index
  selector, an explicit source-location route, default-preserving digest-length option, and the
  anonymous excluded branch. Keep the current named excluded mint expression physically on its old
  path. Do not route named data through reconstructed canonical tuples. Update duplicate diagnostics
  to report available evidence without asserting cause.

### Validation

**Automated:**

- [x] `uv run pytest -q tests/unit/test_source_referent.py tests/unit/test_concrete_constraint_model.py`
- [x] `uv run pytest -q tests/conformance/test_constraint_lowering_integrity.py`
- [x] Run the three F5 overlay nodes on the candidate; all pass without changing the overlay hash.
- [x] Re-run the direct named-ID pins for `non_numerical`, `unassessed_form`, and
  `unsupported_owner`; require exact baseline bytes. Re-run the eligible-anonymous pin; require its
  raw location, ID, 16-hex suffix, and grouping result unchanged.
- [x] Run `uv run ruff check` and `uv run ruff format --check` on the Phase 3 files.

**What We Know Works After This Phase:**

All three legal anonymous exclusion kinds preserve file, line, and column identity, mint stable
distinct 128-bit IDs, and retain correct warning/catalog behavior. Named and eligible-anonymous
bytes remain behind explicit firewalls, and a genuine duplicate still halts with a truthful
diagnostic.

---

## Phase 4: Thread Explicit Live, Capture, and Replay Routes

### Goal

Thread ordered model roots into live lowering and snapshot capture, canonicalize only copied
anonymous excluded facts, validate only those facts on replay, and prove repeated-live,
cross-checkout, multi-root, and snapshot determinism. Use real temporary SysML models to lock the
three observed extraction shapes without adding fixtures.

### Assumption Under Test

The existing callers own enough route information to keep raw paths and canonical snapshot
referents unambiguous, and the v1 facts schema safely carries the canonical string. See
[design.md#architecture](design.md#architecture), D4-D6, and I7-I8 in
[design.md#required-invariants](design.md#required-invariants).

### Test Stencil (Write This First)

```python
def test_live_snapshot_and_relocated_trees_are_byte_identical(tree_a, tree_b):
    live_a = lower_live(tree_a.models, tree_a.roots)
    live_b = lower_live(tree_b.models, tree_b.roots)
    replay = capture_then_rebuild(tree_a)
    assert identity_projection(live_a) == identity_projection(live_b)
    assert identity_projection(replay) == identity_projection(live_a)
```

### Changes Required

- [x] `tests/conformance/test_constraint_snapshot_identity.py` (new): cover repeated lowering,
  equivalent trees under different absolute prefixes, capture/replay, and two ordered roots with
  the same relative filename. Compare IDs, warning values, canonical locations, serialized excluded
  records, and catalog fingerprints byte-for-byte. Assert `ctx.constraint_facts` is not mutated.
- [x] Licensed temporary-model shape leg disposition: external skip because no SysIDE license was
  available. The frozen overlay shape-locks `name=None`, `qualified_name=None`, and non-null
  file/line/column for all three kinds; no licensed live-shape test was added or claimed.
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py`: pass explicit live mode and ordered
  `model_paths` at the existing lowering call.
- [x] `src/sysml_codegen/snapshot/capture.py`: pass ordered model roots into snapshot serialization.
- [x] `src/sysml_codegen/snapshot/serializer.py`: when mode is `applied`, evaluate the profile only
  to consume the shared excluded selector, serialize from a copy, and canonicalize locations only
  where the index is excluded and `identity.name is None`. Emit no warnings and do not duplicate
  `_exclusion_for` policy.
- [x] `src/sysml_codegen/snapshot/graph_rebuild.py`: select explicit snapshot mode at the existing
  lowering call and validate stored canonical referents only on anonymous excluded indices.

### Validation

**Automated:**

- [x] `uv run pytest -q tests/conformance/test_constraint_snapshot_identity.py`
- [x] `uv run pytest -q tests/conformance/test_constraint_non_numerical.py tests/conformance/test_snapshot_constraint_parity.py tests/conformance/test_snapshot_generation.py`
- [x] Run the relocated-tree and two-root cases in fresh processes so editable installs and
  `sys.modules` cannot create false parity.
- [x] License disposition recorded for temporary live shape and live/snapshot comparisons:
  unavailable, external skip, synthetic route tests passed, and no licensed live-shape claim made.
- [x] Confirm named and eligible-anonymous serialized facts remain byte-identical; only anonymous
  selected exclusion copies carry canonical referents.
- [x] Run touched-file Ruff/format and targeted mypy over the six approved production files.

**What We Know Works After This Phase:**

Anonymous excluded identity is deterministic across repeated live lowering, equivalent absolute
checkout roots, and snapshot replay. Route selection is explicit, multiple roots remain distinct,
and capture does not mutate live facts or broaden canonicalization beyond the target records.

---

## Phase 5: Candidate Evidence, Byte Firewalls, Migration Guard, and Final Gates

### Goal

Replay the frozen overlay against an isolated production-only candidate patch, complete the durable
evidence, and run the fixture, migration, focused, broader, full, Ruff, formatting, mypy, and diff
checks. Prove the patch contains Item 2 only and preserves all Item 1 dirty work.

### Assumption Under Test

The localized change fixes F4/F5 without named-ID churn, eligible-anonymous drift, fixture
migration, catalog regression, or contamination from the current dirty worktree. See
[design.md#byte-and-scope-gates](design.md#byte-and-scope-gates) and the resolved evidence/fixture
findings in [design-review.md#resolutions](design-review.md#resolutions).

### Test Stencil (Write This First)

```python
def test_candidate_matches_recorded_scope(candidate_diff, baseline_manifest):
    assert candidate_diff.paths == APPROVED_PRODUCTION_PATHS
    assert fixture_manifest() == baseline_manifest
    assert named_ids_after() == named_ids_before()
    assert eligible_anonymous_after() == eligible_anonymous_before()
```

### Changes Required

- [x] `.project/active/gap-lowering-integrity/evidence/candidate-production.patch` (new): export
  only the six production paths approved in [design.md#integration-strategy](design.md#integration-strategy).
  Record its SHA-256 and exact changed-path set. Do not export tests, evidence, Item 1 paths, or any
  unrelated dirty-worktree content.
- [x] `.project/active/gap-lowering-integrity/evidence.md`: append isolated candidate GREEN,
  regenerated binary-diff hash, no-untracked-files check, direct ID pins, route/cross-checkout
  parity, fixture/migration results, test counts, license state, and static/diff results.
- [x] `.project/active/gap-lowering-integrity/evidence/hashes.txt`: append the candidate patch and
  regenerated diff hashes and the post-fix fixture manifest.
- [x] Do not change `tests/conformance/test_constraint_migration_mapping.py` or any file beneath
  `tests/fixtures/`. Its existing anonymous-corpus loud guard and `CONSTRAINT_BEARING_FIXTURES` list
  remain exact because D10 adds no committed anonymous fixture.

### Validation

**Isolated candidate evidence:**

- [x] Apply the hashed production patch to the clean detached candidate worktree. Require
  `git diff --check`, no untracked files, the exact six-path production allowlist, and a regenerated
  binary diff whose SHA-256 matches the recorded patch before any candidate behavior run.
- [x] Run the unchanged overlay in fresh candidate processes. Require F4, all three F5 kind nodes,
  and the non-blocking exact-warning node to pass. Reconfirm both revisions/import paths, companion
  clean/tree hash, candidate diff/path set, profile v3, and unchanged overlay hash.
- [x] Re-run exact named-ID pins for all three kinds and the eligible-anonymous pin. Require direct
  byte identity with Phase 1 values.

**Fixture and migration gates:**

- [x] Require the complete sorted `tests/fixtures` SHA-256 manifest to equal Phase 1 exactly and
  `git diff -- tests/fixtures` to be empty. Fixture recapture is prohibited.
- [x] Run `uv run pytest -q tests/conformance/test_constraint_migration_mapping.py`; require the
  existing anonymous-corpus guard, fixture list, and catf_mfe 65-exclusion result unchanged.

**Focused and broader tests:**

- [x] Focused normal:
  `uv run pytest -q tests/unit/test_source_referent.py tests/unit/test_concrete_constraint_model.py tests/conformance/test_constraint_lowering_integrity.py tests/conformance/test_constraint_lowering.py tests/conformance/test_constraint_non_numerical.py tests/conformance/test_constraint_snapshot_identity.py`.
- [x] Focused optimized control-flow run with `PYTHONOPTIMIZE=1` over the same Item 2 files; record
  that pytest assertions are stripped under `-O`, so this is not the primary assertion evidence.
- [x] Broader constraint/snapshot/catalog/CLI regression:
  `uv run pytest -q tests/conformance/test_constraint_catalog_determinism.py tests/conformance/test_constraint_generation_integration.py tests/conformance/test_constraint_generation_live.py tests/conformance/test_constraint_migration_mapping.py tests/conformance/test_constraint_pipeline_threading.py tests/conformance/test_snapshot_constraint_parity.py tests/conformance/test_snapshot_generation.py tests/unit/test_concrete_constraint_model.py tests/unit/test_cli_generation.py`.
  The Item 1-owned test file is run but not edited.
- [x] Full: `uv run pytest tests/`. Record pass/skip/fail/error counts and license state. Do not
  relabel license-dependent failures or skips as passing live evidence.

**Static and diff gates:**

- [x] `uv run ruff check src/` plus every new/touched Item 2 test and evidence Python file.
- [x] `uv run ruff format --check` on every new/touched Item 2 Python file. Do not format Item 1 or
  unrelated dirty files.
- [x] `uv run mypy src/`; compare with the recorded project baseline and require no new or changed
  errors. Also run targeted mypy on the six approved production files and record exact results.
- [x] `git diff --check` on the Item 2 candidate patch and Item 2 artifact/test paths. If a literal
  whole-worktree check reports inherited Item 1 or pre-existing artifact whitespace, classify it by
  path and do not rewrite unrelated files to make the command green.
- [x] Review `git diff --name-only`, the candidate patch allowlist, and the pre/post Item 1 path
  hashes. Confirm no Item 1 byte changed, no agentic-mbse source changed, `[ANON-ELIGIBLE-KEY]`
  remains open, and no fixture/catalog/schema/snapshot-version change entered the patch.

**What We Know Works After This Phase:**

The isolated candidate turns the four historical defects GREEN, keeps warning/halt atomicity and
portable anonymous identity across routes/checkouts, preserves named and eligible-anonymous bytes,
rejects real duplicate IDs truthfully, leaves fixtures and migration guards exact, and passes the
available repository quality gates without absorbing Item 1 work.

---

## Environment Setup

Use the commands and environment rules in the repository [CLAUDE.md](../../../CLAUDE.md). Historical
and candidate evidence uses detached worktrees under `mktemp -d`, fresh Python processes,
`PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, and explicit codegen-then-companion source order.
Licensed tests use temporary model trees and never write into `tests/fixtures`.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks) and
[design-review.md#resolutions](design-review.md#resolutions).

- **Phase 1 — false RED or dirty-source imports:** assert revisions, clean/tree state, import paths,
  profile version, environment order, and overlay hash before behavior. Save defect-specific output.
- **Phase 2 — duplicate or late warnings:** pin both blocking and non-blocking exact event lists and
  exercise real output-tree atomicity.
- **Phase 3 — eligible/named scope leak:** keep named minting physically unchanged, test the shared
  selector, and require direct exact-ID/raw-location pins rather than only corpus hashes.
- **Phase 4 — route ambiguity or serializer drift:** use separate live mapping and replay validation,
  share the excluded selector, serialize a copy, and test relocated and multi-root trees.
- **Phase 5 — evidence or worktree contamination:** export a six-path binary patch, compare hashes
  and path sets, preserve fixture and Item 1 bytes, and classify inherited whole-tree failures.

## Implementation Notes

Fill this section during implementation. Check off each action immediately after it passes and
record actual commands, counts, license state, issues, and justified deviations. A deviation that
crosses the Scope Firewall stops implementation for review.

### Phase 1 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added one frozen five-node overlay, durable RED evidence, direct named and
eligible-anonymous ID pins, and a complete 179-file fixture manifest. Created clean detached
codegen baseline/candidate and companion worktrees under `/tmp/gap-lowering-integrity.aXkaZz`.
**Validation:** F4 failed only on `[raised]`; the three independently run F5 kinds failed only on
their genuine baseline duplicate IDs; the non-blocking warning control passed. Both exact HEADs,
clean states, tree hashes, import roots, profile v3, and overlay hash were asserted in-process.
**Issues / Deviations:** `uv` could not open its cache inside the restricted sandbox, so the same
commands were rerun with approved access to the existing cache. No production or kept-test file
changed in this phase. The fixture manifest is stored as a dedicated evidence file rather than
inlining 179 rows into `hashes.txt`.

### Phase 2 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added license-free mixed and non-blocking warning-order tests. Moved the exact
existing warning rendering into one read-only reporting pass before BLOCK aggregation and removed
the later loop emission.
**Validation:** The new mixed test was RED with no warnings, then GREEN. Focused lowering and
non-numerical family: 43 passed, 8 license skips. The frozen candidate overlay is completed in
Phase 5.
**Issues / Deviations:** The available environment has no SysIDE license, so the planned temporary
licensed context and real `run_codegen` atomicity legs remain external skips. The license-free test
and code path prove the synchronous halt occurs before concrete records; existing orchestration
still assembles catalogs and mutates output only after lowering returns.

### Phase 3 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added the pure live mapper/snapshot validator, shared exclusion selector,
anonymous-excluded-only canonical file/line/column mint with a 32-hex suffix, and evidence-based
duplicate diagnostics. Added the complete 3-kind by 3-dimension matrix and grammar/guard tests.
**Validation:** 56 Phase 3 tests passed. Exact named IDs for all three kinds and the corrected
baseline eligible-anonymous ID passed byte-for-byte. The forced genuine duplicate named both
records and contained no causal blame.
**Issues / Deviations:** The initial eligible-anonymous evidence pin used the anonymous usage label
as the owner instance. Direct execution at the untouched baseline showed package expansion uses
`Pkg__Owner`; the evidence and test were amended to the actual baseline ID before completion.

### Phase 4 Completion

**Completed:** 2026-07-18
**Actual Changes:** Threaded ordered roots through live lowering and capture, canonicalized a deep
copy of anonymous selected exclusions only, and selected strict snapshot validation on replay.
Added relocated-tree, repeated-live, two-root, capture-copy, serialized-record, and catalog
fingerprint parity tests.
**Validation:** New snapshot identity suite: 3 passed. Combined identity suites: 15 passed. Existing
snapshot/non-numerical/migration selection: 9 passed, 28 license skips. Named serialized locations
remain raw; only copied anonymous exclusions are canonicalized.
**Issues / Deviations:** Licensed temporary SysIDE shape tests could not run in this environment.
The frozen overlay and synthetic facts assert the independently verified live shape for every kind;
the full kind-by-dimension and route product is license-free. Independent audit cure: the parity
test now captures the real lowering logger and asserts exact warning bytes across repeated live,
relocated live, and serialized snapshot replay. Anonymous warnings use the same canonical referent
as exclusions; the pinned strings contain `root-0/model.sysml:10:2` and `:20:2` in every route.

### Phase 5 Completion

**Completed:** 2026-07-18
**Actual Changes:** Exported and applied the exact six-path production patch; finalized candidate
GREEN, direct ID pins, fixture manifest, Item 1 hashes, and all quality evidence. Synchronized the
plan, spec, design, and current-work records.
**Validation:** Final candidate overlay 5 passed. Focused normal 102 passed/8 skipped; optimized
102/8; broader 45/37. Full default suite 2,206 passed, 205 skipped, 9 deselected, 23 failed, 96
errors, all license-dependent. Ruff passed. Full mypy returned to the 76-error baseline. Candidate
and Item 2 diff checks passed; fixture manifest and migration source are exact.
**Issues / Deviations:** No SysIDE license was available, so the explicitly licensed Phase 2/4
tests remain unchecked external legs and are not claimed. Whole-file format checking still reports
the same three inherited failures as the untouched baseline; nine Item 2-owned/touched files are
formatted, and unrelated legacy formatting was preserved. The first candidate patch hash changed
after a formatting/type-narrowing correction; evidence was amended to the final regenerated hash
and the unchanged overlay was rerun GREEN against it.

---

**Status:** Certified in GAP-CLOSE re-audit
