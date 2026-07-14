# Brief: Item 8 audit — Snapshot v3

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/snapshot-v3/`.
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...`. Never run capture scripts yourself except where a probe explicitly requires regeneration into a temp dir.

## Audit target
The five Item 8 phase commits (`1a5c591..df5ed97`) against `spec.md`, `design.md` (rev 2), `plan.md` (+ deviation notes).

## What to verify by execution
1. **The rejection matrix**: run the 8-cell gate tests; mutation probe one cell (delete the mode-enum validation → the unknown-mode test goes RED; revert). Both epic rejection cases (old version; missing section) fire with re-capture messages.
2. **Live/snapshot artifact parity**: run the parity tests for the three clean constraint-bearing fixtures; verify they compare ARTIFACTS (bytes), not just catalogs.
3. **The default flip + grandfather**: lowering on by default (verify the signature/default); plant_values + fusion_tea captured flag-off with the loud marker (read their snapshots' constraint_lowering_mode); their baselines byte-identical to pre-Item-8 (git diff the baseline files across the item).
4. **The corpus re-capture**: per-fixture expected-diff conformance — spot-check three fixtures' diffs against the design's enumerated classes (constraint-bearing: facts+occurrences+lowered structure; constraint-free: facts section present-empty per the design's D5). The d38_caret out-of-band diff: verify the root-cause note (pre-existing drift) by checking it reproduces on the parent commit.
5. **The 5+5 test fixups**: each must be a legitimate re-anchor (new expected behavior), not a weakened assertion — read each diff.
6. **Gates**: full suite (license env), mypy 76, ruff.
7. **Spec success-criteria walk** with evidence; flag silent scope cuts. Note for SC-4 handoff: Item 9's fingerprint-stability canary depends on this item — state whether its preconditions now hold.

Verdict: Certify / Certify-with-notes / Fail.
