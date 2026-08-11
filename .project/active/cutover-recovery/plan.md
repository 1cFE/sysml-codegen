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
- [x] Phase 3 — Rebuild and commit the cutover as functional vertical slices
- [ ] Phase 4 — Retire production, tests/probes/snapshots, and docs under separate gates
      — **RESEQUENCED**: retirement steps 1–4 move behind the Phase 5 owner stop; Phase 4 owns
      G0+G1 (done) plus the full disposition preparation. See the ruling at the head of Phase 4.
- [ ] Phase 5 — Assemble a repeatable candidate, audit it, and stop for owner acceptance
      — now also presents the fully-prepared retirement as the headline decision

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

- [x] Write public import/CLI tests proving all supported callers use the exact route and no public
  flag exposes two authorities. `tests/conformance/test_public_authority_switch.py`, 18 tests.
- [x] Switch public callers without deleting the unreachable legacy implementation. `run_codegen`
  and `cmd_snapshot` moved; `pipeline_builder.py`, `snapshot_context.py`, the v5 loader,
  `graph_rebuild.py` and `capture_snapshot` are all untouched and still importable.
- [x] Repeat the full corpus, original suites, generated package comparison, and real TEAx.
  Corpus **15 graphs / 22 typed errors, zero rows moved**. Comparison:
  `evidence/3e-package-comparison.md`. Real TEAx through the switched public surface: 38 passed.
- [x] Commit the authority switch separately from all deletion. Nothing was deleted this slice.
- [x] **[AGENT] (orchestrator rulings, 2026-08-11)** Five rulings carried in and applied; recorded
  verbatim enough to audit in the completion notes below.

### Validation for every Phase 3 slice

Reconciled once in Slice 3E **[AGENT] (orchestrator ruling 3, 2026-08-11)**. The checklist had
been left unticked for 3A–3D even where the work was demonstrably done, so each box below now
carries a per-slice evidence pointer, and anything not actually done is marked as such rather
than ticked. The evidence lives in the per-slice completion notes and `evidence/audit-3{a,b,c,d}.md`.

**Automated**

- [x] Start from clean status and record the declared path set. — 3A "Deviation from the brief's
  candidate path list"; 3B, 3C, 3D, 3E "Declared path set" bullets. 3B and 3C each declared two
  paths mid-slice and named them as deviations.
- [x] Run slice-focused tests red before production changes and green afterward. — 3A "Tests, red
  then green" (5 modules failed to collect at `beee0f4`); 3B same section as corrected by audit F4
  (4 failed to collect + 4 failed/8 passed); 3C (5 red of 8 codegen, 3 red of 5 agentic, measured
  red output quoted); 3D (19 of 20 errored at `26e7d04`); 3E "Tests, red then green" below.
- [x] Run the original full suites; record and explain collection-count deltas. — every slice's
  "Gates" block states the delta and its cause: 3A +104 then +11, 3B +46 then +1, 3C +8 then +10
  codegen and +5 then +1 agentic, 3D +1 passed / +20 deselected, 3E +18.
- [x] Run Ruff, mypy baseline comparison, and `git diff --check` on both repositories as
  applicable. — every "Gates" block. **One honest exception:** 3D recorded mypy without re-running
  it and the figure was wrong; caught and corrected by the 3D audit (F1), which is why the box is
  ticked against the follow-up rather than against `848628b`.
- [x] Assert actual changed paths are a subset of the declared path set. — stated as "Changed paths
  equal the declared set" in every slice's Gates block, which is the stronger claim.

**Manual**

- [x] Inspect the complete slice diff before commit, including generated/deleted path summaries. —
  evidenced by the per-file disposition tables in 3A, 3B, 3C and 3D, each of which is a per-hunk
  reading of the diff. No slice deleted a path.
- [x] Open at least one public generated artifact and compare it with the hand/model expectation. —
  3A (`hif_driver__HIF_Driver__efficiency = 0.35` traced to `hif_driver.sysml:81`); 3B
  (`:>> efficiency = 0.75;` at `model.sysml:234`); 3C (the rendered
  `exactcalcordering__rig__split` auto-implementation against the fixture's hand arithmetic);
  3D (the whole real-TEAx table against `fusion_tea_arithmetic.py`); 3E
  (`evidence/3e-package-comparison.md`, whole-tree).
- [x] Confirm no docs, spikes, probes, unrelated tests, or snapshots changed accidentally. — the
  declared-path-set equality in each Gates block is this check. Two deliberate exceptions, both
  recorded at the time: 3A and 3D each amended
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md` under the B37-01 owner
  pre-ruling, and 3E amends rows 12 and 36 under orchestrator ruling 1.
- [x] **[OWNER 2026-08-10]** After each slice commit, an independent audit agent (fresh session,
  not the implementer) reviews the slice diff, tests, and evidence against this plan's slice
  contract. Audit findings are resolved before the next slice begins. — 3A `evidence/audit-3a.md`
  (FINDINGS, 3 closed at `4858911`); 3B `audit-3b.md` (CERTIFY, 7 closed at `2f28dde`); 3C
  `audit-3c.md` (CERTIFY, 4 closed at `a6c41bc`/`cc6c7a7`); 3D `audit-3d.md` (CERTIFY, 5 closed at
  `fa4eea0`). **3E's audit has not run yet** — it is the next action after this slice's commit.

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
| 3D | 848628b, audit follow-up fa4eea0 | N/A (untouched, clean at `cc6c7a7`) | codegen 3539 passed / 47 skipped / 38 deselected (+1 passed, +20 deselected — all new); agentic 1825 passed / 1 skipped / 5 deselected (unchanged) | **PASS** — 20 real-TEAx tests, live + relocated-v6 sealed packages, 11 outputs each, LCOE `270.1211779380445` |
| 3E | 430e26a, audit follow-up c48c132 | N/A (untouched, clean at `cc6c7a7`) | codegen 3557 passed / 47 skipped / 38 deselected (+18, all new); agentic 1825 passed / 1 skipped / 5 deselected (unchanged) | **PASS** — 38 execution nodes through the SWITCHED public `run_codegen`, live + relocated-v6, 11 channels each, LCOE `270.1211779380445` |

---

## Phase 4 — Controlled Retirement and Documentation Repair

> ### ⚠ RESEQUENCING RULING — retirement moves behind the owner stop (2026-08-11)
>
> **[ORCHESTRATOR]** ruling, recorded under the rule-11 delegation. Read this before any
> retirement work; it changes what Phase 4 is for.
>
> **Phase 4's retirement steps 1–4 (the v5 family, G2′, G3′, G4′) do not execute in Phase 4.**
> They are resequenced to the **immediate post-acceptance step after the Phase 5 owner stop**.
>
> **Why.** The 37 v5 fixture rows name `tests/conformance/test_v6_recapture_batch.py` as their
> replacement proof. Gate 4C part 4 recorded that batch as **PROPOSED** and "authority for
> nothing" — acceptance is the owner's, reserved for the Phase 5 stop by the owner's own
> instruction (ping only at final). Gate 4C's rule is that the v5 snapshots stay until their
> **accepted** v6 replacements are ready in the same candidate. Executing the retirement now
> would spend an acceptance nobody has given. A stage brief that ordered steps 1–4 was refused
> on exactly this ground and the refusal was ratified; the record is below.
>
> **Revised shape.**
>
> | Phase | What it now owns |
> |---|---|
> | **Phase 4** | G0 + G1 (executed) + the **full disposition preparation** — Gate 4C part 7 and Gate 4D. Deletes nothing further. |
> | **Phase 5** | Assembles the candidate with the legacy stack **present-but-unreachable** (the 3E pins define that state and stay green), presents the PROPOSED batch **and the fully-prepared retirement** as the headline decision at the owner stop. |
> | **Post-acceptance** | The retirement executes as the immediate next step, with every battery intact. |
>
> This satisfies both plan clauses at once: accepted-replacements-before-v5-deletion, and the
> final candidate decision resting with the owner.
>
> **Standing consequence — option (a) is closed.** No node retires without per-file replacement
> proof or a recorded per-node disposition. Wholesale `retire-with-owner` over an undispositioned
> blast radius is **refused permanently** for the rest of this recovery.

### Goal

Remove only the superseded production authorities proven unnecessary by Phase 3. Treat production
code, test responsibilities, historical probes, committed snapshots, and documentation as separate
decisions and separate commits.

**Amended by the resequencing ruling above:** in Phase 4 that means *preparing* every retirement
decision to the point where executing it is mechanical. The execution itself is post-acceptance.

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

- [x] Start from the Item 6 path inventory, current Phase 3 tree, original tests, and actual public
  call graph. Import the 54 explicit `delete` rows as presumptively valid proposals because the
  forensic reconciliation found no execution surprises in that class. Recheck their authority,
  reachability, and replacement proof before approval. Re-derive every `migrate`, group-covered,
  and no-row disposition from scratch.
- [x] Generate the candidate inventory from `git diff --name-status <item6-base>` plus untracked
  paths. Require exact equality between that Git-derived set and the reviewed disposition set.
- [x] **Carried ledger inputs from Phase 3.** These are named here so the module deletion sweeps
  them rather than leaving them behind:
  - The eight retained transitional duals recorded in the Slice 3C completion notes. Each is one
    behavior under two names; deleting the legacy member and dropping the `Exact`/`identified`
    qualifier from the survivor is the Phase 4 half of that slice.
  - `_CONSTRAINT_LOGGER = logging.getLogger("sysml_codegen.analysis.constraint_lowering")`
    (`src/sysml_codegen/elaboration/project.py:83`). A string, not an import — it predates Item 7
    (`b9c22c0`) and does not weaken the exact route's decoupling, but left alone it becomes a
    logger named after a module that no longer exists. Retire the name with the module.
    **[AGENT]** raised as F4 of the Slice 3C audit (`evidence/audit-3c.md`), informational.
  - **Dead v5 residue inside the public writer**, both in `src/sysml_codegen/cli/__init__.py` and
    both unreachable since the Slice 3E switch: the `GrandfatheredSnapshotError` import (`:1061`)
    and the handler that catches it inside `_generate_package_from_graph` (`:1139`). Its only
    raiser is `assert_snapshot_certifiable`, which the public route no longer calls and which the
    legacy test adapter calls *before* that function. Retire both with the v5 route.
    **[AGENT]** raised as F5 of the Slice 3E audit (`evidence/audit-3e.md`), low.
  - **`sysml_codegen.orchestration.__init__`'s re-export of `build_pipeline_context`**, and the
    v5 re-exports in `snapshot/__init__.py` that keep `pipeline_builder`, `snapshot.loader` and
    `snapshot.graph_rebuild` inside `sysml_codegen.cli`'s transitive import closure. Nothing is
    constructed through them — the construction closure is clean — but they are the whole of the
    named import residual, pinned by
    `test_the_generation_half_still_reaches_v5_modules_and_that_residual_is_pinned`. Phase 4
    empties that pin.
- [x] For every proposed production deletion, name the public behavior and kept test that prove its
  replacement.
- [x] For every proposed test deletion or rewrite, state the behavior responsibility, replacement
  node, and why keeping the old test is impossible or misleading.
- [x] Implement and test `replacement_is_green(row)`: every deleted or migrated test row names an
  exact replacement node that exists, collects, and passes in the required suite. Add negative
  tests for a missing node, a deselected node, and a failing node. Absence-only checks cannot make
  this gate green.
- [x] Present the exact production, test, snapshot, probe, and doc lists to the owner. No broad
  catch-all rows.
- [x] Commit the ledger before deletion. Approval is the orchestrator's review, which has not happened yet.

### Gate 4B — Delete legacy production in small groups

- [x] **Read the Gate 4C responsibility rows before deleting anything.** Sixteen rows carried from
  Slice 3E block this gate: no legacy production owner may be deleted while a row it serves still
  lacks its exact-route replacement, and `replacement_is_green(row)` is the check. The rows and the
  blocking language live in Gate 4C below; they govern *this* gate.
  **[AGENT]** added after the Slice 3E audit (F6b), which found the constraint stated only in 4C —
  i.e. only after the deletions it governs.
- [x] **G0 and G1 executed** (`db00482`, `6ba346e`). These are the whole of 4B's deletion in Phase 4.
- [ ] **POST-ACCEPTANCE, not Phase 4** — per the resequencing ruling at the head of this phase.
  Delete one coherent production owner group at a time, beginning with unreachable adapters and
  ending with the central legacy resolver/registry/snapshot owners. Order: v5 family → G2′ → G3′ → G4′.
- [ ] **POST-ACCEPTANCE.** Before each group, add or identify kept public tests that fail if its
  responsibility is lost. Gate 4C part 7 is where those are authored, so this reduces to *identify*.
- [ ] **POST-ACCEPTANCE.** Run the complete public corpus and real TEAx after each group.
- [ ] **POST-ACCEPTANCE.** Commit each deletion group separately. Do not include tests, docs,
  snapshots, or probes except an already-approved test migration necessary for that exact group.

### Gate 4C — Review tests, probes, and snapshots

- [ ] **Carried from Slice 3E: sixteen responsibility rows, and a hard gate on 4B.** The authority
  switch left 100 test nodes across 16 modules running against the legacy implementation, because
  their *specimens* are what the cutover retires — a v5-only snapshot, or a fixture the exact route
  refuses on a ratified `expected-collapse` row. Every row is in the Slice 3E completion notes with
  its behavior responsibility, why the specimen cannot survive, and the Gate 4C owner that must
  author an exact-route specimen for it.
  **Gate 4B may not delete a legacy production owner while any row that owner serves still lacks
  its exact-route replacement.** These rows are inputs to `replacement_is_green(row)`: a row is
  green only when a named exact-route node exists, collects, and passes. Absence scanning cannot
  make it green, and neither can the legacy node still passing.
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
- [ ] **Carried from Gate 4C (S4 ruling, 2026-08-11): document the aggregation modelling
  requirement the exact route imposes.** An assembly cannot write
  `sum(a.capital_cost) + sum(b.capital_cost)`: the projection names an expression parameter
  after the reference's last member and drops the qualifier, so two terms reading a same-named
  attribute off different children both render `capital_cost` and the model is refused with
  `SI_RENDERING_COLLISION`. The refusal is correct recovery-era behaviour — a silent collapse
  is the incident again — but no document states the requirement, and every child of a costed
  assembly exposes the same attribute names by construction. The subject must give the working
  idiom: one named intermediate attribute per child role (`panel_capital`, `caster_capital`),
  added by the rollup. Worked example: `tests/fixtures/costed_cart_d5/library.sysml`. Refusal
  pinned by `test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_is_refused`.
  Cross-reference: this is the filed Item 10 cross-part `child.attr` collapse class, where the
  resolver does not follow per-child `:>>` redefinitions.
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

- [ ] **The headline decision at the owner stop, per the Phase 4 resequencing ruling.** Present
  together: the PROPOSED v6 recapture batch (15 captured / 22 typed refusals), and the
  **fully-prepared retirement** — every one of the 4B groups with a per-file disposition and a
  green replacement proof, so that acceptance makes the retirement mechanical. State plainly that
  the candidate ships with the legacy stack **present-but-unreachable**, and name the 3E pins that
  hold that property.
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

- **Completed:** 2026-08-11 — all five slices done and independently audited (3A FINDINGS then closed; 3B, 3C, 3D, 3E CERTIFY). Phase 3 complete.
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
  Recorded at `d78788f`. Commit: fa4eea0
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

#### Slice 3E Completion — Public authority switch

- **Completed:** 2026-08-11
- **Commit:** 430e26a (sysml-codegen only; agentic-mbse `N/A` — nothing changed there, and its
  suite was still run from the paired worktree: 1825 passed / 1 skipped / 5 deselected, unchanged)
- **Declared path set, sysml-codegen:** `src/sysml_codegen/cli/__init__.py`,
  `src/sysml_codegen/snapshot/envelope.py`; new `tests/conformance/test_public_authority_switch.py`,
  `tests/helpers/legacy_route.py`, `tests/fixtures/fusion_tea/instance_graph_snapshot.json`;
  `tests/fixtures/fusion_tea/README.md`; the sixteen repointed test modules and the six
  helper-signature call-site modules named in the tables below;
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md`; this plan,
  `briefs/phase3e.md`, and `evidence/3e-package-comparison.md`. **Plus three modules named
  explicitly after the Slice 3E audit (F6a), which found them changed but not nameable from any
  table:** `tests/conformance/test_snapshot_v6_envelope.py` (a message-match update following the
  `envelope.py` change) and `tests/execution/{test_fusion_tea_real_teax,test_fusion_tea_mutation_teax}.py`
  (helper-rename call sites). 41 changed paths, all named.

**What switched.** `run_codegen` is now the single public generation authority and constructs
exactly one way: `--models` seals an `ExactPipelineContext` from live elaboration,
`--from-snapshot` seals one from a v6 instance-graph snapshot. Two *sources*, one authority.
`cmd_snapshot` captures v6 (`capture_instance_graph_snapshot`), so the CLI no longer emits a
format its own `generate` refuses. Nothing was deleted: `pipeline_builder.py`,
`snapshot_context.py`, `snapshot/loader.py`, `snapshot/graph_rebuild.py` and `capture_snapshot`
are byte-unchanged and still importable, which is Phase 4's ledger to spend.

**How single authority is proven, by behaviour rather than by spelling.** A test asserting "the
CLI imports the exact builder" passes the moment the import exists. These do not:

- `d38_caret` ships *different packages* on the two routes. Through the public CLI it now emits
  `inputs/library_params.json` with six parameters; the legacy route emits
  `inputs/design_params.json` with one. Both arms are measured in the same module, so the
  discriminator is proven to discriminate.
- `chain_spike_model` — ledger row 7, three self-named bindings — is now *refused* by the public
  CLI and still generated by the legacy route. A public refusal is a public behaviour.
- A v6 snapshot captured by `sysml-codegen snapshot` round-trips through
  `generate --from-snapshot` to the same package.
- The construction closure is clean **transitively**, not just at the CLI's own import line:
  nothing reachable from `orchestration/exact_pipeline_context.py` imports
  `pipeline_builder`, `snapshot_context`, `snapshot.loader`, `snapshot.graph_rebuild`, or
  `analysis/constraint_lowering.py`.
- The flag surface is enumerated. Every subcommand's `--help` is scanned for a route-selecting
  flag, `GenerationConfig`'s fields are pinned by value, `cli.__all__` is pinned by value, and no
  `SYSML_CODEGEN*` environment variable is read.

**One residual, stated rather than rounded down.** `sysml_codegen.cli`'s *transitive* import
closure still contains `pipeline_builder`, `snapshot.loader` and `snapshot.graph_rebuild`, because
`snapshot/__init__.py` re-exports the v5 machinery and the CLI imports that package for other
reasons. Nothing there is constructed through — the check above proves the construction closure is
clean — but importable is importable, and this slice's own contract is that written claims survive
checking. Pinned by name in `test_the_generation_half_still_reaches_v5_modules_and_that_residual_is_pinned`
so it cannot quietly grow. `orchestration/__init__.py` likewise still re-exports
`build_pipeline_context`. Both are Gate 4A ledger inputs; Phase 4 empties them.

**Production diff, three files, each with its reason.**

| Path | Change | Why |
|---|---|---|
| `cli/__init__.py` — `run_codegen` | Constructs through `build_exact_pipeline_context` / `build_exact_pipeline_context_from_snapshot`, reads `computation_graph` **once**, then calls the writer. | The switch. The single read matters: on the exact route every `.computation_graph` access re-decodes and re-projects, so passing the context down would assemble one package out of ten separately derived graphs. |
| `cli/__init__.py` — `_generate_package_from_graph` | The write-and-seal half, split out, taking a `ComputationGraph`. Private; not in `__all__`. | Authority-neutral by construction: it takes a graph and chooses nothing, so `run_codegen` is the only thing that decides. It is also the seam the retired-specimen tests drive; Phase 4 removes those callers with the legacy owners. |
| `cli/__init__.py` — the nine `_generate_*` / `_seal_package` / `_preflight_constraint_names` helpers | Take `graph: ComputationGraph` instead of `ctx: PipelineContext`. | They only ever read `ctx.computation_graph`. Taking the graph is the honest signature and removes the repeated re-projection above. |
| `cli/__init__.py` — elaboration refusals | `ElaborationError` and `ElaborationDiagnosticError` are caught **separately** and logged with different messages. | Neither is a `CodeGenerationError`, so before this they escaped to the bottom `except Exception` and were reported as "Unexpected error". Keeping the two classes distinct in the log is the same rule the corpus driver follows: readiness findings and validation diagnostics are different answers. |
| `cli/__init__.py` — `--design-path-filter` | Typed refusal naming why, on both `generate` and `snapshot`. | Orchestrator ruling 3. The flag selects which design files the *legacy* deriver reads; the exact route derives groups from the instance graph, where it has no meaning. Honouring it is impossible and ignoring it would silently ship a package the operator did not ask for. The now-false "baked into the snapshot at capture" message is gone. Flag removal is Phase 4's. |
| `cli/__init__.py` — `cmd_snapshot` | Captures v6. | Orchestrator ruling 4. |
| `snapshot/envelope.py` — `_validate_version` | Names the format actually found. | A v5 document carries no `version` key, so the old message reported `None` and left the reader guessing. It now reads "this is a v5 extraction snapshot, but the instance-graph route requires snapshot v6. Recapture with `sysml-codegen snapshot`." |

**Tests, red then green.** `test_public_authority_switch.py` cannot collect at `0a812af` at all —
it imports `tests.helpers.legacy_route`, which imports `_generate_package_from_graph`, which does
not exist there. Measured red at HEAD by the switch's own construction: before the production
change, the module's discriminator tests fail on the legacy answer (`design_params` where the
exact route ships `library_params`), the v5 refusal test fails because the CLI accepts v5, and the
`--design-path-filter` test fails because the flag is silently honoured. After: **18 passed**.

**Test dispositions — 116 nodes moved, nothing deleted.** Measured by applying the switch and
running the full suite before writing any disposition: **69 failed + 47 errors = 116 nodes**, and
every one is accounted for below. The three groups are the measurement, not a category invented
afterwards.

*Group C — patch target or signature moved (16 nodes). Mechanical; responsibility unchanged, and
two of them got stronger.*

| Module | Nodes | Disposition |
|---|---:|---|
| `tests/unit/test_cli_generation.py` | 10 | Monkeypatched `pipeline_builder.build_pipeline_context` to return a `SimpleNamespace` context. **The monkeypatch is now gone entirely**: these are writer-half tests, so they call `_generate_package_from_graph` with the graph they were already building. Strictly better — they exercise the real function instead of a fabricated stand-in. |
| `tests/conformance/test_constraint_profile_route_parity.py` | 5 | Forged-identity fail-before-mutate specimen. Repointed at the legacy route; see ruling 5 below. |
| `tests/unit/test_elaboration_import_boundaries.py` | 1 | `test_shipped_cli_and_capture_remain_on_the_legacy_black_box_route` **inverted, not deleted**, and renamed `test_the_shipped_cli_is_on_the_exact_route_and_the_legacy_owners_are_unreachable`. Its docstring records the old expectation and why it was right until this slice. |

*Groups A and B — the specimen is what the cutover retires (100 nodes across 16 modules).*
**[AGENT] (orchestrator ruling 1, 2026-08-11): repoint, with teeth.** Each row names the
responsibility, why the specimen cannot survive, the Gate 4C owner that must author an exact-route
specimen before the legacy owner is deleted, and the repointed target. All 16 rows are carried into
Gate 4C above as a hard gate on 4B.

| Module | Nodes | Behaviour responsibility | Why the specimen dies | Gate 4C owner must author | Repointed to |
|---|---:|---|---|---|---|
| `integration/test_costed_component_e2e.py` | 25 | Costed-component pattern end to end: leaf costs, allocation, idiot_index aggregation, zero backlog, numerical ground truth | `solar_battery_model` — 24× `SI_SELF_BINDING`, ledger row 33 | A D-5-form costed-component fixture with the same aggregation shape | `generate_via_legacy_route` |
| `integration/test_computed_attributes_e2e.py` | 8 of 21 | FORMULA computed attributes reach modules, wiring and YAML | `solar_battery_model`, `catf_mfe_model`, `chain_spike_model` — rows 33, 5, 7 | A computed-attribute fixture on the exact route | same |
| `integration/test_expression_compilation_e2e.py` | 16 of 17 | Auto-implementation classification, stub fallback, backlog contents, expression ground truth | rows 33, 5, 7 | An expression-compilation fixture on the exact route | same |
| `integration/test_full_pipeline.py` | 4 of 20 | `run_codegen` phase sequence, design params JSON, exit-point schema types | `chain_spike_model`, row 7 | Phase-sequence coverage on an accepted fixture | same |
| `integration/test_hierarchy_e2e.py` | 3 of 17 | BF3–BF5 aggregation wrappers, instance-scoped paths, YAML artifacts | `solar_battery_model`, row 33 | A hierarchy fixture on the exact route | same |
| `conformance/test_snapshot_generation.py` | 12 of 16 | Licence-free offline generation; no provenance leakage into artifacts; live-vs-snapshot byte identity | v5 `--from-snapshot`, plus rows 33, 7, 18, 23, 3 | The same three claims for v6 | `_run_legacy` subprocess |
| `conformance/test_seal_step9.py` | 9 of 13 | Seal step 9: three contract files, manifest, coverage policy | v5 snapshot of `chain_spike_model`, row 7 | Seal coverage on a v6 package | `generate_via_legacy_route` |
| `unit/test_warning_reconciliation.py` | 5 | Warning reconciliation categories and alias-collision collapse | v5 snapshot; `chain_spike_model`, `solar_battery_model` | Reconciliation on the exact route | same |
| `conformance/test_fingerprint_stability.py` | 4 | Fingerprint stability across independent generations and live-vs-snapshot | v5 snapshot | v6 fingerprint stability | `generate_via_legacy_route` + subprocess |
| `runtime/test_fusion_tea_acceptance.py` | 4 | The migrated hand-arithmetic customer oracle | v5 snapshot **only** | — **discharged in this slice**, see ruling 2 | shipped `run_codegen`, v6 |
| `conformance/test_gen_registry.py` | 2 of 22 | Registry generation across module kinds | v5 snapshot; rows 5, 7, 33 | Registry coverage on the exact route | `generate_via_legacy_route` |
| `conformance/test_alias_agg_probe_generation.py` | 2 | Alias-aggregation probe generation | `alias_agg_probe`, `issue22_model` — rows 3, 20 | An alias-aggregation fixture on the exact route | same |
| `conformance/test_constraint_snapshot_portability.py` | 2 of 3 | Constraint portability live vs replay | `catf_mfe_model`, row 5 | Portability on a v6 pair | same |
| `conformance/test_whole_tree_portability.py` | 1 of 2 | Whole-tree checkout-root portability | `catf_mfe_model`, row 5 | Portability on the exact route | same |
| `runtime/test_pipeline_runner.py` | 2 | In-repo runner input override | v5 snapshot of `spec_chain_twolevel`, row 35 | — superseded by the real-TEAx mutation lane (3D) | same |
| `unit/test_uncovered_params.py` | 1 of 10 | V11 seeded strict-generation abort | v5 snapshot | V11 abort on the exact route | same |

The adapter is `tests/helpers/legacy_route.py`. Its module docstring states what it is and is not:
a test-only adapter, deliberately not a second product route, that keeps retired specimens running
against the implementation that still understands them. Where a subject genuinely needs a
subprocess — licence-free generation, byte identity between two independent processes — it keeps
one, via `python -m tests.helpers.legacy_route`, rather than being quietly downgraded to an
in-process call.

*Eight further modules changed only because the generation helpers now take a graph, or because a
message they match moved:*
`test_exact_route_generated_package.py`, `test_constraint_generation_live.py`,
`test_constraint_generation_integration.py`, `test_module_kind_faildloud.py`,
`test_gen_stencils.py` (a static-analysis pin on the parameter name), `tests/unit/test_stencils.py`,
`tests/conformance/test_snapshot_v6_envelope.py`, and
`tests/execution/{real_teax,test_constraint_execution,test_fusion_tea_real_teax,test_fusion_tea_mutation_teax}.py`.
No responsibility moved. *(Count and membership corrected after the 3E audit, F6a: the sentence
said "six" and named eight, and omitted three of the modules it should have listed.)*

**Ruling 2 — the customer oracle is back on the shipped public route.**
`tests/fixtures/fusion_tea/instance_graph_snapshot.json` is committed and
`test_fusion_tea_acceptance.py` now generates from it through `run_codegen --from-snapshot`. The
fixture README marks it plainly as **a test fixture, not the accepted corpus recapture batch**,
which stays Phase 5 / owner territory. One expected value moved and the reason is recorded at the
site: `_GAIN_EP_KEY` is now `hif_plant_pkg__hif_plant__gain` rather than
`hif_plant_pkg__hif_plant__lcoe_calc__gain_in`, because the exact route mints one key per modelled
attribute instead of one per consuming formal. The independently hand-computed
`216.55528392479388` at gain=100 is unchanged, which is a second confirmation that the collapse
preserved the arithmetic.

**Ruling 5 — fail-before-mutate is re-pinned on the new authority, not just repointed.** Two new
specimens that reach the guard through public `generate`:

- `test_an_elaboration_refusal_leaves_an_existing_output_tree_untouched` — `chain_spike_model` is
  refused during construction, and a populated output tree (including a handwritten file) is
  byte-unchanged afterwards.
- `test_a_refusal_after_the_context_but_before_the_writer_also_leaves_the_tree` — the refusal is
  injected at the `_reconcile_params_coverage` boundary, which is *after* construction and *before*
  `_clear_output_directory`. This one pins the **ordering**: the tree is safe only because no
  writer runs before those checks.

The forged-identity specimen is retired with a disposition and the reason is a measurement, not an
argument: it forged an `IdentityFact` on the neutral `ConstraintFacts` that
`analysis/constraint_lowering.py` consumes, then monkeypatched `build_pipeline_context`. Both
halves live on modules the construction closure does not import, so the exact route produces no
such refusal to observe. Recorded in
`test_the_construction_path_reaches_no_legacy_authority_even_transitively`.

**Ruling 1's two named divergences are now expected-state pins.** Diff-ledger rows 12 and 36 carry
measured before/after **shipped-package** cells with the old cells retained, and the two tests in
`test_exact_group_identity.py` no longer say "needs a disposition before Slice 3E" — they say the
disposition was made and this is what the product ships. Both are flagged to the Phase 5 owner
packet. `unresolvable_attr_probe` turned up one thing worth naming: on the exact route it now
reaches generation and the generator's module-class collision guard **refuses the package**,
because two of the nine formulas legacy dropped alias to one class name. Fixture-internal, no test
generates from it, corpus row unchanged — recorded in row 36 and in the evidence file rather than
smoothed over.

**Generated-package comparison — full trees, 14 fixtures, zero unexplained.** Complete table and
reasoning in `evidence/3e-package-comparison.md`. Headlines:

- `sample_model` is **byte-identical** between routes.
- Every difference on the other fixtures reduces to five named mechanisms: provenance comments;
  declaration-site attribution; Slice 3B's `model.sysml` package fallback; the legacy-only
  `system_design` hierarchy group; and modules/entry points the legacy route dropped. Each maps to
  a ratified ledger row or a recorded slice mechanism.
- `quoted_owner_formula` is the one where the *legacy* column is broken: it renders
  `run_net margin,` — a Python identifier with a space — and the exact route sanitizes it. The
  3D `sanitize_name` hunk, seen from the other side.
- **fusion_tea, the customer package.** Module and schema class names are equal between routes
  (census `PROD-24` holds), no group was renamed (ruling 1's "no customer-model group naming
  changes" re-verified), and every hand-checked modelled value is unchanged. What changed is how
  **every** entry-point key is named: legacy names one after the consuming calc-usage formal, the
  exact route after the modelled attribute that supplies it. Legacy publishes 31 keys, exact 27,
  sharing 13, and the evidence file enumerates all 32 deltas — three collapses, eleven one-to-one
  renames, ten group moves. Two exact-only groups (`hif_economics_params`, `ife_lcoe_params`)
  follow from declaration-site attribution. *(This bullet said "the per-consumer-mint collapse"
  and listed three rows until the 3E audit, F1, found a shipped key rename it had omitted; the
  fix was to enumerate every delta rather than add one row.)* **This is the largest customer-visible change in the
  recovery and is flagged to the Phase 5 owner packet** — an owner accepting this candidate should
  see the table, not a summary of it.
- `constraint_inline` and `constraint_non_numerical` are refused **identically by both routes**
  (pre-existing constraint name-safety violation). Measured on both so the equality is recorded
  rather than assumed.

**Corpus, 37 paths, after the switch.** Exact **15 public graphs / 22 typed errors**, all 22
`ElaborationError` (readiness `.findings`); legacy 36 graphs / 1 error. **Zero rows moved** versus
the amended ledger, exactly as ruling 1 predicted, and
`test_elaboration_corpus_ledger.py::test_dual_run_ledger_outcomes_match_a_live_corpus_run` compares
the per-fixture strings rather than the totals. Error-class separation is unchanged: the driver
records `error_type` beside the code list and never collapses either class.

**Real TEAx, after the switch, through the switched public surface.** `tests/execution/real_teax.py`
no longer drives the generation steps directly — it calls the shipped `run_codegen`, which is what
Slice 3D recorded as the limit it could not close. `pytest tests/execution -m execution`: **38
passed**, zero skipped. Live and relocated-v6 both publish 11 channels with LCOE
`270.1211779380445`, identical to the pre-switch anchor at `0a812af`, with every value still
asserted against the hand transcription in `tests/execution/fusion_tea_arithmetic.py`. The
provenance-comment `executable_fingerprint` difference between live and relocated is unchanged and
remains the ruling-2 residual for the Phase 5 packet.

**Gates.**

- Full licensed codegen suite: **3557 passed / 47 skipped / 38 deselected**, zero failures, zero
  `no live syside license` lines. Delta versus `0a812af` (3539/47/38) is exactly **+18 passed** —
  the 18 nodes of `test_public_authority_switch.py`. Skips and deselections unchanged, and no test
  module lost a node: the 116 that moved were all repointed, none deleted, none silenced, none
  xfailed.
- Execution lane: **38 passed**, unchanged in count.
- Full agentic-mbse suite from the paired rebuild worktree: **1825 passed / 1 skipped /
  5 deselected**, unchanged. Nothing in that repository changed this slice.
- 37-path corpus: 37/37 rows reproduce the amended ledger.
- `ruff check src`: **byte-identical** to the `0a812af` baseline (16 findings) — verified by
  diffing the two outputs, not by comparing counts. The new test modules and helper lint clean.
- `mypy src`: **71 errors in 17 files, measured after the final tree, identical to the baseline.**
  Re-run against the committed state rather than carried over — the 3D audit's F1 is why that
  sentence is worth writing.
- `git diff --check` clean. Changed paths equal the declared set. agentic-mbse: `N/A if unchanged`
  → unchanged, clean at `cc6c7a7411f6338a4811a7cc58ca002c29ef177b`.

**Issues and deviations.**

- **The measurement that shaped the slice.** Applying the switch and running the suite before
  writing anything produced 116 broken nodes, and the plan's own rules left no in-slice route out:
  migrating the collapsing fixtures would have moved ratified corpus rows (a rule-10 stop),
  deleting the tests is a rule-10 stop, and leaving them red breaks rule 3. That is a genuine
  premise conflict, so it was surfaced rather than resolved silently in either direction. The five
  orchestrator rulings above are the resolution, and they are recorded here in enough detail to
  audit against the measurement.
- **`--design-path-filter` now fails where it used to succeed.** A shipped flag became a hard
  error. That is a deliberate product change under ruling 3, on the reasoning that a silently
  ignored filter ships a package the operator did not ask for.
- **`sysml-codegen snapshot` now emits a different format.** Under ruling 4. `capture_snapshot`
  (v5) is unreachable from public surfaces but untouched, and
  `scripts/capture_extraction_snapshots.py` is deliberately not modified — the committed v5
  fixture snapshots stay regenerable for Phase 4's snapshot decisions.
- **One new committed fixture artifact**, `tests/fixtures/fusion_tea/instance_graph_snapshot.json`,
  marked in the fixture README as a test fixture and explicitly not the accepted corpus recapture.
- No deletions in either repository. No Item 6 test was removed, silenced, deselected, or xfailed.

#### Slice 3E audit follow-up — F1 through F6

- **Completed:** 2026-08-11
- **Audit:** `evidence/audit-3e.md`, verdict **CERTIFY** (nothing blocked Phase 4), 6 findings —
  1 Medium, 4 Low, 1 Informational. Recorded at `f2f2016`. Commit: c48c132
- **Declared path set:** `tests/conformance/test_public_authority_switch.py`,
  `tests/unit/test_elaboration_import_boundaries.py`,
  `evidence/3e-package-comparison.md`,
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md`, and this plan.
  Actual changed paths equal that set. **No production file changed** — all six findings are
  evidence, record-keeping, or test-strength defects, which is what CERTIFY meant.

All six are closed. Two changed tests, three changed records, one is a Gate 4A/4B ledger input.

**F1 (Medium) — a shipped fusion_tea input key was renamed and the evidence file did not list it.
Verified against the graph before classifying, and the obvious reading was wrong.**

The key is `hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b__threshold` (legacy,
`system_design`) → `hif_plant_pkg__hif_plant__viability__threshold` (exact, `ife_plant_params`),
value `10.0` unchanged. The natural reading — a per-consumer hash-suffixed mint collapsing into
the exact route's clean semantic key, i.e. the same ratified single-source family as
`gain`/`availability` — **does not survive measurement.** Measured on both routes:

- **One consumer on each side, and it is the same one**: module
  `hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b`, formal `threshold`. Nothing collapsed;
  a collapse needs several consumer keys folding into one, and there was never more than one.
- The disambiguating id `81ddf10fb1d1749b` is **retained identically on both routes** in the
  module id and in the evaluation channel `…viability__81ddf10fb1d1749b__evaluation`. It is
  dropped only from the entry-point key.

So it is the same *mechanism* as the collapse family — legacy keys an entry point by its consuming
formal, the exact route by the modelled attribute's declaration path — but the one-to-one case of
it, not the N-to-one case. The hash is incidental to the mechanism, not its subject. Recorded that
way rather than filed under a family it does not belong to.

*The fix is not one table row.* Adding a row would leave the same class of omission possible, so
the fusion_tea section is rewritten to **enumerate every key delta**: 18 legacy-only, 14
exact-only, 10 group moves, each with its consumer set, grouped into five sub-tables (collapse /
one-to-one rename / the threshold / group move / definition→occurrence). Every legacy-only key is
matched to an exact-only or shared key by identical consumer set, which is the proof that no entry
point was lost or gained. **Re-checked for a second missed rename: there is none** — the
enumeration is closed by construction, 18 + 14 + 10 = every delta.

Diff-ledger row 15 now carries the shipped input-key cells for this family. One consequence is
flagged to the Phase 5 owner packet on its own merits: dropping the disambiguator means two
constraint usages with the same name under one owner would mint the same `…__threshold` key. No
corpus model has that shape and no failure was measured, so it is a packet question, not a defect
claim — but the exact route keeps the disambiguator everywhere except the surface an operator edits.

**F2 (Low) — "five named mechanisms" was not true as written.** A sixth was always in the measured
diffs and correctly classified per fixture against ledger rows 26 and 37: entry-point keys move
from consumer-scoped and definition-scoped naming to the modelled attribute's declaration path
(`toy_plant__Toy_Plant__plant_budget` → `toy_plant__demo_plant__plant_budget`). Named as mechanism
6, and the rule-10 sentence is reworded to what the per-fixture tables actually show — "every
difference maps to a ratified ledger row or a recorded slice mechanism" — rather than claiming six
summary sentences cover every hunk.

**F3 (Low) — the environment pin measured the test process, not the product.** It asserted that
`os.environ` carries no `SYSML_CODEGEN*` name, which would fail spuriously for an operator who
exports one and, worse, would still pass if `run_codegen` started reading `SYSML_CODEGEN_ROUTE`
tomorrow. It now walks the construction closure and asserts no reachable module references
`os.environ`/`os.getenv`, the same AST style as the neighbouring import pins. The product claim
the plan makes is now the claim the test makes.

**F4 (Low) — a dropped import-boundary assertion is restored.** Inverting
`test_shipped_cli_and_capture_remain_on_the_legacy_black_box_route` also stopped it reading
`orchestration/__init__.py`, quietly dropping
`assert "build_elaborated_pipeline" not in public_orchestration` — the pin keeping the *exact*
route's elaborator entry out of the public orchestration API. The property still held; nothing
enforced it. Restored, with a comment saying why it survives the inversion: that package already
re-exports the legacy builder as a named Gate 4A input, and this pin is what stops the exact one
joining it.

**F5 (Low) — two v5 residues inside the public writer, now named.** Both carried to the Gate 4A
ledger inputs above rather than changed here, because both are deletion-shaped:

- The `GrandfatheredSnapshotError` import and its handler in `_generate_package_from_graph` are
  unreachable on both paths — the public route no longer calls `assert_snapshot_certifiable`, and
  the legacy test adapter calls it before that function.
- The `unresolvable_attr_probe` refusal (row 36) is **untyped**: the collision guard raises a bare
  `ValueError`, so it reaches the bottom `except Exception` and the operator sees "Unexpected
  error" with a traceback — the exact shape this slice eliminated for the v5 refusal. It also
  fires inside `_generate_modules`, after the output tree was cleared, leaving a half-written
  package (measured: 34 files, no contracts, no seal). Neither is a regression this slice
  introduced, but the switch is what made the path reachable from public `generate`, so both are
  now product behaviour. Added to ledger row 36 and to the Phase 5 owner packet.

**F6 (Informational) — two record-keeping fixes.** (a) The declared path set is extended to the
three modules that were changed but nameable from no table
(`test_snapshot_v6_envelope.py`, `test_fusion_tea_real_teax.py`, `test_fusion_tea_mutation_teax.py`),
and the sentence that said "six further modules" and then named eight now says eight and names
eight. (b) Gate 4B's own bullet list now opens with a cross-reference to the Gate 4C
responsibility rows, so a Phase 4 agent meets the constraint before the deletions it governs
rather than after them.

**Gates.** Affected lanes re-run and measured, not carried over. Slice module
`test_public_authority_switch.py` **18 passed** and `test_elaboration_import_boundaries.py`
**14 passed** (unchanged counts — F3 strengthened an assertion and F4 restored one, neither adding
a node). Full licensed codegen suite **3557 passed / 47 skipped / 38 deselected**, zero failures,
zero `no live syside license` lines — **delta versus `430e26a` is zero on every axis**, since no
test node was added or removed. Execution lane **38 passed**. Full agentic-mbse suite from the
paired worktree **1825 passed / 1 skipped / 5 deselected**, unchanged; nothing in that repository
changed. `ruff check src` byte-identical to the baseline set (16 findings) and both changed test
modules lint clean. `mypy src` **71 errors in 17 files, measured** — no production file changed
this follow-up, and it was re-run rather than assumed. `git diff --check` clean. Changed paths
equal the declared set.

### Phase 4 Completion

- **Completed:** Pending
- **Retirement/doc commits and evidence:** Pending
- **Issues/deviations:** Pending

#### Gate 4A Completion — the responsibility/deletion ledger

- **Completed:** 2026-08-11. **Nothing was deleted.**
- **Artifacts:** `ledger-4a.md` (reviewable), `ledger-4a.json` (`ledger-4a/v1`, what the checker
  reads), `scripts/check_ledger_4a.py`, `tests/unit/test_check_ledger_4a.py`.
- **Declared path set:** those four paths, `briefs/phase4a.md`, and this plan. Actual changed
  paths equal that set. No production, test-behaviour, or documentation file changed.
- **276 rows**, every path listed individually: 37 production, 159 test, 37 snapshot, 23 doc,
  15 probe, 5 script. Dispositions: 18 delete, 19 migrate, 227 retain, 12 archive. 245 rows
  claim the Git-derived candidate set (222 deletions + 22 architecture docs + `CLAUDE.md`), 22
  are Phase-3 carried, 7 derived blast-radius, 2 cross-repository.
- **The checker sees deletions**, because it reads `git diff --name-status 1672c57 07531e64`
  rather than a worktree — the original census's defect. `paths`: 276 rows, 0 problems.
  `replacements`: 38 green, 14 pending, 222 not-required, 0 failures.
- **`replacement_is_green` is real**: it resolves the node, requires it to collect *and* pass in
  the suite the row declares, and reports MISSING / DESELECTED / FAILED / PENDING otherwise.
  All four negatives are tested. It found one defect while being written: the superseded
  `test_pipeline_runner.py` responsibility names a replacement in the `execution` lane, which
  the default marker expression deselects, so rows now declare the suite they are checked in.
- **Two CONFLICT rows, surfaced not resolved** (rule 10): `analysis/signature_extractor.py` is a
  responsibility with no possible replacement, and `cli/__init__.py` item (4) — the untyped
  clear-then-fail refusal from the 3E audit's F5 — is a product change hiding inside a
  retirement row.
- **The derivation that shapes 4B:** one import edge
  (`exact_pipeline_context.py:41` → `pipeline_context`'s `CodeGenerationError`) holds the whole
  legacy analysis stack inside the exact route's import closure, so Group 4B-G0 is a
  prerequisite migration that deletes nothing. Only one row is unblocked today, and it is a
  CONFLICT row: 65 rows block `pipeline_builder.py`, 35 block `snapshot_context.py`.
  `orchestration/elaborated_pipeline.py` is live on the exact route
  (`exact_pipeline_context.py:245`), so its deletion proposal is recorded as **rejected**.
- **Two measured findings the ledger records rather than assumes:** the 22 architecture
  documents are byte-identical to the Item 6 base at rebuild HEAD, so Gate 4D has nothing to
  restore and only the rewrite remains; and 120 test files beyond the sixteen 3E responsibility
  modules import a legacy owner directly, which is the real blast radius of 4B.
- **Gates.** Full licensed codegen suite **3571 passed / 47 skipped / 38 deselected**, zero
  failures, zero `no live syside license` lines — delta versus `c48c132` (3557/47/38) is exactly
  **+14 passed**, the checker's own tests. `ruff check` and `mypy` clean on both new files.
  agentic-mbse unchanged and not re-run: nothing in that repository was touched.
- **Commit:** 804d8a2 (sysml-codegen only; agentic-mbse `N/A` — unchanged).

#### Gate 4A approval — orchestrator record (2026-08-11, under the rule-11 delegation)

The orchestrator read the ledger (structure, both CONFLICTs, all five 4B group tables, the
retain/archive families, and the findings sections), independently verified the C1 history, and
approves the ledger with the two conflicts ruled as follows:

- **C1 ruled — delete, with the living owner named.** `analysis/signature_extractor.py` is a
  dead duplicate, not a lost responsibility: the COST-PATTERN refactor (`d6c725f`) copied the
  signature/preservation logic into `generation/preservation.py`, which is live production
  (imported by `generation/__init__.py`, drives `should_regenerate_stencil`) and covered by
  passing tests (`tests/conformance/test_gen_stencils.py` + `test_generation_boundary.py` +
  `tests/unit/test_stencils.py`, 73 passed, measured 2026-08-11). Row L-006 gains those nodes as
  its replacement proof; the module and `tests/unit/test_signature_extractor.py` retire together
  in G1. The original run deleted the test without this derivation — that remains the recorded
  difference between an evidenced retirement and an absence-driven one.
- **C2 ruled — fix inside Phase 4, in G0.** The untyped clear-then-fail refusal (3E audit F5,
  ledger row 36) is a product defect on the now-public exact route and contradicts the pinned
  fail-before-mutate property. It gets a typed refusal ordered before the output-tree clear,
  red→green with an `unresolvable_attr_probe`-shaped specimen, landing with the other L-025
  items in G0. Carrying a known publicly-reachable defect into the Phase 5 candidate was
  rejected as an option; the fix is a defect repair with a pinned specimen, within the
  orchestrator's quality remit, and is flagged in the Phase 5 packet either way.

Approved 4B order: G0 → G1 → (4C specimen authoring for the 14 pending rows + the 120-file
blast-radius dispositions) → G2 → G3 → G4, with the full battery per group as tabled. The
`replacement_is_green` gate is binding at every group boundary.

#### Gate 4B-G0 Completion — the prerequisite migrations (deleted nothing)

- **Completed:** 2026-08-11. **Commit:** `db00482` (sysml-codegen only; agentic-mbse `N/A` —
  worktree clean, nothing touched, not re-run).
- **Declared path set, and what actually changed:** two new production files
  (`core/errors.py`, `resolution/uncovered_params.py`), ten repointed production files
  (`orchestration/{pipeline_context,exact_pipeline_context,elaborated_pipeline}.py`,
  `extraction/source_manifest.py`, `analysis/diagnostic_screen.py`,
  `generation/{errors,initialization,constraint_catalog,registry}.py`,
  `resolution/graph_builder.py`, `cli/__init__.py`), five test modules, and
  `scripts/check_ledger_4a.py` + its test. Actual changed paths equal that set.
- **The neutral home is `core/errors.py`, and the choice is recorded rather than assumed.**
  `generation/errors.py` already exists, but it is a *generation-seam helper* that builds errors,
  and `extraction/source_manifest.py` cannot import from `generation` without inverting the
  layering `core/__init__.py` states. `core` is the one package every layer may import.
  `orchestration/pipeline_context.py` re-exports both names — the same class objects, so every
  existing `raise` and `except` is untouched — until the module retires in G3.
- **A ledger correction the execution measured (rule 10, surfaced not silent).** Gate 4A derived
  that *one* import edge (`exact_pipeline_context.py:41`) held the legacy analysis stack inside
  the exact route's closure. There were two of the same kind:
  `orchestration/elaborated_pipeline.py:21` — row L-009, **retained**, live on the exact route via
  `exact_pipeline_context.py:245` — imported both classes from `pipeline_context` too. Repointing
  only the six named rows left the closure unchanged, measured. With the seventh file repointed,
  the exact route's construction closure reaches none of `pipeline_context`,
  `dependency_backtracker`, `parameter_groups`, `part_instance_index`, `phantom_detector`,
  `producer_resolution` or `core/output_registry` — which is what G0 exists to achieve. No
  disposition changed: L-009 stays retained, and the correction is recorded on its row. The
  `sysml_codegen.cli` closure still reaches them through the `snapshot/` and `orchestration/`
  re-exports, which are G2 and G3 rows.
- **The four `cli/__init__.py` items (L-025), all spent.** (1) The unreachable
  `GrandfatheredSnapshotError` import and handler are gone. (2) `--design-path-filter` is gone
  from both subcommands *and* from `GenerationConfig`: leaving the field would have re-created the
  silent-ignore the 3E refusal existed to prevent, this time for API callers. (3) The two
  collectors are repointed. (4) **C2 as ruled.**
- **C2, measured before and after.** Before: public `generate` on `unresolvable_attr_probe`
  cleared the output tree, wrote 34 files with no contracts and no seal, and reported "Unexpected
  error" with a traceback from a bare `ValueError` at `generation/registry.py:146`. The raise sits
  in the *registry* pass (Slice 3E's F5 said `_generate_modules`; the measured site is
  `_generate_registry`). After: detection is split from the raise — `residual_class_name_collisions`
  is pure, logs nothing and raises nothing — and `cli._preflight_registry_class_names` runs it as
  step 1.7, beside the two existing pre-clear guards. The refusal is the package's own
  `CodeGenerationError`; the target tree is byte-identical to what it was. `generate_registry`
  keeps the same check as a typed backstop for direct callers.
- **Test-node accounting, every changed node named.** +1 specimen
  `test_a_registry_class_name_collision_refuses_before_the_writer_runs` (C2, red→green through
  public `generate`). +7 checker tests for the new executed-row state model (requirement 3: extend
  the checker rather than special-case it). −2 in `tests/integration/test_full_pipeline.py`
  (`test_design_path_filter_cli_flag`, `test_generation_config_has_design_path_filter`) — the FR-4
  flag-existence responsibility is what L-025 item (2) retires. Three nodes changed rather than
  removed, same subjects: `test_design_path_filter_is_gone_from_the_public_surface` and
  `test_the_snapshot_subcommand_takes_no_filter_either` (was: refused rather than ignored),
  REQ-SNAP-16 now pinning argparse's refusal, and `test_sc11_recheck`'s grandparent-collision node
  now pinning the typed error. L-025's `replacement_proof_node` is renamed with its test.
- **Battery.** Full licensed suite **3577 passed / 47 skipped / 38 deselected**, zero failures,
  zero `no live syside license` lines; delta versus `c21f86b` (3571) is exactly +1 +7 −2. 37-path
  corpus **15 graphs / 22 errors** on the exact route, 36/1 legacy — zero rows moved, and
  `test_elaboration_corpus_ledger.py` compares per-fixture strings, so that is a full-set match.
  Execution lane (`pytest tests/execution -m execution`) **38 passed**. `ruff check src` **16
  findings**, byte-identical to baseline. `mypy src` **71 errors in 17 files, measured**, equal to
  baseline. `git diff --check` clean.

#### Gate 4B-G1 Completion — the first deletion

- **Completed:** 2026-08-11. **Commit:** `6ba346e` (sysml-codegen only; agentic-mbse `N/A`).
- **Deleted:** `src/sysml_codegen/analysis/signature_extractor.py` (L-006),
  `tests/unit/test_signature_extractor.py` (L-241), and the `analysis/__init__.py:26` re-export
  that was the module's last reference in `src`.
- **The C1 ruling, re-verified rather than taken on trust.** `generation/preservation.py` is live
  production (`generation/__init__` → `cli/__init__.py:432`, `should_regenerate_stencil`), and the
  three replacement modules were run explicitly and green **before** the deletion, through the
  gate itself (`check_ledger_4a.py replacements --row L-006 --row L-241`):
  `tests/conformance/test_gen_stencils.py` **32**, `tests/conformance/test_generation_boundary.py`
  **20**, `tests/unit/test_stencils.py` **21** — **73 nodes**. That is the recorded difference
  between this retirement and the original run's, which deleted the same test on absence alone.
- **L-241 moved from retain to delete**, group 4C-blast-radius → 4B-G1, on the C1 ruling. That
  move *is* the responsibility-level disposition rule 6 requires before a test may go; the
  blast-radius family is 119 rows now, and the ledger says so by name.
- **Battery.** Full licensed suite **3565 passed / 47 skipped / 38 deselected**, zero failures,
  zero license lines. Delta versus G0 (3577) is **−12**: the deleted module's **13** nodes
  (`test_matches_with_identical_fields`, `_added_field`, `_removed_field`, `_renamed_field`,
  `_field_order_independent`, `_none_fallback_extracted`, `_none_fallback_both`,
  `_type_change_still_detected`, `_return_type_change_still_detected`,
  `test_extract_input_field_refs_from_impl`, `_empty_stub`, `_auto_impl`,
  `test_extract_nonexistent_file`), less the **+1** multi-node replacement-proof test. 37-path
  corpus 15/22, zero rows moved. Execution lane **38 passed**. `ruff` **16**; `mypy` **69 errors
  in 16 files** — baseline less the deleted module's two. `git diff --check` clean.

#### Gate 4B — ledger state after G0 and G1

- **Row states are now checked, not asserted.** The JSON carries `state`
  (`proposed` / `partially-executed` / `executed`), `executed_commit`, and `remaining`;
  `check_ledger_4a.check_states` verifies every claim against Git — an executed `delete` whose
  file is still at `HEAD` fails, an executed `migrate` whose file vanished fails, and a
  `partially-executed` row that does not say what is left fails. Six G0 rows are fully spent;
  L-011, L-018 and L-021 are `partially-executed` with their G3 remainder stated; L-006 and L-241
  are executed deletions.
- **Checker after both groups:** `paths` **276 rows, 0 problems** — an executed deletion is what
  its row already claimed, because the candidate set is read from the diff. `replacements`
  **40 green, 14 pending, 220 not-required, 0 failures** (38/14/222 at Gate 4A; L-006 and L-241
  moved to green on the C1 proof modules).
- **The record commit's own delta.** Marking the rows needed the `partially-executed` state, so
  the suite moves **3565 → 3568**: `test_a_partially_executed_row_must_say_what_is_left`,
  `test_a_partially_executed_row_whose_file_is_gone_fails`, and
  `test_the_committed_row_states_agree_with_the_tree`, which runs the state check over the
  committed ledger itself. `ruff` 16, `mypy` 69/16, corpus and execution lane unchanged.
- **Still blocked, unchanged:** G2 (6 rows, 35 block `snapshot_context.py`), G3 (16 rows, 65 block
  `pipeline_builder.py`) and G4 (5 rows). The 14 pending 4C responsibilities and the 119-row
  blast radius are the work between here and G2.

#### Gate 4C Part 1 Completion — the fourteen exact-route specimens

- **Completed:** 2026-08-11. **Commit:** `5dfb900` (sysml-codegen only; agentic-mbse `N/A`).
- **What this stage did:** authored exact-route specimens for the fourteen pending
  responsibility rows. It deleted nothing and repointed nothing. Twelve rows are now green;
  two are rule-10 surfacings and stay pending with their reason in the row.
- **Checker:** `paths` **276 rows, 0 problems**. `replacements` **52 green, 2 pending,
  220 not-required, 0 failures** — was 40/14/220 after G1.

##### Row → specimen

| Row | Responsibility | Fixture | Specimen node | Green |
|---|---|---|---|---|
| L-099 | Alias-aggregation probe generation | **new** `alias_agg_d5` | `conformance/test_exact_route_alias_aggregation.py` | 7 |
| L-118 | Constraint portability live vs replay | `constraint_non_numerical` (corpus row 10) | `conformance/test_exact_route_constraint_portability.py` | 6, **row stays pending** |
| L-140 | Fingerprint stability | committed `fusion_tea` v6 snapshot; `wi014_toy`, `constraint_multi_instance` live | `conformance/test_exact_route_fingerprint_stability.py` | 4 |
| L-148 | Registry across module kinds | `source_identity_mixed_consumers` + **new** `costed_cart_d5` | `conformance/test_exact_route_registry.py` | 7 |
| L-169 | Seal step 9 | committed `fusion_tea` v6 snapshot | `conformance/test_exact_route_seal_step9.py` | 12 |
| L-179 | Licence-free generation, no provenance leak, route parity | committed `fusion_tea` v6 snapshot | `conformance/test_exact_route_snapshot_generation.py` **+ cited** `test_exact_route_generated_package.py::test_the_two_packages_differ_only_in_provenance_comments` | 10 + 1 |
| L-188 | Whole-tree checkout-root portability | committed `fusion_tea` v6 snapshot | `conformance/test_exact_route_whole_tree_portability.py` | 3 |
| L-198 | FORMULA computed attributes | `attr_expr_probe` (corpus row 4) + **new** `costed_cart_d5` | `integration/test_computed_attributes_exact_route.py` | 15 |
| L-199 | Costed-component pattern end to end | **new** `costed_cart_d5` | `integration/test_costed_component_exact_route.py` | 18 |
| L-201 | Auto-impl classification, stub fallback, backlog | **new** `expr_compile_d5` | `integration/test_expression_compilation_exact_route.py` | 7 |
| L-202 | `run_codegen` phase sequence, design params, exit-point types | **new** `costed_cart_d5` | `integration/test_full_pipeline_exact_route.py` | 5 |
| L-203 | BF3–BF5 aggregation wrappers, instance-scoped paths | **new** `costed_cart_d5` | `integration/test_hierarchy_exact_route.py` | 5 |
| L-249 | V11 seeded strict-generation abort | — | — **row stays pending**, cause pinned in the L-251 module | — |
| L-251 | Warning reconciliation categories | five accepted fixtures + v6 replay | `unit/test_warning_reconciliation_exact_route.py` | 22 |

**121 new nodes, all green.** Three new fixtures, none of them in the 37-path corpus and none
of the 37 touched: `costed_cart_d5`, `alias_agg_d5`, `expr_compile_d5`, each with a
`PROVENANCE.md` recording why it exists, what it differs from, and its hand-derived values.

##### Rule-10 surfacings

Four, in the order a reader should care about them. The first two block rows; the last two are
product defects this stage measured and pinned rather than routed around.

**S1 — L-118 is blocked by a portability defect, not by a missing specimen.** A constraint the
catalog *excludes* records its source `location` as an absolute path: the checkout path in a
live run, and the capture-time staging directory (`/tmp/sysml-codegen-sources-XXXXXXXX/root-0/…`)
in a replay. That field is inside the catalog fingerprint, which is inside the model contract's
semantic fingerprint. One model at two checkout roots on two routes produced **four different
semantic fingerprints**. Exactly three files move with the root — `contracts/model_contract.json`,
`contracts/package_contract.json`, and the constraint report module that embeds the catalog
fingerprint — and every other generated file is identical. A fingerprint that moves with the
build directory authenticates nothing, and that is the property L-118 exists to protect, so the
row cannot go green. **Gate 4B may not delete the legacy constraint owners while it stands**;
the legacy route passed this specimen.

**S2 — L-249 is unreachable by construction on the exact route.** `elaboration/project.py`
builds every `ComputationGraph` with `fallback_entry_points=set()`, in both `run()` and
`select()`, and both collectors filter on membership in that set. So
`cli._reconcile_params_coverage` — the V11 abort and the reconciliation summary — runs on every
generation and can never fire. No fixture can seed the gap through the public surface, so the
row's specimen is not merely unwritten, it is unwritable. Two consequences the owner should
weigh: the Gate 4A note that the two migrated collectors are "live public-route code that the
CLI calls on every run" is true only in the calling sense, and V11 coverage for the shipped
route now rests entirely on the nine route-neutral graph-level nodes in
`tests/unit/test_uncovered_params.py`. Pinned at its cause by
`test_the_projection_hard_codes_an_empty_fall_through_set`, which fails the day the projection
starts populating the set.

**S3 — the params schema does not parse when a modelled multiplicity indexes an entry-point
key.** A finite multiplicity mints keys like `…__caster[0]__load_rating`, and
`schemas/library_params.py` writes those keys as Python field names, so the file is a
`SyntaxError`. This is **not** new and **not** fixture-specific: it reproduces at `HEAD` on the
ratified corpus fixture `d38_caret`, whose `…__cell[0]__base_cost` keys break the same file, and
`d38_caret` is corpus row 12 — a shipped-package cell the 3E switch already flagged to the
Phase 5 owner packet. No existing test parses a generated package's schema files, which is why
it went unseen. Both new fixtures that use a multiplicity pin the set of unparseable files
rather than asserting emptiness, so a *second* file failing is a test failure and so is this one
being fixed without the surfacing being closed.

**S4 — the exact route refuses the Costed Component pattern's central idiom.** An assembly
cannot write `sum(deck_panel.capital_cost) + sum(caster.capital_cost)`: the projection names an
expression parameter after the reference's *last member* and drops the qualifier
(`elaboration/elaborate.py:1901`), so both terms render `capital_cost` and the model is refused
with `SI_RENDERING_COLLISION` (`elaboration/project.py:598-604`). Every child of a costed
assembly exposes the same attribute names by construction, so this is the pattern, not an edge
case. The workaround the fixture uses — one named intermediate attribute per child role, added
by the rollup — is legal and natural, but it is a *remodelling requirement the route imposes*,
and no document says so. This is the same qualifier-dropping collapse recorded as the Item 10
cross-part blocker. Pinned by
`test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_is_refused`, which also
proves the refusal leaves no half-written tree.

##### Notes a reviewer should not have to re-derive

- **Live-vs-snapshot byte identity is not an exact-route property, and must not be asserted as
  one.** A v6 snapshot records its sources under the portable `root-0/` referent, never the
  checkout path — that portability is the point of the referent — so every file carrying a
  `SysML Source:` comment differs between the two routes by construction. What holds is that the
  difference is *only* the provenance comment (already pinned, cited on row L-179) and that the
  model contract's **semantic** fingerprint is equal across the two (newly pinned on L-140,
  alongside the executable fingerprint's divergence, so the difference is recorded rather than
  ignored). The plan's own wording — byte identity "where still required" — is what this
  discharges.
- **The alias-collision count-summary retired with its mechanism.** L-251's second half is
  emitted while building an `OutputRegistry`, and the exact route never constructs one. The
  specimen asserts the message's absence, including on `costed_cart_d5`, whose four same-named
  module classes are the nearest thing the exact route has to those collisions. Nothing was
  lost; `output_registry_builder` is already a G3 deletion row.
- **`costed_cart_d5` warns once, legitimately.** Three assemblies rolling the same four
  attributes give four colliding module class names, and the registry aliases the imports
  (REQ-REG-04). The zero-WARNING sweep names that fixture as the exception with its reason
  rather than being scoped down to whatever passes.

#### Gate 4C Part 2 Completion — the four surfacings, ruled and discharged

- **Completed:** 2026-08-11. **Commit:** `6d58ad2` (sysml-codegen only; agentic-mbse `N/A`).
- **Checker:** `paths` **276 rows, 0 problems**. `replacements` **54 green, 0 pending,
  220 not-required, 0 failures** — every responsibility row in the ledger now names a proof
  node that collects and passes.

| Surfacing | Ruling | Outcome |
|---|---|---|
| S1 — constraint location leaks an absolute path | FIX | Fixed and closed. L-118 green on 8 nodes. |
| S2 — V11 abort unreachable | CLOSE BY PROOF | Closed. L-249 green on 3 proof nodes, two of them rot pins. |
| S3 — params schema does not parse | FIX | Fixed. New coverage module, 21 nodes. |
| S4 — same-name rollup refused | REFUSAL STANDS | Documented and filed. No code change. |

##### S1 — the excluded-constraint location is now route- and root-invariant

**Cause.** `exclusion_location` was a second, unnormalized copy of a source path. The
elaborator built it from the raw parser path (`elaboration/elaborate.py:1136`) and the one
place that rewrites paths to referents,
`orchestration/elaborated_pipeline._rewrite_sources_as_referents`, only touched `source_file`.
So the field escaped normalization on both routes: the checkout path live, the private
`/tmp/sysml-codegen-sources-XXXXXXXX/root-0/` staging path on replay.

**Fix.** `_rewrite_exclusion_locations` re-renders the field against a portable referent, and
each route supplies the mapping it can prove — the live route maps the raw path against its
model roots with `map_live_source_referent`, the capture route re-renders from the referent it
has already written onto `source_file`. One rendering shape, two policies at the call sites.
A snapshot sealed before the fix is **refused at load** (`snapshot/envelope.py`), because its
digest is unkeyed and replaying it would mint a fingerprint that varies by capture machine;
the refusal names the field and says "re-capture".

**Measured, red to green.** Same model, two checkout roots, live and replayed from each:

| | before | after |
|---|---|---|
| distinct semantic fingerprints | 4 | **1** |
| distinct catalog fingerprints | 4 | **1** |
| files differing across the four routes | 3 | **0** |
| excluded location | `///tmp/…/checkout-a/models/model.sysml:13` | `root-0/model.sysml:13` |

**The enumeration the ruling asked for.** Every catalog and contract field was scanned, not
assumed: five constraint-bearing fixtures × two routes × three contract files, matching any
absolute `.sysml` path. `exclusion.location` was the **only** hit, in `model_contract.json`
alone. Three further constraint shapes (`constraint_inline`, `constraint_shared_polarity`,
`constraint_def_owned_redefining`) were scanned at catalog level and are clean; three more
(`constraint_occurrence_demand/anonymous`, `constraint_blocked_profile`,
`constraint_malformed_mixed`) are refused by the elaborator and reach no catalog. The scan is
not a one-off: `test_no_contract_field_carries_an_absolute_source_path` re-runs it on every
route each time the suite runs, so a newly added leaking field fails there.

##### S2 — L-249 closed by proof, with the V11 coverage owner named

The row's disposition is the derivation, recorded in the row itself:
`elaboration/project.py` constructs every `ComputationGraph` with
`fallback_entry_points=set()` in both `run()` and `select()`, and both collectors filter on
membership in that set, so `cli._reconcile_params_coverage` runs on every generation and cannot
fire. No fixture can seed the gap through the public surface.

The row's proof node is a list of three, all run by the checker: the two rot pins
(`test_the_projection_hard_codes_an_empty_fall_through_set`, which asserts the projection
literal, and `test_the_exact_route_projects_no_fall_through_entry_points`, which asserts an
empty collector result on every accepted fixture) and **`tests/unit/test_uncovered_params.py`,
named in the row as the V11 coverage owner** — its nine route-neutral graph-level nodes build
their graphs directly and are what still proves the collector's semantics. The day the exact
route starts producing fall-through entry points, the pins fail and the row becomes authorable
as a behavioural specimen.

**Flagged to the Phase 5 owner packet:** V11's guard is structural, not behavioural. The
generation boundary still calls it, and the call is not dead code in the reachability sense,
but on the shipped route it can only ever return empty.

##### S3 — the generated params schema parses, and the JSON surface did not move

**Cause and blast radius.** A modelled finite multiplicity mints keys carrying an occurrence
index, and the schema template wrote the key straight into a class body as a field name, so
`schemas/*_params.py` was a `SyntaxError`. Pre-existing and reachable from public `generate`:
it reproduced at `HEAD` on the ratified corpus fixture `d38_caret`.

**Fix.** `core/qualified_names.params_field_name` sanitizes `[0]` to `_0`, and the schema
declares the sanitized field with the exact key as its **alias**. The JSON keys are untouched.
A key with no index passes through unchanged and gets no alias, so every package without a
multiplicity is byte-identical to before — asserted, not asserted-by-hope, in
`test_only_an_indexed_key_gets_an_alias`.

**The one thing the alias did not cover, found by asking where the field is read.** The runtime
resolves a pipeline input `group.<field>` with `getattr` on the loaded params model
(`teax-simkit`, `pipeline_executor.py:411`), so the YAML's field path had to follow the field
name or the package would have parsed and then failed at execution with an `AttributeError` —
strictly worse than the `SyntaxError` it replaced. One helper, used at both sites, keeps them
in step; `test_the_pipeline_reads_the_field_name_the_schema_declares` checks the agreement
against the imported model's real `model_fields`. **No shipped JSON key changed anywhere**, so
the ruling's stop condition was not met. No committed baseline carries an indexed entry-point
key (checked: the one `[0]` in `baseline_outputs` is a constraint id), so no byte-identity gate
moved.

**Coverage.** `tests/conformance/test_generated_schema_importable.py`, 21 nodes over five
fixtures — three that mint an index and two that do not. It parses every generated file,
**imports** each schema and validates the package's own emitted JSON through it (the layer a
parse check cannot reach), and asserts the emitted keys equal the graph's entry-point names
verbatim. A collision guard refuses a group whose two keys would sanitize onto one field rather
than letting the second declaration silently replace the first.

##### S4 — the refusal stands; the modelling requirement is now documentation work

No code change. The fail-closed `SI_RENDERING_COLLISION` is correct recovery-era behaviour, and
a silent collapse is the incident this recovery exists to undo. What was missing is that no
document states the requirement, so the working idiom — one named intermediate attribute per
child role, added by the rollup — is now a **Gate 4D documentation subject** (added to that
gate's checklist above, with `tests/fixtures/costed_cart_d5/library.sysml` as the worked
example). The Item 10 cross-reference — the cross-part `child.attr` collapse class, where the
resolver does not follow per-child `:>>` redefinitions — is recorded on ledger row L-199 and
carried to the Phase 5 packet. The refusal pin stays where it is.

#### Gate 4C part 3 — the disposition pass and the regrouping (awaiting approval)

**Why this gate exists.** Gate 4B-G2 stopped under rule 10 instead of executing. Three findings
forced it: all 45 of G2's declared dependents were `retain` with no rewrite and no recorded
retirement, two live conformance files had no ledger row at all, and the retained v5 capture
script imported three of the symbols G2 proposed to delete. The orchestrator ruled G2 blocked and
ordered a per-row disposition pass over the entire remaining deletion blast radius.

**The measurement.** `check_ledger_4a.py surface` now derives the removal surface from the rows
themselves and walks `tests/` and `scripts/` by AST. Measured at HEAD: **18 modules and 36 symbols
of surface, touching 175 test and script files**, 154 at module level.

**The finding that recomposed the groups.** Nobody had measured what retaining the last v5
producer costs. `capture_snapshot` calls `build_pipeline_context` (`snapshot/capture.py:55`), and
`pipeline_builder` imports the whole legacy analysis and resolution stack at its top. So **12 of
the 18 removal-surface modules sit inside the retained v5 writer's own import closure** — eleven of
G3's twelve, plus `snapshot/serializer.py`. Under the orchestrator's v5-family ruling they defer to
Phase 5 owner acceptance with the 37 fixtures.

**Revised group composition.**

| Group | Rows | Affected files | State |
|---|---:|---:|---|
| 4B-G2′ — the v5 read path (`snapshot_context`, `graph_rebuild`, `loader`, 3 re-exports) | 4 | 82 | **BLOCKED**, 76 deferred blockers |
| 4B-G3′ — `producer_completeness.py` | 1 | 3 | **BLOCKED**, 3 deferred blockers |
| 4B-G4′ — `elaboration/diff.py`, `tests/helpers/legacy_route.py` | 2 | 19 | **BLOCKED**, 3 deferred blockers (16 ready) |
| 4B-v5-family — the v5 writer and its closure | 23 | 133 | **DEFERRED to Phase 5** |

`snapshot/__init__.py` (L-028) splits: three read-path re-exports to G2′, three write-path to the
family. The 3E residual pin is **amended to the measured remainder, not deleted**.

**Coverage delta each group will cause when executed.** G2′ and G3′: none authorised yet, every
affected file still deferred. G4′: 124 nodes retire across 14 files, each against a named green
Gate 4C part-1 specimen, and 29 nodes survive by repoint across 2 files.

**Dispositions — 175 files, each with its own responsibility statement.**

| Disposition | Files | Nodes |
|---|---:|---:|
| `retire-with-owner` (names the green replacement) | 14 | 124 |
| `repoint` (live coverage, legacy arm removed) | 2 | 29 |
| `defer-to-v5-family` | 159 | — |

**No row is dispositioned `rewrite`, and that is measured, not skipped.** A rewrite replaces
coverage a deletion orphans. No group can run in Phase 4, so nothing is orphaned in Phase 4, and
every file that would need one needs it against an owner that now retires in Phase 5. Authoring
them now would stand up a second coverage lane against a route that is not retiring, and each
would still need its own rule-6 review at Phase 5. **This is a deliberate departure from the
ruling's "author the rewrites in this pass", recorded for the orchestrator to rule on at the
regrouping approval** — the premise that rewrites unblock Phase 4 deletions did not survive the
measurement.

**Ten rows added** (L-277 … L-286), every one found by the surface check, none visible to the
candidate diff. Seven break at module level; `test_generation_boundary.py` and
`test_pipeline_e2e.py` are live conformance files carrying 30 nodes between them. Running the new
check caught five more the manual G2 sweep had missed.

**Checker extended** so this class cannot recur: `paths` now fails when a file with no row imports
removed surface at module level, and a new `groups` mode reports per-group readiness with the
blocking rows named. 11 new checker tests, all green.

**Battery.** Full licensed suite **3723 passed / 47 skipped / 38 deselected**, zero failures —
delta versus the 3712 measured at HEAD on the same command is **+11, every one a new node in
`tests/unit/test_check_ledger_4a.py`** for the new surface and readiness checks; no other count
moved, and no test was removed. 37-path corpus ledger **3 passed**, outcomes equal to the committed
ledger. Execution lane **38 passed** including the 12 real-TEAx nodes at the recorded anchors
(unchanged — this gate touched no production code). `ruff check` **870 → 870**, `mypy src/`
**69 errors in 16 files → unchanged**, `ruff format --check` drift unchanged from HEAD.
`git diff --check` clean. `check_ledger_4a.py paths` **286 rows, 0 problems**; `surface`
**0 unrowed breakages**; `replacements` **54 green / 0 pending / 0 failures / 230 not-required**.

**Commit:** `8b5a2e3` (`8b5a2e32bf4ff5ebc98808e49c5c471fe4b046bb`).

**Deletes nothing.** This gate amended the ledger, extended the checker and recorded dispositions.
No production or test file was removed. **Stopped for the orchestrator's approval of the
regrouping before any deletion group runs**, per the ruling.

#### Gate 4C part 4 / Part A — the PROPOSED v6 recapture batch (owner acceptance pending)

**Why now.** The deferral cascade ended somewhere incoherent: a v5 writer and 37 fixtures with
no reader, and the legacy stack retained solely as that writer's import closure. The plan's own
Gate 4C rule is the exit — the v5 snapshots stay until their accepted v6 replacements are ready
*in the same candidate*. Readiness is producible now; **acceptance stays the owner's at the
Phase 5 stop**, so this batch is marked PROPOSED and is authority for nothing.

**What was produced.** `scripts/capture_v6_batch.py --verify`, using the shipped public
`capture_instance_graph_snapshot` and no capture code of its own, so the batch cannot drift from
the product.

| | Count | Where |
|---|---:|---|
| v6 snapshots | **15** | `tests/fixtures/<name>/instance_graph_snapshot.json` |
| typed refusal records | **22** | `tests/fixtures/v6_recapture_batch/batch.json` |

**Every outcome matched the amended Phase 2 corpus ledger — 0 deviations**, both error classes
with their exact code multisets (`SI_SELF_BINDING` and `SI_EXPRESSION_SOURCE_UNSUPPORTED`,
counts included: 21× for `ife_plant`, 24× for `solar_battery_model`, the 6+3 mix for
`expression_binding_probe`). No rule-10 stop was triggered.

**Live↔replay equality, per fixture, at the 3A/3B route-test bar.** For all 15: in-place and
relocated reads agree on the instance fingerprint and on the projected computation graph, and the
projected graph equals the live route's modulo the one module `source_file` divergence Slice 3B
pinned and 3E carried.

**Two independent confirmations worth recording.** `fusion_tea`'s already-committed v6 snapshot
was reproduced **byte-identically** by this run, so capture is deterministic and the committed
artifact was not a one-off. And no snapshot or manifest entry contains an absolute path, so the
batch is portable across checkout roots — the defect class L-118 closed on.

**Kept honest by a test, not by the manifest.** `tests/conformance/test_v6_recapture_batch.py`
(58 nodes) re-derives every claim from the committed bytes: each fixture claimed once, each
snapshot loading and projecting to its recorded outcome, each digest re-checked, each refusal
typed with a canonical code multiset, the whole set still agreeing with the corpus ledger, and no
absolute paths. Most of it runs license-free, which is the point — the batch must be checkable by
someone who cannot capture.

**Battery.** Full licensed suite **3781 passed / 47 skipped / 38 deselected**, zero failures —
delta **+58** against 3723, every one a node in the new batch test file; no other count moved.
Corpus ledger **3 passed**. Execution lane **38 passed** including the 12 real-TEAx nodes at the
recorded anchors. `ruff` **870 → 870**, `mypy src/` **69 in 16 files → unchanged**,
`git diff --check` clean, `check_ledger_4a.py paths` **286 rows / 0 problems**, `surface`
**0 unrowed breakages**.

**Commit:** ``d2d032f` (`d2d032f5613ec1d7cc29b70a0ba80567ece33e87`)`.

**Reversibility.** The batch and every retirement commit that follows it are separate commits. If
the owner revises the batch at Phase 5, the retirement reverts with it by Git.

#### Gate 4C part 5 — the second axis, and the refused-fixture stop

**Ordered after Part B step 1 stopped.** The approved Gate 4C part 3 blast radius was measured
on one axis: imports of `src/` modules. Retiring the v5 family breaks two more it never looked
at — reading a delete row's **bytes** (`tests/fixtures/*/extraction_snapshot.json`, by path or
by glob) and importing a **script** that is itself a row
(`from scripts.capture_extraction_snapshots import MODELS`). Neither is a package import.

**The checker now measures both, permanently.** `data_surface` / `check_data_surface_coverage`,
wired into `paths` alongside the part-3 check, so steps 2–4 cannot hit this class again. The
scan is deliberately textual and therefore conservative — a glob, an f-string and a subprocess
argument all count — because under-reporting is what produced the stop. 9 new checker tests
(45 total in that file, all green), covering path reads, globs, script imports, subprocess
invocation, retained rows contributing nothing, and a script not reporting itself.

**Ledger amendments.** The 37 v5 fixture rows and `scripts/capture_extraction_snapshots.py`
(L-275) moved from `retain` to `delete` in `4B-v5-family` — their step-1 disposition — and each
now names `tests/conformance/test_v6_recapture_batch.py` as its replacement proof node, which is
the "replacements ready in the same candidate" link made machine-checkable. Ten rows added,
L-287 … L-296, for every file the second axis revealed.

**Ruling 4 executed.** `MODELS` / `EXTRACTION_ONLY_MODELS` stay in the capture script, which is
where their capture-specific rationale belongs. The two consumers only ever needed the corpus
*names*, so the neutral home is the v6 batch manifest, surfaced by `tests/helpers/corpus.py`
(recorded pick). Checked before the move: the capture script's corpus and the batch manifest name
**the same 37 fixtures**, so no test's corpus changed. `test_calc_compat_parity.py` gets L-287
with disposition `repoint` and its Gate 4A out-of-scope subject status noted on the row.

**Ruling 3 executed in part.** `tests/conftest.py` is now L-289, `migrate` — infrastructure, not
coverage. Its `snapshot_fixture` helper names a v5 path and is used by ~50 call sites; the v6
equivalent is authored with the proof-node repoint, so the row honestly carries
`PENDING-4C` rather than a green node it has not earned. `scripts/capture_filter.py` survives
untouched, as ruled.

##### The stop: 22 of 37 corpus fixtures have no v6 graph, and coverage rides on them

Ruling 2 asked me to say per row where a proof node cannot honestly be repointed. It is not one
row, and the reason is not "intrinsically v5".

**The exact route refuses 22 of the 37 corpus fixtures** — the outcome the amended Phase 2 ledger
records and the owner approved. The refusal is by design: `SI_SELF_BINDING` means "binding
resolves to its own formal; the binding is legal, inert SysML and supplies no enclosing feature"
(`extraction/source_evidence.py:230`). The legacy route tolerated the idiom; the exact route
fails closed on it.

Measured consequence: **66 test/script files carrying 699 nodes need a graph from at least one
refused fixture**, and **27 files (241 nodes) use only refused fixtures**. For those, no v6
evidence exists and none can be produced — not for want of authoring, but because the route
declines the input.

The sharpest cases:

| File | Nodes | Fixtures it uses | Proof node for |
|---|---:|---|---|
| `test_gen_stencils.py` | 23 | `catf_mfe_model`, `solar_battery_model` — both refused | **L-006, L-241 (already executed, `6ba346e`)** |
| `test_gen_schemas.py` | 17 | same two, both refused | — |
| `test_gen_json_templates.py` | 15 | same two, both refused | — |
| `test_gen_module_wrappers.py` | 14 | same two, both refused | — |
| `test_parameter_group_deriver.py` | 25 | three, all refused | — |
| `test_entry_point_classifier.py` | 22 | three, all refused | — |

The generation-layer conformance family builds every graph from the two largest models in the
corpus, and the exact route refuses both. So the exact route has never been shown to generate a
package from a model of that size and shape, and retiring v5 removes the only coverage that says
it can.

**Disposition of the remaining ~100 files is parked on the owner ruling**, per rule 10: following
the instruction (repoint to v6) works against the recorded goal (keep the gate meaningful),
because the v6 evidence cannot exist for these fixtures. Migrating the coverage means remodelling
the 22 refused fixtures onto idioms the exact route accepts — the same named-per-child-intermediate
requirement the S4 ruling already carried to Gate 4D — which is SysML authoring work, and it
changes what a regression fixture *is*.

**Battery.** Full licensed suite **3790 passed / 47 skipped / 38 deselected**, delta **+9**
against 3781, every one a new checker node. Corpus ledger **3 passed**. Execution lane **38
passed** including the 12 real-TEAx nodes at the recorded anchors. `ruff` **870 → 870** (three
new findings introduced and fixed to hold parity), `mypy src/` **69 in 16 files → unchanged**,
`git diff --check` clean, `check_ledger_4a.py paths` **296 rows / 0 problems**, `surface`
**0 unrowed breakages on either axis**.

**Commit:** ``1d66705` (`1d66705a326df5b795ba2fffa9e1d01a04865094`)`. **Deletes nothing.** No retirement commit was made.

#### Gate 4C part 5, Class C — the dispositions part 6 does not touch

**Measured, not estimated.** 183 files are affected across both axes. **89 files (941 nodes) need
a graph from a fixture the exact route refuses** and are parked on Gate 4C part 6. The remaining
**94 files (879 nodes) are decidable now**, and 92 of them already carried a part-3 disposition.
Two did not:

- **L-127 `test_elaboration_corpus_ledger.py` → `repoint`, done here.** Its corpus enumeration
  globbed the v5 snapshots, so the test that counts the corpus depended on the files it counts.
  It now reads `tests/helpers/corpus.py`, which reads the v6 batch manifest. Its live dual-run
  half still drives `pipeline_builder` and retires with the v5 family; the file survives.
- **L-290 `test_literal_totality.py` → `defer-to-part-6`.** It names `expression_binding_probe`
  by path — a refused fixture — and its subject is literal totality *across the corpus*, a claim
  whose scope moves with which fixtures the route accepts. Not decidable until the variants exist.
  (My earlier report put this file in Class C; the classifier missed a fixture named inside a
  path string rather than on its own. Corrected here.)

##### Named temporary weakness — L-006 / L-241, CLOSED

**Closed at Gate 4C part 6 completion.** All three proof modules the C1 ruling named are now
repointed and v6-backed, and `check_ledger_4a.py replacements --row L-006 --row L-241` reports
both rows **green against all three**: `test_gen_stencils.py` (32 passed),
`test_generation_boundary.py` (20 passed), `test_gen_schemas.py` (21 passed) — 73 nodes, the
full set. No module of legacy-only evidence remains behind either row.

*(This section previously recorded the weakness as narrowed-not-gone, because
`test_generation_boundary.py` still read `catf_mfe_model` and `solar_battery_model`. It now
reads `catf_mfe_d5` and `solar_battery_d5`.)*

#### Gate 4C part 6 — the D-5 variants: rename stage done, second layer surfaced

**The corpus is untouched, and that is checked.** `catf_mfe_model` and `solar_battery_model`
still carry their refused shapes; `test_d5_variants.py::test_the_original_is_untouched_by_its_variant`
asserts no `_in` formal appears in either original and that each still has its v5 snapshot. The
ratified 15/22 corpus split is unchanged (`test_elaboration_corpus_ledger.py`, 3 passed) and the
v6 batch is unchanged (58 passed).

**Stage 1 — the D-5 rename — is complete and proved for both models.**

| Variant | Formals renamed | Files | Strip check |
|---|---:|---:|---|
| `catf_mfe_d5` | 1 (`pumping_speed_total`) | 2 | **0 problems** |
| `solar_battery_d5` | 21 | 2 | **0 problems** |

The inventory the ruling asked for: **all 25 refused bindings across both models are
`SI_SELF_BINDING`** — one code, no indexed forms, nothing outside the recipe. So the recipe
applied, mechanically, by `scripts/make_d5_variant.py`.

The proof is the 3D strip check, and it is stronger than a diff review: removing the `_in`
suffix must reproduce the original **byte for byte, file for file**. That holds only if the
rename was the sole edit, so a stray reformat or a nudged literal fails it. It runs
license-free and is pinned by `tests/conformance/test_d5_variants.py` (9 nodes). The generator
refuses to emit at all for a fixture carrying any code outside `SI_SELF_BINDING`.

##### The stop — a second refusal layer the rename cannot reach

With the self-bindings gone, both models still refuse, for reasons of a different kind that the
first refusal was masking. Every refused *binding* mapped to the recipe; what did not map is
what lay behind them.

**`solar_battery_d5` — elaborates and seals, then projection refuses.** One
`SI_RENDERING_COLLISION`, on `solar_array__raw_material_cost`. This is the S4-ratified
behaviour and `costed_cart_d5` already shows the cure: one named term per aggregation, because
the exact route names an expression parameter after the last member of a reference and drops
the qualifier, so `sum(pv_module.raw_material_cost) + sum(inverter.raw_material_cost) + …`
renders every term the same. **Measured scope: 16 colliding rollups over 50 terms**, across
`capital_cost`, `raw_material_cost`, `fabrication_cost` and `installation_cost` in every
assembly. The cure adds ~50 named intermediate attributes and rewrites all 16 rollups.

That is a *shape* change, not a rename, and it is why this stops rather than proceeds: **the
strip-check proof this gate is built on cannot cover it.** Stripping a suffix cannot recover an
original from a model that has different attributes. Applying it on the rename gate's authority
would ship the one class of edit the gate exists to make impossible.

**`catf_mfe_d5` — elaboration refuses: 152 × `SI_OCCURRENCE_MISSING`**
(`ElaborationDiagnosticError`), of the form `CATFMFERadialBuild__catf_radial_build__ht_shield__thickness:
leaf declaration 146016c8-… has no feature slot`. These are nested-occurrence resolutions on
deep part hierarchies, not bindings. No rename addresses them. Slice 3D met the same error
*code* on the customer model at 7 diagnostics and closed it with a **product change**
(`_enumeration_literal`); 152 diagnostics on nested part paths is not obviously that sub-case,
and it may be the filed nested-occurrence class.

**Consequence for the evidence gap.** The gap ruling 1 ordered closed — the exact route has
never generated from a model of `catf_mfe`'s size — is **not closed by this gate**.
`solar_battery_d5` is one ratified-but-large modelling change away; `catf_mfe_d5` is behind
something that looks like product work. The generation-layer family repoint (L-006/L-241
re-proof included) waits on both, so the **named temporary weakness recorded in the Class C
notes stands unchanged**.

**Battery.** Full licensed suite **3799 passed / 47 skipped / 38 deselected**, delta **+9**
against 3790, every one a node in `test_d5_variants.py`. Corpus ledger **3 passed** (37 rows,
15/22 unmoved). v6 batch **58 passed**. Execution lane **38 passed** including the 12 real-TEAx
nodes at the recorded anchors. `ruff` **870 → 870**, `mypy src/` **69 in 16 files → unchanged**,
`git diff --check` clean, `check_ledger_4a.py paths` **298 rows / 0 problems**, `surface`
**0 unrowed breakages on either axis**.

**Commit:** ``1935af3` (`1935af374e1d99c2f919801ddcdb6aa9db2a58d5`)`. **Deletes nothing, and repoints no test yet.**

#### Gate 4C part 6, stage 2 — `solar_battery_d5` accepted, on an enumerated difference

**The exact route now accepts a full twelve-assembly costing hierarchy: 77 modules, 199 entry
points, 221 output aliases.** That is the scale-shaped evidence ruling 1 ordered, for the
solar half.

**What stage 2 did.** With the self-bindings renamed away, projection refused with
`SI_RENDERING_COLLISION` — ratified-correct S4 behaviour. The cure is the `costed_cart_d5`
shape: **16 rollups rewritten, 49 named intermediates added**, one per term that names a
reference path.

**The proof, since byte-identity cannot cover a shape change.** Every added attribute is
derived from the original by one deterministic rule in `scripts/make_d5_variant.py` — a term
naming a reference path gets an attribute called after that path, flattened — and
`strip_check` **undoes exactly that enumerated list before comparing bytes**. An edit the list
does not name survives the undo and fails the comparison, which is the property byte-identity
was there to give. Both variants still report **strip check: 0 problems**.

The three conditions ruling 1 attached, each pinned by a test rather than asserted in prose:

- **The enumeration is published.** The full list of 49 attributes is in
  `tests/fixtures/solar_battery_d5/PROVENANCE.md` with the S4 / Gate-4D citation, and
  `test_the_enumerated_list_matches_what_the_readme_publishes` fails if the README and the
  generator disagree.
- **Same summands.** `test_the_aggregation_split_changed_no_summand` re-derives every rollup's
  terms from the original and requires each to appear as an authored attribute in the variant.
- **The disease stays visible.**
  `test_the_rename_alone_still_collides_so_the_cure_is_not_hiding_the_disease` builds the
  stage-1-only text in `tmp_path` and asserts the exact route *still* refuses it with
  `SI_RENDERING_COLLISION`. If the collision ever stops firing, that fails here rather than
  passing silently in a variant that no longer needs the cure.

**Hand arithmetic — Site Infrastructure, checked against the projected graph.** Derived from
the model, never copied from a route's output. Racking: 20 × 57 = 1140.0 material, 513.0
fabrication, 342.0 installation, **1995.0** total. Electrical Panel: 150 + 4×34 = 286.0
material, 128.7, 85.8, **500.5**. Permitting: zero material, 8 × 187.5 = **1500.0**. Rollups:
capital **3995.5**, raw material **1426.0**, fabrication **641.7**, installation **427.8**.
The test evaluates each leaf's own `calc_expressions` seeded from the graph's entry points —
so a design attribute that failed to reach the graph fails the test instead of quietly
defaulting — and separately asserts each rollup reads exactly three named intermediates wired
to the child channels the table names.

**The corpus is still untouched**: `solar_battery_model` keeps its refused shape and its v5
snapshot, the 15/22 split is unmoved, and the v6 batch is unchanged (61 nodes green).

**Battery.** Full licensed suite **3804 passed / 47 skipped / 38 deselected**, delta **+5**
against 3799, all in `test_d5_variants.py`. Corpus ledger and v6 batch **61 passed**. Execution
lane **38 passed** including the 12 real-TEAx nodes at the recorded anchors. `ruff`
**870 → 870**, `mypy src/` **69 in 16 files → unchanged**, `git diff --check` clean,
`check_ledger_4a.py paths` **298 rows / 0 problems**, `surface` **0 on both axes**.

**Commit:** ``57016f0` (`57016f0decfc36e367450dd5fbbbc00930a26968`)`. **Deletes nothing; no test repointed yet.**

#### Gate 4C part 6, ruling 2 — the `catf_mfe` investigation: it is a bounded product gap

**Report only. Nothing was fixed and no model was remodelled**, per the ruling.

##### It is not 152 problems. It is six, and they are SI units.

All 152 diagnostics resolve to **six distinct declaration ids**, and instrumenting
`_resolve_semantic_reference` to print the referent identifies every one:

| declaration id | referent | diagnostics |
|---|---|---:|
| `146016c8-c0f8-5b9b-882d-33c75906e6ee` | `SI::metre` | 113 |
| `a2be67e5-1c89-5bc6-8784-b2828a99746d` | `SI::kelvin` | 17 |
| `3cfd22ed-a3cb-567d-b426-2d83d58a3fc5` | `SI::ampere` | 10 |
| `bb1d79c2-1306-5b35-a807-93e46fc3431c` | `SI::kilogram` | 8 |
| `7868f4f7-fb26-549d-9984-bcf2b125cd1c` | `SI::tesla` | 3 |
| `171004a3-cb1f-5874-9174-e2bade7c67b3` | `SI::weber` | 1 |

They are the unit annotations on `catf_mfe`'s attribute values — `attribute thickness : Real =
0.2 [m];` and its 147 siblings. Nothing to do with nested occurrences, which is what the
message's wording suggested.

##### The mechanism

`elaborate.py:1727` (`_resolve_leaf`) asks `occurrence.py:70` (`FeatureSlotIndex.slot_of`) for
the leaf's slot. `slot_of` raises `KeyError` for any declaration outside its index, and the
index (`occurrence.py:152`, `build_feature_slot_index`) is built from
`SysideAdapter.elements_of_type(model, "Feature", …)` — **the user model's features**. `SI::metre`
lives in the standard library, so it is not there, and the `KeyError` becomes
`SI_OCCURRENCE_MISSING`.

##### Is it legal SysML the exact route should resolve? Yes — and it should not be resolving it at all

SysIDE resolved the reference perfectly well: the fact arrives carrying
`qualified_name = 'SI::metre'`, which is how the referent could be named in the table above. The
failure is downstream, in codegen's own index.

More to the point, **a unit annotation is not a data dependency**. `= 0.2 [m]` supplies one
value and one unit; the unit is metadata on the literal, not a producer of anything. Sending it
down the occurrence-resolution walk is a category error — and it is *the same category error
Slice 3D already fixed once*, for enumeration members (`_enumeration_literal`, Phase 3D notes:
"the elaborator was sending it down the alias walk, producing 7 `SI_OCCURRENCE_MISSING`
diagnostics that had nothing to do with the renames"). 3D closed one sub-case of "a reference to
a standard-library element that is not a data source". Unit references are the sibling sub-case,
still open.

##### Evidence that this is a gap and not an unsupported idiom

- **The legacy route accepts every probe.** Same parser, same model.
- **The exact route already supports units in the other spelling.**
  `modeled_default_fidelity` is a ratified corpus fixture whose stated subject is "signed and
  unit-annotated defaults survive (DD-A11, DD-A12)", it writes `in attribute rated_power : Real
  default 40.0 [W];`, and it is one of the **15 the exact route accepts**. So the route handles
  `default <value> [unit]` on a calc-def formal and fails on `= <value> [unit]` on an attribute.
  That asymmetry is a defect, not a policy.
- **One character isolates it.** `.project/active/cutover-recovery/evidence/catf-occurrence-probe/`
  holds two eleven-line models differing only by ` [m]`: with it the exact route refuses with the
  same `146016c8-…` declaration, without it the route accepts. Both are accepted by the legacy
  route.

##### Verdict: product gap, bounded, with a precedent fix shape

Not must-remodel. Remodelling would mean deleting unit annotations from **148 sites** in a
customer-derived model — destroying modelled information the legacy route preserves and that
DD-A11 / DD-A12 exist to protect. The bound is small: six library elements, one code path, and a
fix of the shape 3D already landed for enumerations.

**Recorded as a finding, not fixed.** Whether it is fixed inside part 6, filed as a follow-on,
or carried to the Phase 5 packet is the orchestrator's ruling. The reproducer is deliberately
**not** under `tests/fixtures/` — a fixture that asserts known-broken behaviour needs its own
disposition, and that is part of the same ruling.

**Consequence for ruling 3.** `catf_mfe_d5` remains unaccepted, so catf-shaped depth is still
unproven on the exact route. `solar_battery_d5` is accepted and carries the twelve-assembly
costing hierarchy. The named temporary weakness on L-006 / L-241 stands.

#### Gate 4C part 6, ruling 1 — the units fix, and `catf_mfe_d5` accepted

**`catf_mfe_d5` now elaborates: 42 modules.** No third refusal layer.

**The fix is one rule applied once, up front.** `_ExactElaborator._without_unit_annotation`
unwraps a unit annotation to the expression it annotates, at the top of `_create_value_node`,
*before* anything downstream decides whether the expression is a literal, an enumeration
member or a reference. Doing it there rather than at each downstream test is what keeps it one
rule instead of a second special case beside `_enumeration_literal`. Structural throughout — a
unit annotation is an `OperatorExpression` whose operator is `[`, value first, unit second — so
the F30 boundary guard's ban on name/QN-keyed association is untouched, and
`test_elaboration_import_boundaries.py` stays green.

**The asymmetry is closed as one rule, and stated once at both sites.** The rule is "a unit
annotation contributes its value and never a reference", which
`extraction/modeled_defaults._resolve_default_node` already states for the `default 40.0 [W]`
lane. The two lanes **cannot share an implementation** — that one reads a parsed
`ExpressionIR`, this one the syside AST — so the rule is named identically at both sites
instead of being duplicated as logic. Recorded plainly because it is the one place the ruling's
"prefer a shared helper" could not be met literally.

**Scope check, measured, all three clean.**

- **Corpus 15/22 unmoved.** `test_dual_run_ledger_outcomes_match_a_live_corpus_run` compares
  the exact per-fixture outcome strings for all 37 and passes, so no refused fixture became
  accepted and no accepted one moved.
- **v6 batch byte-unchanged.** Re-ran `capture_v6_batch.py --verify` after the fix: 15 captured,
  22 refused, 0 deviations, and `git status tests/fixtures/` reports no modified tracked file —
  every one of the 15 snapshots is byte-identical.
- **Suite delta is only new tests**: 3804 → **3810**, +6, all in
  `tests/conformance/test_unit_annotation_values.py`.

**Red → green, proved by reverting.** With `elaborate.py` stashed the new file is **5 failed /
1 passed**; with the fix applied it is **6 passed**. The one that passes in the red state is the
bare-model parametrisation, which is correct — it never carried a unit.

**The pins (ruling 2).** `tests/fixtures/unit_annotation_lanes` carries **both spellings in one
model** — `default 40.0 [W]` on a calc-def formal and `= 0.5 [m]` on an attribute value — with
`unit_annotation_lanes_bare` as the same model minus the annotations. The tests assert the
annotated value resolves, the default value still resolves, **the two models resolve to
identical values**, no `SI::` element appears as a graph dependency, and 0.5 × 40.0 = 20.0 read
off the model by hand. The asymmetry cannot come back silently.

The one-character evidence probe under `evidence/catf-occurrence-probe/` is **deleted**: it
documented a red state that no longer reproduces, and the fixtures supersede it. Keeping a
reproducer that no longer reproduces would be a trap for the next reader.

**Battery.** Full licensed suite **3810 passed / 47 skipped / 38 deselected**, delta **+6**.
Corpus ledger **3 passed**, 15/22 unmoved. Execution lane **38 passed** including the 12
real-TEAx nodes at the recorded anchors. `ruff` **870 → 870**, `mypy src/` **69 in 16 files →
unchanged**, `git diff --check` clean, `check_ledger_4a.py paths` **298 rows / 0 problems**,
`surface` **0 on both axes**.

**Commit:** ``bba3d92` (`bba3d92becd4b1e20c9b52dfc745aa326e144ddd`)`.

#### Gate 4C part 6 — the generation-layer repoint, first chunk

**`tests/conformance/test_gen_stencils.py` is repointed and green on the exact route: 32 nodes,
same count as before, no assertion thinned.** It is the highest-value file in the family — the
named replacement proof for L-006 and L-241 — so it went first.

`chain_spike_model` needed a variant too (three generation-layer files parametrise over it). It
is refused with 3× `SI_SELF_BINDING`, pure recipe: **`chain_spike_d5`, 3 formals, strip check
byte-identity 0 problems**, accepted at 3 modules / 3 entry points.

**Two expectations were re-derived from the model, not copied.**

- The exact route **expands an arrayed part into one module per occurrence**. `part pv_module :
  'PV Module' [module_count]` yields `…pv_module[0]__cost_model` … `[9]`, where the legacy route
  produced one collapsed module. 38 `cost_model` modules across the plant. The five-output pin
  now names `pv_module[0]` and the comment says why the index is there.
- The graph-only fixture returns a graph rather than `(graph, classifier_inputs)`. Every
  consumer in this file had already bound the second element to `_inputs`, so nothing was lost —
  which is the check that the legacy intermediate was not load-bearing here.

**Six files remain, with a measured inventory rather than an estimate.** After the mechanical
repoint they stand at **17 failures**, every one a genuine expectation re-derivation, not a
mechanical swap:

| File | Failures | What has to be re-derived |
|---|---:|---|
| `test_generation_boundary.py` | 7 | graph-only preservation, backlog and auto-impl dispatch on variant graphs |
| `test_gen_pipeline_yaml.py` | 5 | YAML baselines, entry-point fusion counts |
| `test_gen_json_templates.py` | 5 | parameter-group counts and schema-field sets — the 3E group-derivation change is visible here (`2 == 3`), and the D-5 rename moves entry-point keys (`width` → `width_in`) |
| `test_gen_schemas.py`, `test_gen_module_wrappers.py` | 0 after the mechanical pass | — |
| `test_gen_registry.py` | 18 errors | deepest: several tests read `inputs["snap"]`, the legacy classifier intermediate, to derive aggregation names, and one drives `generate_via_legacy_route` from a v5 snapshot |

Those six were **reverted to `HEAD` rather than committed half-migrated**. Re-deriving 17
expectations properly is more than this session's remaining budget allows, and the ruling is
explicit that assertions must not be thinned to fit. The tree stays green and the next session
starts from a known state with the inventory above.

> **Corrected by the completion chunk below.** The failure *counts* in this table held, but
> "every one a genuine expectation re-derivation" did not: seven of the seventeen — the whole
> `test_generation_boundary.py` row — were the `graph, _inputs = …` tuple unpack meeting a
> graph-only fixture, and that file needed no expectation re-derived. Five real re-derivations
> remained, and `test_gen_registry.py` retired no node at all. See the completion section.

**Battery.** Full licensed suite **3810 passed / 47 skipped / 38 deselected**, unchanged — the
repoint moved no node count. Variants, corpus ledger and v6 batch **75 passed**; corpus 15/22
unmoved. Execution lane **38 passed** including the 12 real-TEAx nodes at the recorded anchors.
`ruff` **870 → 870**, `mypy src/` **69 in 16 files → unchanged**, `git diff --check` clean,
`check_ledger_4a.py paths` **298 rows / 0 problems**, `surface` **0 on both axes**.

**Commit:** ``6822685` (`6822685f47b8b2a5d3dd6726ddd682682849e3d5`)`.

#### Gate 4C part 6 — the generation-layer repoint, COMPLETE but for four baseline-bytes nodes

**All six remaining files are repointed and green: 138 nodes before, 138 after, nothing thinned
and no node dropped.** With `test_gen_stencils.py` from the first chunk the family stands at
**170 nodes, all v6-backed except a named four.**

| File | nodes before → after | what was actually re-derived |
|---|---|---|
| `test_generation_boundary.py` | 20 → 20 | nothing: the seven "failures" were the tuple unpack, not expectations |
| `test_gen_schemas.py` | 21 → 21 | nothing beyond the repoint |
| `test_gen_module_wrappers.py` | 19 → 19 | nothing beyond the repoint |
| `test_gen_json_templates.py` | 28 → 28 | group counts and names; schema field-vs-alias |
| `test_gen_registry.py` | 22 → 22 | aggregation-import count; four legacy-intermediate subjects rebuilt |
| `test_gen_pipeline_yaml.py` | 28 → 28 | group counts; **4 baseline-bytes nodes remain legacy-backed** |

**The inventory the last chunk left was right about the count and wrong about the kind.** It
recorded "17 failures, every one a genuine expectation re-derivation." Measured: seven of the
seventeen — all of `test_generation_boundary.py` — were the `graph, _inputs = …` unpack meeting
a graph-only fixture. That file needed no expectation re-derived at all. Five real re-derivations
remained, listed below.

##### The five re-derivations, each against a ratified mechanism

1. **Solar entry-point groups, 3 → 2.** Legacy published `design_params`, `library_params` and
   `system_design`; the exact route publishes the first two. `system_design` is legacy's synthetic
   `hierarchy`-source group — **legacy-only by construction** (3E, "the legacy-only `system_design`
   hierarchy group"), so there is nothing for the exact route to match.
2. **Catf groups, 8 → 8, and two names move.** Legacy: `blanket_params` … `system_params`. Exact:
   the same eight less those two, plus `geometry_params` and `thermal_loads_params`. **3E
   declaration-site attribution** — a group is named after the file that *declares* its parameters,
   read off the fixture tree by hand: `f_exposed` at `library/physics/geometry.sysml:181`, and the
   `pump_load` formals in `library/analyses/thermal_loads.sysml`. Legacy named both after the
   *using* design file. Because the count is unchanged, a count-only assertion would have accepted
   a wholly renamed set, so **the names are now pinned alongside the counts**.
3. **Schema field names vs JSON keys.** **Per-occurrence expansion** mints keys carrying an
   occurrence index (`…__battery_pack[0]__capacity_kwh`), which no Python class body can declare.
   `core/qualified_names.params_field_name` sanitizes the field and the template keeps the exact
   key as the field's `alias`. The old assertion compared field names to raw QNs and could only
   ever fail here. It now asserts **both halves** — sanitized field names *and* the alias set —
   which is strictly stronger than what it replaced: the JSON-facing key can no longer drift.
4. **Aggregation imports, 20 → 12 (REQ-REG-01).** Hand-counted from the model, not from output:
   `solar_battery_d5/library.sysml` declares exactly twelve `attribute <n> : Real = sum(<child>.<a>);`
   intermediates — four each for `pv_module` and `inverter` (lines 615-643) and four for
   `battery_pack` (lines 672-696). Legacy counted 20 because it also synthesized an aggregation per
   assembly `:>>` rollup; the D-5 cure makes those rollups plain sums over named terms, so they
   render as FORMULA modules. **The load-bearing half is unchanged**: all twelve import paths are
   design-scoped, because the registry's aggregation branch derives the path from the module's own
   name — the design-scoped EQN (`generation/registry.py:325`, the Bug 8a rule) — and not from the
   library part def that declares the attribute. *(Worth recording because the graph's
   `module_type` for those modules **is** library-scoped; reading that field rather than the
   rendered import line briefly looked like a REQ-REG-01 regression, and is not one.)*
5. **Collision arithmetic, 20 aliased imports — unchanged.** Re-derived rather than carried:
   five colliding element names (the `Costed Item` surface) × four assemblies that redefine them
   (`solar_array`, `battery_system`, `site_infra`, `solar_battery_plant`) = 20. What changed is the
   *kinds* — the exact route renders some of the twenty as computed-attribute modules — which the
   assertion does not depend on.

##### `test_gen_registry.py`: four legacy-intermediate subjects rebuilt, none dropped

The brief expected retired nodes here. **There are none.** Every subject that read
`inputs["snap"]` had a public-surface equivalent, so all 22 nodes survive with their subjects
intact:

- **REQ-REG-01** derived aggregation element names from `snap["aggregation_expressions"]` → now
  from the graph's `AGGREGATION` modules (the element name is the last EQN segment).
- **REQ-REG-04** derived assembly names from `agg.module_eqn` → now from the EQN of each module
  that renders a colliding class name, which is a *narrower* and more exact set than before.
- **REQ-REG-05** built expected import paths from `snap["calc_defs"]` / `["computed_attributes"]` /
  `["aggregation_expressions"]` → now from each module's own definition QN, with the aggregation
  branch using the design-scoped EQN per REQ-REG-01. The requirement's subject is "one SQN →
  PythonModulePath pipeline, no ad-hoc string work," which survives intact.
- **REQ-REG-07** read `snap` and never used it. Deleted, no subject touched.
- **REQ-REG-02** drove `generate_via_legacy_route` from a v5 snapshot → now the public
  `run_codegen` from the committed v6 instance-graph snapshot, still license-free. This node is
  the strongest of the six files: it generates a real package to disk and checks every registry
  import against a file that exists.

##### The honest remainder — four YAML baseline-bytes nodes

`TestYamlBaselineComparison` (3 parametrized + `wi014_toy`) compares **bytes** against
`tests/fixtures/baseline_yaml/*.yaml`. Those four nodes stay on the legacy route, in one
clearly-labelled fixture, and the file is green. The reason is not a re-derivation this chunk
declined to do:

- The baseline bytes are captured by `scripts/capture_baseline_yaml.py` — **ledger L-039, census
  SCR-02 MIGRATE, retained precisely because "no v6 capture driver exists"**. Authoring that
  driver is SCR-02's own migration, not this chunk's declared path set.
- The files have a **second consumer outside this chunk**: `tests/integration/test_e2e_output_registry.py`
  drives the *live legacy* route against the same bytes. Overwriting them breaks it; hand-editing
  them is exactly what a byte baseline forbids.

**What the new bytes would say, measured so the next chunk starts from fact rather than a guess.**
All four differ from their committed baseline, each by a named mechanism: the D-5 formal rename
moves chain_spike's input keys (`width` → `width_in`, `length` → `length_in`, `rate` → `rate_in`);
the exact route keys `wi014_toy`'s entry points by the usage (`toy_plant__demo_plant__plant_length`)
where legacy used the definition (`Toy_Plant`); `attr_expr_probe` gains `minor_radius` and loses
three modules (17 vs 16); solar_battery grows 526 → 1343 lines on per-occurrence expansion. **No
unexplained diff** — these are the new baselines, waiting on the capture driver.

##### A measured finding, recorded not fixed — the empty-catalog report aggregator

Legacy emits a `constraint_report_aggregator` module **whenever the constraint pathway runs at
all, even with zero eligible constraints** — a deliberate D11 choice, so "a model that asserts
nothing still produces the `not_assessed` report surface" (`analysis/constraint_lowering.py:1511`).
The exact route returns early instead (`elaboration/project.py:887`, `if not constraint_outputs:
return`). Measured on `catf_mfe`: legacy 43 modules including that aggregator, exact 42 without it.
The exact route *does* emit one when there are entries (`constraint_inline`, `constraint_multi_instance`).

**Consequence, which is why it is recorded here rather than left to be noticed later.** That
aggregator was the only non-`FULLY_COMPILABLE` module across all four models
`test_generation_boundary.py` parametrizes over, so its
`test_auto_impl_context_none_for_manual` — 4 nodes — now quantifies over an empty set on every one. It was already vacuous for three of the four under legacy; catf_mfe was
the one live subject and is now vacuous too. **No assertion was thinned: the universe shrank.**
The node still fails loudly if a non-FC module ever appears carrying an auto-impl context, and
`test_from_graph_stencil_stub_dispatch` synthesizes the non-FC case directly, so the *dispatch*
behaviour keeps a live subject. Whether the empty-report surface is a behaviour the exact route
should carry is a product question for the Phase 5 packet, not a test question.

**Battery.** Full licensed suite **3810 passed / 47 skipped / 38 deselected** — **delta zero**,
node for node, against the inherited count; the repoint moved 138 nodes onto v6 without moving a
single count. Variants, corpus ledger and v6 batch **75 passed**. `capture_v6_batch.py --verify`
**15 captured / 22 refused / 0 deviations**, corpus 15/22 unmoved and no tracked fixture modified.
Execution lane **38 passed** (`-m execution tests/execution/`) including the 12 real-TEAx nodes at
the recorded anchors. `ruff check src tests scripts` **870 → 868** — two *fewer*, both dead code
this chunk removed (an unused `build_classifier_inputs_from_snapshot` import and the unused `snap`
binding); no new finding. `mypy src/` **69 in 16 files → unchanged**. `git diff --check` clean.
`check_ledger_4a.py paths` **298 rows / 0 problems**, `surface` **0 on both axes**, `replacements`
**L-006 and L-241 green against all three proof modules** — the named temporary weakness is closed
above.

*Environment note for the next session, since it cost this one real time:* the wired pair is
`/home/reid/1cfe/item7-rebuild-venv` + `/home/reid/1cfe/agentic-mbse-item7-rebuild`, **not**
`/home/reid/1cfe/agentic-mbse`. Running against the latter fails `test_exact_constraint_route.py`
at import (`preflight_identified` absent) and errors all 12 real-TEAx nodes on the lane's own
checkout guard (`tests/execution/test_fusion_tea_real_teax.py:111`). Both are environment
artifacts, not regressions.

##### Readiness for the retirement steps — 3 files in this repo, and one needs a ruling

**Not started, as instructed.** Re-derived from the ledger rather than from the Part B list: of
the **35 distinct files named as a `replacement_proof_node`**, **30 are clean** and **3 in this
repo still build from a legacy specimen** in code. Parts 5 and 6 accounted for the rest.

| Proof-node file | rows it backs | what still holds it |
|---|---|---|
| `tests/conformance/test_public_authority_switch.py` | **11** — L-005, L-011, L-018, L-019, L-021, L-022, L-023, L-025, L-028, L-030, L-031 | drives `generate_via_legacy_route` **by design**: its subject *is* the authority switch, and `chain_spike_model`'s refusal is what two of its nodes assert. The largest single block, and the one that needs a ruling rather than a repoint — there is no v6 specimen for "the legacy route still accepts what the exact route refuses." |
| `tests/unit/test_uncovered_params.py` | L-249 | genuine full house: `snapshot_fixture`, `build_full_graph_from_snapshot`, `generate_via_legacy_route`, and both refused models. A real repoint, comparable in size to one of this chunk's files. |
| `tests/conformance/test_gen_pipeline_yaml.py` | L-039 | this chunk's named remainder — the 4 baseline-bytes nodes, waiting on the SCR-02 v6 capture driver |

**Two more sit in the paired repo**, which is why a scan run here reports their files missing:
L-036 (`test_constraint_extraction.py`) and L-037 (`test_executable_profile.py`) are
`agentic-mbse` rows. They are that repo's chunk, not this one's.

**A textual scan over-reports here, so this list is the checked one.** A first pass flagged
`tests/unit/test_elaboration_import_boundaries.py` (L-032) and
`tests/conformance/test_elaboration_corpus_ledger.py` (L-044) as well. Both are false positives
and neither needs anything: L-032's `build_full_graph_from_snapshot` is a *forbidden token* in a
boundary assertion — the test requires the elaborator source **not** to contain it
(`test_elaboration_import_boundaries.py:324`) — and L-044's hit is the substring `snapshot_fixtures`
inside a test *function name* (`test_dual_run_ledger_classifies_all_snapshot_fixtures`). Anyone
re-deriving this list by grep should expect the same two and discard them.

**`replacements` state: 91 green, 204 not-required, 1 pending, 0 failures — and measured
identically at `ec41817`.** Worth stating plainly: **this chunk moved no row's aggregate state.**
L-006 and L-241 already read green before it, on `test_gen_stencils.py` alone, because the checker
reports a row green once *any* named proof node passes. What changed is underneath that counter —
all three named modules are now v6-backed, which is exactly what the C1 ruling's weakness note was
about and what the aggregate cannot see. The `--row L-006 --row L-241` output is the evidence, not
the summary line.

The one row that *did* change state is **L-289 `tests/conftest.py`**, the suite's only pending
row, whose proof placeholder read "PENDING-4C: the v6 fixture helper, and a repointed test that
uses it." Both halves now exist — `instance_graph_fixture()` and `exact_graph_from_fixture()` in
`tests/conftest.py`, and seven repointed conformance modules reading them — so the row gets two
real nodes, one per half: REQ-REG-02, which drives the public `run_codegen` from
`instance_graph_fixture`'s path, and REQ-REG-05, which reads `exact_graph_from_fixture`'s
projected graph. `check_ledger_4a.py replacements --row L-289` reports **green**, taking the
suite to **92 green / 0 pending / 204 not-required / 0 failures**.

**CORRECTION (Gate 4B step-0 measurement, below).** The table above reads as three files needing
work. Measured: **`test_uncovered_params.py` needs none**, and the `test_public_authority_switch.py`
row understates the reason — both are legacy-arm-retires-with-owner, not repoint. Only
`test_gen_pipeline_yaml.py`'s four baseline-bytes nodes are genuinely outstanding, and they wait on
the acceptance gate. See "Gate 4B step 0 — the repoint that was already done" below.

**One staleness spotted outside this chunk's path set, flagged not fixed.**
`tests/conformance/test_gen_stencils.py:345` still reads
`assert multi_output_count > 0 or model_name == "catf_mfe_model"`. `model_name` is now
`catf_mfe_d5`, so that escape hatch is dead code — the assertion is *stricter* than authored and
passes on its own merits (catf_mfe_d5 does carry multi-output modules). Harmless, but it belongs
to the first chunk's file and a one-word edit there is not this chunk's to make.

**Commit:** ``15b8486` (`15b8486913179caf120f5debf335a16aaa1e0d73`)`. **Deletes nothing.**

#### Gate 4B step 0 — the repoint that was already done, and the retirement brief that was refused

**A stage brief ordered the retirement sequence (steps 0–4). Step 0 was measured as a no-op, steps
1–4 were refused on the acceptance gate, and the orchestrator ratified both.** The resequencing
ruling at the head of Phase 4 is the outcome. Recorded here because the *measurements* are reusable
and the refusal is the kind of thing a later session must not quietly re-litigate.

##### Step 0 was already done — L-249 is green on exact-route evidence

The brief ordered `tests/unit/test_uncovered_params.py` (10 nodes) repointed onto v6 evidence.
`check_ledger_4a.py replacements --row L-249` is **green**, and it is green on the *first two*
nodes in its list, both exact-route: `test_warning_reconciliation_exact_route.py::test_the_projection_hard_codes_an_empty_fall_through_set`
(1 passed) and `::test_the_exact_route_projects_no_fall_through_entry_points` (5 passed). The
file's own 10 nodes are the third, supplementary entry.

**And the 10 nodes cannot be repointed at all** — verified at source, not taken from the row:
`elaboration/project.py:229` and `:264` both construct `ComputationGraph(fallback_entry_points=set())`,
and `collect_uncovered_params` filters on membership in that set (`resolution/uncovered_params.py:68`).
So on the exact route the collector is empty by construction, and:

- **4 nodes have a structurally unreachable subject on v6** — the `chain_override_probe` one-gap
  pin, `test_reconcile_raises_v11_on_wired_gap`, `test_seeded_strict_generation_aborts_on_v11_gap`,
  and `test_fallback_entry_points_populated_in_memory_but_not_serialized` (which asserts the
  fall-through set is **non-empty**). No v6 specimen exists or can be authored.
- **5 fixture nodes assert an empty collector** on a legacy-built graph. Repointed, they would
  assert what `test_the_exact_route_projects_no_fall_through_entry_points` already asserts across
  every clean fixture — a duplicate pin bought by deleting the real subject, which is that the
  *legacy* backtracker pre-fills those EPs (Item 9 / Item 10 behaviour).
- **1 node** (`test_unwired_fallthrough_partition`) builds its own `ComputationGraph` and is
  already route-neutral.

This is what L-249's recorded disposition already said: `repoint`, note *"Survives its owner: it
holds live coverage nothing replaces. When the owner group runs, the legacy arm is removed and the
retained assertions stay."* That is retire-the-arm-with-the-owner, not repoint-onto-v6-now.
**Executing the brief's step 0 would have been assertion thinning dressed as a migration.**

**`replacements` at HEAD: 92 green / 204 not-required / 0 pending / 0 failures** — 296 of 298 rows,
the two absent being the `agentic-mbse` rows L-036/L-037, which live in the paired repo. The brief's
step-0 goal state was already true before the brief was written.

**The one honest edit, taken.** `test_gen_stencils.py:345`'s `or model_name == "catf_mfe_model"`
disjunct is dead — `PARAMETRIZED_MODELS` is `solar_battery_d5` / `catf_mfe_d5` — so the assertion
has been stricter than authored since `6822685`. Deleted; the file holds its 32 nodes.
**Commit:** ``146bf7c` (`146bf7c667c0c3bf17950cd3c694434a85e80dc0`)`.

##### Steps 1–4 refused — the measurement behind the resequencing

`groups` at HEAD: **4B-v5-family BLOCKED by 128**; G2′ by 71, G3′ by 3, G4′ by 3. Every blocker of
every group is a `defer-to-v5-family` file, so the three later groups sit behind the family.

Retiring the family breaks, measured across **both** surface axes:

| | files | nodes |
|---|---:|---:|
| **no recorded per-file disposition** (`defer-to-v5-family` / `defer-to-part-6` / no row) | **140** | **1,419** |
| — every fixture they name has a v6 graph or a D-5 variant | 61 | 488 |
| — name no fixture at all | 44 | 527 |
| — **need a fixture with no v6 route and no variant** | **35** | **404** |

The brief's "every file executes its recorded row" has no referent: their recorded row is *defer*,
and all 140 notes read *"No green replacement… Retires with the v5 family at Phase 5 owner
acceptance."* Gate 4C part 5 had already parked the decision — *"Disposition of the remaining ~100
files is parked on the owner ruling, per rule 10."*

Underneath that sits the acceptance gate the resequencing ruling turns on, and it reaches step 4
too: `tests/helpers/legacy_route.py` (L-276) is itself `defer-to-v5-family` with the same note, so
G4′ is not independently freeable either.

**The 19 fixtures with no v6 route**, ranked by how many blocked files need them — this is Gate 4C
part 7's variant-authoring work-list, in priority order:

`issue22_model` (8), `ife_plant` (8), `plant_values` (7), `expression_binding_probe` (7),
`chain_override_probe` (6), `shared_producer` (5), `self_named_binding_trap` (5),
`plant_value_shapes` (4), `alias_agg_probe` (3), `gate_a` (3), `invocation_binding_probe` (3),
`gate_a_package_owner` (2), `crosspart_rollup_twolevel` (2), `return_styles` (2),
`self_named_rescue` (1), `agg_localterm_probe` (1), `spec_chain_channel` (1),
`spec_chain_twolevel` (1), `sibling_channel_ambiguity` (1).

#### Gate 4C part 7 — per-file dispositions for the whole deferred blast radius (IN PROGRESS)

**[ORCHESTRATOR]** ruling (2026-08-11): execute option **(b) with (c) targeted**. This is the
disposition preparation Phase 4 now owns, and its end state is the precondition for the
post-acceptance retirement being mechanical.

**Standard: the Gate 4C part 3 bar, per file, no catch-alls.** The 140 files split three ways.

| Class | Files | Nodes | What part 7 does |
|---|---:|---:|---|
| v6- or variant-repointable | 61 | 488 | **actually repoint**, green, committed |
| names no fixture | 44 | 527 | disposition on the file's **real subject**, not on its fixture |
| hard-blocked | 35 | 404 | rule individually; author D-5 variants **only** for the refused fixtures these files actually need |

**Variant standard, unchanged from part 6.** Originals byte-untouched; a variant is a new fixture
beside the original; proof is the strip check or an enumerated difference; the corpus ledger does
not move (15/22). Variants join no corpus ledger.

**Refusal-layer protocol.** Any needed fixture that refuses for something other than
`SI_SELF_BINDING`: investigate-bound-stop. Do not invent a mechanism to make a capture succeed.

**Done when** `groups` shows the v5 family and G2′–G4′ blocked **only** by the acceptance gate
itself — zero undispositioned files — and the retirement brief is purely mechanical on acceptance.

**Chunking.** Multi-session by design. Coherent chunks, full battery per commit, honest remainder
reported at each stop.

- [ ] Class 1 — the 61 repointable files *(13 done, 48 left)*
- [x] Class 2 — the 44 no-fixture files *(38 dispositioned, 6 recorded-and-left-blocked with their reason)*
- [ ] Class 3 — the 35 hard-blocked files, with targeted variants in the ranked order above *(6 done, 29 left)*
- [ ] Final: `groups` green but for the acceptance gate; ledger + checker consistent with Git truth

##### Progress — ten chunks, 100 files dispositioned, nothing deleted

| Chunk | Commit | What |
|---|---|---|
| 1 | `2b5e88f` | the 21 scripts, probes and spikes |
| 2 | `b146ec6` | the legacy resolution-stack unit tests (12 files, 183 nodes) |
| 3 | `d7b7d31` | the legacy constraint stack (6 files) |
| 4 | `6f8e653` | the small legacy-internals files (8 files) |
| 5 | `7ad8186` | the proof nodes that were themselves blocked (5 files) |
| 6 | `7bae77f` | class 2 closed out (5 retired, 6 recorded) |
| 7 | `c5e753b` | the legacy factories, deriver, classifier and registry (11 files) |
| 8 | `5e02832` | twelve more legacy suites, and the class-3 correction |
| 9 | `cd520a5` | G3′ and G4′ reach READY (8 files) |
| 10 | `b176674` | the constraint conformance family (8 files) + the L-130 repoint |
| 11 | `c674064` | **the execution lane** — the last Gate 4C must-restore (6 files) |
| 12 | *this commit* | L-180 repointed and ordered; the expression-compiler premise measured false |

**Blockers, two-axis: 124 → 43.** G2′ 40, **G3′ 0, G4′ 0**. Row dispositions stand at
**74 `retire-with-owner`, 23 `repoint`, 17 `archive-with-findings`**.

> **Count correction, measured at HEAD before chunk 11 (2026-08-11).** "43" above is the
> **v5-family** blocker count, not the remaining work. The two axes overlap but are not nested:
> G2′ blocked on 40 and the v5 family on 43, and their **union is 60 files**. The stage brief's
> "last 43 files" inherits the same undercount. The four named pieces below cover 14 of the 60;
> the other 46 carry the generic part-5 defer note and are the bulk of the "genuine repoints"
> row. Recorded rather than silently corrected, because every earlier chunk's remainder figure
> was quoted off this number.

**READY means dispositioned, not authorised.** G3′ and G4′ have no file whose fate is
unrecorded; the resequencing ruling still puts their execution after the owner stop.

**Remaining: 43 files, 335 nodes.** The class-1/2/3 split no longer organises the work, because
of the correction below. What is left is four named pieces:

| Piece | Rows | Why it is still open |
|---|---|---|
| ~~the execution lane~~ | ~~L-192, L-191, L-193, L-194, and L-113/L-114 behind them~~ | **CLOSED, chunk 11.** See the chunk-11 record below. |
| the expression compiler | L-284, L-281 (L-280 done) | **still blocked, and for a different reason than recorded** — chunk 12 measured the "mechanical rename" premise false. See below. |
| doc-coupled | L-120 `test_data_models.py` | its target list is whatever Gate 4D leaves in `09-data-models.md` |
| the genuine repoints | ~~L-180~~ (done, chunk 12), L-135, L-181, L-182, L-154, L-163, L-164, L-124, L-168, the silent-failure trio, **and the ~40 files the count correction above surfaced** | each needs coverage re-derived, not an import moved |

**`test_snapshot_v5_gate.py` (L-180) is flagged and ordered.** The retirement brief's own
post-step-4 battery requires "the v5 typed refusal still typed", so this file must be
**repointed, never retired** — and the repoint has to land **before G2′ runs**, because G2′
removes the route it currently reaches the gate through. **Done in chunk 12**; the
precondition is satisfied and the runbook step below names the surviving subject.

**Four method notes the next session should not have to re-derive.**

0. **A class-3 label bounds a repoint, not a retirement.** "Needs a fixture the exact route
   refuses" says nothing about a file that retires: a retiring file needs a green replacement,
   not a v6 specimen of its own. Six files in chunk 8 and several since retired without a
   variant. The D-5 variant work-list therefore covers only the files in the "genuine repoints"
   row above — not the 29 the earlier estimate implied.

1. **Localise, don't retire the file.** Repeatedly the legacy touch was one node in a file of
   fifteen or twenty. Moving that import inside the node it serves keeps the rest collecting and
   turns a file-level retirement into a per-node one: L-212 (23 of 26 saved), L-125 (2 of 3),
   L-129 (14 of 15), L-133 (3 of 6), L-132, L-277. The checker sees the scope change — a hit
   recorded as `func` rather than `module`.
2. **Check the proof nodes against the blocker set — every chunk, not once.** Chunk 5 found
   five proof files that were themselves `defer-to-v5-family`, backing fifteen rows including two
   already-executed deletions. Chunk 10 found a sixth the same way (L-130, named by L-157). It is
   a one-liner over `replacement_proof_node` and `group_readiness`, and it has caught something
   twice. **Currently clean: no row's replacement proof rests on a blocked file.**
3. **A row that cannot be finished stays blocked.** Six rows carry their analysis in
   `disposition_4c_note` with no clearing disposition, deliberately, so the checker never reports
   a readiness that is not true. L-120 is coupled to Gate 4D's doc-09 rewrite; L-284 waits on
   L-033's rename; L-168 needs INV-1 re-derived against the v6 envelope; L-242/L-244/L-243 are
   one per-node pass over the silent-failure diagnostics.

**Where the real remaining cost is.** Not the variant list — see method note 0. It is the
execution lane and the genuine repoints in the table above: coverage that must be re-derived
rather than re-pointed, including the one Gate 4C must-restore still outstanding (real constraint
verdict execution). Budget those as their own chunks, and do L-180 before G2′.

##### Named mechanism — the zero-constraint report aggregator (orchestrator ruling 2)

**[ORCHESTRATOR]** ruling, 2026-08-11, recorded here as a named mechanism so later
expectation deltas can cite it instead of re-deriving it. **No code change.**

Legacy emits a `constraint_report_aggregator` module whenever the constraint pathway runs at
all, even with zero eligible constraints — a deliberate D11 choice, so "a model that asserts
nothing still produces the `not_assessed` report surface"
(`analysis/constraint_lowering.py:1511`). **The exact route returns early instead**
(`elaboration/project.py:887`, `if not constraint_outputs: return`), and **that early return
STANDS**: no synthetic module without content, consistent with the epic's no-synthetic-entries
direction. Measured on `catf_mfe`: legacy 43 modules including the aggregator, exact 42
without. The exact route does emit one when there are entries.

Two consequences, both recorded rather than left to be met later:

- `test_generation_boundary.py::test_auto_impl_context_none_for_manual` (4 nodes) now
  quantifies over an empty set on all four models. No assertion was thinned — the universe
  shrank. The dispatch behaviour keeps a live subject in
  `test_from_graph_stencil_stub_dispatch`.
- `tests/execution/test_constraint_execution.py::test_zero_assertion_aggregator_not_assessed`
  is the **live subject of the retiring behaviour**. It gets a per-node disposition when
  that file is repointed, not a silent drop.

**Carried to the Phase 5 packet:** whether the empty-report surface is a behaviour the exact
route should carry is a product question for the owner, not a test question.

##### Gate 4C part 7 chunk 11 — the execution lane, and the last Gate 4C must-restore

**Real constraint verdict execution now exists on the public exact route.** That was the one
must-restore Gate 4C still owed, and it is the piece the whole retirement was waiting on: six
rows (L-192, L-191, L-193, L-194, and L-113/L-114 behind them) whose evidence ran entirely
against owners the retirement deletes.

**Why none of the four execution files could be repointed.** Method note 1 (localise, don't
retire) does not reach them. Nine of L-192's fifteen nodes *construct a `ComputationGraph` by
hand* out of `analysis.constraint_lowering`, `analysis.parameter_groups` and
`resolution.models`; the other six drive `orchestration.pipeline_builder`; and the three
siblings import `_generate_full_package`/`_run` from L-192, so they break twice over. There is
no import to move — the graph assembly *is* the legacy route.

**What replaces them.** `tests/execution/test_constraint_verdicts_exact_route.py`, 15 nodes,
every one going model → `run_codegen` → TEAx's own `ProvisionalPackageLoader` → the real
executor. No graph construction, no patched import, no v5 snapshot anywhere in the path. The
per-node accounting for all fifteen legacy nodes is on the L-192 row; the four things worth
lifting out of it:

- **`test_zero_assertion_aggregator_not_assessed` retires with its subject.** It is the live
  subject named by ruling 2 above. Legacy emits the aggregator with nothing to assess; the
  exact route returns early (`elaboration/project.py:887`) and that early return stands. Not
  replaced, not silently dropped — carried to the Phase 5 packet as the owner's product
  question, exactly as the ruling said it would be.
- **The seal changed how a value moves, and that is recorded rather than worked around.** The
  legacy lane edited a generated `inputs/*.json` and re-ran. The exact route seals what it
  writes, so that edit is now a `SealVerificationError` — and the plan already calls
  edit-and-reseal the invalid route. Values move through TEAx typed entry injection
  (`CandidateBridge` + `PreparedEvaluator`), the protocol Slice 3D ratified. That gives two
  observation surfaces and the specimens use both deliberately: the file-backed sealed run
  publishes whole `ConstraintEvaluation` objects (status, `actual_value`, `margin`,
  `observed`) and persists the report, while injection is what can move a modelled value and
  projects verdict *statuses*. A claim about the shape of a verdict is made against the first;
  a claim about a value driving a verdict against the second.
- **Two replacements are stronger than what they replace.** The R-3 name-safety refusal
  reached the legacy node through a v5 snapshot of `constraint_inline`; the replacement reaches
  the same refusal from the live model and additionally requires that no package tree was left
  behind. And `test_break_the_yaml_surfaces_execution_failure` becomes
  `test_rewiring_the_generated_pipeline_is_caught_before_anything_executes`: under the seal a
  rewired `pipeline.yaml` is refused before the executor sees it, which is earlier and more
  specific than the executor's wiring error.
- **One legacy row had no execution-level counterpart and now does.** The polarity
  parametrization's `strict-boundary` case needed a `>` predicate, and no fixture carried one.
  `constraint_strict_boundary` is `constraint_shared_polarity` with the operator swapped, and
  the replacement pins the two operators *disagreeing at equality* rather than sampling one.

**Three fixtures authored, at the established standards.**

| Fixture | Kind | Standard met |
|---|---|---|
| `gate_a_d5` | D-5 variant of corpus `gate_a` | strip check, 0 problems; original byte-untouched with its v5 snapshot; joins no ledger |
| `constraint_occurrence_demand_overrides_d5` | D-5 variant | strip check plus **one enumerated difference** — see below |
| `constraint_arithmetic_raise`, `constraint_strict_boundary` | new originals, D-5 form from the start | no variant needed; the exact route admits both unchanged |

**The D-5 recipe was widened to `constraint def`, and that was measured, not assumed.** The
first `gate_a_d5` renamed only the *binding's* left side inside `assert constraint viability`,
leaving the declaration saying `gain` and the binding saying `gain_in`. The exact route refused
that model at generation with `cross_scope_binding_disagreement` — a refusal outside
`SI_SELF_BINDING`, which is the refusal-layer protocol's stop trigger. It resolved to a gap in
the tool rather than a premise conflict: the recipe's own wording is "inside the block that
declares the formal", and a `constraint def` declares formals exactly as a `calc def` does.
`_DEFINITION_BLOCK` in `scripts/make_d5_variant.py` now matches both, including single-quoted
names. **Every pre-existing variant's strip check was re-run and still passes.**

**A second-layer refusal, investigated and bounded rather than engineered around.** After the
rename, `constraint_occurrence_demand_overrides_d5` refused again, at projection:

```
SI_RENDERING_COLLISION: package-scoped 'OccurrenceOverride__keep_pipeline' in a model.sysml
has no root occurrence to take a parameter-group identity from
```

That is the ratified Slice 3B option-C rule — group identity comes from the filename stem, and
the `model.sysml` fallback wants the declaring package of the owning root occurrence, which a
package-scoped calc has none of. Nothing was invented to get past it: the file is *named*,
which is what the rule asks a model to do. The difference is **one filename and zero bytes**,
enumerated in the fixture's `PROVENANCE.md` and pinned by
`test_the_occurrence_overrides_variant_differs_by_the_rename_and_the_filename`.

**The proof-integrity cross-check is now a script, not a habit.** Method note 2 said to run it
every chunk and it has caught something twice. `scripts/check_proof_integrity.py` reads the
Gate 4A checker's own `group_readiness` over all six groups and fails any row whose replacement
node lives in a file still blocking a deletion — transitive through G2′/G3′/G4′ by construction,
because readiness is measured over every group's surface. Clean at chunk 11: **0 problems over
54 blocked files.** It is also what unblocked L-113/L-114, whose earlier note held them back
precisely because their owner (L-193) was still scheduled to break.

**Blockers after chunk 11: G2′ 40 → 38, v5-family 43 → 37, union 60 → 54.** G3′ and G4′ stay
at 0.

**Battery.** Full licensed suite **3822 passed / 47 skipped / 53 deselected**, from 3816/47/38.
Delta fully explained: **+6 passed**, all in `tests/conformance/test_d5_variants.py` (the four
parametrized proofs applied to `gate_a_d5`, plus the two nodes that carry the occurrence
variant's enumerated difference); **+15 deselected**, the new execution-marked nodes. Execution
lane `pytest tests/execution -m execution` **53 passed**, from 38 — the 12 real-TEAx anchors
unchanged. `capture_v6_batch.py --verify` **15 captured / 22 refused / 0 deviations**. Corpus
ledger test 12 passed. `ruff check src` **16**, whole tree **868** — both unchanged. `mypy src`
**69 errors in 16 files**, unchanged. `git diff --check` clean. Checker: `paths` 298 rows / 0
problems, `surface` 0 unrowed breakages, `groups` as above, `replacements` green for all six
rows under `required_suite: execution`.

**Deletes nothing.**

##### Gate 4C part 7 chunk 12 — L-180 ordered and satisfied, and a premise measured false

**L-180 `test_snapshot_v5_gate.py` is repointed, and the ordering constraint is now discharged.**
The retirement runbook's post-step-4 battery asks whether "the v5 typed refusal is still typed".
Chunk 12 established that after G2′ **it could not have been**: G2′ deletes
`snapshot/loader.py` (L-016), the only raiser of `SnapshotFormatError`, together with
`orchestration/snapshot_context.py` (L-026). The check had no surviving subject.

It has one now, and the subject was found rather than manufactured. `snapshot/envelope.py` is
in no deletion group and **already** refuses a v5 extraction snapshot with a typed
`SnapshotShapeError` that names what it was handed — `this is a v5 extraction snapshot, but the
instance-graph route requires snapshot v6` — and gives the recapture instruction. Four new
nodes pin it: both skew directions against the v6 reader, the v5 payload refused *by name*
rather than as a null version, the gate running before any semantic read (corrupt the instance
graph past every decoder **and** the version — the version error must win), and the public
`run_codegen` route declining while writing no package.

The six pre-existing v5 nodes are **kept and import-localised** (method note 1):
`build_pipeline_context_from_snapshot` moved from module scope into the three bodies that need
it, so the checker now records the hit as `func` rather than `module` and G2′ no longer breaks
the file's collection. Those six retire with the v5 family, when the fixtures they read do —
which is the row's remaining data-axis hit, correctly unresolved until that step.

**Rule-10 surfacing: the expression-compiler duals are not one behaviour under two names.**

The Gate 4A carried-input note describes each retained 3C dual that way and prescribes "delete
the legacy member and drop the `Exact` qualifier from the survivor". L-284's and L-281's
earlier notes inherited it: the repoint "cannot be finished before L-033's rename lands", and
would then be a re-point at the survivors. **That premise is false**, and it was measured, not
argued.

`scripts/probes/probe_expression_compiler_qualifier_drop.py` rebinds the three legacy names to
their survivors inside the module the tests import from — exactly what dropping the qualifier
leaves behind — and runs both modules against it. **48 passed, 26 failed, 5 errors.** The node
list is archived at
`.project/active/cutover-recovery/evidence/expression-compiler-qualifier-drop-dryrun.txt`.

The duals differ in key type, field names and mutability, not only in name:

| legacy | survivor |
|---|---|
| `CompilationResult(output_name: str, input_refs: list[str], intermediate_refs: list[str])`, mutable | `ExactCompilationResult(output_id: UUID, input_ids: tuple[UUID, ...], dependency_ids: tuple[UUID, ...])`, frozen |
| `CalcDefCompilationResult(calc_def_name: str, …: list)` | `ExactCalcDefCompilationResult(definition_id: UUID, …: tuple)` |
| `compile_calc_def(calc_def, expression_asts, all_member_names, member_expressions)` | `compile_calc_def_exact(calc_def)` |

The failure classes say the same thing in the tool's own words: 18 nodes on
`compile_calc_def_exact() takes 1 positional argument but 2 were given` /
`got an unexpected keyword argument 'all_member_names'`; 10 on
`ExactCompilationResult.__init__() got an unexpected keyword argument 'input_refs'` /
`missing 1 required positional argument: 'output_id'`; 3 on genuine assertion differences.

**Consequence for the runbook, which is why this is a stop and not a footnote.** The
post-acceptance step for these two rows is **not mechanical**. 31 of their 76 nodes are bound
to the legacy *shape*, not the legacy *name*, and re-expressing them against a UUID-keyed
survivor is authoring work with its own per-node dispositions. Scoped so the size is known
rather than estimated: L-284 15 of 52 fail the dry run, L-281 16 of 24. One L-281 node is not
repointable at all — `test_exact_compiler_surface_does_not_replace_the_legacy_adapter` asserts
`compile_calc_def_exact is not compile_calc_def`, so its whole subject is that the two duals
are *distinct*; read the other way, it is the pin that already recorded what this dry run
measured.

**Both rows stay blocked**, per method note 3. Dispositioning them would report a readiness
that is not true, and pre-declaring the step mechanical would put unbudgeted authoring behind
the owner stop — the exact failure the resequencing ruling exists to prevent. **This is the one
open question chunk 12 returns to the orchestrator**: the L-033 dual retirement needs its own
scope, and the Gate 4A "one behavior under two names" characterisation should be re-checked
against the other five retained duals before any of them is scheduled as a rename.

**Blockers after chunk 12: G2′ 38 → 37, v5-family 37 → 36, union 54 → 53.**

**Battery.** Full licensed suite **3827 passed / 47 skipped / 53 deselected**, from 3822/47/53.
Delta: **+5 passed**, all in `tests/conformance/test_snapshot_v5_gate.py` (7 nodes → 12: four
new v6-envelope nodes, one of them parametrized over two skew directions). Deselected
unchanged. `ruff check src` **16**, whole tree **868** — both unchanged. `mypy src` **69 errors
in 16 files**, unchanged. `git diff --check` clean. Checker: `paths` 298 rows / 0 problems,
`surface` 0 unrowed breakages, `replacements` green for L-180. Proof integrity **0 problems
over 53 blocked files**.

**Deletes nothing.**

### Phase 5 Completion

- **Completed:** Pending
- **Candidate/audit/owner disposition:** Pending
- **Issues/deviations:** Pending

---

**Status:** Draft → Owner-approved → In progress → Audited → Owner accepted/revised
