# Stage brief — REVISE step 7b: independent audit of the RETIRED tree

You are the independent auditor of the Item 7 retired tree. You implemented none of it. Your
record is what the owner reads beside the regenerated candidate; overclaiming green is the
failure that caused the original incident — be the person who would have caught it.

## What you audit

The retired tree: sysml-codegen `item7-rebuild` at `48bf1b0 (product content measured at c0ceb24; evidence commits on top)` at
`/home/reid/1cfe/sysml-codegen-item7-rebuild`, paired with agentic-mbse `item7-rebuild` at
`3fbda2f` at `/home/reid/1cfe/agentic-mbse-item7-rebuild`; TEAx pinned `fa0e06a9`.
Available to you:

- The plan (`.project/active/cutover-recovery/plan.md`) — every ruling inline, including the
  REVISE stage notes (steps 1–7a) and the owner disposition
  (`owner-disposition-20260811.md`).
- The prior certification audit (`audit.md` + `product-lens.md`, verdict Needs Work) — your
  primary worklist: every finding it raised must now be CLOSED by citation, EXECUTED, or
  PROPERLY PARKED as a recorded owner question. Re-fire anything that is none of the three.
- The three-run gate table from step 7a (`evidence/phase5-runs/`, the revise-runs artifacts).
- The full commit series `item7-rebuild` (both repos) since `800ec84` / `cc6c7a7`; the
  deletion ledger + checkers; the earlier audit records and their not-verified lists.
- The forensic branches and Item 6 bases, read-only, for diffing.

Environment: venv `/home/reid/1cfe/item7-rebuild-venv` ONLY (assert the three import paths
first); license via `/home/reid/1cfe/agentic-mbse/.env`; NEVER touch the two original repos.
Write only `.project/active/cutover-recovery/evidence/audit-7-retired.md`; no commits.

If execution is unavailable in your session, do the full static audit and close your record
with a **"Requested live probes"** section — exact command or file/line mutation + expected
observation — and mark the affected verdict lines "pending probe"; the orchestrator executes
them and appends the addendum. Do not skip a claim because you could not run it.

## Method

1. **Close the loop on `audit.md`.** For each of its findings (audit-F1..F4, SC1–SC13, the
   design deviations D1–D3/R2/invariants 34–35, every code-integrity item): verify the
   recorded resolution against the code, or verify the parking is a recorded owner question
   with dependent conclusions parked. The five product-drift smells: re-evaluate each on the
   retired tree.
2. **The retirement's completeness:** hunt an escape hatch — any legacy authority, v5
   loader, dual-run, shim, or wrong-oracle test that survived; any `retire`-marked row whose
   file lives; any deleted subject whose matrix/ledger record still claims PASS. The grep
   evidence in the step-6 note is a starting point, not the proof.
3. **The REVISE rulings' faithfulness:** sample the orchestrator's delegated rulings (step-2
   Q1–Q5, the 6b/6d dispositions) against capture-fidelity — did any ruling exceed delegated
   authority or silently resolve an owner-grade question? R8 and audit-F4 must be untouched
   and parked; verify.
4. **Anchors and mutation matrix:** re-derive the C25/C2 LCOE anchors and consumer sets from
   the SysML by hand; verify the six-cell matrix and the R10 refusal pin exist and assert
   what the notes claim.
5. **The new mechanisms:** the REQ-DIAG re-homing (typed halt, both routes), the typed
   `AutoImplContext`, unit-annotation single-owner — read the code, check the pins.
6. **The matrix re-citation honesty:** sample ≥15 re-cited rows (does the heir actually
   prove the requirement text?), all 9 UNTESTED rows, and the RETIRED banners.
7. **Commit series** since `800ec84`: subjects vs contents; any commit claiming more than
   its diff.

## Verdict

CERTIFY (restating the accepted-residual list and the parked owner questions) / FINDINGS
(numbered, severity, evidence, resolution) / BLOCK. State what you did not verify. Close
with a one-page owner summary in plain working voice.
`ARTIFACT: .project/active/cutover-recovery/evidence/audit-7-retired.md`
