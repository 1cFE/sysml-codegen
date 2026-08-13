# Orchestration brief — plan stage — CONSTRAINT-SEMANTICS Item 5

Write `plan.md` in `.project/active/catf-constraint-policy-acceptance/` for the implement stage.
The design is APPROVED at review round 2 (`design.md` rev 2 + review addendum, commit `1afd83e`).
Authorities: `spec.md` (SC-3 twice-amended — identity 65 = 58 + 7), `owner-disposition.md`
(RULED, incl. the D-S1/D-S2 ruling), `design.md` D1–D7 + the SURFACED/RULED record.

## Non-negotiable sequencing (the plan's skeleton)

1. **De-risk first (B2, widened at review):** re-run the composite probe with EVERY remaining
   edit — A1, A4, C37 derivations, the five `@inapplicable:` markers, the C21/C28 deletions —
   on top of the P7 set. P7 tested none of these. Reconcile the result explicitly against the
   **ruled 58-carrier / 2-gate target** (P7 showed 65 rows because it deleted nothing). Only
   after this reconciliation may any expectation file be written.
2. **Expected outputs before the fixture (SC-6):** population JSON, expected-coverage ledger
   row (`inapplicable_gate_count = 0` — verified bucketing), D2's expected identity, expected
   catalog disposition histogram, expected report/study outcomes — committed BEFORE the
   derivative generates or executes. Evidence: for new files `git log --diff-filter=A`; for
   EDITS to existing files (the ledger row!) cite the commit hash that introduced the hunk
   (review M3 residual — `--diff-filter=A` returns the wrong commit for edits).
3. **Author the derivative probe-first in the probe order that worked**, re-elaborating after
   each group. Atomic landing; a late BLOCK costs the whole pass.
4. **PROVENANCE with all record classes:** per-change records; 7 named deletion records (each
   derivation carrying the undirected relation + chosen-basis statement); the 3 parked-row
   records (D-S1/D-S2, Item 8, held intent — field spec in design.md); the 2 O3 model-debt
   entries; per-gate unit reasoning (D3); `renamed_from:` for the two renamed gates; d5's stale
   acceptance paragraph correction.
5. **SC-8 infrastructure (new, per D7 rev 2):** capture the v6 snapshot for
   `constraint_domain_satisfy_calc_def`, commit the two-file golden, add the regenerate-and-diff
   test, and run the deliberate falsification once (mutate → gate fails → revert) — record it.
6. **Acceptance (SC-5/SC-7):** generate/seal/execute/persist/query through TEAx
   (`constraint-semantics-item3` @ `5b70ae9`, checkout stays put); valid candidate satisfied,
   mutated `CATFMFEPhysics__catf_physics__p_fusion` reaches `reject` (physics-chain key ONLY —
   `tritium fusion_power` is an independent attribute, the choice is deliberate and recorded);
   durable case records carry coverage. Three routes gated: licensed live, in-place snapshot,
   relocated snapshot; exact counts + fingerprints into `verification.md`; snapshot recapture =
   timestamp-only-diff + revert discipline.

## Environment facts (repeat in the plan so implement inherits them)

- `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`; never `uv run`.
- Licensed: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero
  `no live syside license` skip lines is the only proof.
- Frozen twins byte-untouched except d5's PROVENANCE paragraph; `make_d5_variant.py --check`
  must still pass.
- Suite baselines to not regress: codegen 2050 passed / 34 skipped at Item 3 close; ruff 12,
  mypy 55; `git diff --check` clean.

Use checkboxes per phase with verification steps inline. Keep phases small enough that each
ends in a green, committable state. End with `ARTIFACT: <path>`.
