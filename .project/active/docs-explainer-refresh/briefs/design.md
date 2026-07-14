# Brief: design — docs-explainer-refresh

Produce `design.md` for the spec at `.project/active/docs-explainer-refresh/spec.md`
(revised post-review 2026-07-13; review + resolutions in `spec-review.md` alongside).

## Intent (why this item exists)

The CONSTRAINT-EXEC epic changed what the system is; the docs tell two contradicting stories
depending on which file a reader opens. This item makes every touched teaching surface tell
ONE story — current HEAD — and turns `EXPLAINER_PROMPT.md` into a truthful, buildable v2
brief another agent can execute without reading the epic archives. Hold that bar: each edit
should serve a reader's single-story experience, not just discharge a survey line.

## Evidence and ground truth

- Primary evidence: `staleness-survey.md` (same folder) — spec-time, verified at HEAD twice
  (spec time + orchestration spot-check incl. the cross-repo claims). Trust it; do not
  re-survey. File:line cites for every stale claim are in it and in the spec.
- Code is truth: `SNAPSHOT_FORMAT_VERSION = 3`, five-value `ModuleKind`
  (`resolution/models.py:161-170`), contracts in `src/sysml_codegen/contracts/`, `seal` CLI,
  teax `entry_models` (`packages/teax-simkit/simkit/evaluation/evaluator.py:107`).

## Repo layout (confirmed at Align, [OWNER])

Four repos: sysml-codegen (home), agentic-mbse `/home/reid/1cfe/agentic-mbse`, teax
`/home/reid/1cfe/teax` (both on `constraint-exec-epic`, open PRs #11 / #3 — work lands as
appended commits), fusion-tea `/home/reid/1cfe/fusion-tea` (local `main`). Note for your
design: this session may be sandboxed to sysml-codegen — if so, design the cross-repo edits
from the survey's cites (they are verified) and say so; do not guess beyond them.

## The four calls delegated to YOU (decide and record; no reserved gates)

1. Verification-matrix shape for contracts/sealing: new family (e.g. REQ-CON-*) vs extending
   an existing one; which existing tests anchor the rows (look in `tests/` for contracts/seal
   tests to anchor against).
2. Home/numbering of the contracts reference doc: new `29-contracts-and-sealing.md` vs
   absorbing into `28-constraint-lowering-and-catalog.md`.
3. Depth of agentic-mbse's durable ConstraintFacts/ExpressionIR docs: full architecture doc
   vs a pointer page into archived `.project/` design artifacts (the constraint: it must
   survive `.project/` archival).
4. Gen-1 `new_pipeline_explainer.html`: in-file deprecation banner vs BACKLOG-mention only.

Also design's call: how the matrix rows citing retired symbols (REQ-AST-06, REQ-CA-02) get
fixed — reworded in place vs re-anchored/renamed.

## Settled items — do not relitigate

- [OWNER] The explainer deliverable is the refreshed `EXPLAINER_PROMPT.md` brief ONLY; the
  v2 HTML build is a separate follow-on item (register it in BACKLOG, pointing at the brief).
- [OWNER] fusion-tea `pipeline-walkthrough.html`: pointer/retirement note only.
- [ORCHESTRATOR, ratified path] fusion-tea `ToyPlantParams` alias: DROP (three sites +
  one stale comment; cites in spec SC-7). The item's only code change.
- Targeted sweep, not a docs scrub (spec Non-Goals).

## Inherited history the design must keep straight (now a success criterion)

- `lower_constraints_enabled` is landed history (default-on, GRANDFATHERED empty) — never a
  live drop path.
- `collect_constraint_manifest` survives deliberately (a kept migration-mapping test needs
  it); only the report/render/serialize surface was retired.
- CE-F1 (standalone catalog emission) / CE-F2 (multi-channel CandidateBridge) are open
  follow-ons — document current embedded-catalog / single-channel-bridge reality.

## Prior art for the explainer brief

`.project/active/EXPLAINER_PROMPT.md` (Gen-2 brief, stale), Gen-1 artifacts under
`.project/active/new-pipeline-explainer/`, survey §"Explainer prior art" (incl. the ~70-80%
machinery-reuse estimate and the eight-area slot map). What Item 14 already flipped is listed
in survey §sysml-codegen — do not redo it.

End with ARTIFACT: path to design.md.
