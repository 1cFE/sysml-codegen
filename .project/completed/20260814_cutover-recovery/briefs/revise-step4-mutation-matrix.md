# Stage brief — REVISE step 4: off-default mutation tests on all three routes

**You are executing owner step 3 of the REVISE path** (local execution order: step 4) on the
Item 7 cutover recovery.
Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: `owner-disposition-20260811.md` (step 3), spec authority
`.project/active/elaborator-cutover/spec.md:61`, `audit.md` SC2/SC6/SC7 and product-lens
audit-F3, `tests/execution/test_fusion_tea_mutation_teax.py` (currently live-generation
only), and the plan's C25/C2 mutation-protocol decision (TEAx typed-entry injection;
reseal-after-edit is refused by `check_reseal_provenance` and that refusal is part of the
proof).

Work synchronously. Never pause for background agents; finish the artifact this turn or stop
with questions as your entire final message.

## Intent

The owner ruled: add the missing off-default mutation tests on all three routes — live,
in-place-snapshot, relocated-snapshot — as KEPT vertical tests. The owner independently ran
relocated gain=100 successfully, so expect certification work, not product work. If a route
actually fails, that is a rule-10 surfacing, not a quiet fix.

## Worklist

1. **The mutation matrix.** Extend `tests/execution/test_fusion_tea_mutation_teax.py` so each
   mutation runs on each route — {live generation, generation from the in-place v6 snapshot,
   generation from a relocated v6 snapshot} × {C25, C2} — with the same exact assertions:
   - **C25**: availability 0.9→0.91 → LCOE `269.5300723203276`; consumer set = Meier COE
     only.
   - **C2**: thermal 0.43→0.44 → LCOE `263.85170462810606`; consumer set = f_recirc only.
   The anchors are owner-payload numbers — verbatim, no tolerance widening. The consumer-set
   assertions are exact: every and only the bound consumers move against the unmutated run.
   Mutations are TEAx typed-entry injections at runtime; sealed bytes are never edited.
   Relocation means a genuinely different checkout root (scratch copy beside the repos, not
   `/tmp`). Share machinery across routes; do not triplicate the harness.
2. **SC7 residue.** The named C19 fixture has internal structural/codec coverage and
   live+relocated Fusion-Tea execution at 80.0, but no kept public-v6 route test of its own.
   Add one: generate from its committed v6 snapshot through the public route and pin the
   behavior with an independently derived expectation.

## Ground rules

- Real-TEAx execution env: venv `/home/reid/1cfe/item7-rebuild-venv` (already wired to both
  rebuild worktrees + teax-simkit); pinned TEAx `/home/reid/1cfe/teax` @ `fa0e06a9`
  read-only. Execution suite runs from `packages/teax-simkit` conventions already used by
  `tests/execution/` — follow the existing lane's own harness.
- Do not modify the accepted v6 batch, the 37 corpus fixtures, or sealed snapshot bytes.
- The `check_reseal_provenance` refusal on an edited input stays pinned; if your work
  touches that area, the refusal test must remain.
- Rule 10 stands: a route that fails a mutation, or an anchor that does not reproduce, STOPS
  the stage for surfacing with the measured value — never adjust an anchor to match.

## Environment

- FIRST ACTION: assert resolved `__file__` for `sysml_codegen`, `agentic_mbse`, `simkit`.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero
  `no live syside license` lines is the only valid proof. Venv `bin` on PATH (tests shell
  out to bare `python`).
- Expected clean start (post step 3): codegen **3866 / 47 / 53** licensed; execution lane
  **53**; corpus `--check` 15/22/0; ruff src **16**; mypy **69 in 16**; ledger paths 304/0;
  surface 0; groups READY; runbook patches 4 passed.

## Battery before commit

Execution lane (state the command; delta = exactly the new nodes, named); full licensed
suite; corpus `--check`; ruff/mypy no-new; `git diff --check`; `check_ledger_4a.py` paths +
surface + groups; `test_runbook_patches.py`. Commit with the matrix in the message; update
the plan stage note and tick the spec's SC6/SC7-relevant boxes only if genuinely closed by
kept tests.

## Report back

The route×mutation matrix (six cells minimum) with per-cell pass evidence and LCOE values;
the C19 public-v6 node; battery numbers; commit OIDs. Any rule-10 surfacing.
`ARTIFACT:` the updated plan.
