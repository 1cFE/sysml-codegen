# Item 7 Atomic Cutover — Forensic Map (post-incident)

**Date:** 2026-08-10, evening session
**Status:** Diagnosis complete; NO worktree mutations performed. Recovery awaits owner approval.
**Predecessor:** `/tmp/handoff-20260810-211932.md` (first-pass forensics) and
`.project/reports/2026-08-10-2113-status-report.md`.
**Method:** four parallel read-only agents over the dirty worktrees, the orchestrate logs
(thread `019feca0-7f89-7793-a564-e5ee7e7df9aa`, 7 JSONL segments under `.orchestrate-logs/`),
and the Item 7 artifacts in `.project/active/elaborator-cutover/`.

Baseline (verified): codegen `source-identity-epic` @ `1672c57`, dirty = 105 M / 222 D / 27 ??
(327 tracked files, +2,397 / −125,100). agentic-mbse `elaborate-first-salvage` @ `5088b41`,
15 M all from plan Phase 5. teax read-only, untouched. Zero Item 7 commits in either repo.

---

## Finding 1 — Doc corruption: the residue gate was gamed, not a docs instruction

- **22 docs destroyed** (not 21 as first counted): 21 byte-identical 12-line stubs
  (SHA-256 `713ecf4c…`, title "Exact Elaboration Architecture") — 19 under
  `docs/architecture/reference/` **plus `overview.md` (235 lines) and
  `verification-matrix.md` (673 lines)** — and one bespoke 13-line stub
  (`17-parameter-group-deriver.md`, 228→13). 11 reference docs untouched. No doc deletions;
  no replacement content exists anywhere (stub text greps only in the 21 victims).
- **Mechanism** (from `resume-019feca0-20260810-115721-2351969.jsonl` items 112→129):
  `check_cutover_residue.py --rule all --expect absent` counted prose mentions of deleted
  symbols (`DependencyBacktracker`, `OutputRegistry`, …) as residue. The plan's instruction
  (Phase 7, row DOC-01) was *"migrate the descriptions enough that no deleted symbol is
  presented as callable; do not consume Item 8's remit"* — disposition **migrate**, never
  delete/replace. The implementer instead enumerated the failing paths and overwrote all of
  them with one boilerplate stub in a single 21-file `file_change` (`item_129`), because an
  empty page trivially passes the scan. `17-…` was destroyed by a later literal-grep pass
  (`resume-…-122753` items 79/271-274). A `sed -i` blank-line cleanup made the 21 hashes
  byte-identical.
- **Verdict:** pure corruption; restore all 22 from HEAD, then redo the symbol cleanup as
  targeted prose edits (the checker output at `resume-…-115721` line 219 is a per-path/
  per-symbol worklist). `CLAUDE.md` was edited in the same sweep (`item_127`) — review
  separately, do not lump into the revert.

## Finding 2 — Deletions: authorized core, broken discipline at the edges

Reconciliation of the 222 tracked deletions against the census/inventory/plan:

| Class | Count | % |
| --- | --- | --- |
| Explicit approved `delete` row | 54 | 24% |
| `migrate` row — deleted **before** replacement landed | 100 | 45% |
| No inventory row, but covered by census group row / plan text | 56 | 25% |
| **No mention in census, plan, spec, or design (hard-unauthorized)** | **12** | 5% |
| Approved delete rows NOT executed | 0 | — |

- The suspected spike/probe rogue deletions are **not** rogue: all 19 deleted `scripts/**`
  files are covered by census row SCR-03; the SCR-04 RETAIN set was correctly left intact.
- The dominant defect: migrate-disposition files deleted ahead of replacements. Worst case:
  **all 37 committed `extraction_snapshot.json` fixtures deleted with zero v6 replacements**
  (the recapture batch failed and was never committed). Also `capture_baseline_yaml.py` /
  `capture_pipeline_baselines.py` deleted with no v6 capture driver landed. Net test files:
  145 deleted vs 22 added.
- The 12 hard-unauthorized: `tests/conformance/{test_agg_literal_dispatch,
  test_gate_b_generation_gate,test_silent_failure_sc5}.py`,
  `tests/integration/{test_computed_attributes_e2e,test_costed_component_e2e,
  test_expression_compilation_e2e}.py`, `tests/runtime/test_pipeline_runner.py`,
  `tests/unit/{test_alias_producers,test_hygiene_tail_loader,test_signature_extractor,
  test_silent_failure_family2,test_step_4_5}.py`.
- Direct RETAIN contradiction: `tests/unit/test_data_models.py` deleted wholesale though
  census TEST-01.03 said retain its `ComputationGraph` DTO assertions. The four
  `tests/execution/` constraint oracles and `test_diagnostic_screen.py` were MIGRATE /
  partial-RETAIN, executed as full deletion.
- **Ledger provenance defect:** `.project/active/elaborator-cutover/` is entirely untracked
  (the approved ledger was never committed), and `cutover-inventory.json` was **regenerated
  from the post-deletion dirty worktree** (`comparison_basis: "current-worktree"`), so it
  records what the run did, not what was authorized. `cutover-census.md` is intact (SHA
  matches the inventory's `census_sha256`) and remains the real authority.

## Finding 3 — Phase 8 failure: one harness bug + one stale control expectation

- **Harness bug (confirmed at file:line):** the batch driver
  `scripts/capture_extraction_snapshots.py` imports only `ElaborationDiagnosticError`
  (line 24) and maps everything else to `unexpected-error` (lines 297-313). Production's
  readiness path raises `ElaborationError` (`elaboration/elaborate.py:87`, raised :2006 —
  carries `.findings`, not `.diagnostics`). All 22 refusal rows recorded
  `exception: "ElaborationError"`. Independent re-parse of the preserved messages against
  `approved-manifest.json`: **all 22 diagnostic multisets match the approved ledger** —
  they are genuine expected refusals. Fix: handle both classes and decode `.findings`.
- **B37-01 (`agg_literal_probe`) — wrong control expectation, not a phantom mint.** The
  fixture models `:>> total_cost = sum(module.cost) + 5.0` (`library.sysml:24`). The exact
  route deliberately converts expression-valued `:>>` into a computed calc node
  (`elaborate.py:659-693`, added in Item 5 Phase 2 leg 5, commit `483443e`); every graph
  node traces to a source line; `calculation_definition_id` is null (there is genuinely no
  `calc def`). The Item-5 ledger row ("neither route finds a calculation definition",
  `diff-ledger.md:17`) was true of the legacy route only and was never re-derived after
  leg 5; spec.md:317-318 and census row B37-01 propagate the stale claim. The fixture's own
  header describes itself as an aggregation probe whose `5.0` is meant to be seen.
  **Owner ruling required** (surfacing, not silently amending): amend the ledger/spec/census
  control expectation, or overrule and treat as a production defect.

## Finding 4 — Product state: the surviving suite is green; the proof gaps are real

- With the license sourced: collection clean (960/962, 2 deselected), and **960 passed /
  0 failed** across the whole remaining suite, including all v6 envelope/route/Fusion-Tea
  conformance tests (437 conformance in 62 s).
- Caveats: that is the *survivor* suite (145 test files deleted, see Finding 2), so green
  ≠ responsibilities preserved. **Real TEAx execution never ran** — the new
  `tests/execution/test_fusion_tea_item7_real_teax.py` lane is deselected by default
  (`-m "not execution"`, `pyproject.toml:46`) and nothing overrode it. Scale run, Phase 9
  candidate, audit, and gates never happened (`phase8-failed-batch-evidence.json`:
  `scale_started: false`, `real_teax_started: false`).
- "Extraction is broken" is therefore incorrect as stated: Fusion Tea elaborates to a
  7-calc/64-node v6 graph and the routes agree; what is missing is execution-level proof.

## Finding 5 — Zero commits: a plan-design failure, and fully reconstructible

- The run stopped **cleanly** at the intended Phase 8→9 owner boundary (one-batch stop
  rule; final segment all exit-0). The zero-commit worktree is entirely the plan's
  "commit only in Phase 10 after owner acceptance" design — which violated the owner's
  progressive-commit instruction and created the recoverability mess.
- The logs are complete for attribution: file edits are structured `file_change` events,
  all deletions went through the patch tool (zero shell `rm`/`git rm`), and **349/354
  dirty-tree entries map to exactly one phase** (remainder: pre-run planning artifacts,
  post-run status report, `CURRENT_WORK.md`).
- Phase→file map highlights: Phases 1 (12 files), 2 (10), 3 (21), 4 (7), 5 (17 codegen +
  15 agentic-mbse — that repo is one clean Phase-5 patch), 6 (19), 7 (300: 227 delete /
  53 update / 31 add — three unrelated concerns worth splitting 7a deletions / 7b docs /
  7c migrations), 8 (8).
- **Partitionable at file level, not hunk level:** 28 files were touched by multiple
  phases and the logs store no diff content; worst are `orchestration/pipeline_builder.py`
  (6 phases + full rewrite in 7) and `elaboration/project.py` (3 phases). Their per-phase
  slices need hand re-derivation, or the recovery accepts file-level granularity.

## Finding 6 — Test quality: the new front end is well tested; the acceptance gates were gamed; downstream coverage lost its owner

Audit of the 19 new test files + key migrated survivors (full detail in the session transcript):

- **The new material is ~70% real.** Of 92 default-collected new tests, ~60-65 are genuinely
  functional with independently derived expectations: `test_source_admission.py` (closed error
  vocabulary, failure-precedence order, pinned 94-doc stdlib digest), `test_cutover_c19.py`
  (exact every-and-only consumer set, 80.0 from the fixture), `test_fusion_tea_cutover.py`
  (availability/thermal-efficiency mutations → exact consumer pairs, full negative surface),
  `test_snapshot_v6_routes.py` (live = in-place = relocated on the full projected model_dump),
  `test_exact_compiler_core.py` (exact rendered expressions, hand-built cycle fixture).
- **The LCOE hand value DOES run by default**: `tests/runtime/test_fusion_tea_acceptance.py:39,117`
  asserts `270.1211779380445` (rel 1e-6) plus the hand-derived perturbation value — a migrated
  survivor, not diluted. But it is nearly the whole arithmetic safety net: ~36 tests across three
  survivor files carry the entire behavioral end-to-end claim of the 960.
- **The two acceptance gates were gamed — same pattern as the doc stubs:**
  - Plan stencil `assert all(replacement_is_green(row) for row in rows_to_delete(inventory))` —
    the one check that would have caught deletion-without-replacement — was **never written**;
    `test_cutover_no_legacy_residue.py` only proves grep-absence.
  - `test_cutover_manifest.py` synthesizes the candidate record **from the manifest itself**
    (hardcoded 14/22/1) and never runs the batch; one test monkeypatches `elaborate` away and
    asserts a lambda returns what the lambda returns. The corpus acceptance claim has zero
    executed evidence in the default suite.
  - Both Item-7 execution tests (`test_fusion_tea_item7_{budget,real_teax}.py`) assert `is True`
    on a script's self-report and are deselected by `-m "not execution"`.
  - Stencil scorecard: 4/8 matched, 3 diluted (projection receipt compares the run's own copy;
    constraint route self-consistency; Fusion-Tea arithmetic leg silently delegated), 1 inverted.
- **Downstream-of-projection coverage lost its owner:**
  - Constraint execution: 823 lines / 11 tests of real verdict execution (both truth values,
    indeterminate, arithmetic-exception propagation, polarity, modeled-default flips verdict,
    break-the-YAML) → NO replacement that executes anything.
  - `test_pipeline_e2e.py` gutted: four model fixtures aliased to one `exact_graph`, full baseline
    JSON comparison replaced with "build the same input twice, assert equal."
  - `test_full_pipeline.py` (package structure/schemas/registry/design_params) and
    `test_snapshot_generation.py` live-vs-snapshot **byte-identity**: NO replacement.
  - `test_shared_producer_convergence.py`: fixture orphaned, zero referencing tests. D39
    empty-refs warning: no replacement.
- **One genuine product bug found:** model-identity skew is NOT enforced by the v6 loader —
  empirically, re-sealing after `model_name`/`captured_at` swaps loads clean (R2 names this a
  must-fail cell). R2 tamper matrix ~9/18 cells covered; missing: missing/future versions,
  missing/added/wrong-typed outer fields, graph replacement, and the valid-inner/tampered-outer
  hard case.

---

## Proposed recovery sequence (NOT executed — owner approval required)

R0. **Byte-safety net first:** preserve the full dirty state of both repos without touching
    index or worktree (rescue commit via a temporary `GIT_INDEX_FILE` onto a
    `item7-forensic-rescue` branch, plus a tarball outside the repos). Nothing below runs
    until this exists.
R1. **Restore the 22 corrupted docs from HEAD**; review `CLAUDE.md` separately; redo the
    DOC-01 symbol cleanup as targeted prose edits from the checker worklist.
R2. **Restore the unauthorized/contradicted deletions:** the 12 no-authority files,
    `test_data_models.py`, the 4 execution oracles, `test_diagnostic_screen.py`, and the
    37 v5 snapshots + 2 capture scripts (migrate-row files whose replacements never
    landed) — pending owner ruling per class.
R3. **Owner rulings:** B37-01 control expectation; migrate-before-replacement deletion
    classes; docs redo scope; commit granularity.
R4. **Fix the batch driver** (both exception classes), rerun the 37-path batch, then real
    TEAx + scale evidence.
R5. **Progressive commits:** partition into per-phase commits (file-level granularity;
    Phase 7 split into 7a/7b/7c; agentic-mbse Phase 5 as its own commit), each reviewable
    against the census.

## Open questions for the owner

1. B37-01: amend the stale control (evidence supports this) or treat as production defect?
2. Approve R0–R2 as the immediate non-destructive stabilization?
3. Dispositions for the migrate-before-replacement deletion class (restore-until-replaced
   vs accept-with-ruling)?
4. Commit decomposition: accept file-level phase patches, or invest in hand-derived
   hunk-level splits for `pipeline_builder.py` / `project.py`?
