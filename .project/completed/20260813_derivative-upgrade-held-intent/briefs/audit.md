# Orchestrator brief — audit stage, CONSTRAINT-SEMANTICS Item 9

Fresh-session audit of Item 9 (derivative upgrade under held intent), item home
`.project/active/derivative-upgrade-held-intent/` (spec, design rev 2, design-review, plan,
verification.md + orchestrator rider). Implementation commits C1–C5 = `28942ec`, `185dec7`,
`da034ac`, `52c6381`, `2633834`; post-C5 orchestrator cure `4155b4d` (Item 8 archive-path test
fix, F5 family — verify it separately, it is not Item 9 scope).

## What the item claims

Executes already-ruled held intent on `tests/fixtures/catf_mfe_gated`
(`.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` rows
A5/A6/A9 — no re-disposition authorized): A5/A6 deleted with 27 in-place derivations on the
ruled basis; A9 asserted via dimension-specific `ProductWithinBand` at 1% relative;
`blocked-by-defect` retired on the live PROVENANCE only (archive frozen — spec ruling); identity
restated 65 = 56 carriers + 9 named deletions and machine-proved by the extended per-occurrence
prover; SC-3 recorded as a not-fired conditional on BOTH sides (PROVENANCE §3b + BACKLOG
one-liner on `[INLINE-PREDICATE-MARKER-DROP]`); expectations committed at C2 BEFORE any
confirmation run (SC-6).

## Audit expectations

- Verify against the spec's success criteria and the epic's Item 9 criteria; probe, don't trust:
  re-run the prover (`scripts/check_gated_manifest.py --check`), the focused tests, and the full
  licensed suite (`/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, license via
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero license-skip lines required;
  expected 2070 passed post-cure, plus the known pre-existing collection-order failure
  `test_the_lane_runs_the_real_simkit` on all-marker runs only).
- **SC-6 provenance check**: confirm by commit order that no expectation value in C2 was
  reverse-engineered (C2 `185dec7` precedes the first confirmation run in C3 `da034ac`), and
  that the values derive from the ruled table/source (spot-derive at least the histogram
  `{eligible 3, excluded 0, non_reaching 53}`, the 56/9 split, and the 26-leave/16-arrive key
  sets).
- **Byte-untouched checks** (tree-hash or diff): `tests/fixtures/catf_mfe_model/`,
  `tests/fixtures/catf_mfe_d5/`, `.project/completed/20260813_catf-constraint-policy-acceptance/`.
  Note: measure against the pre-Item-9 parent (`8942420`-adjacent), not `main...HEAD` — the
  twins were created on this branch (verification.md records both readings).
- **Falsification**: exercise the prover's occurrence-scoped failure modes (doc stripped,
  initializer gone, anchor-block missing/duplicate) on a scratch copy — each must be a reported
  problem, not a skip or a sibling-satisfied pass.
- **Ruled-cell fidelity**: no re-disposition anywhere; the D3 `tf_coil.thickness` edit and the
  A9 def-shape NOTE match their recorded ratifications; the archived owner-disposition and the
  three frozen surfaces untouched.
- ruff (baseline 12) / mypy (baseline 52) zero-new; `git diff --check` clean.

Environment notes: NOT `uv run` (wrong worktree resolution). BACKLOG.md and CURRENT_WORK.md may
receive concurrent edits from other agents — read, don't write them.

Deliver `audit.md` in the item folder with verdict (Certify / Certify-with-residuals / Needs
work), findings, and probe evidence. Do not fix anything; do not commit — the orchestrator
routes cures.
