# Stage brief: design — CONSTRAINT-SEMANTICS Item 3 (Coverage Report and TEAx Policy)

Work in `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`). TEAx is at
`/home/reid/1cfe/teax` (clean `main` at pinned `fa0e06a`) — you have read access this stage;
design against what the code actually says, not the spec's second-hand citations (it flags
them). Do not modify TEAx in this stage.

**Deliverable:** `.project/active/constraint-coverage-policy/design.md`

**Primary input — the reviewed spec:**
`.project/active/constraint-coverage-policy/spec.md` (verdict Revise → all nine findings
resolved; resolutions in `spec-review.md`). It carries requirements, provenance, non-goals, and
the open questions deferred to you. Behind it: the lifecycle contract's "Headline states and
coverage truth" subsection and invariants 32/33/41/46/46a/48/49/50; Item 2's design (the
Item 3-citable disposition/vocabulary section) — consume, don't re-derive.

## First: verify the TEAx premises

Before designing, read and record the actual state of: `evaluation/projection.py`
(`CANONICAL_HEADLINE`, normalization seam), `study/policy.py` (dispatch + defaults),
`ACCEPTED_CATALOG_SCHEMA_VERSIONS` (where it lives, current contents), and the durable
case-record layer (store schema, whether invariant 50's additive-or-versioned route is
available). Correct any stale line numbers in a Research Findings section. If a premise the
spec rests on is wrong, surface it and park dependent conclusions.

## The decisions you own

1. **Token spellings, both vocabularies** — the partial-coverage report token (umbrella left
   `satisfied_partial` vs `partially_satisfied` open) and its canonical TEAx runtime
   counterpart; the full report-token ↔ canonical-token map; fail-closed handling of unknown
   tokens on both sides. Publish in a section Items 5/6 can cite.
2. **Report coverage block** — field names/shapes; the NEW usage-tier assessed-count name (two
   `assessed_count`s must not exist); reason histogram shape; catalog-fingerprint join.
3. **Derivation direction mechanics** — where report coverage is computed from the catalog at
   generation time and what makes divergence a generation/verification failure (spec-F5).
4. **The all-inapplicable precedence crossing** — every asserted gate dispositioned
   inapplicable: full satisfaction vs not assessed. Publish as a RULING with reasoning (the
   spec's surfaced item requires this be a ruling, not a coin flip).
5. **Zero-input aggregator** — generated shape for constraint-bearing models with no applicable
   asserted gate (LC-E10 wording governs, not the epic's looser scope-4); interplay with Item
   2's `ships_constraint_machinery` (this item's deliberate supersession — design the seam
   change, cite the A4 cure).
6. **Headline precedence implementation** — violation > indeterminate > full satisfaction >
   partial coverage > not assessed, over the two-axes model (headline = summary token; coverage
   account always present, always in case records).
7. **TEAx policy + config** — partial → keep-for-boundary default; feed-strategy per-study
   opt-in as a visible auditable config line; where coverage lands in durable case records;
   invariant-50 route (additive or versioned; if neither is possible, that surfaces as an
   owner-visible decision, not a design call).
8. **Schema migration + cross-repo landing order** — generated schemas, package contracts,
   `ACCEPTED_CATALOG_SCHEMA_VERSIONS` += `3.0.0` (the Item 2 hand-off), pins; ordered list with
   what breaks if violated; TEAx is never bumped first; all TEAx work on a branch off `fa0e06a`.

## Quality bar and constraints

- One authority: coverage facts come from the catalog; nothing recomputes per-usage detail
  outside it. No shims; deletion over compatibility layers.
- The four `all_satisfied` assertions in `tests/execution/` move with the vocabulary change —
  the fourth (`test_fusion_tea_real_teax.py:244-259`) needs its expected coverage block
  hand-written BEFORE confirmation tests run (owner sequencing).
- Test design: the six-state matrix pinned independently in both vocabularies; the
  violation+non-full-coverage case; unknown-token fail-closed on both sides; zero-input
  aggregator both branches; cross-repo compatibility tests and their pin/landing order;
  three-route parity where report bytes are involved.
- Provenance discipline; your decisions are agent-grade by construction.
- Run the product-lens pass at the end (reconstructed method per this epic's convention — see
  the item's `product-lens.md` spec-stage entry and Item 2's ledger for format); append the
  design-stage entry with provenance flagged.

## Environment notes

Codegen gates: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (never `uv run`).
License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero license-skip proof.
TEAx suite: run from `/home/reid/1cfe/teax` (check its pyproject for the runner; do not modify
the tree this stage).

Finish with `ARTIFACT: <path>` as the last line of your final message.
