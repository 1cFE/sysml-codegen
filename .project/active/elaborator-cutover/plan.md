# Implementation Plan: Elaborator Atomic Cutover (ELABORATE-FIRST Item 7)

> **Superseded for execution by `.project/active/cutover-recovery/plan.md`; retained as shaping and
> census evidence.**

- **Status:** Implementation in progress; Phases 0–5 complete; owner recapture acceptance pending
- **Created:** 2026-08-10
- **Last updated:** 2026-08-10
- **Owner:** Reid W
- **Primary repository:** `/home/reid/1cfe/sysml-codegen`
- **Coordinated repository:** `/home/reid/1cfe/agentic-mbse`
- **Branches at planning:** codegen `source-identity-epic`; agentic `elaborate-first-salvage`

## Source Documents

Read these completely before implementation. They are the contract for this plan.

- [spec.md](spec.md)
- [product-lens.md](product-lens.md)
- [spec-review.md](spec-review.md)
- [spec-review-v2.md](spec-review-v2.md)
- [design.md](design.md)
- [cutover-census.md](cutover-census.md)
- [cutover-inventory.json](cutover-inventory.json)
- [design-review.md](design-review.md)
- [design-review-v2.md](design-review-v2.md)
- [design-review-v3.md](design-review-v3.md)
- [design-review-v4.md](design-review-v4.md), whose final verdict is **Pass** and explicitly allows planning
- `.project/backlog/epic_elaborate_first_architecture.md`, Item 7
- `.project/CURRENT_WORK.md`
- Item 6 [plan](../../completed/20260810_elaborator-identity-completion/plan.md) and final
  [audit](../../completed/20260810_elaborator-identity-completion/audit_v3.md)

The architecture is fixed by `design.md`: D1–D12, I1–I12, the normative v6 schema and validation
order, the exact Fusion Tea rename table, the closed census, and the paired-candidate protocol are
not implementation choices. This plan supplies sequencing, test-first proof points, file ownership,
and validation commands.

## The Point

One loaded semantic source occurrence must become exactly one runtime source for every and only its
bound calculation, constraint, aggregation, FORMULA, and alias consumers. The resolved instance
graph must preserve that answer across public live generation, in-place snapshot generation, and
relocated snapshot generation. Unsupported authored forms must fail before capture or generation.
Item 7 finishes that obligation by making the exact instance graph the only shipped semantic
authority and deleting every route that can reconstruct another answer from names, qualified names,
rendered paths, or legacy snapshot data.

## Provenance and Gates

- **[OWNER]** The product must consume referents while the model is loaded, must treat self-binding
  as a modeling error, and may serialize the representation the pipeline actually needs. The
  instance graph is that representation. Source: epic Item 7 and its owner-ruling section.
- **[INHERITED]** Item 6 is certified. Exact payload identity, native effective-child authority,
  structured occurrences, typed IR, one-way projection, fail-closed constraint eligibility, and
  the deny-by-default boundary guard are prerequisites to preserve, not work to reimplement.
- **[AGENT]** The phase boundaries and rollback sequence below are plan decisions. They are
  challengeable if implementation evidence contradicts them; they are not owner-settled product
  requirements.
- **[OWNER GATE — PENDING]** The owner has not accepted the Item 7 recapture candidate. Phase 9 must
  stop for explicit owner accept/revise disposition. No final candidate commit, prepared ref,
  acceptance tag, public-branch promotion, product tag, or release gate may assume acceptance.

## Certified Worktree Baseline to Preserve

Planning inspected both repositories without modifying production code.

- Codegen is at `1672c5766f67e7716f3c9f8f636c21e2ea444601` on
  `source-identity-epic`. Item 6 is contained in certified commit `bee20d8` plus the later design
  commit. Existing dirty state is `.project/CURRENT_WORK.md`, the untracked Item 7 artifact
  directory, and the four untracked census checker/test files.
- Agentic is at `5088b417c9e5453271291d46cd5fb23fc0579b1e` on
  `elaborate-first-salvage`. That commit contains the certified Item 6 identified constraint/profile
  work. Its only current untracked state is `.orchestrate-logs/`.
- Item 6's audit described production changes as uncommitted at audit time; those changes are now in
  the commits above. Treat both commits and all remaining dirty/untracked files as prerequisite
  owner work. Do not reset, checkout, clean, stash, or overwrite them.
- Writes to `/home/reid/1cfe/agentic-mbse` require the coordinated implementation sandbox or
  explicit filesystem authority for that repository. If only the codegen root is writable, stop
  before Phase 5 rather than making a one-sided API change.

Before each implementation session, record both statuses:

```bash
cd /home/reid/1cfe/sysml-codegen
git status --short --branch
git rev-parse HEAD

cd /home/reid/1cfe/agentic-mbse
git status --short --branch
git rev-parse HEAD
```

## Implementation Strategy

### Phasing rationale

Prove a single route before migrating the population. First retain the already-approved census
scaffold. Then establish one live → v6 → relocated vertical route, make document admission exact,
and bind public context lifetime to immutable graph bytes and a projection receipt. Only after those
boundaries work do public semantic proofs, cross-repository compiler/constraint convergence, and the
Fusion Tea migration run. The bulk deletion follows green independent replacements. The 37-path
batch, scale run, and real TEAx smoke happen once against the stable sole authority. Candidate
assembly then stops for owner review. Preparation and promotion are a separate, acceptance-gated
phase.

### Critical path

```text
validated census scaffold
  -> one v6 vertical route
  -> exact staged admission + standard-library authority
  -> builder-created context + canonical selection/receipt
  -> public exact semantic proofs
  -> one compiler/constraint route across both repositories
  -> Fusion Tea/C19/F26 proofs
  -> full legacy/test/script/doc deletion + absence
  -> exact 37-path batch + scale + real TEAx
  -> immutable paired candidate + quality gates
  -> OWNER ACCEPT/REVISE STOP
  -> accepted evidence materialization + paired preparation/promotion
```

### First proof point

On one maintained runtime fixture, public live elaboration and a v6 envelope loaded both in place and
after relocation must yield the same instance fingerprint and complete projected semantic digest.
A hand-tampered authoritative outer field with a correctly re-fingerprinted inner graph must fail
before projection. Do not begin bulk migration until that test is red, implemented, and green.

### Progress

- [x] Phase 0 — Retain and validate the design-time census scaffold
- [x] Phase 1 — Prove one live → v6 → relocated vertical route
- [x] Phase 2 — Make staged source admission and standard-library digest the sole source owner
- [x] Phase 3 — Cut public builders to a defensive `PipelineContext` and projection receipt
- [x] Phase 4 — Prove exact occurrence, binding, aggregation, selection, and public mutation
- [x] Phase 5 — Converge compiler and constraint authorities across both repositories
- [x] Phase 6 — Migrate Fusion Tea and pin C25, C2, C19, F26, and arithmetic
- [x] Phase 7 — Execute the full census deletion/migration ledger and absence gates
- [ ] Phase 8 — Recapture exactly 37 paths and record route, diff, scale, and real-TEAx evidence
- [ ] Phase 9 — Assemble the immutable paired candidate, run final gates, and stop for owner review
- [ ] Phase 10 — After recorded acceptance only, materialize, prepare, verify, and promote the pair

## Global Implementation Rules

- Start every unchecked phase with the named red test or failing gate. Record the exact command and
  failure in that phase's Implementation Notes before production edits.
- A phase is not complete when its focused tests pass. Its census rows, replacement tests,
  completion evidence, and interaction/rollback notes must all be satisfied.
- Keep [cutover-census.md](cutover-census.md) and [cutover-inventory.json](cutover-inventory.json)
  current. Preserve stable IDs. Split a row only when file responsibilities differ; never silently
  drop or change a disposition.
- Public and exact tests must derive expected values from the model, governing contract, hand
  arithmetic, fixed schema, or explicit typed graph fixture. They may not run the legacy front end,
  copy its output, or read a private compatibility field.
- Every internal phase is non-releasable. Both public authorities may coexist temporarily only in
  the coordinated working state while the final landing is being built. No flag, adapter, alias, or
  published intermediate state may make that coexistence a supported product state.
- If a test reveals semantics outside the inherited contract, a new census disposition, a TEAx
  product change, a v6 schema change, or an Item 6 regression, stop and surface it. Do not resolve a
  premise conflict by changing the design silently.
- Do not commit generated packages or TEAx outputs. Use a task-specific `mktemp -d` directory.

---

## Phase 0 — Retain and Validate the Design-Time Census Scaffold

### Objective

Keep the census/inventory tooling already created during design. Prove it still describes the
certified current worktrees. Do not recreate it and do not count it as production implementation.

### Assumption under test

The 231-row closed inventory and self-safe residue scanner can still distinguish current inventoried
transition residue from the final required absent state.

### Red test first

This scaffold predates the implementation plan. No red-first history is claimed. Retain the existing
malformed-inventory and self-match refusal tests; do not rewrite them merely to manufacture a red
run.

### Exact files and census rows

- [x] `scripts/check_cutover_census.py` — `SCR-07`, `INV-CG-CENSUS-SCRIPT`
- [x] `tests/unit/test_check_cutover_census.py` — `SCR-07`, `INV-CG-CENSUS-TEST`, `CUT-CENSUS-01`
- [x] `scripts/check_cutover_residue.py` — `SCR-08`, `INV-CG-RESIDUE-SCRIPT`
- [x] `tests/unit/test_check_cutover_residue.py` — `SCR-08`, `INV-CG-RESIDUE-TEST`, `CUT-RESIDUE-01`
- [x] `.project/active/elaborator-cutover/cutover-census.md` and
  `cutover-inventory.json` — R3/R6, `NR-13`

### Implementation steps

- [x] Retain the generated inventory schema, stable row keys, Unicode-encoded residue vocabulary,
  Python AST checks, and bounded non-Python scan.
- [x] Retain `comparison_basis:"current-worktree"` and `exact_base_comparison:false`; design-time
  evidence must not be rewritten to claim a clean-base comparison.
- [x] Record that final candidate closure changes `--expect inventoried` to `--expect absent`; it
  does not weaken the rules or delete the transitional baseline.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
.venv/bin/python -m pytest -o addopts='' \
  tests/unit/test_check_cutover_census.py \
  tests/unit/test_check_cutover_residue.py -q
.venv/bin/python scripts/check_cutover_census.py compare \
  --census .project/active/elaborator-cutover/cutover-census.md \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --require-sorted --require-closed
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule all --expect inventoried
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule item6-dual-2 --expect inventoried
```

### Completion evidence

- [x] `4 passed in 0.38s`
- [x] `{"closed":true,"rows":231,"sorted":true}`
- [x] `363` inventoried `all` hits and `5` inventoried `item6-dual-2` hits

### Rollback and interaction notes

Retain these files as owner-approved design scaffolding. If later inventory generation changes an
existing disposition or reveals an uncensused path, stop the dependent phase and return to design;
do not broaden a catch-all row.

---

## Phase 1 — One Live → V6 → Relocated Vertical Route

### Objective

Establish the smallest complete exact route on one maintained runtime fixture: staged live load,
strict elaboration, v6 encode, in-place load, relocated load, one-way projection, semantic digest
equality, and strict outer tamper refusal. This is the first proof point, not the bulk migration.

### Assumption under test

The certified `instance-graph/v2` payload is sufficient to reproduce the same projected generation
semantics after relocation when the complete v6 authority is intact.

### Test stencil — write this first

```python
def test_one_live_v6_relocated_route_has_one_digest(tmp_path):
    live = load_and_elaborate(single_runtime_fixture())
    path = capture_v6(live, tmp_path / "case.json")
    moved = relocate(path, tmp_path / "moved" / "case.json")
    assert instance_fingerprint(load_v6(path)) == instance_fingerprint(load_v6(moved))
    assert computation_digest(project(live)) == computation_digest(project(load_v6(moved)))
    assert_outer_authority_tamper_fails_before_projection(moved)
```

### Exact files and census rows

- [x] `tests/conformance/test_snapshot_v6_envelope.py` — `CUT-V6-01`, `CUT-V6-02`
- [x] `tests/conformance/test_snapshot_v6_routes.py` — `CUT-V6-03`
- [x] `tests/conformance/test_snapshot_v6_capture.py` — `CUT-CAP-01`
- [x] `src/sysml_codegen/snapshot/envelope.py` (new) — `API-06`, `PROD-12`
- [x] `src/sysml_codegen/snapshot/instance_graph.py` — `PROD-13`
- [x] `src/sysml_codegen/snapshot/capture.py` — `API-04`, `PROD-12`, `INV-RES-CG-023`
- [x] `src/sysml_codegen/orchestration/snapshot_context.py` — `API-05`, `PROD-12`,
  `INV-RES-CG-020`
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py` — private
  `load_and_elaborate` owner under `API-01`/`PROD-01`, without a second export
- [x] `src/sysml_codegen/elaboration/project.py` and `resolution/models.py` — `PROD-11`, `PROD-17`

### Implementation steps

- [x] Write the three focused tests and record failures for absent v6 envelope/loader, unequal
  relocated semantics, and accepted tamper.
- [x] Add the exact v6 envelope shape, duplicate-key JSON loading, canonical JSON, inner fingerprint
  verification, and one outer digest covering every field except its own value. Follow
  `design.md#v6-envelope` and `#validation-and-failure-order`; do not create a compatible range.
- [x] Reuse the certified `InstanceGraph` and codec. Harden exact key/type/order/cardinality checks
  needed by v6; do not create another graph DTO.
- [x] Add one package-private strict live `load_and_elaborate` path under the canonical builder
  owner. Do not promote `build_elaborated_pipeline` or add another public entry point.
- [x] Make capture build and validate the complete envelope in memory, write/fsync one sibling
  temporary file, and `os.replace` only after validation. Pre-existing destinations remain
  byte-identical on every failure.
- [x] Make low-level v6 load return a validated, projectable `InstanceGraph`. The temporary vertical
  test may call the low-level loader directly; Phase 3 owns the final public `PipelineContext`.
- [x] Prove a tampered authoritative outer field fails even when the inner graph is correctly
  re-fingerprinted. Add the field-order-only success case separately.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/conformance/test_snapshot_v6_envelope.py \
  tests/conformance/test_snapshot_v6_routes.py \
  tests/conformance/test_snapshot_v6_capture.py -q
uv run pytest \
  tests/conformance/test_elaboration_graph_roundtrip.py \
  tests/conformance/test_elaboration_projection_one_way.py \
  tests/conformance/test_elaboration_fail_closed.py -q
uv run ruff check \
  src/sysml_codegen/snapshot \
  src/sysml_codegen/orchestration/pipeline_builder.py \
  src/sysml_codegen/orchestration/snapshot_context.py \
  tests/conformance/test_snapshot_v6_envelope.py \
  tests/conformance/test_snapshot_v6_routes.py \
  tests/conformance/test_snapshot_v6_capture.py
uv run mypy src/ --show-error-codes --no-error-summary --no-pretty --hide-error-context
git diff --check
```

### Completion evidence

- [x] Record the red and green focused outputs.
- [x] Record one instance fingerprint and complete computation digest equal across live,
  in-place-v6, and relocated-v6.
- [x] Record each ordered tamper failure type and prove projection was not called.
- [x] Record sentinel-destination hashes before/after every refusal.

### Rollback and interaction notes

This phase is an incomplete, non-releasable vertical slice. Keep its changes isolated in the
coordinated implementation worktree. If the certified graph lacks a required semantic field, stop
and surface the contradiction to the design; do not add envelope reconstruction from names or
retain v5 as a fallback.

### Implementation Notes

- 2026-08-10 red command: `uv run pytest tests/conformance/test_snapshot_v6_envelope.py
  tests/conformance/test_snapshot_v6_routes.py tests/conformance/test_snapshot_v6_capture.py -q`.
  Result: `5 failed, 2 passed in 0.92s`. The failures prove the format is still v5, the package-
  private exact live route and v6 loader are absent, and successful capture still enters the legacy
  builder and refuses the maintained fixture before any v6 artifact exists. The two passing atomic
  refusal checks preserve an existing sentinel and leave no new destination, but do not yet prove
  the final v6 writer.
- Codec hardening red command: `uv run pytest -o addopts=''
  tests/conformance/test_elaboration_graph_roundtrip.py::test_graph_codec_rejects_duplicate_and_unknown_keys
  -q`. Result: `1 failed in 0.30s`; the certified codec accepted a duplicate top-level key before
  v6 hardening.
- Sequencing note: `snapshot/source_manifest.py` received the final staged-admission owner needed by
  this vertical slice. Deferring it to Phase 2 would force capture to hash original files after
  SysIDE parsed them, contrary to D3/I6a. Phase 2 still owns the exhaustive policy matrix and sole-
  route convergence; no temporary second admission implementation was added.
- Green focused commands: the v6 suite reports `11 passed in 2.81s`; graph round-trip, one-way
  projection, and fail-closed regression report `27 passed in 4.13s`; focused Ruff and
  `git diff --check` pass. The exact mypy command reports the certified Item 6 baseline of `71`
  legacy errors and no error in a new v6 file; `.project/CURRENT_WORK.md` records that maintained
  gate as mypy-zero-new.
- Live, in-place, and relocated instance fingerprint:
  `35f023e5c65fdc628e3276f95a03bce43edf33f37a9dcb855c003ff98513150d`. Complete computation
  digest on all three routes:
  `35d1f168dec68c271f08da78ead798b53e75ecb38db6ae529a839e1693fa6f2d`.
- Ordered refusals prove duplicate/syntax/version/shape → `SnapshotFormatError`, outer/source/inner
  digest → `SnapshotIntegrityError`, marker/standard-library skew → `SnapshotCompatibilityError`,
  typed graph failure → `SnapshotFormatError`, and diagnostic graph →
  `SnapshotCertifiabilityError`. Compatibility and source failures monkeypatch graph decode to
  prove it is not called; the low-level loader never projects.
- The existing-destination sentinel SHA-256 is
  `a1e62bd7ca69b929d860254f409a84f295a875970d9967ee7aa4dd3342ba78ad` before and after strict
  elaboration refusal. Missing-destination refusal leaves no file or sibling temporary. Successful
  relocation preserves snapshot bytes; the measured capture/move SHA-256 pair was
  `5240f2974577021b107638c9ffed19d5b2f195e9fca3af937b21b11e3f40098d`.
- `snapshot_context.py`, `elaboration/project.py`, and `resolution/models.py` required no Phase 1
  production edit. The approved temporary test calls the low-level loader directly; the certified
  projector/model seam passed the complete-digest proof. Phase 3 owns their final public-context and
  receipt changes.

---

## Phase 2 — Sole Staged Source Admission and Standard-Library Digest

### Objective

Implement the complete D3/D6 document-admission algorithm and make it the only owner used by live
load, capture, and optional freshness verification. Pin SysIDE 0.8.4's 94-document standard-library
digest separately from user files.

### Assumption under test

One immutable admission record can bind the exact bytes SysIDE parsed, reproduce the admitted
document set from ordered replacement roots, and distinguish user sources from the standard library
without filesystem discovery or post-parse hashing races.

### Test stencil — write this first

```python
def test_admission_hashes_exact_bytes_parsed_by_syside(tmp_path):
    admission = admit_sources(overlapping_roots(tmp_path))
    model = parse(admission.staged_files)
    assert admitted_model_uris(model) == admission.staged_files
    assert admission.standard_library == PINNED_94_DOCUMENT_DIGEST
    mutate_original_and_add_file(tmp_path)
    with pytest.raises(SourceAdmissionError, match="SOURCE_RACE"):
        finalize_admission(admission, model)
```

### Exact files and census rows

- [x] `tests/unit/test_source_admission.py` and
  `tests/conformance/test_source_admission_routes.py` — `CUT-SRC-01`
- [x] `src/sysml_codegen/snapshot/source_manifest.py` (new) — `PROD-14`, `API-09`
- [x] `src/sysml_codegen/analysis/source_referent.py` — migrate then delete old import owner,
  `PROD-14`
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py` and `snapshot/capture.py` — `PROD-01`,
  `API-01`, `API-04`
- [x] `src/sysml_codegen/snapshot/envelope.py` and
  `orchestration/snapshot_context.py` — `API-05`, `API-06`, `PROD-12`
- [x] `tests/unit/test_source_referent.py`, `test_source_referent_shape_gate.py`,
  `test_capture_fixtures_filter.py` — `TEST-03.08`, `INV-RES-CG-123`

### Implementation steps

- [x] Red-test file/directory roots, duplicate/overlapping ownership, exact-file wins, deepest-root
  wins, root ordinals, `.sysml`/`.kerml`, UTF-8, root symlinks, descendant link refusal, physical
  escape, case/NFC collisions, additions/removals, byte/identity races, staged mutation, and exact
  SysIDE URI equality.
- [x] Implement `SourceAdmission` and `admit_sources` exactly as
  `design.md#one-staged-document-admission-algorithm`. SysIDE receives only the sorted staged file
  list and parses the bytes already hashed into the manifest.
- [x] Implement `SysideStandardLibraryDigestAdapter` over `Environment.get_default()` and pin count
  `94` plus SHA-256
  `ada7a0818f72e95f3953e46592bec91026bbd954efda251decc35d4036272f67`.
- [x] Keep standard-library documents out of `sources.files`. External non-library imports must be
  explicit roots; unresolved imports refuse.
- [x] Map live/capture admission failures to the closed `SourceAdmissionCode` vocabulary, including
  `SOURCE_STANDARD_LIBRARY_UNAVAILABLE`. Map freshness differences/admission failures to
  `SnapshotStaleSourceError`; map stored standard-library skew to `SnapshotCompatibilityError`.
- [x] Preserve the original caller-visible path for `design_path_filter` while the admitted set and
  semantic source referents use the canonical staged record.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/unit/test_source_admission.py \
  tests/conformance/test_source_admission_routes.py \
  tests/unit/test_source_referent.py \
  tests/unit/test_source_referent_shape_gate.py \
  tests/unit/test_capture_fixtures_filter.py -q
uv run pytest \
  tests/conformance/test_snapshot_v6_envelope.py \
  tests/conformance/test_snapshot_v6_routes.py \
  tests/conformance/test_snapshot_v6_capture.py -q
uv run ruff check \
  src/sysml_codegen/snapshot/source_manifest.py \
  src/sysml_codegen/snapshot/envelope.py \
  src/sysml_codegen/snapshot/capture.py \
  tests/unit/test_source_admission.py \
  tests/conformance/test_source_admission_routes.py
uv run mypy src/ --show-error-codes --no-error-summary --no-pretty --hide-error-context
git diff --check
```

### Completion evidence

- [x] Record the exact standard-library count/digest twice, including one run without the license
  environment, matching the design probe.
- [x] Record all admission failure codes and failure order.
- [x] Record source root/file manifests equal after relocation and different on add/remove/change.
- [x] Prove `import SI::*` adds no user-source row and a staged external document does.

### Rollback and interaction notes

Do not fall back to post-parse hashing, recursive globbing, absolute source paths, or nearby-tree
discovery if admission fails. A SysIDE version or default-environment change is a design premise
change and stops the phase.

### Implementation Notes

- 2026-08-10 red command: `uv run pytest tests/unit/test_source_admission.py
  tests/conformance/test_source_admission_routes.py tests/unit/test_source_referent.py
  tests/unit/test_source_referent_shape_gate.py tests/unit/test_capture_fixtures_filter.py -q`.
  Result: `5 failed, 44 passed in 2.34s`. The new admission matrix was already mostly green because
  Phase 1 had to introduce the final staging owner. Red failures identify the remaining migration:
  one dynamic external-import fixture omitted `SI::*`; three old tests still asserted v5 shape;
  and the legacy selective-capture reporter expected extraction DTO fields after capture became v6.
- The legacy filter test wrote `tests/fixtures/sample_model/extraction_snapshot.json` before its old
  reporter failed. It was immediately restored byte-for-byte to certified blob
  `4d4156378f0b5ea1b8b70ee8f70fb459cb55366d`; it is clean again and no recapture output was kept.
- Green commands: the focused admission/referent/migrated-filter suite reports `54 passed in
  2.02s`; the v6 envelope/route/capture regression reports `11 passed in 2.77s`; focused Ruff and
  `git diff --check` pass. The exact mypy command remains at the certified `71` legacy errors with
  no source-admission, envelope, capture, or referent finding.
- Two independent adapter reads report `94
  ada7a0818f72e95f3953e46592bec91026bbd954efda251decc35d4036272f67`; the second ran under
  `env -u SYSIDE_LICENSE_KEY` and matched byte-for-byte.
- Closed admission codes are `SOURCE_ROOT_INVALID`, `SOURCE_ALIAS_COLLISION`,
  `SOURCE_SYMLINK_ESCAPE`, `SOURCE_READ_ERROR`, `SOURCE_RACE`, `SOURCE_STAGE_MUTATED`,
  `SOURCE_ADMISSION_MISMATCH`, and `SOURCE_STANDARD_LIBRARY_UNAVAILABLE`. Root/enumeration/read
  policy runs before staging and the environment pin. After parse, staged bytes refuse first,
  exact SysIDE user-document URI mismatch refuses second, and original membership/identity drift
  refuses third.
- Original and relocated directory manifests both produced root row
  `{ordinal:0, kind:"directory"}` and file row
  `{referent:"root-0/model.sysml", size_bytes:7596,
  sha256:"e36149b70be33ce9723c6abf7fe453b4ed84393b07e4fc2cfd931e571851fee0"}`.
  An addition introduced sorted `root-0/added.sysml`; a byte change produced size `7607` and
  SHA-256 `b7db7eb9c81b6a965f601e53415f0839f8658508c5429156757ec535fcee1733`; removal of the sole
  document refused with `SOURCE_ROOT_INVALID`.
- The maintained fixture imports the SysIDE scalar library but admits exactly one user file,
  `root-0/model.sysml`. The explicit two-root external-import proof admits exactly
  `root-0/model.sysml` and `root-1/external.sysml`; omitting the external root refuses during live
  load.
- `snapshot/source_manifest.py` now owns canonical referent validation. The old analysis module is
  only a compatibility shim for legacy callers that Phase 7 deletes with the old authority; the
  exact live/capture/freshness route never calls its post-parse mapper. Lazy snapshot exports avoid
  an import cycle without adding another admission implementation. Caller-visible root spelling is
  retained privately for `design_path_filter`; envelopes and graph rows contain only logical
  referents.

---

## Phase 3 — Builder-Created PipelineContext, Canonical Selection, and Projection Receipt

### Objective

Switch the supported live and snapshot builders to one builder-created, immutable-byte-backed
`PipelineContext`. Bind canonical target selection and the complete projected graph to a receipt
verified at every certifying generation and seal boundary.

### Assumption under test

Canonical instance bytes plus canonical selection and a complete receipt are sufficient to preserve
the current `.computation_graph` capability while preventing caller construction, persistent
mutation, or a mismatched instance/computation pair.

### Test stencil — write this first

```python
def test_context_reprojects_from_bound_immutable_authority():
    ctx = build_pipeline_context(runtime_fixture(), targets=["b", "a", "a"], include_all=False)
    first = ctx.computation_graph
    mutate_every_public_graph_field(first)
    second = ctx.computation_graph
    assert second == expected_selected_projection()
    assert first is not second
    assert_all_constructor_receipt_and_pickle_tampers_refuse(ctx)
```

### Exact files and census rows

- [x] `tests/conformance/test_cutover_public_api.py` — `CUT-API-01`, `CUT-API-02`
- [x] `tests/conformance/test_cutover_projection_receipt.py` — `CUT-REC-01`
- [x] `tests/conformance/test_cutover_target_selection.py` — `CUT-SEL-01`
- [x] `tests/unit/test_cli_generation.py` — `CUT-CLI-01`, `API-07`, `API-08`
- [x] `src/sysml_codegen/orchestration/pipeline_context.py` — `API-02`, `INV-DISC-037`
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py` — `API-01`, `PROD-01`
- [x] `src/sysml_codegen/orchestration/snapshot_context.py` — `API-05`, `PROD-12`
- [x] `src/sysml_codegen/elaboration/project.py` — `PROD-17`
- [x] `src/sysml_codegen/cli/__init__.py` — `API-07`, `API-08`, `INV-RES-CG-017`
- [x] `src/sysml_codegen/generation/constraint_plan.py`, `generation/pipeline.py`, and certifying
  package-writing/sealing calls in `cli/__init__.py` — `PROD-23`
- [x] `src/sysml_codegen/orchestration/__init__.py`, `generation/__init__.py`, and
  `generation/initialization.py` — `API-10`, `API-11`, `API-12`

### Implementation steps

- [x] Red-test direct `PipelineContext` construction, every legacy field/kwarg, arbitrary graph
  pair, `object.__setattr__`, copy/deepcopy, pickle, mutated derived view, stale selection, stale
  projector marker, excluded computation field, and stale receipt.
- [x] Replace the wide context with the exact private state from D1. The two public builders alone
  call the package-private factory after validation/projectability and canonical selection.
- [x] Implement canonical target validation/dedup/sort and exact-edge closure in `project.py`.
  Constraints and their typed dependencies remain roots. Rendered strings may identify a requested
  public output but may not discover a semantic edge.
- [x] Compute the full computation digest over every semantic `ComputationGraph` field, including
  fields omitted from normal Pydantic serialization. Non-finite values refuse.
- [x] Make `.computation_graph` decode, validate, require projectability, reproject, recheck the
  receipt, and return a fresh graph on every access.
- [x] Give certifying generation one verified projection lease. Obtain one graph per generation
  operation, verify immediately before writing and again before sealing, and never reread a mutable
  property midway.
- [x] Delete `lower_constraints_enabled` from the live builder and `constraint_lowering_mode` from
  the context/API. Preserve target/include/filter and CLI flag/exit behavior exactly.
- [x] Preserve only the API-10/11/12 alias set. Do not add builder aliases to generation or root.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/conformance/test_cutover_public_api.py \
  tests/conformance/test_cutover_projection_receipt.py \
  tests/conformance/test_cutover_target_selection.py \
  tests/unit/test_cli_generation.py -q
uv run pytest \
  tests/conformance/test_generation_boundary.py \
  tests/conformance/test_elaboration_generation_boundary.py \
  tests/conformance/test_pipeline_e2e.py \
  tests/unit/test_contract_models.py \
  tests/unit/test_verify_package.py -q
uv run ruff check \
  src/sysml_codegen/orchestration \
  src/sysml_codegen/elaboration/project.py \
  src/sysml_codegen/cli \
  src/sysml_codegen/generation \
  tests/conformance/test_cutover_public_api.py \
  tests/conformance/test_cutover_projection_receipt.py \
  tests/conformance/test_cutover_target_selection.py
uv run mypy src/ --show-error-codes --no-error-summary --no-pretty --hide-error-context
git diff --check
```

### Completion evidence

- [x] Record every constructor/tamper refusal and every bound receipt field.
- [x] Record exact node sets for include-all and targeted closure, including mandatory constraint
  roots, on live/in-place/relocated routes.
- [x] Prove two `.computation_graph` reads are equal but distinct and mutations do not persist.
- [x] Prove sealing fails when the receipt changes after generation begins.

### Rollback and interaction notes

Do not retain the wide context, a public factory, a two-graph constructor, deprecated fields, or a
flagged old builder as rollback. If an existing consumer needs a capability beyond
`.computation_graph`, surface that uncensused API requirement before proceeding.

### Implementation Notes

- 2026-08-10 red focused command collected `68 items / 1 error`: the new receipt test could not
  import `_computation_digest`, proving the wide mutable context had no byte authority, selection,
  receipt, or verified lease before production changed.
- The final context is slotted with exactly `_instance_bytes`, `_selection`, and `_receipt`.
  Public and legacy-kwarg construction, normal assignment/deletion, shallow/deep copy, and pickle
  refuse. `object.__setattr__` changes to the instance bytes, selection, projector marker, or digest
  make the next view/lease verification fail. Mutating every returned graph field does not persist.
- Canonical target selection accepts only nonempty strings, sorts/deduplicates them, and follows
  `NodeRef`/`ProducerRef` edges only. The exact targeted live/in-place-v6/relocated-v6 receipt is:
  instance fingerprint `35f023e5c65fdc628e3276f95a03bce43edf33f37a9dcb855c003ff98513150d`,
  computation digest `dfa92d17b8e892a2386991e7937d91514dc4903e937e20f59897c124add1e081`,
  one canonical target, `include_all=False`, and marker `instance-projector/v1` on all three routes.
- The targeted node set is exactly the computed producer and consumer, five mandatory admitted
  constraint modules, and `constraint_report_aggregator`. `CUT-SEL-01` also pins the exact 24-node
  include-all set. Two fresh reads compare equal and are distinct objects.
- Certifying CLI generation obtains one graph from `_verified_projection_lease`; graph-only helpers
  receive that graph, and `_seal_package` rechecks the context and leased graph before its first
  seal mutation. `CUT-REC-01` changes the receipt after lease creation and proves pre-seal refusal.
- The inherited boundary command first reported `61 passed, 31 errors` because its setup still
  called deleted v5 DTO rebuilds. The approved census marks both files `TEST-03 MIGRATE`; their
  graph-only invariants now use the public exact fixture and their Phase-0 DTO baseline assertions
  are deleted. No v5 loader or lenient exact-elaborator path was restored. Projection also renders
  calculation-definition names as Python identifiers so the exact fixture's generated functions,
  schemas, and tests remain valid.
- Green commands: focused context/receipt/selection/CLI suite `76 passed in 2.96s`; inherited
  generation boundary suite `83 passed in 1.38s`; focused Ruff plus migrated caller files clean;
  exact mypy command reports `70` established legacy errors and no Phase-3-file error (one fewer
  than the certified 71-error Item-6 baseline); `git diff --check` clean. The evidence pass used one
  temporary fixture capture only; the 37-path recapture was not run.

---

## Phase 4 — Exact Occurrence, Binding, Aggregation, Selection, and Public Mutation

### Objective

Carry the already-certified Item 6 semantic route through the canonical public builders. Prove
exact occurrence structure, D-5 and rejected binding outcomes, typed aggregation edges, target
closure, one-way projection, exact public source cardinality, and every-and-only mutation without
executing a legacy helper.

### Assumption under test

The certified graph has all structure the public projector needs. Moving public callers onto it
does not require `PartInstanceIndex`, VBR, backtracking, key-table resolution, supplied values,
`OutputRegistry`, or any rendered-path reconstruction.

### Test stencil — write this first

```python
@pytest.mark.parametrize("route", ["live", "in_place_v6", "relocated_v6"])
def test_exact_source_changes_every_and_only_bound_consumer(route):
    baseline, changed = run_public_route(route, exact_runtime_cell(), off_default=True)
    assert changed.source_ids == {expected_source_id()}
    assert changed.consumer_ports == expected_positive_consumers()
    assert unchanged_public_values(baseline, changed) == expected_negative_set()
    assert projection_uses_only_typed_occurrences_and_edges(changed)
```

### Exact files and census rows

- [x] Existing exact owners `src/sysml_codegen/elaboration/{identity,occurrence,graph,elaborate,
  diagnostics,display}.py` — `PROD-16`; preserve Item 6 certification
- [x] `src/sysml_codegen/elaboration/project.py` — `PROD-17`
- [x] `tests/conformance/test_elaboration_occurrence.py` — `CUT-OCC-01`
- [x] `tests/conformance/test_elaboration_contract_matrix.py` — `CUT-BIND-01`
- [x] `tests/conformance/test_elaboration_aggregations.py` — `CUT-AGG-01`
- [x] `tests/conformance/test_elaboration_public_mutation.py` — `CUT-RES-01`
- [x] `tests/conformance/test_elaboration_projection.py` — `CUT-REG-01`
- [x] `tests/conformance/test_elaboration_projection_one_way.py` — `CUT-PROJ-01`
- [x] `tests/unit/test_elaboration_import_boundaries.py` — inherited F30 deny-by-default guard
- [x] Public route setup in `TEST-01`, `TEST-03`, and stable children `TEST-03.01` through
  `TEST-03.11`; exact inventory paths remain authoritative

### Implementation steps

- [x] First migrate the focused tests to public live/capture/in-place/relocated builders and record
  their failures while any route still reaches an old owner.
- [x] Preserve native `Usage.usages` child authority, exact occurrence parent/slot/index/type IDs,
  typed `ConsumerPortId`/`ExpressionPortId`/`ProducerRef` edges, closed value sites, and graph
  projectability. Do not rewrite these Item 6 mechanisms.
- [x] Make every runtime cell assert an exact source ID, exact positive consumer set, complete
  negative unaffected set, and identical semantic digest on all required routes.
- [x] Pin aggregation fold/cardinality from authored AST and concrete occurrence membership. No QN
  surgery, key-form table, or registry alias lookup may contribute semantics.
- [x] Extend the deny-by-default guard only when the final cutover adds boundary files. Keep the
  five narrow wire/rendering exemptions self-policing; do not add function allowlists.
- [x] Keep rendering collisions fail-closed. Automatic public-name disambiguation remains out of
  scope.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/conformance/test_elaboration_occurrence.py \
  tests/conformance/test_elaboration_contract_matrix.py \
  tests/conformance/test_elaboration_aggregations.py \
  tests/conformance/test_elaboration_public_mutation.py \
  tests/conformance/test_elaboration_projection.py \
  tests/conformance/test_elaboration_projection_one_way.py -q
uv run pytest tests/unit/test_elaboration_import_boundaries.py -q
uv run pytest tests/conformance -k 'elaboration and not dual_run and not corpus_ledger' -q
uv run ruff check src/sysml_codegen/elaboration tests/unit/test_elaboration_import_boundaries.py
uv run mypy src/ --show-error-codes --no-error-summary --no-pretty --hide-error-context
git diff --check
```

### Completion evidence

- [x] Record route-by-route fingerprints, digests, exact consumer sets, and negative unaffected
  sets for every runtime cell.
- [x] Record exact aggregation term edges and occurrence IDs for the plural/fold witnesses.
- [x] Record the boundary guard test count and every exercised exemption.
- [x] Record zero import/call from the legacy owners for these public semantic proofs.

### Rollback and interaction notes

If a migrated test was only a mechanism oracle, do not preserve its helper to keep the test green.
Move the useful literal behavior to its named `CUT-*` replacement and leave deletion to Phase 7. A
new supported semantic shape is an owner/design question, not a new fallback.

### Implementation Notes

- 2026-08-10 focused migration red command: `uv run pytest
  tests/conformance/test_elaboration_occurrence.py
  tests/conformance/test_elaboration_contract_matrix.py
  tests/conformance/test_elaboration_aggregations.py
  tests/conformance/test_elaboration_public_mutation.py
  tests/conformance/test_elaboration_projection.py
  tests/conformance/test_elaboration_projection_one_way.py -q`. Result after replacing the old
  route setup: `3 failed, 48 passed in 16.91s`. One evidence encoder attempted a nonexistent
  `FeatureSlotId.to_wire`; two constraint-only exact fixtures were refused before projection.
  The fixes serialize the slot's declaration ID and admit a strict semantic graph when it has a
  calculation or constraint. They do not add a legacy fallback.
- The public projector now carries target closure by typed node/output/entry semantics. Module
  display names remain rendering only. Native occurrence records, typed binding edges, authored
  aggregation structure, and fail-closed rendering collision behavior were preserved. The stale
  lowering-flag caller in `test_elaboration_phase5_remediation.py` was migrated to the final public
  builder after the broad gate exposed it.
- Ordered green evidence after Phase 3 closure: focused suite `51 passed in 16.77s`; boundary guard
  `14 passed in 0.29s`; broad elaboration regression first reported `1 failed, 167 passed, 1676
  deselected in 33.30s`, then `168 passed, 1676 deselected in 32.21s` after the stale caller
  migration. Focused and migrated-test Ruff checks pass. The exact mypy command reports `70`
  established errors, including the pre-existing legacy-builder error at
  `pipeline_builder.py:245`, and no new exact elaboration/projector error. `git diff --check` is
  clean.
- Durable route evidence is
  `implementation-evidence/phase4-public-route-evidence.json`, SHA-256
  `4914ff4883f07709b2f8b49910617a5cb86d26aad02111c7a1f9c3a334562dc3`. It validates as 22 runtime
  cells times live/in-place-v6/relocated-v6. Each cell records baseline and changed receipts, exact
  typed source or value-site identity, exact positive consumer ports, changed keys, and the
  complete negative unaffected key set for every route. It also records exact term ports/sources
  and occurrence IDs for five fold witnesses plus the bank and D38 plural occurrences.
- The deny-by-default gate exercises exactly five exemptions: the two identity wire decoders,
  elaboration direction rendering, group identity rendering, and constraint module-type rendering.
  The final legacy-owner scan across all six public proof files returned no match (expected `rg`
  exit 1); no public semantic proof imports or calls the old occurrence, backtracking, producer,
  supplied-value, registry, or dual-pipeline owner. The focused evidence passes recaptured only its
  maintained fixtures; the one-time 37-path candidate batch was not run.

---

## Phase 5 — Exact Compiler and Constraint Cutover Across Codegen and Agentic

### Objective

Converge all four Item 6 transitional duals. The unsuffixed compiler is exact-ID keyed. One
identified constraint extraction pass and one exact profile evaluation own codegen and validation.
Delete the qualified-name association path, transitional exports, sidecars, coexistence assertions,
and name-keyed compiler walk.

### Assumption under test

Every current compiler, validation, preflight, and codegen caller can consume the exact result
directly. No non-codegen caller needs QN candidate selection once it receives an already-decided
identified record.

### Test stencil — write this first

```python
def test_unsuffixed_compiler_and_profile_are_the_only_decision_cores():
    compilation = compile_calc_def(id_keyed_calc_payload())
    facts = extract_constraint_facts(collision_model())
    profile = evaluate_profile(facts)
    assert compilation.definition_id == expected_definition_id()
    assert profile.by_usage_id[expected_usage_id()].effective_definition_id == expected_constraint_id()
    assert_transitional_symbols_and_qn_candidate_selection_are_absent()
```

### Exact files and census rows

Codegen:

- [x] `tests/conformance/test_exact_compiler_core.py` — `CUT-COMP-01`
- [x] `tests/conformance/test_exact_constraint_route.py` — `CUT-CON-01`
- [x] `tests/conformance/test_elaboration_payload_identity.py` — `CUT-PAY-01`
- [x] `src/sysml_codegen/extraction/expression_compiler.py` — `PROD-18`
- [x] `src/sysml_codegen/extraction/data_models.py` and
  `src/sysml_codegen/elaboration/elaborate.py` — `PROD-19`, `PROD-20`, `PROD-21`
- [x] `src/sysml_codegen/elaboration/value_defaults.py` (new) and
  `src/sysml_codegen/generation/constraint_catalog.py` — neutral helpers from `PROD-15`
- [x] `src/sysml_codegen/_upstream_pins.py`, `generation/predicate_compiler.py`, and
  `tests/conformance/test_upstream_pins.py` — `PROD-22`

Agentic, requiring coordinated write authority:

- [x] `src/agentic_mbse/sysml/constraint_extraction.py` and `sysml/__init__.py` — `PROD-20`
- [x] `src/agentic_mbse/sysml/executable_profile.py` — `PROD-21`, `INV-RES-AG-001`
- [x] `src/agentic_mbse/sysml/{constraint_facts,expression_ir}.py` — retain `PROD-22`
- [x] `src/agentic_mbse/validation/level4_constraints.py` and `level6_architecture.py` — `PROD-21`
- [x] `tests/test_sysml/test_constraint_extraction.py`,
  `test_constraint_extraction_ordering.py`, `test_constraint_fact_shapes.py` — `AGENTIC-TEST-01`
- [x] `tests/test_sysml/test_executable_profile.py`, `test_executable_profile_arithmetic.py`,
  `test_executable_profile_v3.py`, `test_executable_profile_v4.py` — `AGENTIC-TEST-02`
- [x] `tests/test_sysml/test_expression_ir_extraction.py`, `test_public_api_exports.py` —
  `AGENTIC-TEST-03`
- [x] `tests/test_validation/test_item12_checks.py`, `test_level4_reconciliation.py` —
  `AGENTIC-TEST-04`

### Implementation steps

- [x] Write the two new codegen conformance tests and update agentic export/caller tests. Record red
  failures for the `_exact`/identified coexistence and QN decision path.
- [x] Promote `compile_calc_def_exact` behavior to the sole unsuffixed `compile_calc_def` accepting
  ID-keyed payload/IR. Delete the parallel name-keyed AST walk, `_exact` symbol, and equality test.
- [x] Replace name-keyed calculation maps and v5-excluded ID sidecars with one declaration-ID keyed
  payload. Names remain metadata only.
- [x] Make agentic `extract_constraint_facts(model) -> IdentifiedConstraintFacts` the one pass.
  Delete `extract_identified_constraint_facts` and its export.
- [x] Make agentic `evaluate_profile(IdentifiedConstraintFacts) -> IdentifiedProfileResult` the one
  decision core. Delete `_evaluate_usage`, the QN definition map, `evaluate_identified_profile`, and
  unreferenced QN result types.
- [x] Migrate levels 4/6 to `item.decision`. Make `preflight` accept already-decided exact data and
  prohibit association. A formatter, if still needed, must be text-only with a `format_*` name.
- [x] Move only `resolve_modeled_default` and `mint_constraint_id` to their design owners. Do not
  retain `analysis/constraint_lowering.py` as a helper bag.
- [x] Update all cross-repository pins and export allowlists as one coordinated API unit.

### Commands

```bash
cd /home/reid/1cfe/agentic-mbse
uv run pytest \
  tests/test_sysml/test_constraint_extraction.py \
  tests/test_sysml/test_constraint_extraction_ordering.py \
  tests/test_sysml/test_constraint_fact_shapes.py \
  tests/test_sysml/test_executable_profile.py \
  tests/test_sysml/test_executable_profile_arithmetic.py \
  tests/test_sysml/test_executable_profile_v3.py \
  tests/test_sysml/test_executable_profile_v4.py \
  tests/test_sysml/test_public_api_exports.py \
  tests/test_validation/test_item12_checks.py \
  tests/test_validation/test_level4_reconciliation.py -q
uv run ruff check src tests
uv run mypy src/ --show-error-codes --no-error-summary --no-pretty --hide-error-context
git diff --check

cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/conformance/test_exact_compiler_core.py \
  tests/conformance/test_exact_constraint_route.py \
  tests/conformance/test_elaboration_payload_identity.py \
  tests/unit/test_expression_compiler.py \
  tests/conformance/test_expression_compiler.py \
  tests/conformance/test_upstream_pins.py -q
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule item6-dual-2 --expect absent
uv run ruff check src tests
uv run mypy src/ --show-error-codes --no-error-summary --no-pretty --hide-error-context
git diff --check
```

### Completion evidence

- [x] Record the exact unsuffixed public exports and return types in both repositories.
- [x] Record one collision/reversed-order trace from usage UUID through definition UUID, decision,
  exact graph node, and projected constraint.
- [x] Record neutral schema/golden disposition and exact graph-v6 round trip.
- [x] `item6-dual-2 --expect absent` reports zero hits.
- [x] Record both repository SHAs/statuses together; no one-sided usable state is claimed.

### Rollback and interaction notes

This phase cannot run in a codegen-only writable sandbox. If agentic authority is unavailable, stop
before editing either repository. Keep coordinated patches/commits paired; never restore a QN
adapter or `_exact` sibling as a compatibility rollback.

### Implementation Notes

- 2026-08-10 coordinated red tests were written before production edits. Agentic's exact focused
  command collected 441 tests and reported `6 failed, 435 passed in 3.12s`: unsuffixed extraction
  still returned `ConstraintFacts`, unsuffixed evaluation still performed QN association, and the
  transitional identified extractor remained exported. Codegen's exact focused command collected
  99 tests and reported `3 failed, 91 passed, 5 errors in 0.53s`: the `_exact` compiler/extractor
  symbols remained, `compile_calc_def` still required the name-keyed AST argument, and five old
  cross-model compiler cases attempted to load v5 fixtures. The five errors are migration evidence,
  not authority to recapture: those useful compiler assertions must move to live exact payloads.
  Production in both repositories was unchanged for these red runs.
- The coordinated cutover now exposes only `extract_constraint_facts(model) ->
  IdentifiedConstraintFacts`, `evaluate_profile(IdentifiedConstraintFacts) ->
  IdentifiedProfileResult`, `preflight(IdentifiedProfileResult) -> PreflightResult`, and
  `compile_calc_def(calc_def) -> CalcDefCompilationResult`. Exact UUIDs own profile association,
  compiler dependency/order maps, graph attachment, and payload identity. Names remain rendering
  metadata. Legacy v5 compiler payload reconstruction now fails because it cannot supply the exact
  declaration UUIDs; no compatibility sidecar or qualified-name adapter was added.
- Ordered final functional evidence: agentic focused `441 passed in 3.07s`; codegen focused `76
  passed in 0.40s`; exact graph-v6 route/codec round trip `15 passed in 3.70s`; and
  `item6-dual-2 --expect absent` returned `0` hits. The neutral `constraint-facts/v2` production
  golden remained byte-identical in the agentic focused suite.
- Quality evidence: codegen full-tree Ruff fell from the Item-6 baseline `358` to `353`, production
  and all Phase-5-file Ruff selections are clean, mypy fell from `71/17` to `68/16` with no
  Phase-5-file error, and `git diff --check` passes. Agentic full-tree Ruff remains exactly `127`,
  all Phase-5-file Ruff selections are clean, mypy fell from `105/23` to `95/20` with no
  Phase-5-file error, and `git diff --check` passes. A voluntary agentic production-only Ruff run
  still reports the certified unrelated `N806` finding in `extraction/index.py`; the Phase 9
  production-clean gate must resolve its ownership without treating it as a Phase 5 cutover fix.
- Durable paired evidence is
  `implementation-evidence/phase5-exact-cutover-evidence.json`, SHA-256
  `edd3d3849caae198dd490bbfe530c342e1d830b9037c6063370d2cbe24a93d7f`. It records both unchanged
  repository HEADs and complete dirty statuses together, exact exports/signatures and version pins,
  the collision/reversed-order guards, two live UUID-to-projection traces, neutral golden hashes,
  graph-v6 disposition, residue, and quality results. It explicitly claims neither owner acceptance
  nor a usable one-sided state. The one-time 37-path recapture was not run.

---

## Phase 6 — Fusion Tea, C25/C2, C19, F26, and Arithmetic Goldens

### Objective

Apply exactly the 15 D-5 formal/binding renames in the maintained Fusion Tea fixture. Prove C25 and
C2 exact consumer sets, two independent arithmetic goldens, C19's `80.0` calc/constraint result,
and F26's literal public names/IDs. Do not create a sibling fixture or change physics.

### Assumption under test

Renaming only calculation formals and their expression references is sufficient to expose the
intended bare RHS referents while preserving equations, defaults, outputs, module/schema identities,
and the hand-derived LCOE.

### Test stencil — write this first

```python
def test_fusion_tea_renames_preserve_topology_and_arithmetic():
    graph = build_pipeline_context(fusion_tea_paths()).computation_graph
    assert exact_renames(graph) == FT_01_THROUGH_FT_15
    assert consumers("hif_plant.availability") == {"lcoe_calc.availability_in", "meier_coe_calc.availability_in"}
    assert consumers("hif_plant.thermal_efficiency") == {"lcoe_calc.thermal_efficiency_in", "recirc_calc.thermal_efficiency_in"}
    assert arithmetic_goldens(graph) == independently_pinned_results()
```

### Exact files and census rows

New/migrated proofs:

- [x] `tests/conformance/test_fusion_tea_cutover.py` — `CUT-FT-01`, `CUT-C25-01`, `CUT-C2-01`
- [x] `tests/conformance/test_cutover_c19.py` — `CUT-C19-01`
- [x] `tests/conformance/test_wi014_toy.py` — migrate `TEST-01.01` to `CUT-F26-01`
- [x] `tests/conformance/test_compile_calc_def_golden.py` — `CUT-ARITH-01`

Exact Fusion Tea files:

- [x] `tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml` — ten occurrence bindings,
  `FIX-01`, `PROD-24`
- [x] `tests/fixtures/fusion_tea/designs/hif_ife/hif_plant.sysml` — three occurrence bindings,
  `FIX-01`, `PROD-24`
- [x] `tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml` — two occurrence bindings,
  `FIX-01`, `PROD-24`
- [x] `tests/fixtures/fusion_tea/library/analyses/ife_lcoe.sysml` — `FTGEN-01..07`
- [x] `tests/fixtures/fusion_tea/library/analyses/fusion_cycle.sysml` — `FTGEN-08..10`
- [x] `tests/fixtures/fusion_tea/library/analyses/hif_economics.sysml` — `FTGEN-11..15`
- [x] `tests/fixtures/golden/calc_def_compilation_golden.json` — `GOLDEN-01`
- [x] `tests/fixtures/golden/calc_compat_parity_golden.json` — `GOLDEN-02`
- [x] `tests/runtime/test_fusion_tea_acceptance.py` — direct callers `FTGEN-08/09/14/15`
- [x] `tests/fixtures/fusion_tea/extraction_snapshot.json` — leave v5 untouched in this phase;
  Phase 8 replaces it only in the candidate batch (`B37-15`)

### Implementation steps

- [x] Write the four focused proof surfaces and record red failures on all 15 self-bindings,
  duplicate C25/C2 topology, the legacy C19 mechanism, and F26 old-route comparison.
- [x] Apply exactly `FT-01` through `FT-15` from `design.md#fusion-tea-migration-and-generated-
  consequences`: each formal becomes `<name>_in`; each bare RHS remains the original source; every
  corresponding equation reference changes. Change no source attribute, default, output, equation,
  or model physics.
- [x] Assert C25 has one `hif_plant.availability` source and exactly
  `lcoe_calc.availability_in` plus `meier_coe_calc.availability_in`; separately enumerate every
  unaffected input/output.
- [x] Assert C2 has one `hif_plant.thermal_efficiency` source and exactly
  `lcoe_calc.thermal_efficiency_in` plus `recirc_calc.thermal_efficiency_in`; separately enumerate
  every unaffected input/output.
- [x] Update `GOLDEN-01` only for the 15 named result records and `GOLDEN-02` only for the three
  direct records. Keep `lcoe`, `gamma`, and `f_recirc` as unchanged controls.
- [x] Prove C19 literal `80.0` reaches one exact calculation and one exact constraint consumer on
  all routes. Its arithmetic proof and absence of supplied-value machinery remain separate.
- [x] Replace F26 live-oracle comparison with the exact literal group, four source keys, sole alias
  tuple, and sole constraint ID in `design.md#independent-semantic-proofs`.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/conformance/test_fusion_tea_cutover.py \
  tests/conformance/test_cutover_c19.py \
  tests/conformance/test_wi014_toy.py \
  tests/conformance/test_compile_calc_def_golden.py \
  tests/runtime/test_fusion_tea_acceptance.py -q
uv run pytest \
  tests/conformance/test_elaboration_contract_matrix.py \
  tests/conformance/test_elaboration_public_mutation.py \
  tests/conformance/test_snapshot_v6_routes.py -q
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule all --expect inventoried
uv run ruff check tests/conformance tests/runtime
git diff --check
```

### Completion evidence

- [x] Exactly 15 `_in = original_bare_name` mappings and zero same-named Fusion Tea bindings.
- [x] Exact positive and complete negative C25/C2 consumer sets on live/in-place/relocated routes.
- [x] Golden diff lists only the designed 15/3 records; unchanged controls remain byte/value equal.
- [x] C19 and F26 literal evidence passes without a legacy import or comparison.

### Rollback and interaction notes

Do not create a corrected sibling, a 38th corpus row, a qualified-RHS escape, or normalized
both-sides parity. If the LCOE or an unchanged control moves, treat it as a failed premise and stop;
do not update the expected arithmetic from runtime output.

### Implementation Notes

- 2026-08-10 focused red command used the five planned proof files and collected 46 tests. Result:
  `11 failed, 26 passed, 9 skipped in 1.37s`. The Fusion Tea route refused all exact 15
  `SI_SELF_BINDING` sites, the static rename proof observed zero `_in = source` mappings, and all
  four live-generation arithmetic tests stopped at the same refusal. The dedicated C19 live/v6
  proofs and F26 exact literal oracle were already green.
- The red run also found five stale golden-test ordering failures outside the designed 15 output
  records. The legacy golden stores name-sorted independent execution order; Phase 5's approved
  exact compiler uses declaration UUIDs and forbids names from deciding order. The output-record
  comparisons will remain keyed by rendered output name while exact dependency/order correctness
  stays owned by `CUT-COMP-01`. No name-based tie-breaker or non-Fusion golden rewrite is permitted.
- The approved `FT-01..15` formal declarations, expression references, and occurrence bindings were
  then applied in place. The static exact-count proof passed `1 passed in 0.05s`, confirming exactly
  15 `_in = original_bare_name` mappings and zero remaining same-named Fusion Tea bindings. The
  first public C25/C2 route still failed `1 failed in 0.25s`, now with seven
  `SI_OCCURRENCE_MISSING` diagnostics for inherited HIF driver/chamber/target scopes. R9, D11, and
  the approved exact-model semantics assign these effective inherited occurrences to the existing
  elaboration identity/occurrence owner. The seven failures are therefore an elaborator regression,
  not a fixture premise conflict: keep the 15 in-place mappings and repair the existing owner without
  a second resolver, name reconstruction, topology change, qualified RHS, or projectability carveout.
  The focused seven-occurrence regression and its red/green evidence are recorded in
  `implementation-evidence/phase6-inherited-occurrence-evidence.json`; no golden workaround or
  corpus recapture is permitted while that repair is underway.
- The focused inherited-enum occurrence regression was then added before production changes. It
  pins all seven occurrence display paths, canonical root slots, exact effective writer declaration
  IDs, and resolved enumeration referents, plus strict projectability. The focused red command
  collected eight tests and failed exactly `8 failed in 0.40s`: seven nodes had `value=None`
  instead of their resolved enum referent and strict elaboration reported the same seven
  `SI_OCCURRENCE_MISSING` findings. This establishes that occurrence population and writer
  selection are correct; enum-valued inherited writers are being misclassified as value aliases.
- The existing value-node owner now classifies a feature reference by its exact resolved referent:
  a referent owned by an enumeration definition becomes the occurrence's qualified enum scalar;
  other feature references remain aliases. No resolver, graph field, model topology, or name-based
  lookup was added. The unchanged focused command is green: `8 passed in 0.30s`.
- The completed focused command reports `45 passed, 9 skipped in 3.29s`; the independent
  compatibility golden reports `28 passed, 9 skipped in 0.32s`; and the prescribed regression
  command reports `34 passed in 14.95s`. Runtime controls remain LCOE `270.1211779380445`,
  gain-100 LCOE `216.55528392479388`, gamma `68.247088`, cost `0.9749584`, and recirculating
  fraction `0.07222302470027446`. Generated multi-output return tuples now follow the same exact
  declaration-ID order as projected schemas.
- `GOLDEN-01` changes exactly 15 named records and `GOLDEN-02` exactly three; `lcoe`, `gamma`, and
  `f_recirc` are unchanged controls. Residue remains the inventoried pre-deletion population
  (`334` hits). The prescribed broad test Ruff scope reports the inherited 93 findings; full-tree
  Ruff remains exactly the Phase-5 baseline of `353`, every Phase-6 file is clean, and
  `git diff --check` passes. Durable evidence is
  `implementation-evidence/phase6-inherited-occurrence-evidence.json`, SHA-256
  `a565f3ffd46caf7fc0407066579bab44c9ac281a09759410b10b33553b12e1bd`. The Fusion Tea v5
  snapshot was not changed and the 37-path recapture was not run.

---

## Phase 7 — Full Ledger Migration, Deletion, Compatibility Removal, and Absence Gates

### Objective

After all independent replacements are green, execute the entire API/production/script/test/doc
ledger. Delete v5, the old semantic front end, every Item 6 dual, the dual-run harness, wrong-oracle
tests, and compatibility surfaces. Finish with the exact inventory and zero-residue gates.

### Assumption under test

Every useful legacy behavior now has an independent exact-route owner. Removing the old files and
symbols will expose missing replacements as test failures rather than require a compatibility shim.

### Test stencil — write this first

```python
def test_closed_census_has_no_runtime_residue():
    inventory = load_closed_inventory()
    assert all(replacement_is_green(row) for row in rows_to_delete(inventory))
    assert scan_residue(rule="all") == []
    assert final_public_exports() == API_10_THROUGH_API_14_ALLOWLIST
    assert no_v5_snapshot_or_projectable_legacy_route_exists()
```

### Exact files and census rows

- [x] `tests/conformance/test_cutover_no_legacy_residue.py` — `CUT-ABS-01`
- [x] Public surfaces `API-01..API-14`; production responsibilities `PROD-01..PROD-24`
- [x] Scripts `SCR-01..SCR-04`; retain/migrate only `SCR-05..SCR-08`
- [x] Test groups `TEST-01..TEST-07`, stable children `TEST-01.01..TEST-05.03`,
  `AGENTIC-TEST-01..04`, and `GOLDEN-01..02`
- [x] Documentation row `DOC-01` for removal of callable legacy/v5 descriptions. Broader Item 8
  certification/guidance work remains out of scope.
- [x] Every one of the 231 exact paths in `cutover-inventory.json`; its path/row key is the
  file-level owner when a broad census row groups responsibilities.

Files that must be deleted as owners, not retained as helper bags:

- [x] `src/sysml_codegen/orchestration/elaborated_pipeline.py`, `elaboration/diff.py`, and
  `scripts/run_elaboration_corpus.py` — `PROD-02`, `SCR-01`, `NR-01`
- [x] `analysis/part_instance_index.py`, `dependency_backtracker.py`, `signature_extractor.py`,
  `phantom_detector.py`, `parameter_groups.py` — `PROD-03`, `PROD-05`, `PROD-06`
- [x] `resolution/producer_resolution.py`, `producer_completeness.py`, `supplied_values.py`,
  `graph_builder.py` — `PROD-07..10`
- [x] `core/output_registry.py`, `orchestration/output_registry_builder.py` — `PROD-09`
- [x] `snapshot/serializer.py`, `loader.py`, `graph_rebuild.py` — `PROD-12`
- [x] `analysis/constraint_lowering.py` after neutral helpers move — `PROD-15`
- [x] Executable legacy probes in `SCR-03` and helper `tests/helpers/registry_compat.py`

### Implementation steps

- [x] Write `CUT-ABS-01` first and make it fail on every current deleted file, symbol, export,
  call, script entry, v5 marker, wrong-oracle test, and compatibility field.
- [x] Migrate all API callers and exact useful test responsibilities before deleting an owner.
  Use the stable inventory path and replacement ID; do not mark a whole suite migrated by the
  29-cell matrix.
- [x] Delete the legacy builder body while retaining the canonical API-01 file as a small exact
  orchestrator. Delete API-03 and the dual-run diff/runner outright.
- [x] Delete rendered-path occurrence reconstruction, VBR/self rescue, specialized-chain repair,
  virtual usages, aggregation scope re-derivation, backtracking semantic discovery, 21-key forms,
  supplied values/C19 tripwire, registry namespaces, and legacy graph assembly.
- [x] Delete v5 capture/serialize/load/rebuild, `GrandfatheredSnapshotError`, mode flags, old DTO
  exports, v5 fixtures for refusal rows, and every projectable adapter/upgrader.
- [x] Prune legacy-only extraction/hierarchy/computed-attribute portions only after exact callers
  move. Preserve independently useful DTO/rendering code under positive nonlegacy owners.
- [x] Migrate the current architecture descriptions in `DOC-01` enough that no deleted symbol is
  presented as callable. Do not consume Item 8's full documentation/certification remit.
- [x] Regenerate the inventory. Every final row must be present/deleted/planned exactly as designed,
  and every deletion replacement must be green before the final zero-residue run.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest tests/conformance/test_cutover_no_legacy_residue.py -q
.venv/bin/python scripts/check_cutover_census.py inventory \
  --census .project/active/elaborator-cutover/cutover-census.md \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --write .project/active/elaborator-cutover/cutover-inventory.json
.venv/bin/python scripts/check_cutover_census.py compare \
  --census .project/active/elaborator-cutover/cutover-census.md \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --require-sorted --require-closed
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule all --expect absent
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule item6-dual-2 --expect absent
uv run pytest tests/
uv run ruff check src
git diff --check

cd /home/reid/1cfe/agentic-mbse
uv run pytest tests/
uv run ruff check src
git diff --check
```

Run the exact `NR-01` through `NR-12` commands from `cutover-census.md#no-residue-and-closure-gates`.
Expected-empty `rg` commands pass only with exit code 1; do not hide a match by excluding an
affected production/test/script/doc path.

### Completion evidence

- [x] Regenerated inventory is closed, sorted, exact, and records the final current bytes/states.
- [x] Both residue rules report zero; Phase-7 absence gates `NR-01..NR-09` and `NR-12` pass.
  Candidate-batch gates `NR-10` and `NR-11` remain owned by Phase 8.
- [x] No v5 fixture or format marker remains outside historical `.project/**`; exactly the later
  accepted runtime rows may have v6 files.
- [x] Every deleted test responsibility names its green independent `CUT-*` replacement.
- [x] Fresh full-suite counts are recorded for both repositories; historical Item 6 counts are not
  reused.

### Rollback and interaction notes

Delete only after its replacement is green. Keep a recoverable local phase patch/commit; do not use
`git reset`, `git clean`, or checkout to recover deleted files because those operations can erase
the certified prerequisite and design scaffold. A missing replacement or new disposition stops
this phase and reopens the census/design, not a compatibility shim.

### Implementation Notes

- 2026-08-10 `CUT-ABS-01` was written before deletion. The focused red command collected eight
  tests and reported `2 failed, 6 passed in 0.08s`: the first all-delete census path
  (`scripts/_q5_debug.py`) is still present, and the snapshot export surface still exposes v5,
  grandfather, rebuild, and serializer names. The same test also pins final inventory path states,
  both residue rules, zero extraction snapshots, API-10..14 exports, alias identity, and refusal of
  six old context fields.
- 2026-08-10 the full ledger cutover deleted the obsolete front end, semantic repair owners, v5
  codec, compatibility scripts/probes, wrong-oracle tests, and all pre-candidate stored captures.
  The retained API-01 file is a 91-line staged exact orchestrator. Virtual calculation-usage
  expansion and its stale model-list oracles were removed after exact occurrence projection was
  green.
- Final JUnit artifacts record codegen `953 passed` in `62.756s` and agentic `1819 passed, 1
  skipped, 33 deselected` in `19.369s`. Codegen production Ruff is clean; repository Ruff improved
  from the Phase-5 baseline `353` to `100` with zero Phase-7 changed-file findings. Codegen mypy
  improved from `68 errors / 16 files` to `56 / 11` with zero Phase-7 production errors. Agentic
  remains byte-identical to its Phase-5 quality baseline: Ruff `127` repository findings and one
  inherited production finding; mypy `95 / 20`. Both `git diff --check` commands are clean.
- The final inventory is closed and sorted at exactly `231` rows. `all` and `item6-dual-2` residue
  rules each report zero hits. Literal scans `NR-01..05`, `NR-07`, and `NR-12` are empty with exit
  code 1; focused `NR-06` and `NR-09` tests are green. Durable evidence:
  `implementation-evidence/phase7-cutover-evidence.json`.

---

## Phase 8 — Exact 37-Path Batch, Outcomes, Normalized Diffs, Scale, and Real TEAx

### Objective

Against the stable sole authority, run exactly the inherited 37 paths once as the candidate batch.
Record graph/refusal/control outcomes, normalized semantic diffs, exact counts, customer-scale
budgets, license state, and real TEAx generation/seal/execute evidence. Keep all outputs temporary
until owner acceptance.

### Assumption under test

The final authority produces exactly 14 v6 graphs, 22 typed capture refusals, and one non-R7
no-calculation control, with zero unclassified semantic diffs and stable scale/execution behavior.

### Test stencil — write this first

```python
def test_manifest_has_exact_37_paths_and_allowed_outcomes(candidate):
    assert candidate.ids == B37_01_THROUGH_B37_37
    assert candidate.counts == {"v6": 14, "refusal": 22, "control": 1}
    assert all(row.actual == row.required for row in candidate.rows)
    assert candidate.semantic_diffs.unclassified == []
    assert candidate.v5_artifacts == []
```

### Exact files and census rows

- [x] `tests/conformance/test_cutover_manifest.py` — `CUT-CORP-01`, `NR-10`
- [x] `scripts/capture_extraction_snapshots.py`, `capture_baseline_yaml.py`,
  `capture_pipeline_baselines.py`, and `capture_filter.py` — migrate `SCR-02` into one public-v6
  batch/capture route; no dual comparison
- [x] `scripts/measure_item7_acceptance.py` (new) — `SCR-05`, `CUT-SCALE-01`, `CUT-TEAX-01`
- [x] `tests/execution/test_fusion_tea_item7_real_teax.py` — `CUT-TEAX-01`
- [x] `tests/execution/test_fusion_tea_item7_budget.py` — `CUT-SCALE-01`
- [x] Snapshot paths identified by `INV-RES-CG-071..110` and manifest rows `B37-01..B37-37`
- [ ] Temporary schema-declared candidate evidence templates for accepted batch, normalized diff,
  quality/license results, scale/TEAx, and owner-review rendering. Phase 9 binds exact final paths
  in the candidate record; Phase 10 materializes their candidate-ID sentinels.

### Implementation steps

- [ ] Write `CUT-CORP-01` and the two execution tests first. Record red failures for wrong count,
  unexpected snapshot on refusal, unclassified diff, missing real TEAx, and an exceeded threshold.
- [ ] Use the exact `B37-01..B37-37` table. Do not discover a 38th path or update an expected
  outcome from the run. Runtime rows get v6; diagnostic/control rows get typed records and no
  snapshot. Remove all stale v5 artifacts.
- [ ] Normalize or isolate `captured_at` and other declared non-semantic churn. Compare actual
  semantic changes to the Item 5 ledger and record every classification; zero unclassified is
  required.
- [ ] Record occurrence, node, edge, envelope-byte, graph-fingerprint, and projected-digest values.
  Repeat counts/digests across one warm-up plus three measured Fusion Tea runs.
- [ ] Run real TEAx from the pinned clean checkout/interpreter in `design.md#scale-and-real-teax-
  evidence`. Generate temporary live and relocated packages, verify with both package verifiers,
  discover through public registry creation, and execute through real `execute_pipeline`.
- [ ] Require LCOE `270.1211779380445` within relative tolerance `1e-6` plus separate C25/C2
  every-and-only mutations. Do not use `tests.runtime.pipeline_runner`, a monkeypatch, or a private
  compatibility API.
- [x] Keep the batch and evidence under one task-specific OS temp directory. Do not copy candidate
  evidence into tracked authority yet.

### Commands

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest tests/conformance/test_cutover_manifest.py -q
uv run python scripts/capture_extraction_snapshots.py

PYTHONPATH=/home/reid/1cfe/sysml-codegen/src:/home/reid/1cfe/agentic-mbse/src \
  /home/reid/1cfe/teax/.venv/bin/python -m pytest -o addopts='' -m execution \
  tests/execution/test_fusion_tea_item7_real_teax.py \
  tests/execution/test_fusion_tea_item7_budget.py --collect-only -q
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src:/home/reid/1cfe/agentic-mbse/src \
  /home/reid/1cfe/teax/.venv/bin/python -m pytest -o addopts='' -m execution \
  tests/execution/test_fusion_tea_item7_real_teax.py \
  tests/execution/test_fusion_tea_item7_budget.py -vv
git -C /home/reid/1cfe/teax status --short --branch
git -C /home/reid/1cfe/teax rev-parse HEAD
```

### Completion evidence

- [ ] Exact 37 unique paths; `14 v6 / 22 refusal / 1 control`; zero v5; zero unclassified.
- [ ] Each runtime row records live/in-place/relocated fingerprint/digest equality. Each refusal
  records the exact diagnostic and proves no artifact. The control records its exact
  `CodeGenerationError` and no artifact.
- [ ] One warm-up plus three measured runs all satisfy: live load/elaborate `<=10s`, projection
  `<=2s`, complete public capture `<=5s`, generation+seal `<=30s`, real TEAx `<=30s`, peak RSS
  `<=512 MiB`, envelope `<=25 MiB`.
- [ ] TEAx collection is exactly two tests; execution is exactly two passed with zero
  skipped/xfailed/deselected. Checkout remains clean at the design-pinned revision/state.
- [ ] Both verifiers agree on hashes; both public packages reproduce LCOE and C25/C2 mutation
  results. No package/run output is tracked.

### Rollback and interaction notes

The “one batch” rule means one accepted committed authority, not one attempt. A failed exploratory
or owner-revised batch remains temporary and is replaced, never appended to the repository. Any
unexpected path outcome or scale/TEAx failure returns to the owning production phase before a new
candidate is assembled.

### Implementation Notes

- 2026-08-10 test-first admission began red at collection: the manifest test could not import the
  missing one-shot batch helpers, and the two execution modules did not exist. Before recapture,
  `CUT-CORP-01` was `7 passed`; the focused manifest/capture/public-route selection was `17 passed`;
  the pinned real-TEAx interpreter collected exactly two execution tests. Phase-8 script and test
  Ruff checks were clean.
- The exact candidate command `UV_CACHE_DIR=/tmp/uv-cache-elaborator uv run python scripts/capture_extraction_snapshots.py`
  was invoked once. It exited 1 with `candidate batch
  failed: B37-01 outcome is unexpected`. No retry or replacement recapture was attempted.
- Preserved raw results contain `15 v6 / 22 typed refusal / 0 control`. The single production
  mismatch is `B37-01 agg_literal_probe`: the ledger requires the no-calculation
  `CodeGenerationError` and no snapshot, while the public route produced a v6 graph with
  `5 occurrences / 3 attributes / 1 calculation / 0 constraints / 4 nodes / 3 edges`.
  Fingerprint `ad63183922961bfb48152205a04e1ea73b1524ddad7e0708c740f90902c7c3aa` and
  projected digest `9d6e1d6e07024b2929c3915ecc1f4fe1d7e1822806e9593c286c7484601558f2`
  identify that unexpected artifact.
- The driver also reported the 22 expected refusal rows as `unexpected-error` because it decoded
  `ElaborationDiagnosticError` but production raised `ElaborationError`. Read-only inspection of
  every preserved live/capture message confirmed all 22 exact approved diagnostic multisets. This
  is a candidate-harness classification defect; it was recorded without changing or rerunning the
  batch.
- The immutable failed candidate remains at `/tmp/elaborator-cutover-item7-candidate`: 15 graph
  snapshots and 15 relocated copies total `423014` bytes; snapshot-manifest SHA-256 is
  `f40d6fd6b2430b2ec35105e19c2ae6bec4928e8158509fd768f57b5a3b289034`. Scale and real-TEAx
  execution were not started. Durable evidence is
  `implementation-evidence/phase8-failed-batch-evidence.json`. Phase 8 and all later phases remain
  unchecked pending resolution of the B37-01 production mismatch and explicit authority for any
  replacement batch.

---

## Phase 9 — Immutable Paired Candidate, Quality/License Gates, and Owner Stop

### Objective

Implement the singular candidate coordinator and workflow contract, run final two-repository
quality/license/evidence gates, assemble one canonical candidate record and review rendering, then
stop for the pending owner accept/revise decision. Do not prepare refs, make final candidate commits,
publish acceptance tags, promote branches, or publish product tags in this phase.

### Assumption under test

One finite candidate preimage can bind both repository contents, patches, batch/evidence templates,
contracts, commands, results, environment, and TEAx state. Any bound change yields a new candidate
ID and invalidates review.

### Test stencil — write this first

```python
def test_candidate_id_binds_both_repositories_without_a_hash_cycle(tmp_path):
    record, templates = build_candidate(two_repo_fixture(tmp_path))
    assert record.candidate_id == recompute_id_with_self_sentinel(record)
    materialized = materialize_declared_pointers(templates, record.candidate_id)
    assert reverse_materialization(materialized) == templates
    mutate_one_bound_byte(record)
    assert verify_candidate(record).candidate_id_mismatch
```

### Exact files and census rows

- [ ] `scripts/check_cutover_candidate.py` — `SCR-06`, `PROMO-22`,
  `INV-PLAN-CANDIDATE-SCRIPT`
- [ ] `tests/unit/test_check_cutover_candidate.py` — `PROMO-02`, `CUT-PROMO-01`
- [ ] `tests/integration/test_cutover_candidate_promotion.py` — `PROMO-03`, `CUT-PROMO-02`
- [ ] `tests/conformance/test_cutover_candidate_workflows.py` — `PROMO-04`, `CUT-PROMO-03`
- [ ] Codegen workflows `.github/workflows/elaborator-cutover-{branch,tags,release}.yml` —
  `PROMO-07`, `PROMO-09`, `PROMO-11`
- [ ] Agentic workflows at the same paths — `PROMO-08`, `PROMO-10`, `PROMO-12`; coordinated write
  authority required
- [ ] `.project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json` — `PROMO-01`
- [ ] `.project/active/elaborator-cutover/evidence/quality-baseline.json` — design-required Item 6
  Ruff/mypy identity baseline
- [ ] Schema-declared JSON evidence templates bound under `candidate.evidence_templates`; exact
  final paths and JSON pointers must be present in the canonical record before review

### Implementation steps

- [ ] Write unit/integration/workflow tests first using two temporary bare authoritative origins.
  Record red failures for circular ID materialization, local-only promotion, missing compensation,
  foreign OIDs, hard-block recovery, one-sided product tags, and wrong workflow caller.
- [ ] Implement only the phase grammar in D12: `prepare`, `verify`, `promote-branches`,
  `publish-tags`, `recover-hard-block`, `verify-tags`, and `verify-release`. Reject aliases,
  additional repos, relative paths, phase lists, and a second record.
- [ ] Implement canonical record-self exclusion and schema-declared evidence-template sentinel/
  JSON-pointer reversal exactly. No materialized candidate-ID-bearing final-byte hash may enter its
  own candidate ID.
- [ ] Bind both exact origins, bases, public refs, complete path inventories/content roots,
  normalized patches, accepted batch templates, contracts, commands/results, environment, TEAx,
  and promotion schema. Any change makes a new ID.
- [ ] Implement remote-CAS/compensation/recovery logic in tests, but do not call real remotes in this
  phase. Workflows and ruleset prerequisites are static candidate content, not authorization to
  mutate GitHub.
- [ ] Run the exact final quality, changed-file, license, census, residue, 37-path, scale, and TEAx
  gates. Record fresh counts. Compare Ruff/mypy identities to `quality-baseline.json`; do not compare
  totals alone.
- [ ] Assemble the canonical candidate record and human-review rendering from the Phase 8 temporary
  batch/templates. Verify recomputation locally without `prepare`.
- [ ] **STOP.** Present the singular candidate ID, both content roots/patch digests, exact 37
  outcomes, normalized diffs, quality/license counts, scale/TEAx results, and ruleset/App
  prerequisites to the owner. Record only the owner's explicit `accept` or `revise`; do not infer it.

### Commands

Candidate/coordinator proof:

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest \
  tests/unit/test_check_cutover_candidate.py \
  tests/integration/test_cutover_candidate_promotion.py \
  tests/conformance/test_cutover_candidate_workflows.py -q
.venv/bin/python scripts/check_cutover_census.py compare \
  --census .project/active/elaborator-cutover/cutover-census.md \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --require-sorted --require-closed
.venv/bin/python scripts/check_cutover_residue.py \
  --repo codegen=. --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule all --expect absent
```

Codegen final gates:

```bash
cd /home/reid/1cfe/sysml-codegen
uv run pytest tests/
uv run ruff check src --output-format json
uv run ruff check src tests --output-format json
uv run mypy src --show-error-codes --no-error-summary --no-pretty --hide-error-context
test -n "$SYSIDE_LICENSE_KEY"
env SYSIDE_LICENSE_KEY="$SYSIDE_LICENSE_KEY" uv run pytest -o addopts='' \
  tests/conformance/test_constraint_generation_live.py::test_s4_slice_generation_level_reproduction \
  tests/conformance/test_elaboration_phase5_remediation.py::test_inline_constraint_references_a_real_modeled_input \
  --junitxml=.project/active/elaborator-cutover/evidence/codegen-live.xml -vv -rA
git diff --check
```

Agentic final gates:

```bash
cd /home/reid/1cfe/agentic-mbse
uv run pytest tests/
uv run ruff check src --output-format json
uv run ruff check src tests --output-format json
uv run mypy src --show-error-codes --no-error-summary --no-pretty --hide-error-context
test -n "$SYSIDE_LICENSE_KEY"
env SYSIDE_LICENSE_KEY="$SYSIDE_LICENSE_KEY" uv run pytest -o addopts='' \
  tests/test_validation/test_level4_reconciliation.py::TestLevel4PopulationReconciliation::test_single_file_categories_sum_to_assessed_denominator \
  tests/test_validation/test_item12_checks.py::test_c3_admitted_constraint_is_silent \
  tests/test_sysml/test_constraint_extraction_ordering.py::test_identified_anonymous_usages_keep_exact_ids_when_enumeration_reverses \
  --junitxml=/home/reid/1cfe/sysml-codegen/.project/active/elaborator-cutover/evidence/agentic-live.xml -vv -rA
git diff --check
```

### Completion evidence

- [ ] Candidate record is canonical; candidate ID recomputes; evidence templates reverse exactly;
  undeclared ID occurrences refuse.
- [ ] Both repositories' complete content roots and normalized patch digests are bound.
- [ ] Fresh full-suite and license counts match captured command/JUnit evidence. Codegen licensed
  selection is exactly `2 collected/2 passed`; agentic is `3 collected/3 passed`; no license skip,
  xfail, or deselection.
- [ ] Production Ruff is clean; full-tree Ruff/mypy has zero new identity and no changed-file
  finding versus the Item 6 baseline.
- [ ] Candidate review package includes exact 37 outcomes, normalized diffs, scale, real TEAx,
  repository states, and promotion prerequisites.
- [ ] Owner disposition is explicitly recorded as `accepted` or `revise`. Until then the status
  remains `pending-owner-acceptance` and Phase 10 stays unchecked.

### Rollback and interaction notes

An owner `revise` disposition invalidates the candidate. Return to the owning phase, rebuild the
temporary batch/templates, compute a new ID, rerun all gates, and request review again. Never edit a
candidate in place while retaining its ID. Do not create or publish acceptance tags on the owner's
behalf.

---

## Phase 10 — Accepted Evidence Materialization and Paired Preparation/Promotion

### Objective

Only after the owner explicitly accepts the singular candidate ID, materialize declared evidence,
prepare clean detached paired commits/hidden refs, obtain the two owner-created acceptance tags,
verify the accepted pair, and execute only the allowed remote CAS branch/tag/release gates. This
phase owns operations, not new product behavior.

### Preconditions and red gate first

- [ ] The owner disposition for the exact candidate ID is recorded as `accepted`. A prior candidate,
  ambiguous response, or approval of only one repository does not satisfy this gate.
- [ ] Before mutation, run read-only verification and record its expected refusal while prepared
  refs/dual acceptance tags are absent. This proves the gate is closed; do not weaken verification
  to make it pass early.
- [ ] Both authoritative GitHub repositories have the D12 branch/tag rulesets and promotion App
  installed. The acceptance namespace is owner-only; the App cannot create those tags.
- [ ] The promotion token is supplied only through `CUTOVER_PROMOTION_GITHUB_TOKEN`. Never print,
  persist, or bind the token value.

### Exact files and census rows

- [ ] Materialized evidence at the exact schema-declared paths in
  `elaborator-cutover-candidate.json` — `PROMO-01`
- [ ] Clean detached worktrees `/home/reid/1cfe/cutover-prepared/sysml-codegen` and
  `/home/reid/1cfe/cutover-prepared/agentic-mbse`
- [ ] Hidden prepared refs `PROMO-13`, `PROMO-14`
- [ ] Owner acceptance tags `PROMO-15`, `PROMO-16`
- [ ] Protected public refs `PROMO-17`, `PROMO-18`
- [ ] Runtime journal/lock `PROMO-05`, `PROMO-06`
- [ ] Protected paired product tags `PROMO-21`
- [ ] `.project/active/elaborator-cutover/evidence/release-manifest.json` — `PROMO-19`
- [ ] `scripts/check_cutover_candidate.py recover-hard-block` — `PROMO-22`, used only on a recorded
  hard block

### Implementation/operation steps

- [ ] Recompute the accepted candidate ID immediately before materialization. Any byte, environment,
  command result, TEAx state, base/ref, or evidence-template change invalidates acceptance and
  returns to Phase 9.
- [ ] Let the sole coordinator deterministically replace only declared candidate-ID sentinels and
  verify reversal/template hashes. Do not use a second materializer.
- [ ] Run `prepare` against the exact clean detached worktrees. It creates local hidden refs and a
  durable `PREPARED` journal only; it must not advance a public branch.
- [ ] Have the owner create and publish both immutable annotated acceptance tags targeting the
  prepared commits. Stop if either tag is missing, mismatched, moved, or cites another ID.
- [ ] Run read-only `verify`. It must freshly read both authoritative origins and acceptance tags.
- [ ] Run `promote-branches` under the App/lock. Require exact remote leases and observed/returned
  OIDs. If the second origin fails, accept only recorded successful compensation or
  `HARD_BLOCKED`; never continue through a hard block.
- [ ] Run `publish-tags`, then read-only `verify-tags`. A second-tag failure must compensate the
  first or enter `TAGS_HARD_BLOCKED`.
- [ ] Create the exact paired release manifest and run read-only `verify-release`. This is a gate,
  not permission to publish a release outside the requested scope.
- [ ] Use `recover-hard-block` only for one of its exact allowed observed states/targets. Foreign or
  ambiguous OIDs require owner intervention; do not improvise Git repair.

### Commands

Common arguments shown in full on every phase:

```bash
cd /home/reid/1cfe/sysml-codegen
.venv/bin/python scripts/check_cutover_candidate.py prepare \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse \
  --codegen-worktree /home/reid/1cfe/cutover-prepared/sysml-codegen \
  --agentic-worktree /home/reid/1cfe/cutover-prepared/agentic-mbse

.venv/bin/python scripts/check_cutover_candidate.py verify \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse

.venv/bin/python scripts/check_cutover_candidate.py promote-branches \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse \
  --token-env CUTOVER_PROMOTION_GITHUB_TOKEN

.venv/bin/python scripts/check_cutover_candidate.py publish-tags \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse \
  --token-env CUTOVER_PROMOTION_GITHUB_TOKEN

.venv/bin/python scripts/check_cutover_candidate.py verify-tags \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse

.venv/bin/python scripts/check_cutover_candidate.py verify-release \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse \
  --release-manifest .project/active/elaborator-cutover/evidence/release-manifest.json
```

Recovery commands are not routine steps. Use only the exact design-approved forms after a recorded
hard block:

```bash
.venv/bin/python scripts/check_cutover_candidate.py recover-hard-block \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse \
  --token-env CUTOVER_PROMOTION_GITHUB_TOKEN \
  --scope branches --target bases

.venv/bin/python scripts/check_cutover_candidate.py recover-hard-block \
  --record .project/active/elaborator-cutover/evidence/elaborator-cutover-candidate.json \
  --state-dir /home/reid/1cfe/.cutover/elaborator-cutover \
  --codegen-repo /home/reid/1cfe/sysml-codegen \
  --agentic-repo /home/reid/1cfe/agentic-mbse \
  --token-env CUTOVER_PROMOTION_GITHUB_TOKEN \
  --scope product-tags --target absent
```

The other allowed recovery targets are `branches/candidate` and `product-tags/published`, exactly
as D12 specifies. Choose a target only from the freshly observed bound state and recorded owner
direction.

### Completion evidence

- [ ] Materialized evidence reverses to every accepted template; candidate ID is unchanged.
- [ ] Both prepared commits exactly match bound content roots/patches/bases and both owner tags cite
  the same accepted ID.
- [ ] Journal reaches an allowed paired state with complete authoritative observations. No
  `HARD_BLOCKED` or `TAGS_HARD_BLOCKED` remains.
- [ ] Both public refs, both acceptance tags, and both product tags verify against the accepted
  candidate; release manifest binds the exact paired tuples.
- [ ] Final repository states reconstruct the owner-accepted bytes and no one-sided state passes a
  tag/release gate.

### Rollback and interaction notes

Any post-acceptance bound-byte change invalidates acceptance and returns to Phase 9. A failed second
remote update is handled only by the coordinator's exact compensation/recovery state machine. Do
not run ad hoc pushes, force updates, tag deletions, resets, or manual journal edits. Public branch
and tag mutation requires the accepted owner gate, installed rulesets/App, valid short-lived token,
and the implementation session's external-mutation authority.

---

## Risk Management

- **Envelope/source mismatch:** Phase 1 proves integrity and Phase 2 proves exact parsed bytes before
  broad use. No post-parse hash fallback is allowed.
- **Mutable derived graph:** Phase 3 binds immutable canonical bytes, selection, projector marker,
  and every computation field. Generation verifies the receipt twice.
- **Useful legacy oracle deleted:** Phase 7 requires the row-specific independent replacement green
  before deletion. The 29-cell matrix is never a blanket replacement.
- **Cross-repository skew:** Phase 5 needs both writable roots and coordinated evidence. Phases 9–10
  bind both repositories under one ID and remote-CAS protocol.
- **Fusion Tea arithmetic drift:** Phase 6 keeps hand-authored goldens and unchanged controls; Phase
  8 real TEAx is additional evidence, not the source of expected values.
- **Recapture churn:** Phase 8 isolates mechanical timestamps and classifies all semantic changes;
  only the accepted batch becomes tracked authority.
- **Owner acceptance assumed:** Phase 9 is a hard stop. Phase 10 cannot start from silence,
  inference, an old ID, or a one-repository approval.
- **Scale/license evidence skipped:** explicit collection/count commands fail on skip, xfail,
  deselection, wrong interpreter, dirty TEAx, or missing license.
- **Deletion makes rollback tempting:** use isolated coordinated worktrees and recoverable local
  patches/commits. Never erase the certified baseline or owner files with destructive Git commands.

## Implementation Notes

The implementation agent must update this section and the phase checkbox immediately after each
phase. Include timestamp, exact files, commands/counts, issues, deviations, both repository states,
and whether the next phase is unblocked. Do not reconstruct progress at the end.

### Phase 0 completion

- **Completed:** 2026-08-10 during design closure; revalidated during planning.
- **Actual changes:** Existing census/inventory scripts/tests retained; no production code.
- **Evidence:** 4 focused tests; 231 closed/sorted rows; 363/5 inventoried transitional hits.
- **Deviations:** None. Design evidence remains current-worktree based, not a clean-base claim.

### Phase 1 completion

- **Completed:** Pending
- **Red evidence:** Pending
- **Actual changes:** Pending
- **Commands/results:** Pending
- **Issues/deviations:** Pending
- **Repository states:** Pending

### Phase 2 completion

- **Completed:** Pending
- **Red evidence:** Pending
- **Actual changes:** Pending
- **Commands/results:** Pending
- **Issues/deviations:** Pending
- **Repository states:** Pending

### Phase 3 completion

- **Completed:** 2026-08-10 after ordered gate reconciliation.
- **Red evidence:** The first focused run collected 68 items and stopped with one collection error:
  `_computation_digest` did not exist on the wide mutable context. The inherited boundary run then
  reported 61 passed / 31 errors because its setup still called the deleted v5 DTO rebuild route.
- **Actual changes:** Public live and v6 builders now return the same frozen, slotted, immutable-
  byte-backed context. Canonical selection and full receipts cover the complete computation graph.
  Certifying generation uses one verified lease and rechecks before sealing. Generation-boundary
  tests were migrated from v5 rebuild/baseline setup to the public exact fixture per census
  `TEST-03`; no compatibility loader or second semantic route was added.
- **Commands/results:** Reconciled focused command `76 passed in 2.93s`; inherited regression
  command `83 passed in 1.35s`; exact Phase-3 Ruff command clean; exact mypy command reports the
  established 70-error baseline with no Phase-3-file error; `git diff --check` clean. Receipt,
  constructor/tamper, exact live/in-place/relocated node sets, equal-but-distinct views, mutation
  isolation, and post-generation/pre-seal receipt refusal are all checked above.
- **Issues/deviations:** The inherited tests' v5 setup was a censused migration, not a product
  premise conflict. Calculation-definition display names are sanitized only at projection so
  exact-model generated identifiers remain valid. The one-time 37-path recapture was not run.
- **Repository states:** Codegen HEAD remains
  `1672c5766f67e7716f3c9f8f636c21e2ea444601` with the preserved certified Item-6 dirty work plus
  Item-7 implementation. Agentic HEAD remains
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`; its only dirt is the pre-existing
  `.orchestrate-logs/` directory.

### Phase 4 completion

- **Completed:** Pending
- **Red evidence:** Pending
- **Actual changes:** Pending
- **Commands/results:** Pending
- **Issues/deviations:** Pending
- **Repository states:** Pending

### Phase 5 completion

- **Completed:** Pending
- **Red evidence:** Pending
- **Actual changes:** Pending
- **Commands/results:** Pending
- **Issues/deviations:** Pending
- **Repository states:** Pending

### Phase 6 completion

- **Completed:** 2026-08-10. Every Phase-6 production, proof, and completion checkbox is green.
- **Red evidence:** Initial `11 failed, 26 passed, 9 skipped`; focused inherited-occurrence proof
  `8 failed in 0.40s`, preserved in the Phase-6 evidence JSON.
- **Actual changes:** Exact FT-01..15 migration, inherited enum occurrence values, declaration-ID
  multi-output ordering, 15/3 golden records, C25/C2/C19/F26 proofs, and direct runtime callers.
- **Commands/results:** Focused `45 passed, 9 skipped`; compatibility golden `28 passed, 9 skipped`;
  regression `34 passed`; inventoried residue `334`; Phase-6 Ruff clean; diff check clean.
- **Issues/deviations:** Broad test Ruff retains 93 inherited findings and full-tree Ruff remains the
  certified Phase-5 count of 353. No new or changed-file finding was introduced.
- **Repository states:** Heads remain codegen `1672c5766f67e7716f3c9f8f636c21e2ea444601` and agentic
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`; certified Item-6 dirt is preserved in both.

### Phase 7 completion

- **Completed:** 2026-08-10; all Phase-7 production, migration, inventory, absence, and quality
  boxes are green. Phase 8 had not been invoked when this phase closed.
- **Red evidence:** `CUT-ABS-01` began at `2 failed, 6 passed`; failures named the first retained
  delete path and the wide snapshot export surface.
- **Actual changes:** Removed the census-approved old semantic front end, v5 codec/captures,
  compatibility routes, repair/registry/backtracking owners, stale probes, and wrong-oracle test
  responsibilities. Retained exact projection/rendering behavior and migrated current callable
  documentation.
- **Commands/results:** Codegen `953/953` passed; agentic `1819 passed, 1 skipped, 33 deselected`.
  Inventory `231`, closed/sorted. Both residue rules `0`. Production Ruff: codegen clean, agentic
  one inherited finding. Repository Ruff: codegen `100` with zero changed-file findings, agentic
  `127` unchanged. Mypy: codegen `56/11` with zero Phase-7 production errors, agentic `95/20`
  unchanged. Both diff checks clean.
- **Issues/deviations:** Phase-order wording was made explicit: `NR-10`/`NR-11` require the Phase-8
  batch and real-TEAx evidence; the Phase-7 absence gates are `NR-01..09` plus `NR-12`.
- **Repository states:** codegen HEAD `1672c5766f67e7716f3c9f8f636c21e2ea444601`, 364 dirty
  entries (`105 M / 222 D / 37 ??`), status digest
  `491be466212cb1e47d65faba0c49338264ab21766ebe56fdbe2fd4df770f3c62`; agentic HEAD
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`, 87 dirty entries (`15 M / 72 ??`), status digest
  `e3b97a7c6067c60846eb1907339c081b4254b7747d6eb3ec9126f8785f94f65f`. Certified Item-6
  changes remain intact.

### Phase 8 completion

- **Completed:** No. The sole permitted candidate batch stopped on an unexpected B37-01 outcome;
  Phase 8 remains unchecked.
- **Red evidence:** Initial manifest/execution collection failed on missing Phase-8 helpers and
  modules. The one-shot accepted-candidate command then exited 1 on B37-01.
- **Actual changes:** Added the manifest, scale, and real-TEAx proof surfaces; consolidated SCR-02
  into the one-shot public-v6 driver; added the acceptance measurement helper; and preserved the
  complete failed candidate outside tracked authority.
- **Commands/results:** Pre-batch `7 passed`, focused `17 passed`, real-TEAx collection exactly two.
  Batch invocation count `1`; preserved raw outcomes `15 v6 / 22 refusal / 0 control`; no scale or
  real-TEAx execution.
- **Issues/deviations:** B37-01 produced a v6 graph instead of the required no-calculation control.
  The driver additionally mislabeled 22 exact typed refusals because it did not decode
  `ElaborationError`. Per the one-batch rule, neither issue was repaired or retried after capture.
- **Repository states:** Both dirty Item-6 worktrees remain preserved. HEADs remain codegen
  `1672c5766f67e7716f3c9f8f636c21e2ea444601` and agentic
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`; no commit, tag, ref promotion, or owner acceptance
  occurred. Failed-batch details and candidate-file digests are recorded in
  `implementation-evidence/phase8-failed-batch-evidence.json`.

### Phase 9 completion / owner checkpoint

- **Candidate ID:** Pending
- **Quality/license/recapture/scale/TEAx evidence:** Pending
- **Owner disposition:** **Pending — do not assume acceptance**
- **Accepted/revise record:** Pending

### Phase 10 completion

- **Completed:** Blocked on Phase 9 owner acceptance
- **Prepared refs/commits:** Pending
- **Acceptance tags:** Pending
- **Promotion journal terminal state:** Pending
- **Release verification:** Pending

## Pipeline Handoff

Implementation starts with `$my-implement`. After all allowed phases are complete and the accepted
landing exists, run an independent `$my-audit`; the implementing agent does not self-certify.
`$my-close` and `$my-pre-pr` happen only after audit certification and the owner-accepted landing.
For this epic, run the branch-level pre-PR gate at the shipping boundary specified by the epic, not
mid-item or per internal phase.

**Next Step:** `$my-implement`
