# Brief: plan — docs-explainer-refresh

Produce `plan.md` (phased, checkboxed) for the item at
`.project/active/docs-explainer-refresh/`. Read in order: `spec.md` (revised 2026-07-13),
`design.md` (revised post design_review; both reviews Approved-after-revision — resolutions
recorded in `spec-review.md` and the design's Design-Review Resolutions section),
`staleness-survey.md` (evidence; trust, do not re-survey).

Work synchronously; never pause for or spawn background agents.

## Constraints the phases must respect

- **Four repos, appended commits on live PR branches.** sysml-codegen (home),
  agentic-mbse `/home/reid/1cfe/agentic-mbse`, teax `/home/reid/1cfe/teax` (all three on
  `constraint-exec-epic` with open PRs — never rebase/force-push), fusion-tea
  `/home/reid/1cfe/fusion-tea` (local `main`). Pushing is the orchestrator's job at the end —
  plan phases must NOT push.
- **Serialize per repo; group each repo's edits into its own phase(s)** with explicit
  `git -C <repo>` commit steps and pathspec-limited commits (`git add <paths> && git commit
  -- <paths>`). One commit per coherent phase, subject leading with the decision.
- **Cross-repo edits: re-grep each survey cite before editing it** (cites verified 2026-07-13
  but line numbers can drift). If a cite doesn't match, stop and record rather than guess.
- **Implementer sandbox reality:** the implement session usually has execution in-repo but
  may lose it on resume; design phases so each is completable file-edit-first with a small
  verification tail the orchestrator can run if needed.
- **Verification gates are cheap here (docs item):** the greps named in the spec's success
  criteria (retired symbols zero-hit outside historical notes; explainer caveats gone;
  decision-table vocabulary gone), the matrix recount (from the Index, not the summary —
  design INV-4), and for the one code change (fusion-tea alias drop) a syntax check of the
  two scripts. Full test suites are NOT required for doc-only phases; the fusion-tea phase
  should state what minimal check applies. agentic-mbse: never run `pytest tests/ -m ""`
  (pulls in the PDF-corpus subsystem); default suite only if a suite is needed at all.
- **BACKLOG follow-on registration** (v2 HTML build pointing at the refreshed brief) is a
  phase deliverable in sysml-codegen's BACKLOG.md.
- Include a final phase: update `.project/CURRENT_WORK.md` docs-explainer-refresh entry +
  spec/design checkbox reconciliation.

## Ordering guidance

Sequence sysml-codegen doc corrections → new doc 29 + matrix CON family + recount →
explainer brief rewrite (biggest single deliverable; INV-6 buildability) → agentic-mbse →
teax → fusion-tea → BACKLOG + close-out. Keep the explainer rewrite its own phase with its
own commit.

End with ARTIFACT: path to plan.md.
