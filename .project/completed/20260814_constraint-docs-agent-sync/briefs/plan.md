# Plan-stage brief — Item 7 (constraint-docs-agent-sync)

**From:** orchestrating session, 2026-08-14. Provenance: `[OWNER…]` = owner-grade, `[AGENT]` =
orchestrator inference/decision — don't upgrade my grades.

## The work item

Write `plan.md` in `.project/active/constraint-docs-agent-sync/` for Item 7. The **spec is the
contract**: `.project/active/constraint-docs-agent-sync/spec.md` — read it in full, including its
Open Questions resolved-by-amendment pointers and the product-lens ledger beside it. Also read
`owner-checkpoint-20260813.md` (same folder) — verbatim payload rules apply.

## Orchestrator decision you execute (record it, don't re-open it)

**[AGENT, orchestrator 2026-08-14]** No separate design stage runs for this item — it is
documentation-only and the spec already carries the requirements. Your plan therefore includes a
short **Design decisions** section making and recording the four calls the spec defers to design,
each with a one-paragraph rationale:

1. **Exact ADR/product home shape.** Default of record: first `.project/product/INDEX.md` ledger
   entry + a per-repo ADR convention. Decide the concrete layout, id-minting rule, and whether
   ADR-009 back-registers. Look at how `modeling-assumptions.md` sections and the epic's citation
   habits work before choosing.
2. **Sweep-record home and format.** One row per raw hit (spec requirement, from lens item7-F1).
3. **Matrix row granularity.** Read `docs/architecture/verification-matrix.md` against the recount
   baseline (276 rows / 275 PASS / 32 families, BACKLOG:464-466) and decide per-gate vs per-family.
4. **TEAx sweep scope boundary.** The sweep record must state a defined TEAx scope.

## Sequencing constraints (handoff-carried, verified against Item 1's records)

- **Inventory before edits:** run the S1–S5 sweep inventory FIRST (S4 must run pre-edit — the
  spec records the pre-resolved S4 collision), then edit.
- **Amendments before rewrites that cite them:** the item3-F2 contract amendment and the
  design-F2 Appendix C cell fix land before the cross-repo doc rewrites that cite the amended
  clauses. Item 1's five-term method (`.project/completed/20260813_constraint-semantics-contract-amendments/design.md:1202-1218`)
  is the referent.
- Promise filing + lens-trail citation (spec's item7-F2 requirement) is its own phase; the
  ledger home must exist before the trail cites it.
- Last phase: verification — doc checks, `git diff --check` in every touched repo, and a pytest
  collect sanity check in codegen (archival/path breakage is a known failure mode at close).

## Facts for your phases (verified by orchestrator)

- Repos: codegen = this checkout (branch `item7-rebuild`); agentic-mbse =
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch `item7-rebuild`, clean); TEAx =
  `/home/reid/1cfe/teax` (branch `constraint-semantics-item3`, clean — ALL TEAx edits stay on
  this branch, never `main`, nothing is ever pushed).
- You have bypassPermissions this run **specifically so you can re-grep agentic-mbse and TEAx**
  — the spec flags its cross-repo facts as carried-not-verified. Verify them (the named stale
  sites, the absence claims) and let real hit lists shape the phases. Do not edit anything
  outside `.project/` in any repo at plan stage.
- Elaboration-check execution terms are in the spec (item7-F3): license via
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, interpreter
  `/home/reid/1cfe/item7-rebuild-venv/bin/python`, never `uv run`; zero
  `no live syside license` skip lines is the only proof of a licensed run. Plan the implement
  phase to use exactly these.

## Plan shape

Phases with checkboxes (multi-session-safe per workflow-accountability), each phase with: goal,
files, verification step. Keep it lean — this is a 0.5–1 day item; the plan should be executable
by one implement session with resumes. End with `ARTIFACT: <path>`.
