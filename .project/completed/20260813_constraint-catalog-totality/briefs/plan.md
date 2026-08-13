# Stage brief: plan — CONSTRAINT-SEMANTICS Item 2 (Canonical Usage Domain and Catalog Totality)

Work in `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`; companion worktree
`/home/reid/1cfe/agentic-mbse-item7-rebuild`).

**Deliverable:** `.project/active/constraint-catalog-totality/plan.md` — a phased, checkboxed
implementation plan an implementing agent can resume mid-way.

**Inputs, in authority order:**
1. `.project/active/constraint-catalog-totality/design.md` (rev 2 — all review and lens findings
   resolved; carries the eight decisions, the disposition precedence table, invariants, the
   five-step cross-repo landing order, and the test design)
2. `.project/active/constraint-catalog-totality/spec.md` (success criteria and provenance)
3. `.project/active/constraint-catalog-totality/design-review.md` (resolution notes — useful for
   what the design is committed to)

## Planning requirements

- Phase the work so the design's five-step cross-repo landing order is respected, and the
  recapture is the **last fixture-committing step** (lens design-F3 resolution). Documentation
  corrections and expected outputs land BEFORE confirmation tests run (owner-directed sequence in
  the spec) — sequence the doc/requirement-row edits and expected-population files accordingly.
- Each phase gets: checkboxes at task grain, the tests that pin it, and its verification gate
  (what must be green before the next phase starts).
- Include the kept failing characterization first (the epic's de-risking note: Item 2 starts from
  a reproduced failure — 65 authored usages → 9 carriers on catf_mfe_d5).
- Name the exact final gates from the spec: focused tests, full licensed codegen + companion
  suites (license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; verify zero
  license-skip lines), ruff zero-new, mypy zero-new, fixture diff review under the
  timestamp-churn protocol, `git diff --check`, exact counts recorded in `verification.md`.
- The plan must state what does NOT change: frozen twins' constraint syntax, catf_mfe_d5 still
  generates with exactly 65 carriers, generated baselines outside the recapture scope stay
  byte-identical, the four `all_satisfied` assertions in tests/execution/ untouched (Item 3's).
- TEAx re-vendor is a named handoff step in the landing order, not work this item performs —
  carry it as an explicit hand-off checkbox with what breaks while it's pending.
- Keep the plan honest about scale: this is a ~2-day item (design estimates execute+validate
  ~11h). If your phasing implies materially more, say so rather than compressing silently.

Finish with `ARTIFACT: <path>` as the last line of your final message.
