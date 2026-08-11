# Implementation Plan: Item 7 Cutover Recovery

**Status:** Owner-approved for execution **[OWNER 2026-08-10]**, with two amendments applied at
approval: the external archive moved to a durable non-temp path, and an independent audit agent
required after every Phase 3 slice.
**Created:** 2026-08-10
**Last Updated:** 2026-08-10

## Authority and Source Material

This is intentionally a standalone recovery plan. There is no separate recovery spec or design.
The owner requested one plan that a fresh agent can execute without relying on chat history.

- **[OWNER]** Preserve recoverability, restore real functional regression protection, commit work
  progressively, and determine which Item 7 changes are actually sound.
- **[EXAMPLE]** The owner proposed either correcting the Item 7 plan and restarting from the
  committed project artifacts, or preserving the current candidate elsewhere and selectively
  recovering good changes.
- **[AGENT] (ratified for capture by owner, 2026-08-10)** Use the hybrid: preserve the entire
  current candidate on forensic branches, rebuild from the certified Item 6 commits in clean
  worktrees, and import only reviewed changes in tested vertical slices.
- **[REFERENT]** Recovery incident handoff:
  `/tmp/handoff-20260810-211932.md`.
- **[REFERENT]** Incident forensics:
  `.project/research/20260810-213932_item7-cutover-incident-forensics.md`.
- **[REFERENT]** Phase/file map, deletion reconciliation, and test-quality audit:
  `.project/research/20260810-220500_item7-cutover-forensic-map.md`.
- **[INHERITED]** Item 7 shaping and execution record:
  `.project/active/elaborator-cutover/{spec.md,design.md,cutover-census.md,cutover-inventory.json,plan.md}`.
  These are evidence and inputs to review. They are not automatically trusted recovery authority.
- **[INHERITED]** Certified Item 5 and Item 6 records:
  `.project/completed/20260809_elaborator-breadth/` and
  `.project/completed/20260810_elaborator-identity-completion/`.
- **[REFERENT]** Raw implementation history:
  `.orchestrate-logs/run-implement-20260810-100248-2302614.jsonl` and
  `.orchestrate-logs/resume-019feca0-*.jsonl`.

## The Point

Item 7 is supposed to replace the legacy string-resolution front end with one exact instance-graph
authority without breaking the product. The current uncommitted candidate cannot establish that:
it combines useful new work, 222 tracked deletions, 22 corrupted architecture documents, a smaller
surviving test suite, one unresolved corpus outcome, and no progressive commits. Independent
forensic runs show that its live and relocated package paths can execute in real TEAx at the
expected LCOE, but that evidence came from repaired copies of a failed candidate and is not an
accepted Phase 8 result.

Recovery must preserve every current byte, return development to the certified Item 6 baseline,
and rebuild the cutover so each reviewable commit proves a complete public behavior slice. Legacy
production code, tests, probes, snapshots, and documentation may be retired only after the new
route has passed the same public behavior and real execution checks while the old evidence is still
available.

## Verified Incident Baseline

Re-verify these facts at execution start. Stop if any differ.

- sysml-codegen branch `source-identity-epic`, HEAD
  `1672c5766f67e7716f3c9f8f636c21e2ea444601`.
- agentic-mbse branch `elaborate-first-salvage`, HEAD
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`.
- sysml-codegen currently has 105 unstaged modifications, 222 unstaged deletions, no staged
  changes, and untracked Item 7 paths.
- agentic-mbse currently has 15 unstaged modifications, no staged changes, and untracked
  `.orchestrate-logs/`.
- No Item 7 commit, tag, promotion, accepted audit, accepted scale run, or accepted TEAx evidence
  set exists. Independent forensic diagnostics did execute live and relocated packages in real
  TEAx; preserve those outputs as evidence, not as certification.
- The failed temporary candidate is `/tmp/elaborator-cutover-item7-candidate` while that OS-temp
  path survives.

## Non-Negotiable Execution Rules

1. **Preserve before changing.** No reset, restore, checkout, clean, stash, revert, branch switch,
   or candidate repair until Phase 1's external archive is verified.
2. **The forensic candidate is a parts bin, never a merge source.** Do not cherry-pick or merge its
   monolithic commit into the rebuild branches.
3. **One vertical slice, one green commit.** Begin the next slice only from clean worktrees. Record
   both repository OIDs after every coordinated slice.
4. **Declare paths before editing.** Each slice records its expected path set. An unexpected changed
   path stops the slice before commit.
5. **Functional gates use public behavior.** Internal graph-shape checks supplement load →
   elaborate → project → generate → seal → execute evidence; they never replace it.
6. **Keep the Item 6 tests until after product proof.** A lower test count is a finding, not a green
   gate. Every removed or rewritten test needs a responsibility-level disposition reviewed before
   deletion.
7. **No bulk spike or probe deletion.** Preserve by default. Archive or delete only an explicit,
   owner-reviewed list with a recorded reason for each path or coherent family.
8. **No bulk documentation replacement.** Restore every incident-modified file under
   `docs/architecture/` from the Item 6 commit. Rewrite one subject at a time after the
   implementation is stable. Review `CLAUDE.md` separately because it was changed in the same
   sweep but is not part of the 22-file architecture-doc restore.
9. **Run real TEAx before legacy production deletion.** Graph capture or generated-file comparison
   alone is insufficient.
10. **Surface premise conflicts.** B37-01, an unexplained product diff, a changed corpus outcome, a
    new deletion disposition, or a test responsibility without a replacement stops the dependent
    work for owner review.
11. **No automatic continuation, amended [OWNER 2026-08-10] at execution approval.** The Gate 4A
    deletion-ledger approval is delegated to the orchestrator, which must record every disposition
    against this plan's rules before Gate 4B starts. The live owner stop is final candidate
    acceptance (Phase 5). Rule 10 premise-conflict stops are unchanged by this delegation.
12. **No promotion in this plan.** Pushes, tags, public-ref updates, and releases remain out of
    scope.

## Implementation Strategy

### Phasing rationale

Preserve the mixed worktree first because every later action depends on being able to recover it.
Then establish clean Item 6 worktrees and a measured functional baseline. Rebuild the new route in
small vertical slices while the old implementation and tests remain available. Only after the new
public route generates, seals, and executes the customer model may production retirement begin.
Tests, probes, snapshots, and documentation are separate review surfaces, not collateral inside a
production deletion phase.

### Critical path

```text
external byte archive
  -> paired forensic snapshot commits
  -> clean Item 6 rebuild worktrees
  -> one executable recovery plan + measured Item 6 baseline
  -> pinned rebuild/TEAx environment + supported mutation protocol
  -> kept public acceptance tests
  -> v6 vertical route
  -> exact public graph route
  -> coordinated compiler/constraint route
  -> Fusion Tea generation + real TEAx execution
  -> public authority switch
  -> reviewed production retirement in small groups
  -> reviewed test/probe/snapshot dispositions
  -> subject-specific documentation
  -> repeatable corpus + scale + TEAx candidate
  -> independent audit
  -> OWNER ACCEPT/REVISE STOP
```

### First proof point

In the clean rebuild worktree, a kept public acceptance test must run the same maintained fixture
through the certified Item 6 route and the rebuilt v6 route, including relocation and package
generation, and compare modeled public inputs, modules, wiring, outputs, and execution result. The
original Item 6 tests and reference documents must still be present. Do not begin authority
switching or deletion until this passes.

### Overall validation

- Record a baseline test inventory and node count from clean Item 6 before importing code.
- Add kept, oracle-independent public behavior tests before each implementation slice.
- Use a recovery-only comparator for old/new differences while both implementations exist. Its
  output informs review; production behavior must not depend on the old result.
- Run the original maintained suites after every slice. Explain every count change.
- Run real TEAx before the public authority switch, after the switch, and after production deletion.
- Require a clean status and a recorded commit before starting the next slice.

## Progress

- [x] Phase 1 — Preserve the incident and create paired forensic snapshot commits
- [x] Phase 2 — Create clean rebuild worktrees, correct the Item 7 plan, and measure Item 6
- [ ] Phase 3 — Rebuild and commit the cutover as functional vertical slices
- [ ] Phase 4 — Retire production, tests/probes/snapshots, and docs under separate gates
- [ ] Phase 5 — Assemble a repeatable candidate, audit it, and stop for owner acceptance

---

## Phase 1 — Preserve the Incident

### Goal

Make the current mixed state recoverable without altering either original branch reference. Preserve
tracked changes, untracked files, raw logs, the temporary Phase 8 candidate, repository metadata,
and content hashes. Then commit the repository-resident state to paired local forensic branches
that are explicitly not merge candidates.

### Assumption under test

The complete incident can be represented by verified external archives plus one local commit per
repository, while `source-identity-epic` and `elaborate-first-salvage` remain at their Item 6 OIDs.

### Test stencil — write this first

```bash
assert current_heads_match_recorded_item6_heads
archive tracked_binary_diffs untracked_files raw_logs temp_candidate
write sha256_manifest
verify_every_archive_member_and_digest
assert original_branch_refs_unchanged
assert forensic_commits_reproduce_recorded_status_content
```

### Changes required

- [x] Create the external archive directory at `/home/reid/1cfe/item7-recovery-archive/`
  **[OWNER 2026-08-10]** — durable, outside both repositories and outside OS-temp, because the
  archive is the safety net the whole recovery depends on and `/tmp` does not survive a reboot.
  Record the final absolute path in this plan before any Git mutation.
- [x] Save `git status --porcelain=v1 -z`, `git diff --binary`, HEAD/branch/worktree listings, and
  SHA-256 manifests for both repositories.
- [x] Archive every untracked file separately from the tracked patch. Include ignored/untracked
  orchestration logs deliberately; do not rely on `git add -A` to discover them.
- [x] Archive `/tmp/elaborator-cutover-item7-candidate` and the recovery handoff if present. Record
  missing temp artifacts honestly instead of recreating them. Also archive the independent
  forensic TEAx outputs named by the incident report while those OS-temp paths survive.
- [x] Create `item7-forensic-20260810` from the current HEAD in each repository while carrying the
  dirty state. Verify the original branch refs before committing.
- [x] Commit the repository-resident candidate on each forensic branch with message
  `FORENSIC SNAPSHOT: failed Item 7 candidate; do not merge`.
- [x] Exclude `.orchestrate-logs/` and OS-temp artifacts from product commits; they remain in the
  verified external archive.
- [x] After the external manifest verifies, move any repository-local untracked orchestration logs
  into the archive so the original directories can become clean without `git clean` or deletion.
- [x] Switch the two original directories back to `source-identity-epic` and
  `elaborate-first-salvage` after the forensic commits exist. Verify both directories are clean at
  their recorded Item 6 OIDs. From this point forward, the dirty incident exists only in the
  forensic commits and verified external archive.
- [x] Record both forensic commit OIDs and the archive manifest digest in this plan.

If normal commit hooks reject the intentionally failed candidate, the two `FORENSIC SNAPSHOT`
commits may use `--no-verify` **[OWNER 2026-08-10 pre-authorization]**; record the bypass in this
plan if used. Every other commit in this recovery must pass hooks normally.

### Validation

**Automated**

- [x] Recompute every archive SHA-256 and compare it with the manifest.
- [x] `git diff <forensic-commit>^ <forensic-commit>` reproduces the tracked incident diff in each
  repository.
- [x] `git status --porcelain` is empty on both forensic branches after the intended exclusions are
  accounted for.
- [x] `git rev-parse source-identity-epic` remains
  `1672c5766f67e7716f3c9f8f636c21e2ea444601`.
- [x] `git rev-parse elaborate-first-salvage` remains
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`.
- [x] The original sysml-codegen and agentic-mbse directories are checked out on those two Item 6
  branches and have empty `git status --porcelain` output.

**Manual**

- [x] Open representative archived files: one modified production file, one deleted test recovered
  from the patch, one untracked Item 7 test, one corrupted reference doc, one raw log, and the
  failed candidate record.
- [x] Confirm both forensic commits are local and unpushed.

**What we know works after this phase**

The incident is recoverable by content hash, the bad and good changes can be inspected through Git,
and clean development can proceed without destructive cleanup of the original directories.

### Commit gate

Phase 1 itself creates only the two labeled forensic commits. Record:

- sysml-codegen forensic OID: `07531e64ed912d6046afce47ef0d958605e6ca08`
- agentic-mbse forensic OID: `ed5b8b02a3064e767799cc6ee58e0119e9bfecba`
- external archive path and manifest SHA-256: `/home/reid/1cfe/item7-recovery-archive` / `26bdc230df583f4c444621369931ecaca3e7c6bb24a469d0858606d36c1c819c`

---

## Phase 2 — Establish Clean Recovery Authority and Baseline

### Goal

Create clean rebuild worktrees from the unchanged Item 6 branches, re-establish the real baseline,
resolve the B37-01 premise, and commit corrected project artifacts before production changes.

### Assumption under test

The certified Item 6 commits remain buildable and contain the full pre-cutover functional evidence.
The recovery can distinguish an Item 7 regression from an incorrect expected-outcome ledger by
running the clean baseline rather than trusting the failed candidate.

### Test stencil — write this first

```python
def test_recovery_baseline_is_measured_not_assumed():
    baseline = run_clean_item6_public_corpus()
    assert baseline.full_suite_inventory == recorded_fresh_inventory()
    assert baseline.fusion_tea_public_result == hand_checked_result()
    assert b37_evidence_traces_fixture_to_item5_change_and_legacy_ledger()
    assert baseline.reference_docs_are_subject_specific()
```

### Changes required

- [x] Create `/home/reid/1cfe/sysml-codegen-item7-rebuild` on new branch `item7-rebuild` from
  `source-identity-epic`.
- [x] Create `/home/reid/1cfe/agentic-mbse-item7-rebuild` on new branch `item7-rebuild` from
  `elaborate-first-salvage`.
- [x] Create a task-specific rebuild environment. Install agentic-mbse editable from
  `/home/reid/1cfe/agentic-mbse-item7-rebuild`, sysml-codegen editable from
  `/home/reid/1cfe/sysml-codegen-item7-rebuild`, and the pinned TEAx checkout into that same
  environment. Assert the imported package paths resolve into those exact worktrees. Never let the
  rebuild silently import `/home/reid/1cfe/agentic-mbse`.
- [x] Create `.project/active/cutover-recovery/evidence/baseline.json` with exact heads, environment,
  suite collection/pass counts, test path inventory, reference-doc hashes, corpus outcomes, and
  real public Fusion Tea result available at Item 6.
- [x] Restore this recovery plan and the two forensic research records from the forensic commit
  into the clean rebuild. Restore the Item 7 spec, design, census, inventory, and original plan only
  as shaping and incident evidence. Do not restore Phase 7 completion checkboxes or the unreviewed
  status report as authority.
- [x] Put a prominent banner at the top of
  `.project/active/elaborator-cutover/plan.md`: `Superseded for execution by
  .project/active/cutover-recovery/plan.md; retained as shaping and census evidence.` Do not amend
  the old plan into a second executable recovery plan.
- [x] Verify the existing B37-01 evidence on the clean baseline: the fixture deliberately contains
  `sum(module.cost) + 5.0` in `tests/fixtures/agg_literal_probe/library.sysml`; Item 5 commit
  `483443e` deliberately added computed-calculation handling; the fixture header says the literal
  is meant to be observed; and the row in
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md` came from the legacy
  pre-elaboration `calc def` check. **[OWNER 2026-08-10] Pre-ruling: modeled aggregation is
  accepted as executable.** Phase 2 still re-verifies the evidence above on the clean baseline;
  if the evidence diverges from what is recorded here, stop and surface instead of applying the
  ruling. With the ruling applied, amend the ledger/spec/census rows, restore the literal-bearing
  aggregation test, and create a genuinely empty control. Do not restart the investigation or pick
  `14/22/1` versus `15/22/0` because one count is already written down.
- [x] Resolve the supported C25/C2 mutation protocol before Slice 3D. Use a supported runtime
  override, regenerate from an approved changed model/input, or define an explicit mutable-input
  contract. Editing a sealed generated input and asking the seal command to bless it is invalid.
  **[OWNER 2026-08-10]** Decision delegated: Phase 2 investigates what the seal contract and TEAx
  actually support, picks the soundest route, and records the decision and rationale here. Ping
  the owner only if every route would weaken package integrity.

  **Decision (Phase 2, delegated authority): mutate at runtime through TEAx's typed entry
  injection. Never touch sealed bytes. No owner escalation needed — a supported route exists that
  keeps package integrity fully intact.**

  What the seal actually covers (measured, not assumed). `seal_package`
  (`src/sysml_codegen/contracts/seal.py:93-122`) hashes every file under the package root under a
  *deny*-list policy that excludes only `contracts/package_contract.json` and `__pycache__`
  (`seal.py:18-21`). So **`inputs/*.json` is inside the sealed set** — confirmed against a real
  sealed package contract in the TEAx fixtures. The reserved un-sealed escape hatch,
  `runtime_output_globs`, is empty everywhere and documented as "empty until Item 10"
  (`contracts/models.py:93,112`), so there is no mutable-input carve-out to define today.

  The invalid route is already blocked in code, not merely by policy. `check_reseal_provenance`
  (`contracts/manifest.py:99-105`) refuses a re-seal of any changed codegen-produced file; only
  `handwritten/**` may change across a re-seal. Editing an input JSON and re-sealing raises
  `ProvenanceError`. Confirming this closes the plan's stated invalid route by construction.

  **Chosen route — runtime typed-entry injection (TEAx side).** `PreparedEvaluator.evaluate(
  typed_inputs)` (`teax/packages/teax-simkit/simkit/evaluation/evaluator.py:171`) replaces only the
  file-backed entry *loading* step; the package is loaded and seal-verified normally
  (`evaluator.py:130`) and nothing on disk is written. For a field-keyed map — which is the natural
  shape for C25 availability and C2 thermal efficiency — `CandidateBridge.build(selected_fields)`
  (`simkit/study/bridge.py:50`) routes each entry-model field (PQN) to its owning channel and fills
  the remainder from the modeled defaults. A declarative equivalent exists as `teax-study --config`
  with `grid`/`fixed` keys (`simkit/study/config.py:47-59`), which lives in an un-sealed YAML file
  *outside* the package. `MappingEntrySource.validate` (`simkit/evaluation/entry_source.py:41`)
  fails closed on missing, extra, or mistyped channels, so "every-and-only" mutation sets are
  checkable rather than assumed.

  Rationale for preferring it over regeneration: it mutates *the very package that was sealed and
  verified*, so the LCOE/C25/C2 assertions and the integrity proof are about one artifact. It is
  also the only route that keeps the seal an active check during the mutation test instead of a
  step performed before it.

  **Secondary route — regeneration, for modeled changes only.** Editing the source model or a copy
  of the snapshot's `literal_value` and re-running `run_codegen` produces a freshly and honestly
  sealed package (generation is deterministic; no timestamps enter sealed artifacts). Use this only
  when the claim under test is that a *modeled* change propagates through extraction → generation.
  It is not a substitute for runtime mutation, because it yields a different
  `executable_fingerprint` — a different package, not a mutated one.

  **Trap this decision closes for Slice 3D.** The Item 6 in-repo runner
  `tests/runtime/pipeline_runner.py` accepts `inputs={...}` (`:165-183`) and is what
  `test_gain_perturbation_is_consumed` uses. That runner installs a **fake `simkit`**
  (`_install_simkit_stub`, `:28-99`) and its `inputs=` argument has no counterpart in the real
  `simkit.core.pipeline.execute_pipeline`, which takes no overrides parameter. Slice 3D's "no
  monkeypatch or private runner counts" rule therefore forbids reusing it: the real-TEAx mutation
  test must go through `PreparedEvaluator` / `CandidateBridge`. Porting the hand-arithmetic
  assertions onto the real evaluator is 3D work, and no existing test in either repository yet
  mutates a value and observes the result through real TEAx.
- [x] Update `.project/CURRENT_WORK.md` to name recovery as active only after the owner approves the
  corrected plan.

### Validation

**Automated**

- [x] Run the full clean sysml-codegen suite and record collection, pass, skip, and deselection
  counts. Treat prior reported counts as comparison data, not the expected answer.
- [x] Run the full clean agentic-mbse suite and record the same facts.
- [x] Run the clean Item 6 37-path comparator or reconstruct it from the certified Item 5/6
  artifacts if it is not callable at HEAD.
- [x] Any 37-path driver used here must classify readiness `ElaborationError.findings` and
  validation `ElaborationDiagnosticError.diagnostics` separately and compare exact diagnostic
  multisets. This rule applies even if the clean baseline happens to exercise only one class.
- [x] Run the clean public Fusion Tea generation/execution path that exists at Item 6. Record any
  environmental limitation explicitly.
- [x] Derive the 22 incident-modified paths under `docs/architecture/` from the forensic diff. Hash
  all architecture docs at the Item 6 baseline and reject unexplained identical-content groups.
- [x] Review the forensic `CLAUDE.md` diff separately and record `restore` or `accept with exact
  edits`; do not let the architecture-doc disposition decide it implicitly.
- [x] `git diff --cached --name-only` for the planning commit contains only `.project/**`.

**Manual**

- [x] Review the corrected critical path, test-retirement rules, doc rules, and commit rules with
  the owner. Satisfied at the 2026-08-10 execution-approval Align: the owner approved this plan
  for execution with the recorded amendments (durable archive path, per-slice audits, B37-01
  pre-ruling, C25/C2 delegation, Gate 4A delegation, forensic-commit hook pre-authorization).
- [x] Review B37-01's baseline outcome and decide whether the ledger or implementation owns the
  correction.

**What we know works after this phase**

Recovery has clean, measured starting points; the expected product behavior is explicit; and the
project plan can be reviewed independently of implementation.

### Commit gate

Commit the approved recovery and corrected Item 7 project artifacts before production work.

- sysml-codegen planning OID: `4e6a1167d10a36288cc4bcbc051b5448445c9516` on branch
  `item7-rebuild`. 25 staged paths, every one under `.project/**`, verified with
  `git diff --cached --name-only`. Commit hooks passed; no bypass was used or authorized.
- agentic-mbse planning OID, if project metadata changes there: `N/A` — no project metadata
  changed in that repository during Phase 2. Its rebuild worktree is clean at
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`.

---

## Phase 3 — Rebuild as Functional Vertical Slices

### Goal

Recover or reimplement useful Item 7 work in small commits. Keep the old route, original tests,
spikes, snapshots, and docs available until the new public route has passed the full corpus and real
TEAx. The old route is a recovery oracle only; it must not become a second shipped authority.

### Assumption under test

The sound parts of the failed candidate can be isolated by behavior and imported without also
importing its deletion decisions, corrupted docs, or weakened test surface.

### Test stencil — write this first

```python
@pytest.mark.parametrize("route", ["live", "v6", "relocated_v6"])
def test_public_vertical_slice(route, real_teax):
    package = generate_public_package(route, maintained_model())
    verify_and_seal(package)
    result = real_teax.execute(package)
    assert_public_inputs_modules_wiring_and_outputs(result)
    assert result == hand_checked_product_result()
```

### Recovery import rule

Use the forensic phase-to-file map as a review accelerator. Most dirty-tree entries have one phase
owner and can take the fast path through the relevant slice. That provenance makes them easier to
review; it does not prove correctness. The 28 files touched by multiple phases, especially
`orchestration/pipeline_builder.py` and `elaboration/project.py`, require per-hunk review or clean
reimplementation.

For each slice, declare one of three dispositions per hunk:

- **Reuse:** the hunk is understandable, independently tested, and applies cleanly.
- **Reimplement:** the idea is sound but the final hunk is entangled with later deletion.
- **Reject:** the hunk weakens evidence, deletes unrelated material, reconstructs identity, or
  changes product behavior without authority.

Record the disposition in the slice's completion notes. Never import an entire modified file only
because it exists on the forensic branch.

### Test import rule

The forensic test audit is the starting shortlist, not a certification result.

- Fast-track the functional candidates through normal red/green review:
  `tests/unit/test_source_admission.py`, `tests/conformance/test_cutover_c19.py`,
  `tests/conformance/test_fusion_tea_cutover.py`,
  `tests/conformance/test_snapshot_v6_routes.py`, and
  `tests/conformance/test_exact_compiler_core.py`. Preserve the migrated hand-arithmetic oracle at
  `tests/runtime/test_fusion_tea_acceptance.py` throughout recovery.
- Reject `tests/conformance/test_cutover_manifest.py` as written because it builds its candidate
  from the manifest it claims to verify.
- Reject `tests/execution/test_fusion_tea_item7_budget.py` and
  `tests/execution/test_fusion_tea_item7_real_teax.py` as written because they assert `is True` on a
  script's self-report. Replacement tests must assert real outputs and must run in the acceptance
  command rather than being silently deselected.
- Reject `tests/conformance/test_cutover_no_legacy_residue.py` as a deletion-certification gate in
  its present form. Absence scanning may remain a supplementary residue check only after the
  Git-derived inventory and executable replacement gate exist.

### Slice 3A — V6 envelope and source admission

- [ ] Write kept live/v6/relocated public behavior tests first.
- [ ] Review and selectively recover `snapshot/{envelope,source_manifest,instance_graph,capture}.py`
  plus the minimum live/load integration.
- [ ] Preserve v5 production and tests during this slice.
- [ ] Pin the complete v6 envelope matrix: missing/current/future versions; missing, added, and
  wrong-typed outer fields; graph replacement; `model_name` and `captured_at` skew; ordinary inner
  tamper; and a valid inner graph inside a tampered outer envelope. The loader must reject a
  re-sealed model-identity swap, which the failed candidate currently accepts.
- [ ] Run original full suites, the named relocation/tamper matrix, and one generated package
  smoke.
- [ ] Commit only the declared 3A path set.

### Slice 3B — Defensive context and exact public projection

- [ ] Write kept public selection, receipt, mutation, aggregation, and route-equality tests first.
- [ ] Selectively recover `orchestration/{pipeline_context,pipeline_builder,snapshot_context}.py`
  and `elaboration/project.py` changes without deleting the old builder or registry.
- [ ] Run both old/new recovery comparison and oracle-independent public assertions.
- [ ] Run original full suites and commit only the declared 3B path set.

### Slice 3C — Coordinated compiler and constraint authority

- [ ] Write collision, declaration-identity, ordering, and profile behavior tests first in both
  repositories.
- [ ] Selectively recover the exact compiler/constraint changes from sysml-codegen and
  agentic-mbse. Retain the old route until the coordinated new route is proven.
- [ ] Run both full suites from the exact paired worktrees.
- [ ] Commit both repositories and record the paired OIDs together.

### Slice 3D — Fusion Tea customer vertical and real TEAx

- [ ] Write the real TEAx test first. It must load/extract, generate, verify, seal, discover, and
  execute through public APIs.
- [ ] Pin hand arithmetic and the owner-relevant behaviors: LCOE, C25 availability, C2 thermal
  efficiency, C19's 80.0 on both consumer paths, and every-and-only mutation sets.
- [ ] Use the independent forensic baseline as a target to re-prove, not as accepted authority:
  11 outputs, live/relocated equality, and LCOE `270.1211779380445`.
- [ ] Review each proposed Fusion Tea model rename against the exact fifteen-item ledger. Preserve
  equations, defaults, topology, and physics.
- [ ] Run the full 37-path comparison while both implementations remain available.
- [ ] Make every corpus driver handle both readiness `ElaborationError` (`.findings`) and
  validation `ElaborationDiagnosticError` (`.diagnostics`). Assert the exact diagnostic multiset;
  never collapse either class into `unexpected-error`.
- [ ] Run real TEAx on live and relocated v6 packages. No monkeypatch or private runner counts.
- [ ] Run those tests in the pinned shared acceptance environment so SimKit, Jinja2, codegen, and
  the rebuild agentic-mbse checkout are all present. Exercise the owner-approved mutation protocol;
  never edit bytes after sealing and then reseal them as proof.
- [ ] Commit the exact 3D model, test, and required production paths.

### Slice 3E — Public authority switch

- [ ] Write public import/CLI tests proving all supported callers use the exact route and no public
  flag exposes two authorities.
- [ ] Switch public callers without deleting the unreachable legacy implementation.
- [ ] Repeat the full corpus, original suites, generated package comparison, and real TEAx.
- [ ] Commit the authority switch separately from all deletion.

### Validation for every Phase 3 slice

**Automated**

- [ ] Start from clean status and record the declared path set.
- [ ] Run slice-focused tests red before production changes and green afterward.
- [ ] Run the original full suites; record and explain collection-count deltas.
- [ ] Run Ruff, mypy baseline comparison, and `git diff --check` on both repositories as applicable.
- [ ] Assert actual changed paths are a subset of the declared path set.

**Manual**

- [ ] Inspect the complete slice diff before commit, including generated/deleted path summaries.
- [ ] Open at least one public generated artifact and compare it with the hand/model expectation.
- [ ] Confirm no docs, spikes, probes, unrelated tests, or snapshots changed accidentally.
- [ ] **[OWNER 2026-08-10]** After each slice commit, an independent audit agent (fresh session,
  not the implementer) reviews the slice diff, tests, and evidence against this plan's slice
  contract. Audit findings are resolved before the next slice begins.

**What we know works after this phase**

The new route has passed public behavior, full-corpus comparison, and real TEAx before any legacy
production owner or regression evidence is removed. Each functional increment is recoverable as a
green commit.

### Commit gate

Record every slice. Do not combine them later.

| Slice | sysml-codegen OID | agentic-mbse OID | Full suites | Real TEAx |
|---|---|---|---|---|
| 3A | PENDING | N/A | PENDING | smoke PENDING |
| 3B | PENDING | N/A | PENDING | smoke PENDING |
| 3C | PENDING | PENDING | PENDING | N/A |
| 3D | PENDING | PENDING if changed | PENDING | PENDING |
| 3E | PENDING | PENDING if changed | PENDING | PENDING |

---

## Phase 4 — Controlled Retirement and Documentation Repair

### Goal

Remove only the superseded production authorities proven unnecessary by Phase 3. Treat production
code, test responsibilities, historical probes, committed snapshots, and documentation as separate
decisions and separate commits.

### Assumption under test

With public callers already on the proven exact route, legacy production owners can be removed in
small groups without changing public behavior. Existing tests will reveal missing responsibilities
when they remain present long enough to do so.

### Test stencil — write this first

```python
@pytest.mark.parametrize("checkpoint", deletion_checkpoints())
def test_retirement_preserves_public_product(checkpoint, real_teax):
    before = load_signed_pre_deletion_evidence(checkpoint)
    after = run_public_corpus_and_execute(real_teax)
    assert after.semantic_results == before.semantic_results
    assert after.test_responsibilities == before.test_responsibilities
    assert checkpoint.unapproved_deleted_paths == []
```

### Gate 4A — Rebuild the responsibility/deletion ledger

- [ ] Start from the Item 6 path inventory, current Phase 3 tree, original tests, and actual public
  call graph. Import the 54 explicit `delete` rows as presumptively valid proposals because the
  forensic reconciliation found no execution surprises in that class. Recheck their authority,
  reachability, and replacement proof before approval. Re-derive every `migrate`, group-covered,
  and no-row disposition from scratch.
- [ ] Generate the candidate inventory from `git diff --name-status <item6-base>` plus untracked
  paths. Require exact equality between that Git-derived set and the reviewed disposition set.
- [ ] For every proposed production deletion, name the public behavior and kept test that prove its
  replacement.
- [ ] For every proposed test deletion or rewrite, state the behavior responsibility, replacement
  node, and why keeping the old test is impossible or misleading.
- [ ] Implement and test `replacement_is_green(row)`: every deleted or migrated test row names an
  exact replacement node that exists, collects, and passes in the required suite. Add negative
  tests for a missing node, a deselected node, and a failing node. Absence-only checks cannot make
  this gate green.
- [ ] Present the exact production, test, snapshot, probe, and doc lists to the owner. No broad
  catch-all rows.
- [ ] Commit the approved ledger before deletion.

### Gate 4B — Delete legacy production in small groups

- [ ] Delete one coherent production owner group at a time, beginning with unreachable adapters and
  ending with the central legacy resolver/registry/snapshot owners.
- [ ] Before each group, add or identify kept public tests that fail if its responsibility is lost.
- [ ] Run the complete public corpus and real TEAx after each group.
- [ ] Commit each deletion group separately. Do not include tests, docs, snapshots, or probes except
  an already-approved test migration necessary for that exact group.

### Gate 4C — Review tests, probes, and snapshots

- [ ] Preserve all tests by default. Rewrite useful mechanism tests against public behavior before
  considering deletion.
- [ ] Restore or replace the known lost product responsibilities before deleting their old owners:
  real constraint verdict execution, customer E2E, full generated-package structure and schemas,
  live-vs-snapshot byte identity where still required, Gate-B missing-input reconciliation,
  smart-regeneration preservation, shared-producer/D39 behavior, and literal-bearing aggregation.
- [ ] Require an owner-reviewed disposition for every remaining deleted test path. Record the
  collected-node delta and behavior replacement.
- [ ] Preserve spikes/probes by default. If they no longer run, archive them with their findings or
  fix their entry point; do not erase history merely to satisfy a residue scan.
- [ ] Treat v5 runtime rejection, committed historical snapshots, and new v6 accepted snapshots as
  separate decisions. Keep the 14 runtime v5 snapshots until their accepted v6 replacements are
  ready in the same candidate. B37 may change that replacement count only through the Phase 2
  owner ruling. Do not delete all stored evidence simply because v5 is not callable.
- [ ] Commit each approved family separately.

### Gate 4D — Restore and rewrite documentation

- [ ] Restore all 22 incident-modified files under `docs/architecture/` from the clean Item 6 base
  before writing new content. This set includes 20 reference documents plus
  `docs/architecture/overview.md` and `docs/architecture/verification-matrix.md`. Do not rewrite the
  11 untouched reference documents merely to make the set uniform.
- [ ] Build a subject-by-subject update list that states which claims became stale and which new
  public behavior replaces them.
- [ ] Update one coherent documentation subject per commit. Preserve subject-specific requirements,
  rationale, examples, and cross-links.
- [ ] Add a check rejecting identical full-file content across distinct numbered reference docs,
  except an explicit allowlist that should normally be empty.
- [ ] Review rendered/readable content manually; residue scans are secondary.
- [ ] Give `CLAUDE.md` its own reviewed disposition and commit. Restore it first if any Item 7 claim
  is not yet true, then apply only narrow changes that match the accepted final architecture.

### Validation

**Automated**

- [ ] Run full suites, public 37-path corpus, and real TEAx after each production deletion group.
- [ ] Compare collected test paths and counts with the Phase 2 baseline and approved ledger.
- [ ] Require zero unexplained deleted paths in `git diff --name-status`.
- [ ] Require all public behavior results equal to the signed Phase 3E evidence.
- [ ] Hash all files under `docs/architecture/` and reject the generic-content collapse seen in the
  failed candidate.
- [ ] Confirm the verification matrix and overview retain their subject-specific traceability and
  architecture content; a reference-only glob is not a complete documentation gate.

**Manual**

- [ ] Owner reviews the ledger before 4B and every remaining test/probe/snapshot deletion before 4C.
- [ ] Read every changed architecture document, including the overview and verification matrix, as
  its own subject.

**What we know works after this phase**

The product has one production authority, regression coverage remains behaviorally accounted for,
historical evidence was not erased by default, and documentation describes the actual architecture
without generic replacement text.

### Commit gate

Record one OID per deletion group, test/probe/snapshot family, and documentation subject. A dirty
worktree or combined cross-category diff blocks Phase 5.

---

## Phase 5 — Repeatable Candidate, Independent Audit, and Owner Stop

### Goal

Prove the recovered cutover as a stable, reviewable two-repository candidate. The acceptance run is
repeatable during development; only the final owner-accepted evidence set becomes authoritative.

### Assumption under test

The progressively committed rebuild produces stable public results, contains no hidden legacy
authority, retains justified regression coverage, and can be reviewed without relying on the failed
candidate or self-reported phase notes.

### Test stencil — write this first

```python
def test_final_candidate_is_repeatable_and_executable(real_teax):
    runs = [run_full_candidate(real_teax) for _ in range(3)]
    assert all(run.corpus_outcomes == approved_ledger for run in runs)
    assert all(run.public_results == hand_checked_results for run in runs)
    assert all(run.performance.within_budget for run in runs)
    assert explained_test_delta(runs[-1].test_inventory)
```

### Changes required

- [ ] Build a fresh candidate record binding both repository OIDs, exact diffs, path inventories,
  test inventories, corpus outcomes, environment, real TEAx revision, performance, and evidence
  hashes.
- [ ] Run the complete 37-path corpus repeatedly. Expected outcomes come from the Phase 2 owner-
  reviewed ledger, not the failed candidate's automatic recapture.
- [ ] In every run, classify both `ElaborationError.findings` and
  `ElaborationDiagnosticError.diagnostics` and compare their exact multisets with the approved
  ledger.
- [ ] Run live and relocated v6 generation, verification, sealing, registry discovery, and real
  TEAx execution.
- [ ] Run warm-up plus repeated scale measurements with declared budgets and environment.
- [ ] Run both complete repository suites, lint, type-baseline comparison, diff checks, import
  boundaries, no-residue checks, documentation checks, and test-inventory reconciliation.
- [ ] Run `$my-audit` with the forensic branch, clean Item 6 baseline, corrected plan, commit series,
  and final candidate all available to the auditor.
- [ ] Stop for explicit owner accept/revise disposition. Do not commit evidence materialization,
  tag, push, promote, or release from this plan.

### Validation

**Automated**

- [ ] Three consecutive complete runs produce identical semantic results and approved outcomes.
- [ ] Both real TEAx tests pass with no skip, xfail, monkeypatch, or private compatibility runner.
- [ ] Every test-count/path delta from Item 6 is explained by the approved responsibility ledger.
- [ ] No unapproved deleted path, generic reference doc, v5 callable route, legacy public authority,
  or forensic-branch import remains.
- [ ] Each repository is clean at its recorded candidate OID.

**Manual**

- [ ] Independent audit reads code and runs checks rather than trusting implementation notes.
- [ ] Owner reviews the commit series, functional evidence, deletions, test delta, docs, and audit.

**What we know works after this phase**

Item 7 is either a reviewable, executable candidate with a trustworthy regression story, or it has
a precise failing gate attached to one small commit or assumption. No ambiguous 327-file dirty tree
remains.

### Owner gate

- Owner disposition: `PENDING`
- Final sysml-codegen candidate OID: `PENDING`
- Final agentic-mbse candidate OID: `PENDING`
- Audit artifact: `PENDING`

---

## Environment Setup

Use the commands and dependency rules in `CLAUDE.md`. Before every session, record:

```bash
git -C /home/reid/1cfe/sysml-codegen-item7-rebuild status --short --branch
git -C /home/reid/1cfe/sysml-codegen-item7-rebuild rev-parse HEAD
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild status --short --branch
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild rev-parse HEAD
git -C /home/reid/1cfe/teax status --short --branch
git -C /home/reid/1cfe/teax rev-parse HEAD
```

Use one task-specific acceptance environment for the paired rebuild. Its editable sources must be
the two `*-item7-rebuild` worktrees, plus the pinned TEAx checkout. Install all declared codegen and
TEAx dependencies into that environment; do not borrow TEAx's existing interpreter and assume it
contains Jinja2. At session start, print and record the resolved import locations for
`sysml_codegen`, `agentic_mbse`, and SimKit. Fail setup if any import resolves to an original or
forensic worktree.

Do not install from or point editable dependencies at the frozen forensic worktrees.

## Risk Management

- **Mixed candidate cannot be split faithfully:** preserve it first, then reimplement entangled
  hunks. Do not manufacture historical phase commits.
- **Green suite after coverage deletion:** compare collected test paths against the measured Item 6
  inventory and require a reviewed responsibility disposition for every delta.
- **Differential test blesses old bugs:** keep hand/model-derived public assertions. Old/new
  comparison detects change but does not define correctness.
- **One-authority rule blocks safe comparison:** keep both implementations only on unreleasable
  rebuild branches. The final public route has one authority; the old code remains available in Git
  history and forensic worktrees.
- **Cross-repository skew:** commit coordinated slices in both repositories, record paired OIDs, and
  run both suites from that exact pair.
- **Editable-install skew:** one explicit rebuild environment points at the two rebuild worktrees;
  record resolved import paths in every acceptance record.
- **Harness self-certifies:** assert package outputs and diagnostic multisets directly. Do not
  accept boolean script self-reports or a manifest generated from the expected manifest.
- **Temporary evidence disappears:** archive and hash it in Phase 1 before relying on it.
- **Documentation passes residue scans while losing meaning:** restore from Item 6, update by
  subject, and read every changed document.
- **Recovery plan becomes another unchecked authority:** require owner review before Phase 1 Git
  mutations and independent audit before acceptance.

## Implementation Notes

Fill these during execution. Amend incorrect content rather than appending contradictory status.

### Phase 1 Completion

- **Completed:** 2026-08-10
- **Commits/archive:**
  - External archive: `/home/reid/1cfe/item7-recovery-archive/` **[OWNER 2026-08-10 durable path]**
  - Archive manifest: `MANIFEST.sha256`, SHA-256 `26bdc230df583f4c444621369931ecaca3e7c6bb24a469d0858606d36c1c819c`, 2198 members, all digests re-verified.
  - Pre-mutation manifest: `MANIFEST-premutation.sha256`, SHA-256 `557c551dc285dbc1ccf07c68530283978c7a13f43edf009c7ffc73d264dd782d`, 2126 members, computed and verified before any Git mutation.
  - sysml-codegen forensic OID: `07531e64ed912d6046afce47ef0d958605e6ca08` on branch `item7-forensic-20260810` (parent `1672c576`), 105 M + 222 D + 47 A.
  - agentic-mbse forensic OID: `ed5b8b02a3064e767799cc6ee58e0119e9bfecba` on branch `item7-forensic-20260810` (parent `5088b417`), 15 M.
  - Both forensic commits are local and unpushed. Neither used `--no-verify`; hooks accepted both, so the owner pre-authorization was not exercised.
  - Original refs unchanged and verified: `source-identity-epic` = `1672c5766f67e7716f3c9f8f636c21e2ea444601`, `elaborate-first-salvage` = `5088b417c9e5453271291d46cd5fb23fc0579b1e`. Both original directories are checked out on those branches with empty `git status --porcelain`.

- **Issues/deviations:**
  - The `git diff --binary` patches were verified by `git apply --check --reverse` against the live worktrees before any mutation. This is stronger than a name-list comparison: it proves each archived patch is an exact byte representation of the pre-mutation tracked state.
  - `.orchestrate-logs/` in sysml-codegen is gitignored, so the worktree was already clean with it present. It was archived and digest-verified (1374 files) but left in place, because moving it is unnecessary for cleanliness and it carries pre-incident orchestration history still being written to. The agentic-mbse copy is untracked-but-not-ignored and was genuinely moved into `moved-from-repos/` so that repository could reach clean status without `git clean`.
  - Two manifests exist for that reason. The moved tree was confirmed byte-identical (`diff -rq`) to the archived copy, so the second manifest covers a duplicate, not new content.
  - The untracked count is 30 porcelain entries rather than the forensics' 27. The three extra are the recovery artifacts written after the forensics run: `.project/active/cutover-recovery/` and the two `.project/research/2026081*-item7-cutover-*.md` records. Expected, not a divergence.
  - Because `.project/active/cutover-recovery/` was untracked, it was committed to the forensic branch and removed from the original worktree on switching back. The Phase 1 OIDs therefore could not be written into the plan in place; they are recorded in `/home/reid/1cfe/item7-recovery-archive/phase1-results.json`. Phase 2 restores the plan into the rebuild worktree and writes these values into it.
  - No other deviation. All automated and manual Phase 1 validations passed.

### Phase 2 Completion

- **Completed:** 2026-08-10

- **Worktrees and environment:**
  - `/home/reid/1cfe/sysml-codegen-item7-rebuild`, branch `item7-rebuild`, from
    `source-identity-epic` @ `1672c5766f67e7716f3c9f8f636c21e2ea444601`.
  - `/home/reid/1cfe/agentic-mbse-item7-rebuild`, branch `item7-rebuild`, from
    `elaborate-first-salvage` @ `5088b417c9e5453271291d46cd5fb23fc0579b1e`.
  - Pinned TEAx `/home/reid/1cfe/teax` @ `fa0e06a99b070346e68a3b3c29cfec546f3ac728` (`main`, clean).
  - One task-specific venv at `/home/reid/1cfe/item7-rebuild-venv`. Resolved import paths, all
    inside the rebuild worktrees: `sysml_codegen` →
    `/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py`; `agentic_mbse` →
    `/home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py`; SimKit →
    `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py`. Nothing resolves into an
    original or forensic worktree.

- **Measured baseline** (full detail in `evidence/baseline.json`):
  - sysml-codegen, licensed: **3358 passed / 47 skipped / 18 deselected**, 3423 collected across
    218 test files, zero failures, and **zero `no live syside license` skip lines**. This matches
    the Item 6 comparison data exactly.
  - agentic-mbse: **1819 passed / 1 skipped / 5 deselected**, 1825 collected across 67 test files,
    zero failures.
  - Execution lane (`pytest tests/execution -m execution`, the 18 deselected nodes): 18 passed.
  - 37-path corpus via `scripts/run_elaboration_corpus.py`: **37/37 outcomes reproduce the
    certified Item 5/6 ledger, zero mismatches.**
  - Fusion Tea: green, headline LCOE `270.1211779380445`, and the gain-perturbation test lands its
    independently hand-computed `216.55528392479388`.

- **Corpus error classification.** `ElaborationError` (`.findings`) and
  `ElaborationDiagnosticError` (`.diagnostics`) are disjoint classes, neither inheriting the other
  (`elaboration/elaborate.py:87` and `:100`), so each instance populates exactly one attribute. The
  driver records `error_type` beside the code list and never collapses either class into
  `unexpected-error`, which makes `error_type` + codes lossless. This baseline exercises
  `ElaborationError` (23 fixtures) and `CodeGenerationError` (2); `ElaborationDiagnosticError` is
  not exercised. The separate-classification rule still binds every later driver.

- **Fusion Tea limits at Item 6.** Execution runs through the in-repo fixture runner
  `tests/runtime/pipeline_runner.py`, which installs a **fake** `simkit`
  (`_install_simkit_stub`). Generation is real and license-free from the committed v5 snapshot, but
  real TEAx seal/discovery/execution does not exist at this baseline; it is Slice 3D work.

- **B37-01: evidence matched on the clean baseline, so the owner pre-ruling was applied.** All four
  legs confirmed — the fixture literal `:>> total_cost = sum(module.cost) + 5.0;`
  (`tests/fixtures/agg_literal_probe/library.sysml:24`); Item 5 commit `483443e` deliberately
  converting a `:>>` expression redefinition into a computed calculation node; the fixture header
  declaring the literal must be observed; and the ledger row's recorded provenance. The decisive
  new measurement: **both routes raise the same pre-elaboration calc-def presence gate** (legacy
  `orchestration/pipeline_builder.py:885`, exact `orchestration/elaborated_pipeline.py:37`), so the
  elaborator is never reached and row 1 measured a front-gate, not aggregation semantics. **The
  ledger owned the correction, not the implementation.** Amended: the ledger row basis plus a new
  B37-01 ruling section (measured outcome cells left untouched, so the certified record stands and
  the three ledger tests remain green), the spec's non-R7 control claim, and the census rows —
  `B37-01` now requires a V6 graph with the `5.0` operand observed, and a new `B37-01c` row holds
  the empty-control responsibility. Carried to Phase 3/4: restore the literal-bearing aggregation
  test, build a genuinely empty control, and re-derive `14/22/1` vs `15/22/0` from those rather
  than preferring the count already written down.

- **C25/C2 mutation protocol: decided under delegated authority; no owner escalation needed.**
  Mutate at runtime through TEAx typed-entry injection (`PreparedEvaluator.evaluate(typed_inputs)`
  / `CandidateBridge.build(selected_fields)` / `teax-study` `grid`+`fixed`), which never writes to
  disk and keeps the seal an active check during the test. `inputs/*.json` is inside the sealed set
  (`contracts/seal.py:18-21`), and the invalid route is already refused in code by
  `check_reseal_provenance` (`contracts/manifest.py:99-105`). Regeneration is a sound secondary
  route for modeled changes only, since it yields a different `executable_fingerprint`. Full
  rationale is recorded against the Phase 2 changes-required item above.

- **Documentation.** The forensic diff names exactly 22 modified paths under `docs/architecture/`
  (20 reference documents plus `overview.md` and `verification-matrix.md`), matching the plan. At
  the Item 6 baseline all **34** architecture documents have distinct content — zero identical
  content groups, so the baseline passes. For contrast, on the forensic branch **21 of those 22
  collapsed into one identical 12-line generic stub** (`713ecf4c…`); the only modified document
  that is not the stub is `docs/architecture/reference/17-parameter-group-deriver.md`, and the stub
  reached no unmodified document. 31 reference documents exist, so 11 are untouched, matching the
  plan's Gate 4D note.

- **`CLAUDE.md`: RESTORE.** The rebuild worktree already carries the Item 6 content. The forensic
  diff is coherent and targeted rather than stub collapse, but every claim in it is false at this
  baseline: it names Elaboration and Projection as pipeline stages 2 and 3 while `analysis/` (9
  files) and `resolution/` (6 files) are the live shipped route, and it describes strict v6
  instance-graph envelopes while `SNAPSHOT_FORMAT_VERSION = 5` (`snapshot/__init__.py:30`). Its
  wording is a good starting point for Gate 4D once Phase 3E has made the claims true.

- **Issues/deviations:**
  - **F1 (low).** The agentic-mbse comparison figures `~1811/1/33` come from `CURRENT_WORK.md`'s
    Item 2 entry, measured at agentic-mbse `65a35d7`, not at this baseline. The passed delta is
    explained: `65a35d7..5088b417` adds 441 test insertions including a 188-line new test file, so
    +8 passing is correct. The deselect delta is **not** explained — both commits carry exactly 4
    `@pytest.mark.slow` functions and an identical `addopts`, which yields the 5 deselections
    measured, and `1811+1+33 = 1845` exceeds this commit's whole collection universe of 1825. Most
    likely a transcription error in the status note. Recorded rather than resolved silently. No
    impact on the baseline; the codegen suite matches its comparison data exactly.
  - **F2 (informational, and a trap for later phases).** `uv pip install -e <rebuild worktree>`
    silently reused a globally cached editable wheel for `agentic-mbse 0.1.2` built earlier from
    the **original** worktree, so `agentic_mbse` imported from `/home/reid/1cfe/agentic-mbse`. The
    plan's mandatory import-path assertion caught it; `--reinstall --no-cache` fixed it. Any phase
    that rebuilds this venv must re-assert import paths rather than trust a successful install.
    Without that assertion every paired-worktree measurement would have been quietly invalid.
  - **F3 (informational).** `python3 -m venv` is unusable on this host (`ensurepip` absent). Use
    `uv venv`.
  - **F4 (informational).** The agentic-mbse suite needs the `[web]` extra and its own venv `bin`
    on `PATH`; without them 28 tests fail on missing `trafilatura`/`PIL` or on shelling out to
    `agentic-mbse`/`python`. Environment shape, not regressions — with both fixed the suite is
    fully green.
  - No rule-10 premise conflict arose. The B37-01 evidence matched, the corpus reproduced the
    certified ledger exactly, and no unexplained product diff appeared.
  - The one Phase 2 validation box left unticked is the owner review of the corrected critical
    path, test-retirement rules, doc rules, and commit rules. It is an owner action and this phase
    ran non-interactively.

### Phase 3 Completion

- **Completed:** Pending
- **Slice commits and evidence:** Pending
- **Issues/deviations:** Pending

### Phase 4 Completion

- **Completed:** Pending
- **Retirement/doc commits and evidence:** Pending
- **Issues/deviations:** Pending

### Phase 5 Completion

- **Completed:** Pending
- **Candidate/audit/owner disposition:** Pending
- **Issues/deviations:** Pending

---

**Status:** Draft → Owner-approved → In progress → Audited → Owner accepted/revised
