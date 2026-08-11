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

- [x] Write kept live/v6/relocated public behavior tests first.
- [x] Review and selectively recover `snapshot/{envelope,instance_graph,capture}.py` and
  `extraction/source_manifest.py` plus the minimum live/load integration.
- [x] Preserve v5 production and tests during this slice.
- [x] Pin the complete v6 envelope matrix: missing/current/future versions; missing, added, and
  wrong-typed outer fields; graph replacement; `model_name` and `captured_at` skew; ordinary inner
  tamper; and a valid inner graph inside a tampered outer envelope. The loader must reject a
  re-sealed model-identity swap, which the failed candidate currently accepts. **Partially met, and
  the remainder is pinned rather than claimed.** `model_name`/`captured_at` re-labelling is refused.
  Re-labelling through the `sources` manifest is *not* refusable offline; it is refused when the
  caller supplies `source_roots`, and the three offline-accepted shapes are pinned as tests naming an
  accepted, documented limit. See "F1" in the 3A follow-up notes. **[AGENT] (orchestrator ruling,
  2026-08-10):** the residual limit is accepted for the rebuild. The plan's named must-fail cell
  (model-identity swap) is closed structurally; the residual is source-referent provenance, which
  no offline check of forger-controlled bytes can validate — mandating `source_roots` would break
  the relocated-snapshot route the cutover exists to support. Pinned tests + docstring state the
  truth, and the freshness path refuses all three shapes. Flagged for the Phase 5 owner review
  packet as a named residual, not silently absorbed.
- [x] Run original full suites, the named relocation/tamper matrix, and one generated package
  smoke.
- [x] Commit only the declared 3A path set.

### Slice 3B — Defensive context and exact public projection

- [x] Write kept public selection, receipt, mutation, aggregation, and route-equality tests first.
- [x] Selectively recover `orchestration/{pipeline_context,pipeline_builder,snapshot_context}.py`
  and `elaboration/project.py` changes without deleting the old builder or registry. **All three
  `orchestration/` files were Rejected as written** — each forensic hunk *replaces* a shipped
  authority. The recovered ideas (receipt-bound context, typed target selection) landed in a new
  `orchestration/exact_pipeline_context.py` beside them. See the 3B dispositions below.
- [x] Run both old/new recovery comparison and oracle-independent public assertions.
  Comparison: `evidence/3b-old-new-comparison.md`.
- [x] Run original full suites and commit only the declared 3B path set.
- [x] **[AGENT] (orchestrator ruling, 2026-08-11)** Group identity derives from the filename stem,
  with the `model.sysml` fallback moved from the parent directory to the declaring package of the
  owning root occurrence. Ruled as option (C) after the implementer stopped under rule 10: a
  package-wide rule would have retired the owner-ratified compatibility responsibility pinned by
  `test_parameter_group_name_drives_the_compatible_json_filename`. Under (C) no owner-ratified
  responsibility is retired. One residual is carried, named below: `d38_caret`.

### Slice 3C — Coordinated compiler and constraint authority

- [x] Write collision, declaration-identity, ordering, and profile behavior tests first in both
  repositories.
- [x] Selectively recover the exact compiler/constraint changes from sysml-codegen and
  agentic-mbse. Retain the old route until the coordinated new route is proven. **The forensic
  Phase-5 material turned out to be almost entirely rename-and-delete, not new behavior** — see
  the 3C completion notes. Every rename hunk was Rejected for this slice and recorded as a
  retained dual for Phase 4; the behavior the slice does recover is named per file below.
- [x] Run both full suites from the exact paired worktrees.
- [x] Commit both repositories and record the paired OIDs together.

### Slice 3D — Fusion Tea customer vertical and real TEAx

- [x] Write the real TEAx test first. It must load/extract, generate, verify, seal, discover, and
  execute through public APIs.
- [x] Pin hand arithmetic and the owner-relevant behaviors: LCOE, C25 availability, C2 thermal
  efficiency, C19's 80.0 on both consumer paths, and every-and-only mutation sets.
- [x] Use the independent forensic baseline as a target to re-prove, not as accepted authority:
  11 outputs, live/relocated equality, and LCOE `270.1211779380445`. All three re-proved
  independently; every number is compared against a hand transcription of the SysML
  (`tests/execution/fusion_tea_arithmetic.py`), never against the forensic record.
- [x] Review each proposed Fusion Tea model rename against the exact fifteen-item ledger. Preserve
  equations, defaults, topology, and physics. **All fifteen accepted; zero extra hunks** — see the
  rename review below, including the mechanical revert check.
- [x] Run the full 37-path comparison while both implementations remain available. **Measured
  15 public graphs / 22 typed errors on the exact route**; exactly one row moved versus the amended
  ledger, `fusion_tea`, which is the census obligation `B37-15`.
- [x] Make every corpus driver handle both readiness `ElaborationError` (`.findings`) and
  validation `ElaborationDiagnosticError` (`.diagnostics`). Assert the exact diagnostic multiset;
  never collapse either class into `unexpected-error`.
- [x] Run real TEAx on live and relocated v6 packages. No monkeypatch or private runner counts.
- [x] Run those tests in the pinned shared acceptance environment so SimKit, Jinja2, codegen, and
  the rebuild agentic-mbse checkout are all present. Exercise the owner-approved mutation protocol;
  never edit bytes after sealing and then reseal them as proof.
- [x] Commit the exact 3D model, test, and required production paths.

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
| 3A | fe0b855, audit follow-up 4858911 | N/A | 3473 passed / 47 skipped / 18 deselected (+115, all new) | smoke PASS (fusion_tea, 48-file sealed package) |
| 3B | d91431b, audit follow-up 2f28dde | N/A | 3520 passed / 47 skipped / 18 deselected (+47, all new) | smoke PASS (live + v6-snapshot packages, group names equal; legacy CLI package unchanged at 48 files) |
| 3C | 7af5dc9, audit follow-up a6c41bc | 8b63393, audit follow-up cc6c7a7 | codegen 3538 passed / 47 skipped / 18 deselected (+18, all new); agentic 1825 passed / 1 skipped / 5 deselected (+6, all new) | N/A |
| 3D | 848628b, audit follow-up PENDING_3D_FU | N/A (untouched, clean at `cc6c7a7`) | codegen 3539 passed / 47 skipped / 38 deselected (+1 passed, +20 deselected — all new); agentic 1825 passed / 1 skipped / 5 deselected (unchanged) | **PASS** — 20 real-TEAx tests, live + relocated-v6 sealed packages, 11 outputs each, LCOE `270.1211779380445` |
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
- [ ] **Carried ledger inputs from Phase 3.** These are named here so the module deletion sweeps
  them rather than leaving them behind:
  - The eight retained transitional duals recorded in the Slice 3C completion notes. Each is one
    behavior under two names; deleting the legacy member and dropping the `Exact`/`identified`
    qualifier from the survivor is the Phase 4 half of that slice.
  - `_CONSTRAINT_LOGGER = logging.getLogger("sysml_codegen.analysis.constraint_lowering")`
    (`src/sysml_codegen/elaboration/project.py:83`). A string, not an import — it predates Item 7
    (`b9c22c0`) and does not weaken the exact route's decoupling, but left alone it becomes a
    logger named after a module that no longer exists. Retire the name with the module.
    **[AGENT]** raised as F4 of the Slice 3C audit (`evidence/audit-3c.md`), informational.
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

- **Completed:** In progress — 3A done, 3B–3E pending
- **Slice commits and evidence:** see the per-slice notes below
- **Issues/deviations:** see the per-slice notes below

#### Slice 3A Completion — V6 envelope and source admission

- **Completed:** 2026-08-10
- **Commit:** fe0b855 (sysml-codegen only; agentic-mbse untouched and clean at
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`)

**What the slice proves.** One model elaborated live, captured to a v6 snapshot, and loaded back
both in place and from a different directory produces one instance graph and one projected
computation graph. The snapshot is self-contained — deleting the model tree does not change what
loads — and capture is deterministic: the same model in the same environment produces byte-identical
snapshot bytes. v5 is untouched and every Item 6 test still passes.

**The identity hole, and how far it is actually closed.** The forensic candidate sealed a free-form
`capture.model_name` and a `capture.captured_at` timestamp under `integrity.digest`. That digest is
an unkeyed SHA-256, so anyone who edits the file recomputes it: the candidate's loader accepted a
re-labelled, re-sealed snapshot. No internal check can fix that, because every internal check is a
function of the document the forger controls.

Both fields are gone, and reintroducing either — at the top level or smuggled into `authority` — is
refused by the exact-shape gate. Dropping `captured_at` also removes the byte-identity churn a
re-capture used to cause.

**That is less than this slice first claimed, and the correction is recorded below under F1.** The
`sources` manifest is itself self-declared: a referent, size, and SHA-256 per file, checked for
canonical form but never against the files. Offline, three re-labelling shapes still load, and the
independent audit demonstrated all three against the real loader. They are refused when the caller
supplies `source_roots`. What did change relative to the candidate is that no envelope field is now
unverifiable *even with the sources in hand* — `model_name` was.

This is a deliberate change to sealed-format semantics, which the slice brief sanctioned. It is not
a rule-10 stop, but the residual limit is an owner decision, flagged against the 3A checkbox above.

**Per-file dispositions.**

| Path | Disposition | Reason |
|---|---|---|
| `extraction/source_manifest.py` | **Reuse**, relocated + 3 edits | Staged admission, referent normalization, collision/symlink/race policy, and the closed failure vocabulary are sound and independently tested. Edits: `PINNED_SYSIDE_VERSION` constant instead of a literal in two places; `envelope_sources()` lost its `capture_options` argument with the capture-options block; both `import syside` statements routed through `agentic_mbse.sysml.syside_adapter.get_syside()`. |
| `snapshot/envelope.py` | **Reimplement** | Structure, layered failure order, and distinct error types kept. Rewritten for the identity closure (no `capture` block); the ~200-line hand-copy of every graph node's field list dropped, because the codec already owns that contract and a second copy silently diverges; error names no longer collide with v5's `SnapshotFormatError`; the referent regex replaced by the one `validate_source_referent`. |
| `snapshot/instance_graph.py` | **Reuse** (strictness hunks only) | Exact-key rejection per node kind plus duplicate-JSON-key rejection. The candidate's reformatting-only hunks were left out. |
| `snapshot/capture.py` | **Reimplement** as an addition | The candidate *replaced* `capture_snapshot`, which would have taken v5 with it. `capture_instance_graph_snapshot` was added beside it with the atomic-write behavior kept and the never-applied `design_path_filter` dropped. |
| `orchestration/pipeline_builder.py` | **Reject** | The candidate rewrote this 6-phase file down to 95 lines, deleting the legacy builder mid-slice. The minimum seam was reimplemented as `elaborated_pipeline.elaborate_admitted_sources` instead. |
| `snapshot/{loader,serializer,graph_rebuild}.py` deletions, `snapshot/__init__.py` rewrite | **Reject** | v5 production; retirement is Phase 4 work. The v6 API is reached through `sysml_codegen.snapshot.envelope`, so the package `__init__` keeps `SNAPSHOT_FORMAT_VERSION = 5` and no name collides. |
| `tests/unit/test_source_admission.py` | **Reuse** + 3 added cases | Real behavior with independently derived expectations. Added the `PINNED_SYSIDE_VERSION` environment check and referent round-trip/refusal cases. |
| `tests/conformance/test_snapshot_v6_{envelope,capture,routes}.py`, `test_source_admission_routes.py` | **Reimplement** from the candidate as material | The candidate's envelope matrix covered about half the cells and asserted the identity behavior that was wrong. Rewritten to the full matrix, with every refusal exercised against a *re-sealed* document. |

**Two Item 6 architectural invariants the candidate broke, caught here.** The first draft of this
slice failed `tests/unit/test_extractor.py::test_no_direct_syside_imports` (only the agentic-mbse
adapter may import syside) and
`tests/conformance/test_elaboration_dual_run.py::test_internal_route_is_not_a_shipped_builder_flag_or_legacy_adapter`
(the internal exact route must not reach into the snapshot machinery). Both were fixed properly:
syside now comes from `get_syside()`, and `source_manifest.py` moved from `snapshot/` to
`extraction/`, which is its real home — it is the extraction front door, used by the live route as
well as capture. **The forensic candidate deleted both of those test files** (347 lines), which is
why the same two violations went unnoticed there. This is direct evidence for plan rule 6.

**Deviation from the brief's candidate path list.** The brief named
`src/sysml_codegen/snapshot/source_manifest.py`. It landed at
`src/sysml_codegen/extraction/source_manifest.py` for the isolation-invariant reason above. The
declared path set was updated before editing; no other path moved.

**Tests, red then green.** All five modules failed to collect at `beee0f4` (missing
`capture_instance_graph_snapshot`, `elaborate_admitted_sources`, `envelope`, `source_manifest`).
After the slice: 104 new tests pass — 31 unit source-admission, 60 envelope matrix, 6 admission
routes, 4 capture atomicity, 3 route equality.

**Gates.**

- Full licensed suite: **3462 passed / 47 skipped / 18 deselected**, zero failures, zero
  `no live syside license` skip lines. Delta versus the Item 6 baseline is exactly +104 passed and
  nothing else — the 104 new tests. Skips and deselections are unchanged, so no Item 6 test was
  removed, silenced, or deselected.
- Execution lane (`pytest tests/execution -m execution`): 18 passed, unchanged.
- Generated-package smoke: `sysml-codegen generate --models tests/fixtures/fusion_tea` produced and
  sealed a 48-file package. Manual artifact check: `inputs/hif_driver_params.json` carries
  `hif_driver__HIF_Driver__efficiency = 0.35`, which traces to `:>> efficiency = 0.35;` at
  `tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:81`.
- `ruff check src`: 16 findings, byte-identical to the baseline set — zero new.
- `mypy src`: error set compared line by line against the baseline — zero new, zero fixed.
- `git diff --check`: clean. Changed paths equal the declared set.

**Scope note for 3B.** The v6 route ends at the projected `ComputationGraph`. Generating a package
from a v6 snapshot needs a full `PipelineContext`, which is Slice 3B's declared work, so the smoke
above runs the live route.

#### Slice 3A audit follow-up — F1, F2, F3

- **Completed:** 2026-08-10
- **Audit:** `evidence/audit-3a.md`, verdict FINDINGS. Commit: 4858911.
- **Declared path set:** `snapshot/envelope.py`, `orchestration/elaborated_pipeline.py`,
  `tests/conformance/test_snapshot_v6_{envelope,routes,capture}.py`, this plan, the two audit
  artifacts, and — declared mid-slice, see F3 — `.project/completed/20260809_elaborator-breadth/diff-ledger.md`.

**Correction to the record.** `fe0b855`'s commit message is headed *"v6 instance-graph snapshots
that cannot be re-labelled"* and its body claims a model-identity swap "can no longer be expressed".
That overclaims: it is true of `capture.model_name` and `capture.captured_at`, and false of the
`sources` manifest. History is not rewritten; this note is the correction, and the module docstring,
the test-module docstring, and the 3A notes above now state the actual guarantee.

**F1 — the identity closure was overclaimed.**

*(a) What is genuinely offline-checkable.* The audit asked for a converse membership check — every
`sources.files[]` row referenced by at least one graph row — which would structurally kill the
appended-phantom-row shape. **Measured first, and not shipped: it would be a false invariant.** The
elaborator records a node's *declaration* site, so a file holding only usages contributes no graph
row at all. Across the 33 multi-file fixtures, 11 capture cleanly and **5 of those 11 have a sealed
source that no graph row references**: `agg_literal_probe` and `retype_model` and `d38_caret`
(`design.sysml` unreferenced), `quoted_owner_formula` (`library.sysml` unreferenced), and
`sample_model` (an empty graph, which the F3 gate now refuses at capture). No narrower crisp form
survives either: occurrence records carry no source location, and calculation definitions are not
separate graph rows, so `attrs`/`calcs`/`constraints` is already the widest set of "recorded kinds"
available. Per the owner's third branch, no fuzzy heuristic was shipped. The one-way check is now
commented at `snapshot/envelope.py` with this measurement, and pinned by
`test_a_sealed_source_need_not_be_referenced_by_any_graph_row` against `agg_literal_probe`.

*(b) The residual limit is now pinned, not implied away.* Six new cells in the envelope matrix,
parametrized over the audit's three probe shapes — referent renamed consistently, phantom row
appended, real row's digest and size restated — each re-sealing the sources fingerprint, the inner
fingerprint, and the outer digest the way a forger would:

- `test_a_resealed_relabelling_is_accepted_offline` asserts each one **loads**, and that the forged
  snapshot yields a full usable graph. The docstring states this is an accepted, documented limit.
- `test_source_roots_refuse_every_resealed_relabelling` asserts each one raises
  `SnapshotStaleSourceError` when `source_roots` is supplied. The freshness path catches all three.

*(c) Overclaiming artifacts corrected.* `snapshot/envelope.py`'s module docstring now separates what
is anchored from `sources`, which is not, names the three shapes, and states plainly that a caller
needing provenance rather than structure must pass `source_roots`. The envelope test module's
docstring, this plan's 3A checkbox, and the 3A identity paragraph are all corrected. The commit
message correction is recorded above.

**F2 — route equality's live arm was not independent.** It called the same two functions capture
calls, so the audit's injected defect in `elaborate_admitted_sources` moved the graph while the
assertion stayed green. The live arm is now `build_elaborated_pipeline`, the Item 6 public builder
path, which reaches the elaborator without admission.

Making the arms independent immediately exposed that a projected comparison alone is not enough:
projection drops `display_name`, which is exactly what the audit corrupted, so the injection was
*still* invisible. The test therefore carries two comparisons — the projected public surface via the
public builder, and the encoded instance graph via an independent `elaborate()` call, with only
`source_file` neutralised.

*Injection re-run, the audit's own scenario:* corrupting every calc `display_name` inside
`elaborate_admitted_sources` and running
`test_live_in_place_and_relocated_routes_have_one_graph` — `UNPATCHED exit=0 (1 passed)`,
`DEFECT INJECTED exit=1 (1 failed)`. The file was restored and byte-compared afterwards. The audit's
result was `exit=0` both ways.

**A real product defect this uncovered — 3B blocker.** With the arms independent, the two routes
disagree on more than `source_file`. `_group_identity`
(`src/sysml_codegen/elaboration/project.py:164`) names each entry-point group after the source path,
so on the v6 route the group is named after the *staging referent*: a package generated from a v6
snapshot would ship `inputs/root_0_params.json` and a `Root0Params` schema class instead of names
taken from the model. The v6 side is otherwise the improvement the referent design exists for — the
live route still emits absolute checkout paths, one carrying a leftover `//` URI prefix.
`test_the_two_routes_diverge_only_on_source_derived_naming` pins both sides by value.
**Slice 3B owns `elaboration/project.py` and must resolve this before the public authority switch.**

**F3 — one shared emptiness gate, per the B37-01 ruling.** `require_executable_content`
(`orchestration/elaborated_pipeline.py`) refuses only a graph with no calculation, no constraint,
and no calculation definition. Both `build_elaborated_pipeline` and `elaborate_admitted_sources` call
it, so capture can no longer seal a model the live route refuses. The legacy pre-elaboration
`calc def` precheck was not copied — that is the front-gate the B37-01 ruling identified as measuring
the wrong thing.

*This moved a certified corpus outcome, exactly as the ruling predicted.* The ruling says: "when a
cutover moves or removes that front-gate, this fixture correctly produces a graph. That outcome is
the ruling being satisfied, not a regression." `test_dual_run_ledger_outcomes_match_a_live_corpus_run`
duly went red: `agg_literal_probe` on the exact route moved from `error: CodeGenerationError` to
`graph 1/3/0/0`. Row 1 of `.project/completed/20260809_elaborator-breadth/diff-ledger.md` is updated
to the measured outcome, reclassified `expected-collapse` → `expected-fix` (the routes now differ),
and the totals block is corrected with the Item 6 figures retained beside it. The ledger's three
carried B37-01 obligations are discharged there, including the re-derived count — **the exact route
now produces 14 public graphs and 23 typed errors** on the 37-fixture corpus, measured rather than
chosen. The `14/22/1` versus `15/22/0` question is a different axis (the Phase-8 batch manifest) and
stays open. **[OWNER visibility]** this edits a completed, certified record; Phase 2 explicitly
carried the update to Phase 3/4, so it is a discharge rather than a rewrite. **Confirmed by the
orchestrator (2026-08-10):** the edit is inside the scope the B37-01 owner pre-ruling authorized
("amend the ledger/spec/census rows"); the Item 6 measured figures are retained beside the
amendment, so the certified history remains readable.

**Gates.**

- Slice tests: **115 passed** (67 envelope, 31 unit admission, 6 admission routes, 6 capture,
  5 routes) — +11 over the 104 at `fe0b855`.
- Full licensed suite: **3473 passed / 47 skipped / 18 deselected**, zero failures, zero
  `no live syside license` lines. Delta versus `fe0b855` is exactly +11 passed, the new tests;
  skips and deselections unchanged, so nothing was silenced.
- Execution lane: 18 passed, unchanged.
- Generated-package smoke: 48-file sealed package, `hif_driver__HIF_Driver__efficiency = 0.35`,
  unchanged.
- `ruff check src`: findings byte-identical to the baseline set — zero new. `mypy src`: error set
  identical — zero new, zero fixed. `git diff --check` clean. Changed paths equal the declared set.

#### Slice 3B Completion — Defensive context and exact public projection

- **Completed:** 2026-08-11
- **Commit:** d91431b (sysml-codegen only; agentic-mbse untouched and clean at
  `5088b417c9e5453271291d46cd5fb23fc0579b1e`)
- **Declared path set:** `elaboration/project.py`,
  `orchestration/exact_pipeline_context.py` (new), `tests/conformance/test_snapshot_v6_routes.py`,
  four new `tests/conformance/test_exact_*.py` modules, this plan, `briefs/phase3b.md`, and
  `evidence/3b-old-new-comparison.md`. Two paths were declared mid-slice and are named as
  deviations below: `orchestration/elaborated_pipeline.py` and
  `tests/conformance/test_exact_group_identity.py`. Actual changed paths equal that set.

**What the slice proves.** The exact route now has a public construction that cannot be mutated
after it is built and cannot hand out a graph that disagrees with what it was built from. A caller
can ask for the whole model or for the exact closure of named outputs. A package generated from a
relocated v6 snapshot and a package generated live carry the same input filenames, the same schema
class names, and the same modelled values — they differ only in `SysML Source:` provenance
comments, and every differing file is named and checked. A modelled aggregation reaches that
package with its literal operand intact, which is the B37-01 ruling at the product surface. The
legacy builder and registry are untouched and remain the shipped authority.

**The rule-10 stop, and the ruling that resolved it.** The brief directed group identity to derive
from model semantics rather than the file path. Measuring that first — as the recovery plan
requires and the brief's own defect note assumed — showed a package-wide rule would rename
`design_params` to `attr_expr_probe_design_params`, breaking
`test_parameter_group_name_drives_the_compatible_json_filename`
(`tests/conformance/test_elaboration_phase5_remediation.py:172`), whose module is headed
*"Owner-ratified Phase 5 remediation"*. At the 3E authority switch it would also rename the
customer package's `hif_plant_params` to `hif_plant_pkg_params`, because `hif_plant.sysml` declares
`package hif_plant_pkg`. That is a narrowing of an owner-ratified compatibility guarantee, so the
slice stopped with the measurement instead of choosing.

The orchestrator ruled option (C): keep the stem, replace only the parent-directory fallback. The
stem is route-invariant — v6 staging rewrites the directory to `root-N` but preserves the filename
— so the parent directory was the sole route-variant input, and it is the only thing that changed.

**`_group_identity`, before and after.** `_group_identity` took a source path and returned
`path.parent.name if path.stem.lower() == "model" else path.stem`. It now takes a `base` chosen by
`_Projection._group_base` (`elaboration/project.py`) and does nothing but render it. `_group_base`
picks the stem, or — for a `model.sysml`, which carries no identity of its own — the
`package_display` of the owning node's root occurrence, which `InstanceGraph.validate` already
requires to be non-empty on every root. `_entry_source` now takes the owning node rather than a
source-file string, because the package is a property of the node, not of the path.

Two rendering choices, both recorded because they go beyond the ruling's literal wording:

- A PascalCase package is read as snake_case before rendering (`ElabMatrixC14` →
  `elab_matrix_c14`). Without it, `sanitize_name(...).lower()` yields `elabmatrixc14`, and eight of
  the nine `model.sysml` fixtures would have been renamed rather than one. Applied only in the
  package fallback; a filename stem is already spelled the way the modeller wants it read.
- `ParameterGroup.source_file` records the normalized identity token, not a path. The ruling asked
  for the bare stem; the measured legacy route actually stores the file *name* (`hif_plant.sysml`),
  so "identical to legacy" was not available either way. The token is what makes the field
  route-invariant, which is what the ruling wanted it for. It reaches generated bytes only as
  `"Parameters from {label}."` (`generation/entry_point.py:226`).

**Measurement the ruling required, all three checks.**

1. *Group identity that changed under (C):* **one fixture.** `elab_constraint_formal_identity`
   moves from `elab_constraint_formal_identity_params` (its directory) to
   `constraint_formal_identity_params` (its package). Every other projecting fixture keeps the exact
   name and class it had at `a7c13a6`. Internal to the unshipped exact route.
2. *Exact vs legacy on stem-named fixtures:* ten compared, eight match (one of them matching once
   the legacy-only `system_design` hierarchy group is set aside). The two that do not are
   `d38_caret` and `unresolvable_attr_probe`, both below.
3. *Strict route equality:* live, in-place v6, and relocated v6 produce byte-equal entry-point
   group payloads including name, class, label, and every parameter. The routes test now asserts
   that equality instead of masking it, and the projected-surface comparison no longer masks
   `param_group` on module inputs either — a strictly stronger comparison than at `a7c13a6`.

**Two named residuals for Slice 3E — `d38_caret` and `unresolvable_attr_probe`.** *(Second one and
the mechanism added 2026-08-11 after the 3B audit, F3 and F5. The earlier note named only
`d38_caret` and described it as a declaration-site difference alone.)*

These are the two stem-named fixtures where the exact and legacy routes ship different packages.
**This slice neither caused nor touches either** — both lack a `model.sysml`, so the changed
fallback never runs on them, and both measure byte-identical before and after. Each is now pinned
by value in `tests/conformance/test_exact_group_identity.py`, and each **needs a disposition before
the Slice 3E authority switch**, where it would change a shipped input filename *and* what that file
contains.

The mechanism in both is legacy fallback attribution, not the naming rule:

- `d38_caret` — exact `library_params` (6 parameters), legacy `design_params` (1). The single
  shared parameter is a declaration-site difference: the elaborator records where the node is
  declared (`library.sysml`), the legacy deriver attributes it to `design.sysml`, and the group
  name follows. The other five are a content difference — the exact route resolves four modelled
  `cell` occurrences and an exponent that the legacy route drops.
- `unresolvable_attr_probe` — exact `design_params` (9 parameters), legacy `system_design` (1).
  **The routes share no entry point at all.** The exact route resolves inherited design attributes
  onto three concrete instances, which `test_elaboration_phase5_remediation.py::
  test_inherited_formulas_are_scoped_to_three_concrete_instances` already pins as correct exact
  behavior; the legacy deriver drops all nine and emits one literal attributed to its synthetic
  `hierarchy` source, and *that* attribution is what names the group `system_design`.

So no group-naming rule can reconcile either: change the naming rule however you like and these
routes still ship different files with different contents. Surfaced, not absorbed. Full measurement
in `evidence/3b-old-new-comparison.md`.

**A second residual, pinned rather than fixed: module provenance.** Module `source_file` still
differs across routes — the live route records absolute checkout paths (one still carrying a
leftover `//` URI prefix), the v6 route records the portable referent. It reaches generated bytes
only as a `SysML Source:` comment. The v6 spelling is the one the design intends
(`generation/stencils.py:243`); making the live route agree means routing it through admission,
which would undo the arm independence Slice 3A's F2 fix established. Carried to 3E, asserted by
value on both sides, and the generated-package test pins the exact set of files the difference
reaches, not merely that the set is non-empty (tightened 2026-08-11 after the 3B audit, F6).

**Per-file dispositions.**

| Path | Disposition | Reason |
|---|---|---|
| `orchestration/pipeline_context.py` | **Reject** | The forensic hunk replaces the whole dataclass with a narrow receipt-bound class, deleting `calc_defs`, `group_deriver`, `backtracking_result`, `output_registry`, `constraint_facts`, and eight more fields the shipped legacy builder and `snapshot/capture.py` populate and read. That is Phase 7 deletion behavior arriving inside a Phase 3 slice. Untouched. |
| `orchestration/snapshot_context.py` | **Reject** | The forensic hunk replaces `build_pipeline_context_from_snapshot` — the shipped v5 `generate --from-snapshot` route — with a v6 loader. Retirement is Phase 4. Untouched. |
| `orchestration/pipeline_builder.py` | **Reject** | Same disposition as 3A: the forensic commit cuts a 6-phase 1194-line file to 95 lines. Untouched. |
| `orchestration/exact_pipeline_context.py` | **Reimplement** as an addition | Carries the recovered receipt idea beside the legacy context rather than on top of it. Dropped from the forensic version: the `_VerifiedProjectionLease` (a sealing-time concern, 3D/3E work) and the `include_all` flag. Added: an explicit refusal when a context is reached without sealed authority. |
| `elaboration/project.py` — typed target selection | **Reuse**, reviewed per hunk, one signature change | The closure walk, the three output spellings, and the ambiguity refusal are sound and now independently tested. Changed: `targets` + `include_all` collapsed to one `targets` parameter, because two parameters selecting between "everything" and "this closure" via a flag makes `include_all=True, targets=[...]` expressible and meaningless. `None` means the whole model; a sequence means that closure; empty is an error. |
| `elaboration/project.py` — `_build_output_aliases(selected_outputs=None)` | **Reimplement** | The forensic version takes an optional set used only in some branches. It now always takes the set, and the complete projection passes all of them. Same for `_build_groups`. |
| `elaboration/project.py` — `mint_constraint_id` import move, `sanitize_name(node.calc_def_name)` | **Reject** | Unrelated to 3B's behavior. The second is a product-visible module-metadata change with no test behind it. |
| `orchestration/elaborated_pipeline.py` | **Reimplement**, declared mid-slice | `build_elaborated_pipeline` split into `elaborate_model_paths` (load → elaborate → gate) plus the projection, so the sealing builder can take the graph. `build_elaborated_pipeline` keeps its exact behavior and both routes still reach the elaborator by one path, which `test_the_live_arm_does_not_share_the_capture_route` still checks. |

**An Item 6 architectural guard fired, and it was right.**
`tests/unit/test_elaboration_import_boundaries.py::test_exact_semantic_boundary_has_no_string_or_legacy_identity_route`
caught two violations in the first draft: `_declaring_package` derived a package by splitting a
rendered qualified name (`owner_qualified_name.split("::")[0]`), and `_output_index` used
`next(iter(...))`. Both were removed rather than exempted. The package-scoped branch now fails
loudly naming the case instead of guessing from a rendered string — no corpus fixture reaches it,
since it needs a package-scoped entry point in a file named `model.sysml`. The index unpacks a
set already proven to hold one element. This is the second slice in a row where a test the forensic
candidate deleted caught a real defect (plan rule 6).

**Tests, red then green.** *(Corrected 2026-08-11 after the 3B audit, F4 — the earlier note said
all five modules failed to collect.)* Four of the five new modules failed to collect at `a7c13a6`,
because `exact_pipeline_context` and `elaborate_model_paths` do not exist there. The fifth,
`test_exact_group_identity.py`, imports only functions that do exist there, so it collects and
reports **4 failed / 8 passed** against the old production code: the four identity assertions are
the red, and the eight that pass are the ones that should — including the `d38_caret` pin and the
stem-compatibility test, which is independent evidence that the stem rule was untouched. Also,
`test_the_two_routes_diverge_only_on_source_derived_naming` was green there asserting
`{"root_0_params"}` / `{"Root0Params"}`. After the slice: **46 new tests pass** — 15 context,
12 selection, 12 group identity, 4 generated package, 3 aggregation — and the routes test is
renamed and flipped to assert equality.

**Gates.**

- Full licensed suite: **3519 passed / 47 skipped / 18 deselected**, zero failures, zero
  `no live syside license` lines. Delta versus the 3A baseline is exactly **+46 passed** and nothing
  else. Skips and deselections unchanged, so no Item 6 test was removed, silenced, or deselected.
- Execution lane (`pytest tests/execution -m execution`): 18 passed, unchanged.
- Generated-package smoke, both exact routes: live and relocated-v6 packages have identical file
  sets, an identical `inputs/source_identity_mixed_consumers_params.json`, and a
  `SourceIdentityMixedConsumersParams` schema class on both sides. No `root_0` anywhere. Traced by
  hand: `:>> efficiency = 0.75;` at `model.sysml:234` reaches the generated input file as `0.75`.
- Shipped legacy CLI smoke: `sysml-codegen generate --models tests/fixtures/fusion_tea` still
  produces 48 files with `inputs/{hif_driver,hif_plant,ife_plant}_params.json` and
  `hif_driver__HIF_Driver__efficiency = 0.35`. The customer-visible package did not move.
- `ruff check src`: **byte-identical** to the `a7c13a6` baseline — zero new. New test modules lint
  clean. `mypy src`: error set **identical** (71 errors in 17 files; 84 → 85 files checked, so the
  new module contributes zero). `git diff --check` clean. Changed paths equal the declared set.

#### Slice 3B audit follow-up — F1 through F7

- **Completed:** 2026-08-11
- **Audit:** `evidence/audit-3b.md`, verdict **CERTIFY** (nothing blocked 3C), 7 findings.
  Recorded at `9d05f49`. Commit: 2f28dde
- **Declared path set:** `elaboration/project.py`,
  `orchestration/exact_pipeline_context.py`, `tests/conformance/test_exact_group_identity.py`,
  `tests/conformance/test_exact_route_generated_package.py`,
  `tests/conformance/test_exact_pipeline_context.py`, this plan, and
  `evidence/3b-old-new-comparison.md`. Actual changed paths equal that set.

All seven findings are closed. Two changed production, three changed tests, two were factual
corrections to this plan and the evidence file.

- **F1 (Low) — the dangling-alias guard could no longer fire.** The `selected_outputs` filter sat
  above the channel lookup in `_build_output_aliases`, and on the complete path its condition is
  identical to `channel is None`, so an alias pointing at an absent producer was silently skipped
  where it used to raise. The filter now sits *below* the lookup, restoring the unconditional check
  the code had at `a7c13a6` while the filter still prunes on the selected path. The reason is
  commented at the site so the ordering is not "tidied" back. It stays defence-in-depth behind
  `validate()` (`graph.py:706`); no fixture reaches it, and I did not manufacture one — a
  white-box probe that removes an indexed channel trips an earlier `KeyError` in module building
  first, so the honest claim is restored reachability, not a demonstrated firing.
- **F2 (Low) — the inert `_targets` slot is deleted.** `_seal` wrote it and nothing read it;
  `receipt.targets` was always the authority. Removed from `__slots__`, the annotations, and
  `_seal`, so the slots now carry only what is verified.
- **F3 (Medium) — `unresolvable_attr_probe` is now a named residual with a by-value pin.** It was
  in the evidence table but not in this plan's residual list and had no test, so unlike `d38_caret`
  it could have moved unnoticed. Pinned by
  `test_the_known_exact_versus_legacy_divergence_on_unresolvable_attr_probe`, added to the residual
  list above, and the "nine compared" count corrected to ten. The mechanism is identified: legacy
  fallback attribution, not the naming rule — the two routes share no entry point at all.
- **F4 (Low) — the red-state claim is corrected** from "all five modules failed to collect" to the
  measured four-failed-to-collect plus 4 failed / 8 passed for the fifth.
- **F5 (Low) — the `d38_caret` pin is widened to the full measured divergence.** It asserted group
  names only; it now asserts both routes' complete parameter sets, which is where five of the six
  differences actually live. The prose in this plan and the evidence file is corrected to say the
  routes disagree on the declaration site *and* the entry-point set.
- **F6 (Low) — the differing-file set is pinned.** `test_the_two_packages_differ_only_in_provenance_comments`
  asserted only that the set was non-empty while this plan claimed every differing file was named.
  The test now asserts the set itself, derived from the live tree rather than hard-coded, so a file
  that newly starts differing fails the test.
- **F7 (Low) — the near-tautological digest assertion is labelled as what it is.** The line compares
  a digest against a graph production has already verified, so it is a field-coverage check on the
  digest formula, not an independent receipt check. The module docstring claimed more than that; it
  now names which assertion is independent (the instance fingerprint, re-elaborated and re-encoded
  by the test) and points at the tamper set as what proves the receipt has teeth.

**Gates.** Slice tests **53 passed** (+1: the new `unresolvable_attr_probe` pin). Full licensed
suite **3520 passed / 47 skipped / 18 deselected**, zero failures, zero `no live syside license`
lines — delta versus `d91431b` is exactly **+1 passed**, that same pin, with skips and deselections
unchanged. Execution lane 18 passed. `ruff check src` byte-identical to the baseline set; the new
test modules lint clean. `mypy src` error set identical (71 errors in 17 files). `git diff --check`
clean. Changed paths equal the declared set.

#### Slice 3C Completion — Coordinated compiler and constraint authority

- **Completed:** 2026-08-11
- **Commits:** agentic-mbse `8b63393` (committed first), sysml-codegen `7af5dc9`
  (names the agentic OID in its message). This is the first slice where both repositories move.
- **Declared path set, sysml-codegen:** `core/identifier_types.py`,
  `extraction/modeled_defaults.py` (new), `analysis/constraint_lowering.py`,
  `elaboration/{elaborate,project}.py`, `generation/constraint_plan.py`, `cli/__init__.py`,
  `tests/conformance/test_exact_{compiler_core,constraint_route}.py` (new),
  `tests/fixtures/exact_calc_ordering/model.sysml` (new), the five
  `build_constraint_generation_plan` call sites in tests, this plan, and `briefs/phase3c.md`.
- **Declared path set, agentic-mbse:** `sysml/executable_profile.py`,
  `validation/{level4_constraints,level6_architecture}.py`,
  `tests/test_sysml/test_executable_profile.py`, `tests/test_sysml_quality_checks.py`.
- Actual changed paths equal both sets. Two codegen call sites were found after the first full
  suite run and declared then — named as a deviation below.

**The premise finding this slice turned up, and why it is a disposition rather than a stop.**
The brief expected the forensic Phase-5 patch to converge the exact compiler and constraint
authority by making the unsuffixed names the one exact route. Reviewing it hunk by hunk in both
repositories shows something narrower: **the exact route already exists at the Item 6 baseline
under suffixed and `*_by_id` names, and the forensic patch is a rename plus a deletion of the
legacy twin.** `compile_calc_def_exact` → `compile_calc_def`, `ExactCompilationResult` →
`CompilationResult`, `extract_identified_constraint_facts` → `extract_constraint_facts`,
`evaluate_identified_profile` → `evaluate_profile`, `CalculationDefinitionData.*_by_id` →
the unsuffixed field names — each reuses a name the legacy route still occupies.

Under this plan those renames are not available in Phase 3, and the brief's own instruction
resolves it: keep both callable, record the dual for Phase 4. Keeping both is only possible by
*not* renaming, because the new names collide with the shipped ones. The measured cost of doing
it anyway is on the record in the forensic tree: its 11 migrated agentic-mbse test modules each
grew a module-local `evaluate_profile` shim that fabricates UUIDs and returns a `SimpleNamespace`
imitation of the deleted `ProfileResult`, so those tests stopped exercising production. Rejecting
the renames avoids that, and it keeps the shipped legacy codegen route
(`analysis/constraint_lowering.py:498`, `orchestration/pipeline_builder.py:896`) working.

No Item 6 pin moved. `SI_CONSTRAINT_BLOCKED` on the strict, lenient, and round-tripped routes
(`tests/conformance/test_elaboration_payload_identity.py:236-266`) is green throughout. No rule-10
stop arose.

**What the slice does prove.** Three things, each behavior rather than spelling:

1. *The exact route no longer takes constraint authority from the legacy lowering module.*
   `elaborate.py` and `project.py` imported `mint_constraint_id` and `resolve_modeled_default`
   from `analysis/constraint_lowering.py` — a 1,650-line legacy module Phase 4 is meant to delete.
   Both now live in modules the two routes share, and neither exact file imports the legacy module
   at all. Pinned by an AST import check over both files.
2. *A rendered calculation implementation is correct for intermediates, cross-referencing outputs,
   and output order.* `_calculation_auto_impl_context` emitted `execution_steps: []` always and
   listed every compiled member as a return value in topological order. On a calculation with an
   undeclared intermediate that renders a function returning the intermediate as an output and
   referencing names it never assigned; with two declared outputs it can also return them in an
   order the projected schema does not use. Both are fixed by one rule — a member becomes an
   assignment step when something else consumes it, and returns follow declaration-UUID order,
   which is the order `_Projection._outputs` sorts on.
3. *The exact gate exists and agrees with the neutral one.* agentic-mbse's `preflight` only took
   neutral facts and re-derived the usage/definition association by qualified name. The new
   `preflight_identified` partitions an already-decided exact result. It follows the UUID
   association where the neutral payload cannot (two definitions, one qualified name, different
   predicates), and it produces the same partition as `preflight` when identity is unambiguous.

**Per-file dispositions — sysml-codegen.**

| Path | Disposition | Reason |
|---|---|---|
| `extraction/expression_compiler.py` | **Reject** (whole forensic hunk) | Pure rename: `compile_calc_def_exact` → `compile_calc_def`, `Exact*Result` → `*Result`, plus deletion of the legacy name-keyed compiler and `_topological_sort`. Both names cannot exist; the legacy compiler is still the shipped route's. Untouched. Four duals recorded. |
| `extraction/data_models.py` | **Reject** | Collapses the name-keyed `output_expression_asts`/`member_expressions`/`all_member_names` into the ID-keyed fields, deleting the legacy halves the extractor and legacy compiler read. Item 6 already carries both; the deletion is Phase 4. Untouched. |
| `extraction/extractor.py` | **Reject** | Same change on the producing side, same reason. Untouched. |
| `elaboration/elaborate.py` — `_calculation_auto_impl_context` | **Reimplement** | The idea (steps for consumed members, declaration-ordered returns) is right and is the slice's real behavior recovery. The forensic version branches on an `output_crossrefs` flag and duplicates both loops under it. Rewritten as one rule with no mode flag: a member is stepped when it is an undeclared intermediate *or* another member depends on it, and a stepped member is returned by name. |
| `elaboration/elaborate.py` — `_enumeration_value` | **Reject for 3C** | Genuinely new behavior (enum literals in attribute values), unrelated to the compiler/constraint authority this slice converges, and no fixture in the tree exercises it. Carried as candidate 3D material rather than imported untested. |
| `elaboration/elaborate.py` — `resolve_modeled_default` import move | **Reuse**, different home | The forensic tree moves it to `elaboration/value_defaults.py`, which would make the legacy `analysis` module import `elaboration`. It landed at `extraction/modeled_defaults.py`, which both layers already import from. |
| `generation/constraint_catalog.py` — `mint_constraint_id` | **Reuse**, different home | The forensic tree adds it to `generation/`, which would make `elaboration/project.py` import `generation/`. It landed in `core/identifier_types.py`, beside `make_scoped_key`, which is the bottom layer both routes already import. |
| `generation/constraint_plan.py` | **Reuse** | `build_constraint_generation_plan` took a whole `PipelineContext` and read one attribute off it. It now takes the `ComputationGraph`, so the exact route calls it with what it has instead of fabricating a context. Five call sites updated, two of which had been fabricating a `SimpleNamespace` context for exactly this reason. |
| `core/{identifier_types,models}.py`, `extraction/binding_evidence.py`, `generation/pipeline.py` docstring hunks | **Reject** | Comment-only edits describing symbols this slice does not retire. They belong with the Phase 4 deletion that makes them true. |
| `tests/conformance/test_exact_compiler_core.py` | **Reimplement** from the candidate as material | The forensic module's collision case and hand-built cycle fixture are good and are kept, retargeted at `compile_calc_def_exact`. Its first assertion — `"compile_calc_def_exact" not in vars(expression_compiler)` — is a naming assertion that contradicts the retention rule and is dropped. Three ordering cases added. |
| `tests/conformance/test_exact_constraint_route.py` | **Reimplement** from the candidate as material | The end-to-end agreement test is sound and is kept, retargeted at the suffixed names and at `preflight_identified`. Its two "the unsuffixed name is the only one" assertions are dropped for the same reason. Two tests added: the legacy-import check, and a check that both routes still reach the moved helpers. |

**Per-file dispositions — agentic-mbse**, including the three quality-cleanup hunks the brief
asked to be judged separately.

| Path | Disposition | Reason |
|---|---|---|
| `sysml/constraint_extraction.py` | **Reject** | Renames `extract_identified_constraint_facts` onto `extract_constraint_facts` and deletes the neutral function. Both are live: codegen's exact route calls the first, its legacy route and both validation levels call the second. Untouched. Two duals recorded. |
| `sysml/executable_profile.py` — rename hunks | **Reject** | Same shape: `evaluate_identified_profile` → `evaluate_profile`, with `ProfileResult`, `_evaluate_usage` and the neutral `evaluate_profile` deleted. Untouched. Three duals recorded. |
| `sysml/executable_profile.py` — `preflight` signature change | **Reimplement** as an addition | The forensic patch *replaces* `preflight(ConstraintFacts)` with `preflight(IdentifiedProfileResult)`. Added `preflight_identified` beside it instead; both delegate to one `_partition_decisions` helper. The exact gate now exists without the neutral one being retired. |
| `sysml/executable_profile.py` — duplicate helper removal (**quality hunk 1**) | **Reuse** | `_promote_non_numerical_diagnostic` is defined twice, byte-identically, at `:950` and `:968`. The second shadows the first and nothing can reach it. Zero behavior change, and mypy loses a `no-redef` error. |
| `validation/level4_constraints.py` — import fallback (**quality hunk 2**) | **Reuse** | The `try: from .common import … except ImportError: from common import …` pair becomes one absolute import. This cannot change direct-file execution: the module already imports `agentic_mbse.sysml.*` absolutely at `:12`, so an installed package is required either way and the `common` fallback could never be the only working path. Measured both ways and now covered by `test_direct_file_execution_resolves_its_shared_helpers`, which runs the module as a script. |
| `validation/level6_architecture.py` — `load_manifest` cleanup (**quality hunk 3**) | **Reuse with added cover** | `except Exception` narrows to `(OSError, yaml.YAMLError)`, and well-formed YAML that is not a mapping is refused here rather than subscripted by a caller. That second part *is* a behavior change, so it did not ship uncovered: `test_manifest_valid_yaml_that_is_not_a_mapping` is the red→green case and `test_manifest_read_failure_is_reported_not_raised` guards the narrowed except. The `dict` → `dict[Any, Any]` annotation is typing only. |
| `validation/level6_architecture.py` — `item.decision` unpacking | **Reject** | Part of the rename migration, not a cleanup. Untouched. |
| The 11 forensic test-file migrations | **Reject** | Each adds a module-local shim that fabricates UUIDs and a `SimpleNamespace` stand-in for the deleted `ProfileResult`, so the migrated tests stop exercising production. `test_public_api_exports.py` also loses assertions. Not imported. |

**Retained duals, for the Phase 4 ledger.** Each pair is one behavior reachable under two names,
retained deliberately this slice. Phase 4 deletes the legacy member and renames the exact one.

| Repository | Exact (kept, suffixed) | Legacy twin (kept callable) |
|---|---|---|
| sysml-codegen | `expression_compiler.compile_calc_def_exact` | `expression_compiler.compile_calc_def` |
| sysml-codegen | `expression_compiler.ExactCompilationResult` | `expression_compiler.CompilationResult` |
| sysml-codegen | `expression_compiler.ExactCalcDefCompilationResult` | `expression_compiler.CalcDefCompilationResult` |
| sysml-codegen | `CalculationDefinitionData.{output_expression_asts,member_expressions,member_names}_by_id`, `all_member_ids` | `CalculationDefinitionData.{output_expression_asts,member_expressions,all_member_names}` |
| agentic-mbse | `constraint_extraction.extract_identified_constraint_facts` | `constraint_extraction.extract_constraint_facts` |
| agentic-mbse | `executable_profile.evaluate_identified_profile` | `executable_profile.evaluate_profile` |
| agentic-mbse | `executable_profile.IdentifiedProfileResult` | `executable_profile.ProfileResult` |
| agentic-mbse | `executable_profile.preflight_identified` | `executable_profile.preflight` |

Two names moved rather than duplicated, so they are *not* duals and Phase 4 has nothing to delete
for them: `mint_constraint_id` (now `core/identifier_types.py`) and `resolve_modeled_default` /
`ModeledDefault` (now `extraction/modeled_defaults.py`). `analysis/constraint_lowering.py` imports
both, so every existing caller and monkeypatch target still resolves;
`test_the_shared_constraint_identity_and_default_helpers_stay_callable_on_both_routes` pins that.

**Tests, red then green.**

- sysml-codegen: 8 new tests, **5 red at `38c2e15`** — the three ordering cases (measured red
  output: `output_expressions` named `['scaled', 'half', 'doubled_half']` against a two-output
  schema, with `execution_steps` empty), the legacy-import check (`elaborate.py` failed it), and
  the shared-helper check (`ImportError` on `mint_constraint_id`). The collision and cycle cases
  pass at head and are guards: they pin behavior the rename would have moved.
- agentic-mbse: 5 new tests, **1 red at `5088b417`** by assertion (`load_manifest` returned
  `['alpha', 'beta']` where `None` is required) and **2 red by collection** (the two
  `preflight_identified` gate tests fail the module import). The remaining two are guards on the
  two cleanup hunks, green both before and after by design.

**Gates.**

- Full codegen suite: **3528 passed / 47 skipped / 18 deselected**, zero failures, zero
  `no live syside license` lines. Delta versus the 3B follow-up baseline is exactly **+8 passed**,
  the eight new tests. Skips and deselections unchanged.
- Full agentic-mbse suite from the paired rebuild worktree: **1824 passed / 1 skipped /
  5 deselected**, zero failures. Delta versus the Phase 2 baseline of 1819/1/5 is exactly
  **+5 passed**, the five new tests.
- Execution lane (`pytest tests/execution -m execution`): 18 passed, unchanged.
- 3A/3B surface re-run (`test_snapshot_v6_routes`, `test_exact_route_generated_package`,
  `test_exact_group_identity`, `test_exact_pipeline_context`, `test_exact_target_selection`,
  `test_elaboration_payload_identity`, `test_constraint_profile_route_parity`,
  `test_constraint_generation_live`): **70 passed**. The coordinated change did not move it.
- Shipped legacy CLI smoke: `sysml-codegen generate --models tests/fixtures/fusion_tea` still
  produces 48 files with `inputs/{hif_driver,hif_plant,ife_plant}_params.json` and
  `hif_driver__HIF_Driver__efficiency = 0.35`. Customer-visible package unchanged.
- Manual generated-artifact check: the auto-implementation rendered for
  `exactcalcordering__rig__split` assigns `scaled = (inputs.total * 2.0)` then
  `half = (scaled / 4.0)` and returns `(half, (half * 2.0))`, matching the module's
  `['half', 'doubled_half']` output schema and the fixture's hand arithmetic
  (`total=8.0 → scaled=16.0 → half=4.0 → doubled_half=8.0`). At `38c2e15` the same template
  renders three return values, two of them referencing names the function never assigns.
- codegen `ruff check src`: **byte-identical** to the baseline set (16 findings) — zero new. The
  two new test modules lint clean. `mypy src`: error set **identical** (71 errors in 17 files;
  85 → 86 files checked, so `modeled_defaults.py` contributes zero).
- agentic-mbse `ruff check src`: identical to its baseline (1 pre-existing finding) — zero new.
  `mypy src`: **118 → 108 errors, zero new and ten fixed**, all ten from the three cleanup hunks.
- `git diff --check` clean in both repositories. Changed paths equal the declared sets.

**Issues and deviations.**

- **Two call sites declared mid-slice.** Narrowing `build_constraint_generation_plan` to a
  `ComputationGraph` reached five call sites, not three. The first full suite run found the two
  missed ones (`tests/conformance/test_constraint_generation_integration.py:158`,
  `tests/execution/test_constraint_execution.py:67`) as a hard failure rather than a silent pass,
  which is the gate working. Declared and fixed before commit.
- **Two forensic helper homes changed**, both to avoid a layering inversion the forensic tree
  introduced: `mint_constraint_id` to `core/`, not `generation/`; `resolve_modeled_default` to
  `extraction/`, not `elaboration/`. Reasons are in the disposition table.
- **The slice is thinner on the agentic-mbse side than the brief implies.** The brief describes
  that repository as "the incident's cleanest phase boundary: one 15-file Phase 5 patch". It is
  clean, but on inspection it contains no new decision behavior — 4 source files of renames plus
  3 cleanup hunks, and 11 test files migrating to the renamed API. The slice therefore recovers
  the cleanups, adds the missing exact gate, and defers the renames. Recorded rather than dressed
  up as more.
- No deletions in either repository. No Item 6 test was removed, silenced, or deselected.

#### Slice 3C audit follow-up — F1 through F4

- **Completed:** 2026-08-11
- **Audit:** `evidence/audit-3c.md`, verdict **CERTIFY** (nothing blocked 3D), 4 findings.
  Recorded at `aaa85e0`. Commits: agentic-mbse `cc6c7a7`, sysml-codegen `a6c41bc`.
- **Declared path set, agentic-mbse:** `validation/level6_architecture.py`,
  `tests/test_sysml_quality_checks.py`, `tests/test_sysml/test_executable_profile.py`.
- **Declared path set, sysml-codegen:** `tests/conformance/test_exact_constraint_route.py` and
  this plan. Actual changed paths equal both sets.

All four findings are closed. One changed production, two strengthened tests, one is a Phase 4
ledger input.

- **F1 (Medium) — the narrowed except let a real failure escape, and the slice introduced it.**
  A `manifest.yaml` that is not valid UTF-8 raises `UnicodeDecodeError` from inside
  `yaml.safe_load`. That is a `ValueError`, so neither `OSError` nor `yaml.YAMLError` caught it,
  and `_check_manifests` (`level6_architecture.py:124`) loops over every design's manifest relying
  on the `None` return to skip a bad one — one mis-encoded file aborted the whole Level 6 check.
  It also contradicted the docstring the same hunk rewrote. `UnicodeDecodeError` is now in the
  except tuple, with the reason commented at the site so it is not "tidied" back out. The guard
  the notes had cited used `chmod(0o000)`, which raises `OSError` and therefore constrained
  nothing about the narrowing; `test_manifest_that_is_not_utf8_is_reported_not_raised` writes
  genuinely non-UTF-8 bytes instead. Reproduced red at `8b63393` with the auditor's exact error
  (`'utf-8' codec can't decode byte 0xe9`), green after. The `chmod` test stays as the `OSError`
  leg.
- **F2 (Medium) — the AST pin is widened to every import spelling.** The check compared
  `ImportFrom.module` against one dotted string. Measured against the six ways to name the
  module: it **caught 3 and missed 3**, including `from sysml_codegen.analysis import
  constraint_lowering`, the ordinary way to import a module object and one this same test file
  uses. `legacy_constraint_imports()` now resolves relative imports against the package
  (accounting for `node.level`) and expands `from <parent> import <name>`, returning every
  offending dotted name. The detector is itself pinned: six positive cases and four negative ones
  (other `analysis` modules, which must not be flagged), so a future weakening of the check fails
  a test rather than passing silently. The decoupling itself was already real; this is the guard
  catching up to the claim.
- **F3 (Low) — the neutral gate's order dependence is now measured, not argued.** The test
  asserted the neutral payload was structurally ambiguous and then exercised only the exact gate.
  It now runs neutral `preflight` over the same twin pair in both definition-list orders and
  asserts the verdicts differ (`{True, False}`) — the neutral gate silently flips whether the run
  is blocked at all. The contrast is completed on the exact side too: reversing the same list
  leaves `preflight_identified` blocking the same usage, because the usage names its definition
  by UUID.
- **F4 (Informational) — carried to the Phase 4 ledger.** The legacy-named
  `_CONSTRAINT_LOGGER` at `elaboration/project.py:83` is now a named Gate 4A ledger input,
  alongside the eight retained duals, so the module deletion sweeps the string with the module.
  No code change: it predates Item 7 and creates no import.

**Gates.** Full codegen suite **3538 passed / 47 skipped / 18 deselected** — delta versus
`7af5dc9` is exactly **+10 passed**, the ten new parametrized detector cases, with skips and
deselections unchanged. Full agentic-mbse suite **1825 passed / 1 skipped / 5 deselected** —
delta versus `8b63393` is exactly **+1 passed**, the non-UTF-8 case; the F3 work strengthened an
existing test rather than adding one. Execution lane 18 passed. codegen `ruff check src`
byte-identical to the baseline set and the changed test module lints clean; `mypy src` error set
identical (71 errors in 17 files). agentic `ruff check src` identical (1 pre-existing finding);
`mypy src` 108 errors, unchanged. `git diff --check` clean in both. Changed paths equal the
declared sets.

#### Slice 3D Completion — Fusion Tea customer vertical and real TEAx

- **Completed:** 2026-08-11
- **Commit:** 848628b (sysml-codegen only; agentic-mbse untouched and clean at
  `cc6c7a7411f6338a4811a7cc58ca002c29ef177b`)
- **Declared path set, sysml-codegen:** `elaboration/{elaborate,project}.py`; the six Fusion Tea
  model files and `tests/fixtures/fusion_tea/extraction_snapshot.json`;
  `tests/fixtures/golden/calc_{compat_parity,def_compilation}_golden.json`; four new modules under
  `tests/execution/`; four updated test modules
  (`tests/conformance/test_elaboration_{contract_matrix,fail_closed,spike_parity}.py`,
  `tests/conformance/test_source_identity_routes.py`) plus
  `tests/runtime/test_fusion_tea_acceptance.py`;
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md`; this plan and
  `briefs/phase3d.md`. Actual changed paths equal that set.
- **Declared path set, agentic-mbse:** `N/A` — nothing changed there. Its suite was still run from
  the paired worktree and is unchanged at 1825 passed / 1 skipped / 5 deselected.

**What the slice proves.** The customer model goes end to end on the exact route and executes in
real TEAx. One model is loaded, elaborated, projected, generated, sealed, verified by TEAx's own
loader, discovered through the public SimKit registry builder, and run by
`simkit.core.pipeline.execute_pipeline` — eleven published channels, LCOE `270.1211779380445`.
The same happens for a package generated from a v6 snapshot read out of a third directory with the
model tree deleted; the two runs produce equal numeric outputs and an identical constraint report.
Mutating one modelled value at runtime moves exactly its consumers and nothing else, on both the
availability and thermal-efficiency axes, and editing a sealed input and re-sealing is refused in
code. Every number is compared against a hand transcription of the SysML equations, never against
the forensic record or a previous run.

**The environment this evidence came from,** asserted by the tests rather than reported
(`test_fusion_tea_real_teax.py`, the `environment` fixture):

- Interpreter `/home/reid/1cfe/item7-rebuild-venv/bin/python` (CPython 3.12).
- `simkit` → `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py`, TEAx pinned at
  `fa0e06a99b070346e68a3b3c29cfec546f3ac728`.
- `sysml_codegen` → `/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py`.
- `agentic_mbse` → `/home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py`.

A run that resolved any of those elsewhere fails the fixture, so the acceptance numbers cannot be
produced from the wrong tree.

**The real-TEAx evidence.** Command, exactly as run:

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/execution -m execution -q
```

**38 passed** — the 18 pre-existing execution nodes plus the 20 new ones. Measured:

| Evidence | Live | Relocated v6 |
|---|---|---|
| Published channels | 11, set pinned by name | 11, same set |
| `lcoe_calc__lcoe` | `270.1211779380445` | `270.1211779380445` |
| `meier_coe_calc__coe_cents_kwh` | `4.735403549076959` | same |
| `meier_capital_calc__total_capital_billions` | `3.303886865568384` | same |
| `meier_reactor_cost_calc__reactor_cost_billions` | `0.7304442587805375` | same |
| `recirc_calc__f_recirc` | `0.07222302470027446` | same |
| `meier_cost__gamma` (both driver instances) | `68.247088` | same |
| `meier_cost__cost_billions` (both) | `0.9749584000000001` | same |
| Constraint report | `all_satisfied`, viability margin `18.0`, `observed` `{eta: 0.35, gain_in: 80.0, threshold: 10.0}` | identical `model_dump` |

Every one of those is asserted against `tests/execution/fusion_tea_arithmetic.py`, a transcription
of `hif_economics.sysml`, `fusion_cycle.sysml`, and `ife_lcoe.sysml` typed out from the model. The
transcription is checked against the epic's headline constant as well, so a drift in the
transcription fails against `270.1211779380445` rather than silently redefining the target.

*Live vs relocated, stated precisely.* Numeric outputs and the constraint report are equal, and the
two packages carry the same `model_contract.json` `semantic_fingerprint`. Their seal
`executable_fingerprint`s **differ**, and that is correct: relocation changes each module's
`SysML Source:` provenance comment, which is the residual Slice 3B named and carried to 3E. The
test asserts the difference is confined to those comment lines, over the whole tree, with each
package's own import name neutralised so the comparison is about the model rather than the name.

*The lane is the real SimKit.* `test_the_lane_runs_the_real_simkit` asserts `simkit` resolves inside
the pinned TEAx checkout and that `tests/runtime/pipeline_runner` — whose `_install_simkit_stub`
installs a fake `simkit`, and whose `inputs=` argument has no counterpart in the real
`execute_pipeline` — was never imported into the process.
`test_the_generated_registry_is_the_public_simkit_builder` asserts the generated
`create_<package>_registry` is backed by the *identical function object*
`simkit.core.registry_builder.create_registry`, not a same-named local.

**Mutation results — every-and-only, in two legs.** Runtime injection through
`PreparedEvaluator.evaluate` / `CandidateBridge.build`, the Phase 2 protocol. Nothing is written to
disk and the same seal-verifying loader backs the evaluator, so the seal stays an active check
during the mutation.

| Mutation | Consumer ports (structural) | Observables that moved (runtime) | Hand-computed values |
|---|---|---|---|
| `hif_plant__availability` 0.9 → 0.91 (C25) | exactly `lcoe_calc.availability_in`, `meier_coe_calc.availability_in` | exactly `lcoe_calc__lcoe`, `meier_coe_calc__coe_cents_kwh` | `269.5300723203276`, `4.6833661474387505` |
| `hif_plant__thermal_efficiency` 0.43 → 0.44 (C2) | exactly `lcoe_calc.thermal_efficiency_in`, `recirc_calc.thermal_efficiency_in` | exactly `lcoe_calc__lcoe`, `recirc_calc__f_recirc` | `263.85170462810606`, `0.07058159232072277` |

Both forensic diagnostic values re-proved to the last digit, and the "nothing else" side is
enumerated rather than asserted. **Why two legs, stated plainly:** the evaluation seam projects
scalar module outputs and constraint verdicts only
(`simkit/evaluation/projection.py`), so its observable set is 5 numeric channels plus 2 constraint
responses — it does not project the two multi-output driver-cost modules' fields. The structural
leg closes that: every `(module, formal)` input port in the whole graph is partitioned into the
ports the mutated entry point feeds and the rest, and the rest is checked to contain no port of
that name. Neither leg alone would be an every-and-only claim.

**C19 — the one modelled 80.0 on both consumer paths.** `:>> gain = 80.0` at
`designs/hif_ife/hif_plant.sysml:87` reaches the calculation path as
`inputs/hif_plant_params.json`'s `hif_plant_pkg__hif_plant__gain = 80.0` (and moving the emitted
key is what `tests/runtime/test_fusion_tea_acceptance.py::test_gain_perturbation_is_consumed`
proves changes lcoe), and the constraint path as the executed predicate's `observed["gain_in"]`
`= 80.0`, with margin `0.35 * 80.0 - 10.0 = 18.0`. The graph-level C19 cell on
`nested_occurrence_override_probe` is unchanged and still owned by
`test_elaboration_spike_parity.py::test_c19_deep_path_override_reaches_both_consumers`.

**The reseal refusal, proved rather than cited.**
`test_editing_a_sealed_input_and_resealing_is_refused` copies the sealed package, edits
`inputs/hif_plant_params.json` to the C25 value, and calls the real `check_reseal_provenance`:
`ProvenanceError: codegen-produced file changed since the seal (only handwritten files may change
across a re-seal): inputs/hif_plant_params.json`. That is the route the plan calls invalid, refused
in code. `test_the_mutations_left_the_sealed_package_untouched` reloads the package after every
mutation and gets the same `executable_fingerprint` back.

**Rename review — the fifteen-item ledger, one row each.** The ledger is
`.project/active/elaborator-cutover/design.md` (D11, "Fusion Tea Migration and Generated
Consequences"); the file-level obligations are `FIX-01` in `cutover-census.md`. Every row is
**Accept**: the diff for each is exactly the binding-name change the ledger authorizes, plus the
matching formal declaration and expression references the same ledger rows require.

| ID | Definition / occurrence | Old → final | Measured diff | Verdict |
|---|---|---|---|---|
| `FT-01` | `IFE LCOE` / `lcoe_calc` | `availability` → `availability_in` | binding + formal + 2 expression refs | Accept |
| `FT-02` | same | `discount_rate` → `discount_rate_in` | binding + formal + 4 expression refs | Accept |
| `FT-03` | same | `frequency` → `frequency_in` | binding + formal + 2 expression refs | Accept |
| `FT-04` | same | `gain` → `gain_in` | binding + formal + 2 expression refs | Accept |
| `FT-05` | same | `om_cost_constant` → `om_cost_constant_in` | binding + formal + 1 expression ref | Accept |
| `FT-06` | same | `plant_cost_constant` → `plant_cost_constant_in` | binding + formal + 1 expression ref | Accept |
| `FT-07` | same | `thermal_efficiency` → `thermal_efficiency_in` | binding + formal + 1 expression ref | Accept |
| `FT-08` | `Recirculating Power Fraction` / `recirc_calc` | `gain` → `gain_in` | binding + formal + 1 expression ref | Accept |
| `FT-09` | same | `thermal_efficiency` → `thermal_efficiency_in` | binding + formal + 1 expression ref | Accept |
| `FT-10` | `Viability Threshold` / `viability` | `gain` → `gain_in` | binding + **constraint** formal + 1 predicate ref | Accept |
| `FT-11` | `Meier Reactor Cost` / `meier_reactor_cost_calc` | `thermal_power_gw` → `thermal_power_gw_in` | binding + formal + 1 expression ref | Accept |
| `FT-12` | `Meier COE` / `meier_coe_calc` | `availability` → `availability_in` | binding + formal + 1 expression ref | Accept |
| `FT-13` | same | `net_electric_power_gw` → `net_electric_power_gw_in` | binding + formal + 1 expression ref | Accept |
| `FT-14` | `Meier HIF Driver Cost` / `meier_cost` | `beam_energy_mj` → `beam_energy_mj_in` | binding + formal + 2 expression refs | Accept |
| `FT-15` | same | `num_chambers` → `num_chambers_in` | binding + formal + 1 expression ref | Accept |

The binding column counts declaration sites, not runtime usages: `meier_cost` is declared once on
the `'HIF Driver'` part definition and reached by two usages (`hif_driver_instance` and
`hif_plant.driver`), both of which show up as separate modules in the executed pipeline. Every
count above is a measured occurrence count, not an estimate.

*Zero extra hunks, checked mechanically rather than by eye.* Stripping the eleven authorized `_in`
suffixes back out of each changed model file reproduces the Item 6 content **byte for byte** in all
six files (10, 2, 3, 5, 10, and 17 changed lines respectively). No equation, default, multiplicity,
containment, or documentation line moved. `FT-10`'s formal lives on a constraint definition rather
than a calculation definition, which is what the census row means by "two calculation formals and
one constraint formal" in `fusion_cycle.sysml`.

*Why the renames are needed at all.* Recorded so the next reader does not relitigate it: `in gain =
gain` resolves its right-hand side to the calc usage's own formal, which the exact route refuses
as `SI_SELF_BINDING`. The v5 snapshot recapture makes that concrete — the viability constraint's
`gain` binding moved from `ReferenceUsage ife_plant::'IFE Power Plant'::viability::gain` (the
formal itself) to `AttributeUsage ife_plant::'IFE Power Plant'::gain` (the plant attribute the
modeller meant). The rename does not change what the model computes; it changes what the model
*says*, from a self-reference to the referent.

**Production recovered, two hunks, both with tests behind them.**

| Path | Disposition | Reason |
|---|---|---|
| `elaboration/elaborate.py` — `_enumeration_value` | **Reimplement** as `_enumeration_literal` | Slice 3C deferred this hunk as "candidate 3D material" because no fixture then exercised it. It is what the customer model needs: `:>> scope = 'CAS Scope'::shared;` is a `FeatureReferenceExpression` whose referent is an enumeration member, and the elaborator was sending it down the alias walk, producing 7 `SI_OCCURRENCE_MISSING` diagnostics that had nothing to do with the renames. Changed from the forensic version: its `SI_ID_MISSING` branch is unreachable (`declaration_id_for` already raises when `qualified_name` is `None`) and is dropped, and the surviving `declaration_id_for(referent)` call is commented as what it is — an identity gate, not a value read. The three-way literal choice is spelled as statements rather than a nested conditional expression. |
| `elaboration/project.py` — `sanitize_name(node.calc_def_name)` | **Reuse** | Slice 3B **Rejected** this exact hunk as "a product-visible module-metadata change with no test behind it". It now has one, and it is not cosmetic: `'Recirculating Power Fraction'` reaches generation as a class name and a schema filename, so without it the exact route ships `class Meier HIF Driver CostOutput(MultiOutput):`, `class TestRecirculating Power FractionRunnable:`, and `schemas/meier hif driver cost_output.py`, and the package does not import. *(Corrected after the 3D audit, F3: this row and the `848628b` commit message both named `class Recirculating Power FractionModule`, which the red state does not emit — the module class takes its name from the module type, not the calc-def name. The three strings above are measured by reverting `project.py` alone.)* It also brings the exact route onto the legacy route's spelling (`Recirculating_Power_Fraction`), which is what the census requires stay fixed. Caught by the real-TEAx test on its first run, which is the gate working. |

**Corpus, 37 paths, measured.** `scripts/run_elaboration_corpus.py` over all 37 fixtures, both
routes: legacy 36 graphs / 1 error; **exact 15 public graphs / 22 typed errors**, all 22 of them
`ElaborationError` (readiness `.findings`). Versus the amended ledger's 14/23, exactly one row
moved — `fusion_tea`, from `error: 15× SI_SELF_BINDING` to `graph 9/27/1/7`, which is census row
`B37-15` ("V6 graph after exactly 15 in-place D-5 renames"). The other 36 rows are unchanged.
`test_elaboration_corpus_ledger.py::test_dual_run_ledger_outcomes_match_a_live_corpus_run` compares
the exact per-fixture strings, so this is a full-set comparison rather than a total.

*Ledger amendment.* Row 15 of `.project/completed/20260809_elaborator-breadth/diff-ledger.md` is
updated to the measured outcome, reclassified `expected-collapse` → `expected-fix`, and the totals
block corrected (24/13; 15 graphs / 22 errors; fourteen fixtures produce graphs on both routes).
The old cell contents and their basis are retained in the row so the certified record stays
readable, the same treatment Slice 3A gave row 1. **This is not a rule-10 stop:** the census names
this outcome as the migration's expected result, so the row moving is the obligation being
discharged. Recorded here for owner visibility all the same.

*Error-class separation.* The driver records `error_type` beside the code list and reads both
`.findings` and `.diagnostics`, so `ElaborationError` and `ElaborationDiagnosticError` are never
collapsed. This corpus still exercises only `ElaborationError`; the rule binds every later driver
regardless. Worth recording: the renamed model *did* raise `ElaborationDiagnosticError` with 7
`SI_OCCURRENCE_MISSING` before the enumeration hunk landed, so the two classes were genuinely
distinguished mid-slice, not just in principle.

**B37's two carried obligations are discharged, and here is who owns each.**

- *Literal-bearing aggregation oracle* — already discharged by Slice 3B.
  `tests/conformance/test_exact_projection_aggregation.py::test_the_modelled_aggregation_is_public_and_carries_its_literal`
  owns it: `sum(module.cost) + 5.0` over three members at 10.0 each projects to a public
  aggregation module carrying the `5.0` operand, with 3 × 10.0 + 5.0 = 35.0 read off the fixture by
  hand. Two sibling tests pin per-member entry points and three-route identity.
- *Genuinely empty control* — discharged by Slice 3A.
  `tests/conformance/test_snapshot_v6_capture.py` builds a model with no calculation, no
  constraint, and no calculation definition and asserts both `build_elaborated_pipeline` and the
  capture route raise `CodeGenerationError` matching "nothing to generate".

**Test dispositions — five modules changed, nothing deleted.** Every responsibility below survives;
the specimen or the expected value moves, and the reason is recorded at the site.

| Test | Disposition | Responsibility after |
|---|---|---|
| `test_elaboration_spike_parity.py::test_fusion_tea_self_binding_fails_loud` | **Re-homed and split** | Renamed `test_self_named_binding_fails_loud`, retargeted at `self_named_binding_trap` — a fixture authored to carry that one mechanism, which the census calls the "Direct SRC-01 negative". A second test, `test_the_customer_model_carries_no_self_named_binding_after_the_d5_migration`, asserts the other half by value: fusion_tea elaborates with an empty diagnostic set and its graph carries exactly the fifteen renamed formals, read off the calc and constraint nodes. |
| `test_elaboration_contract_matrix.py::_src_01` | **Re-homed** | Same specimen change, same reason, commented at the site. The SRC-01 cell still refuses. |
| `test_elaboration_fail_closed.py::test_customer_fixture_lenient_diagnostics_are_accounted_for` | **Expected value updated** | Was 15 `SI_SELF_BINDING` + 7 `SI_OCCURRENCE_MISSING`. Now an empty diagnostic set — and, because empty would go green on an empty graph, it also pins 7 calculations, 1 constraint, and the full seven-entry map of enumeration attributes to their resolved qualified names. The seven former diagnostics and the seven resolved attributes correspond one for one. |
| `test_source_identity_routes.py` (5 tests) | **Field names updated; one assertion moved** | The Path-A silent-literal-stamp pins are unaffected in substance — the legacy route still stamps all fifteen bindings, still fans one modelled `gain` into three public fields, and still keeps the written referent — so only the formal names gained `_in`. The one substantive change is `test_reference_derived_discriminator_on_immutable_evidence`, which asserted `is_self_binding` on the live `gain` binding; that is now `not is_self_binding`, with the reason and the new SRC-01 home named in a comment. The stamp itself is unchanged: the legacy route stamps any bare reference it cannot resolve, self-named or not. |
| `test_fusion_tea_acceptance.py` | **Migrated oracle, preserved** | The four generated call sites the census authorizes: `_GAIN_EP_KEY` gains `_in`, `beam_energy_mj`/`num_chambers` gain `_in`, `gain`/`thermal_efficiency` gain `_in`. All four tests stay green, including the independently hand-computed `216.55528392479388` at gain=100 — which is a second, unrelated confirmation that the renames preserved the arithmetic. |

**Two committed artifacts regenerated, each checked against its authorized change list.**

- `tests/fixtures/golden/calc_def_compilation_golden.json`: **15 records changed**, and they are
  exactly the fifteen the design names — IFE LCOE's ten intermediates, `Meier_COE.coe_cents_kwh`,
  `Meier_HIF_Driver_Cost.{bank_energy_joules,cost_billions}`,
  `Meier_Reactor_Cost.reactor_cost_billions`, `Recirculating_Power_Fraction.fusion_cycle_gain`.
- `tests/fixtures/golden/calc_compat_parity_golden.json`: **3 records changed**, exactly the three
  the design names. `IFE_LCOE.lcoe`, `Meier_HIF_Driver_Cost.gamma`,
  `Recirculating_Power_Fraction.f_recirc`, and `Meier_Total_Capital_Cost.total_capital_billions`
  are unchanged and remain the independent arithmetic controls.
- `tests/fixtures/fusion_tea/extraction_snapshot.json`: recaptured with
  `scripts/capture_extraction_snapshots.py --fixtures fusion_tea`, so the v5 route stays live and
  `test_live_vs_snapshot_byte_identical[fusion_tea]` stays a real gate. The v5 payload is **not**
  deleted; `FIX-01`'s "delete v5" line is Phase 4 work under this plan. Only this fixture's
  `captured_at` moved.

**The customer-visible legacy package did not move in shape.** Generated from the pre-rename and
post-rename model with the shipped CLI and compared tree to tree: 48 files both times, the same four
input groups (`hif_driver_params`, `hif_plant_params`, `ife_plant_params`, `system_design`), the
same values, the same module and schema names. The only differences are the fifteen `_in` field
names, the constraint predicate IR that names one of them, and the hashes that follow. That is
exactly what census row `PROD-24` predicts ("formal-derived generated inputs change; public source
keys/module/schema names stay as design table").

**Tests, red then green.** The two new execution modules were run against the parent commit
`26e7d04` with the production and fixture changes stashed and the new test files left in place:
**19 of 20 errored**, every one at fixture setup with
`ElaborationError: SI_SELF_BINDING ×15` naming all fifteen pre-migration bindings. The one that
passed is `test_the_lane_runs_the_real_simkit`, which asserts the import environment and touches no
model — correctly green on both sides, and a guard rather than a red. After the slice: 20 passed.

**Gates.**

- Full licensed codegen suite: **3539 passed / 47 skipped / 38 deselected**, zero failures, zero
  `no live syside license` lines. Delta versus `26e7d04` (3538/47/18) is **+1 passed and +20
  deselected**. The +1 is `test_the_customer_model_carries_no_self_named_binding_after_the_d5_migration`;
  the +20 are the new `execution`-marked nodes, which `addopts = -m "not execution"` deselects from
  the default run and which the execution-lane command below runs explicitly. Skips are unchanged,
  so no Item 6 test was removed or silenced, and no test module lost a node.
- Execution lane: `pytest tests/execution -m execution` → **38 passed** (18 pre-existing + 20 new),
  zero skipped. The new tests carry no `skipif`: a missing licence or a missing `simkit` fails them.
- Full agentic-mbse suite from the paired rebuild worktree: **1825 passed / 1 skipped /
  5 deselected**, unchanged.
- 37-path corpus: 37/37 rows reproduce the amended ledger.
- Shipped legacy CLI smoke: 48-file sealed package, four input groups, values unchanged; the only
  moves are the fifteen authorized field names.
- codegen `ruff check src`: **byte-identical** to the baseline set (16 findings) — zero new. The
  four new test modules lint clean; the one pre-existing `tests/execution` finding
  (`test_constraint_execution.py:67`, E501) is unchanged, as is the pre-existing `I001` in
  `test_source_identity_routes.py`. `mypy src`: **71 errors in 17 files, identical to the `26e7d04` baseline** — re-measured at the audit follow-up after the figure below was recorded without being re-run. See the correction note in the follow-up section.
- agentic-mbse `ruff check src` and `mypy src`: not re-run against a change — nothing in that
  repository changed this slice.
- `git diff --check` clean. Changed paths equal the declared set.

**Issues and deviations.**

- **The brief expected the renames alone to make the exact route accept the customer model; they do
  not.** Measured first: the renamed model raised `ElaborationDiagnosticError` with 7
  `SI_OCCURRENCE_MISSING` on `scope` and `wall_type`, which are enumeration-value redefinitions and
  have nothing to do with self-bindings. Slice 3C had already deferred exactly that hunk to 3D as
  candidate material, so this is the deferral landing rather than a surprise. Not a rule-10 stop.
- **A second production hunk was needed that the brief did not name:** `sanitize_name` on
  `calc_def_name`. Slice 3B rejected it for want of a test; the real-TEAx test is that test, and
  the failure it produced was a package that would not import.
- **`test_exact_route_generated_package.py` was not extended to fusion_tea.** It stays on
  `source_identity_mixed_consumers`, and the fusion_tea live-vs-relocated comparison lives in the
  new execution module instead, because it needs a sealed package and a real run. The two tests
  make the same claim about the differing-file set on two fixtures.
- **No public exact-route `generate` entry point was added.** `tests/execution/real_teax.py` runs
  the same step sequence `cmd_generate` runs, ending at `_seal_package`, for the reason Slice 3B
  recorded: a second public flag before the 3E authority switch is the dual authority this plan
  bans. That is a real limit on how "public" this route's generation half is today, and it is 3E's
  work to close, not 3D's.
- No deletions in either repository. No Item 6 test was removed, silenced, or deselected.

#### Slice 3D audit follow-up — F1 through F5

- **Completed:** 2026-08-11
- **Audit:** `evidence/audit-3d.md`, verdict **CERTIFY** (nothing blocked 3E), 5 findings.
  Recorded at `d78788f`. Commit: PENDING_3D_FU
- **Declared path set:** `src/sysml_codegen/elaboration/elaborate.py`,
  `tests/execution/test_fusion_tea_real_teax.py`, `tests/execution/fusion_tea_arithmetic.py`, and
  this plan. Actual changed paths equal that set.

All five findings are closed. One changed production, two strengthened tests, one corrected a test
docstring, one corrected this plan.

**F1 (Medium) — the mypy gate was recorded without being re-run, and it was wrong.** The 3D notes
said `mypy src`: error set **identical** (71 errors in 17 files). The measured truth at `848628b`
was **72 errors in 18 files**. The extra one is this slice's:

```
src/sysml_codegen/elaboration/elaborate.py:628: error: Incompatible types in assignment
(expression has type "float | int | str | None", variable has type "str")  [assignment]
```

`literal` takes its type from the first branch, where `enumeration_literal` is narrowed to `str`,
so the `elif` branch's wider `extract_literal_value` return no longer fits. Fixed by annotating the
target — `literal: float | int | str | None` — ahead of the branch, which is what the variable has
always actually held. No runtime behavior changes.

**Say it plainly: the number in the notes was carried over from the previous slice's baseline
rather than measured against the final tree.** Every other 3D gate figure was re-run; this one was
not, and the notes stated it as if it had been. That is the self-certification failure mode this
whole recovery exists to close, and it got into a slice whose own contract is that written claims
survive being checked. Recorded here rather than quietly overwritten.

Re-measured after the fix, with only the two production files swapped between commits and
everything else held fixed:

| tree | `mypy src` |
|---|---|
| `26e7d04` (parent) | 71 errors in 17 files (86 source files checked) |
| `848628b` (as committed) | 72 errors in 18 files |
| this follow-up | **71 errors in 17 files — line-for-line identical to the `26e7d04` baseline** |

The 3D gates block above now carries the measured figure and a pointer to this note.

**F2 (Low) — the live/relocated confinement assertion now matches the claim it backs.** It compared
one direction (`live_lines - relocated_lines`) over three file suffixes, while the prose said the
difference was confined "over the whole tree". Two changes:

- The difference set is symmetric, `(live - relocated) | (relocated - live)`. A line the relocated
  package carries and the live one does not is just as much a divergence, and the one-sided form
  would have let it through whenever a provenance line also differed.
- `tree()` now takes every file rather than `.py`/`.yaml`/`.md`, so the JSON contracts and the
  emitted entry-point payloads — exactly where a real divergence would hide — are inside the
  comparison. `contracts/package_contract.json` is excused **by name, alone, and with the reason at
  the site**: it is a hash manifest over the tree, so it restates every difference below it as a
  changed digest and can carry no independent information. The test asserts it is present and that
  it does differ, so the excuse cannot silently stop applying.

Green with the wider, bidirectional form, which is the same comparison the auditor ran
independently: outside the seal, the only lines differing in either direction are `SysML Source:`
comments.

**F3 (Low) — the red-state specimen is corrected.** The 3D notes and the `848628b` commit message
both said that without the `sanitize_name` hunk the exact route ships
`class Recirculating Power FractionModule`. It does not: the module class takes its name from the
module type, not the calc-def name. Measured by reverting `project.py` alone, the red state ships
`class Meier HIF Driver CostOutput(MultiOutput):`,
`class TestRecirculating Power FractionRunnable:`, and `schemas/meier hif driver cost_output.py`.
The conclusion is unchanged — the package does not import, and 11 of the 12 real-TEAx tests error
without the hunk. History is not rewritten; the disposition row above carries the correction.

**F4 (Informational) — the transcription docstring pointed at the wrong file.**
`tests/execution/fusion_tea_arithmetic.py` credited `designs/generic_ife/ife_subsystems.sysml` with
the blanket multiple 1.15, yield cost 5e6, target cost 10.0, and target-factory cost 0.1. That file
declares those attributes and assigns none of them; all four values live in
`designs/hif_ife/hif_plant.sysml` (`:63-64` on `chamber`, `:48` on `target_factory`, `:202` inside
`meier_capital_calc`). The numbers were right, the pointer was not — which matters because the
module's stated purpose is to be checkable from the model files alone. Corrected with line
references, and `ife_subsystems.sysml` is now named as declaring-only.

**F5 (Informational) — the constraint report is pinned as a whole dump.** It was asserted field by
field, so an added field would have slipped through. It now compares the full
`model_dump(mode="json")` against a literal expectation whose every value is derived from the model
(margin still computed, not read back). `catalog_fingerprint` is popped and checked for shape — 64
lowercase hex characters — rather than by value, because it is a digest of the catalog with nothing
to derive it from by hand. Recorded rather than left as the auditor's optional: the report is the
constraint route's public surface, and a field-by-field pin does not say "and nothing else".

**Gates.** Execution lane `pytest tests/execution -m execution`: **38 passed**, unchanged in count —
F2 and F5 strengthened existing assertions rather than adding nodes. Full licensed codegen suite
**3539 passed / 47 skipped / 38 deselected**, zero failures, zero `no live syside license` lines —
delta versus `848628b` is **zero on every axis**, since no test node was added or removed. Full
agentic-mbse suite from the paired worktree: **1825 passed / 1 skipped / 5 deselected**, unchanged;
nothing in that repository changed. `ruff check src` byte-identical to the baseline set (16
findings) and the two changed test modules lint clean. `mypy src` **71 errors in 17 files, measured,
identical to the `26e7d04` baseline**. `git diff --check` clean. Changed paths equal the declared
set.

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
