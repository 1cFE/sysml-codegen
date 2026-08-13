# Stage brief: plan — CONSTRAINT-SEMANTICS Item 3 (Coverage Report and TEAx Policy)

Work in `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`). TEAx at
`/home/reid/1cfe/teax` — read-only this stage; the implement stage will branch it off `fa0e06a`.

**Deliverable:** `.project/active/constraint-coverage-policy/plan.md` — phased, checkboxed,
resumable mid-way.

**Inputs, in authority order:**
1. `.project/active/constraint-coverage-policy/design.md` (rev 2, commit `dc397e7` — all 13
   review findings resolved; carries the bucket table, token map, D4/D9 rulings, both-repo
   landing order with the forced checkout inversion, and the validation list)
2. `.project/active/constraint-coverage-policy/spec.md` (success criteria, provenance,
   sequencing `[NEED]`s)
3. `design-review.md` resolution notes.

## Planning requirements

- **Sequencing (owner-directed):** documentation corrections and ALL hand-written expected
  outputs land before confirmation tests run. That includes: the four `all_satisfied` sites in
  `tests/execution/` (the fourth, `test_fusion_tea_real_teax.py:244-259`, needs its expected
  coverage block hand-written from the fixture's SysML source), and the per-fixture expected
  coverage accounts (design DR-6 instruction: hand-written from source, never transcribed from
  a catalog dump).
- **Landing order (design D8):** respect the published cross-repo order AND the forced local
  checkout inversion — the codegen execution lane imports simkit from the TEAx working tree, so
  the TEAx branch must exist locally before codegen's execution lane can go green, while
  publication order stays codegen-first. Phase the TEAx branch creation explicitly (branch off
  `fa0e06a`; never commit to TEAx main). State the expected red window and its gate, as Item 2's
  plan did for the PD4 pin window.
- Kept failing characterization first: the report-can-lie shape (partial assessment reading
  `all_satisfied`) and the excluded-only no-report shape, pinned before the vocabulary moves.
- Each phase: checkboxes at task grain, its pinning tests, its gate. Phases must keep both
  suites' states explicit (codegen licensed suite; TEAx suite from /home/reid/1cfe/teax).
- Final gates from the spec: codegen full licensed suite (zero license-skip proof), TEAx full
  suite, cross-repo compatibility tests, ruff/mypy zero-new in both repos, generated-artifact
  review, `git diff --check`, exact counts in `verification.md`. Companion (agentic-mbse) is
  expected untouched — state it as a check, not an assumption.
- State what does NOT change: Item 2's usage-tier schema (no new fields), the frozen twins,
  `instance-graph/v3`, catalog `3.0.0` (this item adds no catalog schema bump — verify the
  design's claim and plan accordingly), generated baselines outside the vocabulary change.
- Scale honestly against the epic's ~2 days (execute+validate ~11h); say so if the phasing
  implies more.

## Environment notes

- Codegen gates: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (never `uv run`).
  License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero-skip proof.
- TEAx suite: from `/home/reid/1cfe/teax` (its own runner per pyproject; the venv note in the
  design's D8 applies).
- Fixtures/baselines format-exempt.

Finish with `ARTIFACT: <path>` as the last line of your final message.
