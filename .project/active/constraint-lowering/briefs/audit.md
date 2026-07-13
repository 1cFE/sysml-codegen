# Brief: Item 5 audit — Concrete Lowering

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/constraint-lowering/`.
- Attempt execution first; if blocked, write "Requested live probes". Never run the snapshot-capture script.

## Audit target
All Item 5 commits (Phases 1–5, including the orchestrator-completed Phase 4: profile-gated lowering behind `lower_constraints_enabled=False`, commits `a1fe7a4`, `0d6eba1`, and the session's `dd181ae` tail) against `spec.md` (review-revised), `design.md` (rev 2, probe-settled), `plan.md` (+ extensive Phase 4/5 notes), and `b1-probe-evidence.md`.

## History you must weigh (this item had real turbulence)
1. The wiring was reverted once, redone behind a transitional flag (default-off until Item 8 restores snapshot parity — 22 measured live/snapshot divergences with it on). Verify the flag semantics: default path byte-identical; enabled path fully functional (the wired-path test).
2. The strict ladder was WIDENED mid-implement beyond design rev 2: `scoped_alias_lookup` + an occurrence-scoped design-attribute match against materializer-synthesized QNs, driven by hif_plant's profile-ADMIT `driver.efficiency`. Adjudicate this as a design amendment: is it recorded properly (not silent), does it preserve the fallback-unreachable [HARD] (the new rungs must not reintroduce EP-key synthesis — the F4 lesson), and does the mini byte-identity evidence cover the widened ladder?
3. A circular-import fix and the Item 8 handoff (hif_plant `gain` hierarchy-extraction gap) — verify both are recorded and the latter genuinely out of scope.

## What to verify by execution
1. The six spec success-criteria tests: run them (S4-reproduction control-prune/retained; strict-resolution probe naming the actual with no synthesized EP; ID determinism across two fresh loads; corpus byte-identity; multi-instance recorded-shared-binding per the B1 adjudication; inline-form).
2. Mutation probe on the fallback-unreachable guard: make the strict resolver's terminal switch fall through to the backtracker fallback → a test must go RED; revert.
3. Full suite, mypy 76 baseline, ruff. Corpus regenerate → empty diff (flag off).
4. The unassessed/blocked paths: a blocked assert halts with reason-grade diagnostics through the WIRED path (not just lower_constraints directly).
5. Spec success-criteria walk with evidence per item; flag silent scope cuts.

Verdict: Certify / Certify-with-notes / Fail.
