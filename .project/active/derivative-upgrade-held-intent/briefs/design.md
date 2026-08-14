# Orchestrator brief — design stage, CONSTRAINT-SEMANTICS Item 9

## Input

Spec: `.project/active/derivative-upgrade-held-intent/spec.md` (committed at `0596f5c`; its
product-lens ledger sits beside it). The spec is the contract; the held-intent rows it cites
(`.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` rows
A5/A6/A9) are the owner payload — no re-disposition, no tolerance invention.

## What design must settle (the spec's deferred questions)

1. **The 27 derivation edits' concrete shape** in `tests/fixtures/catf_mfe_gated/`
   `radial_build.sysml`: which attribute declarations change, in what order, and how each
   derivation carries its documentation. The per-derivation doc obligation is owner-ruled; only
   its *shape* is yours (per-layer one-liner + one block statement is a candidate). The manifest
   prover reads a `//` block within 12 lines above the initializer
   (`scripts/check_gated_manifest.py:119-124`) — design against what the prover will actually
   accept after your extension (next point).
2. **The per-occurrence `DERIVATIONS` prover extension**: A6 produces 14 byte-identical
   `inner_radius + thickness` initializers, and `check_gated_manifest.py:219-227` currently
   refuses non-unique initializers. Design the anchoring (owning `part` block, line range, or
   scoped search). Both existing failure modes (documentation stripped, initializer gone) must
   fail closed for every A5/A6 derivation, per occurrence.
3. **A9's exact authored form**: `assert constraint pumping_speed_agrees : ProductWithinBand`
   relative form, 1% (`rel_tol` dimensionless). If `ProductWithinBand`'s def-shape must change
   materially from the disposition row's sketch, NOTE it in the design (owner-disposition row A9
   requires this) — do not silently adapt.
4. **Unit spelling on derived attributes** (`[m]` on the attribute vs trailing comment) — decide
   from the fixture's dominant idiom and what Item 8 changed about port unit text; record which.
5. **Expected-output derivation plan** (SC-6 discipline): enumerate exactly which expectation
   files/tables get re-derived from the ruled table BEFORE confirmation tests, and what each new
   value is derived from. The spec already fixes the headline numbers (56 carriers, 9 deletions,
   histogram `{eligible 3, excluded 0, non_reaching 53}`, coverage `56/3/3/0/0/{}/complete`,
   `assessed_entry_count = 3`); module count is measured, not pre-committed.

## De-risk instruction (epic lesson, binding)

The epic's Lessons Learned records: **a probe that gates a landing must run generation, not only
elaboration** — Item 5's Phase 1 elaborated after every edit and still hit two generation
preflights late (`constraint_name_safety` refused `value` as a formal name;
`generated_binding_overlap`). Your design must include (or itself run) a cheap probe that authors
A9's assert form plus at least one representative A5/A6 derivation on a scratch copy and drives
**full generation** through the public route, checking the preflights pass and the minted ports
carry the authored unit text. Watch for reserved generated locals in `ProductWithinBand`'s
formals (the `value` trap). Record the probe result in the design. Item 8's freeze
(`62a07e5c870158672eb100f1cba73adfe4c9df28`) is what makes these forms buildable — if any ruled
form still refuses, that is a premise surprise: STOP, record it, and return to the orchestrator
instead of adapting the ruled form.

## Constraints

- Frozen twins (`catf_mfe_model`, `catf_mfe_d5`) and the archived
  `20260813_catf-constraint-policy-acceptance/` byte-untouched (spec's freeze-the-archive ruling).
- Retirement of `blocked-by-defect` happens on the live surface only:
  `tests/fixtures/catf_mfe_gated/PROVENANCE.md` §3a and its disposition row.
- SC-3 two-sided conditional: the one-line `[INLINE-PREDICATE-MARKER-DROP]` BACKLOG edit is in
  scope (BACKLOG.md is now clean of foreign edits); design says where in the sequence it lands.
- No TEAx change, no schema change, no new dispositions, nothing pushed, no `main`.

## Environment

- Interpreter: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (NOT `uv run` — wrong
  worktree resolution for this pair).
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; a licensed proof requires
  zero license-skip lines.
- Scratch space for probes: use the item folder's `probes/` subdir for kept findings; throwaway
  runs under `/tmp/claude-1000/...` scratch are fine but record results in the design.

## Deliverable

`design.md` in the item folder: decisions with reasoning, the probe result, file-level change
list, and the expected-output derivation plan. A fresh-session design_review follows; write for
that reviewer. Do not commit — the orchestrator commits.
