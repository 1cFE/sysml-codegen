# Brief: spec_review — study-layer-to-codegen (WRAP-SPLIT Item 3)

Sent by the orchestrator (agentic-mbse `/_my_orchestrate` run, 2026-10-12) to `/_my_spec_review`, in a fresh session. Review `.project/active/study-layer-to-codegen/spec.md` (committed at `21670e8`). The spec's own brief is `briefs/spec.md` beside it. Read it for the intent and the orchestrator's decisions the spec was given.

## Sources

You cannot read sibling repos. The orchestrator copied what you need into this worktree's gitignored `.orchestrate-logs/src/`: fusion-tea's study layer at `b06585709`, and agentic-mbse's epic, research audit, installer, `CLAUDE.md`, and Item 2's design and runbook. `briefs/spec.md` lists the contents. Read them freely; do not edit or run them. The repackaging check's output is at `.orchestrate-logs/scratch/repack-check/output.txt`.

## What the orchestrator wants from this review

Review the spec as the contract that design, plan, implementation and audit will be held to. Beyond your standard pass, press on these:

1. **Owner intent.** Does any requirement narrow, widen or bend the owner's decisions in the epic header and the run-study concept's "Next-Stage Handoff"? Check that every `[NEED]` is owner-stated, and that every `[INFERRED]` is really derived and not invented. Open Question 10 (a separate distribution) reads the owner's "ships from sysml-codegen" decision. Is the spec right to route it to the owner?
2. **Scope against the budget.** The epic budgets 2 days. The spec has 11 criteria, a two-agent dry run (SC4), a fusion-tea rehearsal (SC9), a new fixture, target-declared gates and installer work. Which criteria are load-bearing for the point of the item, and which are evidence that could shrink without losing it? The spec says scope that does not fit is cut to a recorded deferral. Does it say which parts would be cut first? Recommend; don't cut silently.
3. **Checkability.** Can an auditor pass or fail each criterion without judgment calls? Two cases to look at hardest: SC7 ("a reader can tell it apart from a pre-move document") and SC5. For SC5, check the grep list against the owner's bar: fusion vocabulary is legal in labelled examples, while pointers to internals, machine paths and requirement numbers must go.
4. **Hidden premises.** The spec relies on several things: the moved tools keep identical semantics; `rederived_census` can get a home in sysml-codegen; the fixture can drive `integrate` to completion without fusion-tea's toolchain. Flag any premise that the sources show to be false or unverified, and say what would verify it.
5. **Fit with this repo.** Read sysml-codegen's `CLAUDE.md`, `.project/README.md` and `.project/adr/INDEX.md`. Does the spec conflict with a recorded sysml-codegen decision, for example ADR-0007's dependency direction or P-004's product identity?

Write the review where `/_my_spec_review` puts it, with a verdict and must-fix / should-fix points. The orchestrator feeds the must-fix points back to the spec author.

Do not start background tasks. Finish with `ARTIFACT: <path>`.
