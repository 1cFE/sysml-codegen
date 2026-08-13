# Stage brief — plan (Item 1: Contract and Authoring Policy)

Produce the execution plan for CONSTRAINT-SEMANTICS Item 1 from the approved spec and revised
design:

- Spec: `.project/active/constraint-semantics-contract-amendments/spec.md`
- Design: `.project/active/constraint-semantics-contract-amendments/design.md` (revised;
  `design-review.md` Resolutions are binding)

**Deliverable**: `.project/active/constraint-semantics-contract-amendments/plan.md` with
phases, checkboxes, and per-phase gates.

## Planning constraints from the run so far

- **Run the sweeps early.** S4/S5 were added after design review and are NOT pre-run; S4 is
  expected to hit living prose around the report template and its tests. Phase the sweep
  (all S-terms, both repos, docs + comments/docstrings) BEFORE the editing phases so the hit
  list sizes the work, with each hit dispositioned (fix-here / correct-as-written /
  hand-to-Item-N) in verification.md.
- **Two repos, one committer discipline**: use `git -C <repo>` for companion-repo git; stage
  untracked files before pathspec commits; never touch `uv.lock`. The companion
  (`/home/reid/1cfe/agentic-mbse-item7-rebuild`, branch `item7-rebuild`) starts clean — keep
  its commits scoped to this item's files.
- **Gates**: per-repo `git diff --check`; codegen `scripts/check_doc_distinctness.py`; the
  design's pairwise precedence-agreement check; the sweep re-run as the final proof of the
  "no remaining statement" criterion. No test suites are required (doc-only item) — but the
  plan must state that explicitly so the implementer doesn't burn time on them.
- **Don't forget the small deliverables**: the ADR id cited back into
  `.project/active/constraint-semantics-contract/product-lens.md` (spec-F1); the two
  future-capability lines in `.project/backlog/BACKLOG.md`; the REQ-EXT-09 matrix-row pointer;
  verification.md.
- **Boundaries to restate in the plan**: no TEAx changes; no normative token spellings; the
  parked D-2 vs D-4/SRC-01 statements untouched; comment/docstring-only code edits (zero
  behavior change), executable text out of scope.
- Commit per phase with the decision in the subject; record deviations in plan checkboxes as
  they happen.

Work synchronously — never pause for background agents; finish plan.md this turn. End with
`ARTIFACT: <path>`.
