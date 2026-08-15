# Stage brief — Phase 3, Slice 3D: Fusion Tea customer vertical and real TEAx

**You are executing exactly one slice** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: Non-Negotiable Execution Rules, Slice 3D, per-slice validation, the Phase 2 C25/C2
protocol decision recorded in the plan, completion notes for 3A–3C, and `evidence/audit-3{a,b,c}.md`.
This is the slice the original Item 7 never reached: REAL TEAx execution as accepted evidence.

## Intent

Prove the customer model end-to-end on the exact route through public APIs only:
load/extract → generate → verify → seal → registry discovery → execute in real TEAx — on live
AND relocated-v6 packages — pinned to hand arithmetic. The independent forensic diagnostics
(11 outputs, live/relocated equality, LCOE `270.1211779380445`) are targets to RE-PROVE, not
accepted authority.

## State you inherit

- Paired heads: codegen `26e7d04`, agentic `cc6c7a7`, both clean on `item7-rebuild`. Suites:
  codegen 3538/47/18 licensed; agentic 1825/1/5.
- Venv `/home/reid/1cfe/item7-rebuild-venv` has codegen+agentic (rebuild worktrees) AND
  teax-simkit from the pinned `/home/reid/1cfe/teax` (`fa0e06a9`). Re-assert all three import
  paths first (F2 trap). For old-commit comparisons force PYTHONPATH + assert `__file__`
  (3C audit process note). License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`;
  proof = zero `no live syside license` lines.
- Parts bin: forensic `07531e64` (codegen). Forensic Phase 6 renamed the 15 Fusion Tea
  self-bindings; Phase 8 wrote the harness. The failed harness's three defects are documented in
  the plan and forensics — do not reproduce them.

## The plan's hard content for this slice (all mandatory)

1. **Real TEAx test FIRST.** Public APIs only: no monkeypatch, no private runner. The plan
   REJECTS `tests/execution/test_fusion_tea_item7_{budget,real_teax}.py` as written (they assert
   `is True` on a script's self-report); replacements must assert real outputs (module set,
   channel values, LCOE) and must RUN in the acceptance command rather than being silently
   deselected — if the `execution` marker keeps them out of the default suite, the acceptance
   command you record in the plan must include them explicitly, and they must not be skippable
   silently (no bare `skipif` that can go green without executing).
2. **Known trap:** the in-repo runner's `inputs={...}` path rides a fake SimKit stub
   (`pipeline_runner.py:_install_simkit_stub`) — it must NOT appear in any real-TEAx evidence
   path. Real execution goes through `simkit.core.registry_builder.create_registry` +
   `simkit.core.pipeline.execute_pipeline` from the installed teax-simkit.
3. **Pin hand arithmetic and owner-relevant behavior:** LCOE `270.1211779380445` (rel 1e-6,
   preserving `tests/runtime/test_fusion_tea_acceptance.py` as the migrated oracle); C25
   availability and C2 thermal-efficiency mutations with their EXACT every-and-only consumer
   sets (forensic diagnostic values to re-prove: availability 0.91 → LCOE 269.5300723203276,
   Meier COE moves, nothing else; thermal 0.44 → LCOE 263.85170462810606, recirculating fraction
   moves, nothing else); C19's 80.0 on BOTH consumer paths.
4. **Mutation protocol:** the Phase 2 decision — runtime typed-entry injection via
   `PreparedEvaluator.evaluate` / `CandidateBridge.build`. Never edit bytes after sealing; never
   reseal edited packages (`check_reseal_provenance` refuses it anyway — that refusal is part of
   what you prove).
5. **Fusion Tea model renames:** review each of the forensic Phase-6 renames against the exact
   fifteen-item ledger in the Item 7 shaping artifacts (`.project/active/elaborator-cutover/`,
   restored as evidence). Preserve equations, defaults, topology, physics — the diff per rename
   must be exactly the binding-name change the ledger authorizes. Any extra hunk: Reject that
   hunk. Recall the Item 3 spike: `in gain = gain` → hard SI_SELF_BINDING on the exact route,
   which is WHY the renames are needed for the exact route to accept the model.
6. **Full 37-path comparison** while both implementations remain available. Drivers must
   classify readiness `ElaborationError.findings` AND validation
   `ElaborationDiagnosticError.diagnostics` separately, asserting exact diagnostic multisets.
   Expected outcomes: the Phase 2 ledger as amended by the B37-01 ruling (the exact route now
   produces 14 public graphs / 23 typed errors — measured in the 3A follow-up).
7. **Real TEAx on live and relocated v6 packages.** Record environment (interpreter, resolved
   import paths, teax HEAD) in the evidence. Relocated = generate from a v6 snapshot in a
   different directory with the model tree absent.

## Requirements

- Declare path sets per repo BEFORE editing (agentic likely unchanged; say so if so). Model
  fixture changes (fusion_tea renames) are part of the declared set.
- No deletions. Both suites keep every test; explain deltas exactly.
- The B37-restored literal-bearing aggregation oracle obligation (Phase 2 ruling) — if not
  already discharged by the 3B aggregation package tests, discharge it here and say which test
  owns it now.
- Gates: slice tests red→green; both full suites; execution lane INCLUDING the new real-TEAx
  tests (state the exact command); ruff/mypy per repo unchanged; `git diff --check`; declared
  sets; commit + OID record, plan 3D row updated (agentic `N/A if unchanged`).

## Hard rules

Unchanged. Rule-10 stops: any corpus outcome differing from the amended ledger, any hand-value
mismatch, any mutation touching a consumer outside the exact expected set, any rename needing
more than the ledger authorizes.

## Report back

What the slice proves; the real-TEAx evidence (outputs count, LCOE, mutation results, live vs
relocated equality) with the exact commands; rename review outcomes (15 rows); corpus 37-path
result vs amended ledger; gates; commit OIDs. `ARTIFACT:` the updated plan.
