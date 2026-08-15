# Stage brief — Phase 2: Establish Clean Recovery Authority and Baseline

**You are executing exactly one phase** of the owner-approved recovery plan. The plan is NOT in the
original worktree anymore (Phase 1 moved it to the forensic branch, by design). Read it from the
forensic commit first:

```bash
git -C /home/reid/1cfe/sysml-codegen show 07531e64ed912d6046afce47ef0d958605e6ca08:.project/active/cutover-recovery/plan.md
```

Execute its **Phase 2 only**. Phase 1 is complete and verified; its results (forensic OIDs,
archive manifest, and the completion-notes text you must paste into the plan) are in
`/home/reid/1cfe/item7-recovery-archive/phase1-results.json`.

## State you inherit

- sysml-codegen: `/home/reid/1cfe/sysml-codegen`, clean on `source-identity-epic` @ `1672c576…`.
- agentic-mbse: `/home/reid/1cfe/agentic-mbse`, clean on `elaborate-first-salvage` @ `5088b417…`.
- Forensic branches (never merge, never install from): `item7-forensic-20260810` =
  codegen `07531e64…`, agentic-mbse `ed5b8b02…`.
- External archive: `/home/reid/1cfe/item7-recovery-archive/` (do not modify; read-only evidence).
- Pinned TEAx checkout: `/home/reid/1cfe/teax` (read-only; record its HEAD).

## Owner rulings already recorded in the plan (do not re-ask)

- **B37-01 pre-ruling [OWNER 2026-08-10]: modeled aggregation is accepted as executable** —
  contingent on your clean-baseline re-verification matching the recorded evidence. If the
  evidence diverges, STOP and report; do not apply the ruling.
- **C25/C2 mutation protocol: delegated.** Investigate what the seal contract and TEAx actually
  support, pick the soundest route, record decision + rationale in the plan. Escalate only if
  every route weakens package integrity.
- The owner approved updating `CURRENT_WORK.md` to name recovery as active (approval already given).

## Environment gotchas (hard-won facts; trust these)

- The syside license key lives at `/home/reid/1cfe/agentic-mbse/.env` (there is no `.env` in
  codegen). Before any licensed suite run: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`.
  The ONLY valid license proof is zero `no live syside license` skip lines in pytest output —
  pass/skip counts do not discriminate. An unlicensed full codegen run silently reads as a fake
  baseline (~23F/96E or mass skips).
- TEAx's own `.venv`/`uv run` is broken for executing generated packages. Build ONE task-specific
  rebuild venv containing: agentic-mbse editable from `/home/reid/1cfe/agentic-mbse-item7-rebuild`,
  sysml-codegen editable from `/home/reid/1cfe/sysml-codegen-item7-rebuild`, all their declared
  deps (jinja2 included), and teax-simkit from `/home/reid/1cfe/teax/packages/teax-simkit`.
  Print and record resolved import paths for `sysml_codegen`, `agentic_mbse`, and SimKit; FAIL
  setup if any resolves into `/home/reid/1cfe/agentic-mbse`, `/home/reid/1cfe/sysml-codegen`, or a
  forensic path.
- Never `ruff format` tests/fixtures/baseline_outputs — generator-owned bytes.
- Expected comparison data (not the answer): Item 6 codegen suite was ~3358 passed / ~47 skipped
  licensed; agentic-mbse ~1811/1/33. Record what you actually measure.

## Execution order (plan Phase 2, operationalized)

1. `git -C /home/reid/1cfe/sysml-codegen worktree add /home/reid/1cfe/sysml-codegen-item7-rebuild -b item7-rebuild source-identity-epic`
   and the agentic-mbse equivalent (`-b item7-rebuild elaborate-first-salvage`).
2. Restore into the codegen rebuild worktree from the forensic commit: the whole
   `.project/active/cutover-recovery/` (plan + briefs), the two forensic research records in
   `.project/research/`, and `.project/active/elaborator-cutover/` as shaping/incident evidence
   (git show or git restore --source=07531e64…; never merge/cherry-pick).
3. Paste the Phase 1 completion notes from `phase1-results.json` into the plan (completion section
   + commit-gate PENDING fields + tick the Phase 1 progress checkbox). Add the superseded banner
   to `.project/active/elaborator-cutover/plan.md`. Copy this brief to
   `.project/active/cutover-recovery/briefs/phase2.md` in the rebuild worktree.
4. Build the rebuild venv per above; record import paths.
5. Run the full clean suites (codegen licensed + agentic-mbse) from the rebuild worktrees; record
   collection/pass/skip/deselect counts and full test-path inventory.
6. Run the clean Item 6 37-path comparator (or reconstruct from certified Item 5/6 artifacts —
   `.project/completed/20260809_elaborator-breadth/` has the diff-ledger). Classify readiness
   `ElaborationError.findings` vs validation `ElaborationDiagnosticError.diagnostics` separately;
   exact diagnostic multisets.
7. Run the clean public Fusion Tea generation/execution path available at Item 6; record limits.
8. B37-01: re-verify the four evidence legs on the clean baseline (fixture literal at
   `tests/fixtures/agg_literal_probe/library.sysml`; Item 5 commit `483443e`; fixture header
   intent; ledger row provenance in `.project/completed/20260809_elaborator-breadth/diff-ledger.md`).
   Matching evidence → apply the pre-ruling (amend ledger/spec/census rows in the rebuild tree,
   note the restore-the-test obligation for Phase 3/4). Divergent → STOP.
9. C25/C2 protocol: investigate (seal implementation, TEAx runtime override surface, regeneration
   route), decide, record in the plan.
10. Derive the 22 incident-modified `docs/architecture/` paths from the forensic diff; hash all
    architecture docs at baseline; reject unexplained identical-content groups. Review the
    forensic `CLAUDE.md` diff separately; record `restore` or `accept with exact edits`.
11. Write `.project/active/cutover-recovery/evidence/baseline.json` (heads, env, counts,
    inventory, doc hashes, corpus outcomes, Fusion Tea result).
12. Update `CURRENT_WORK.md` in the rebuild worktree: recovery active, Item 7 execution superseded.
13. Planning commit on `item7-rebuild` (codegen): staged paths must be `.project/**` plus
    `CURRENT_WORK.md`'s home only — verify with `git diff --cached --name-only`. Hooks must pass
    (no bypass authorized for this commit). agentic-mbse planning commit only if project metadata
    changed there; otherwise record `N/A`.

## Hard rules

- Never modify the two original worktrees or move any branch ref other than creating
  `item7-rebuild`. Never touch the archive except reading. The forensic candidate is a parts bin —
  read files from it, never merge it.
- Treat prior reported counts as comparison data, not expected answers. Explain every delta you
  can; record the ones you can't as findings.
- If a rule-10 premise conflict appears (evidence divergence, unexplained product diff), STOP and
  report rather than resolving silently.

## Report back

Summary must include: worktree paths + heads, venv import-path proof, measured suite counts vs
Item 6 comparison data with explanations, 37-path corpus outcome summary, Fusion Tea result,
B37-01 verdict (evidence matched → ruling applied, or divergence), C25/C2 decision + rationale,
doc-hash findings, CLAUDE.md disposition, planning commit OID(s), and
`ARTIFACT: /home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/evidence/baseline.json`
