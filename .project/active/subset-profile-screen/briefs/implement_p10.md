Phase 10, replaced. The readiness rule (D8) is not an owner question; the record already settles it, and the third outcome was the pipeline's invention, not the owner's. Remove it.

Sources, graded:
- [OWNER-ratified 2026-10-20, briefs/align.md Q1] The generator's own route alone decides whether `generate` and `check` refuse.
- [INHERITED: epic Item 2b Success Criteria] "check and generate fail at the same preparation seam without mutating a sentinel destination." `check` gives `generate`'s answer without writing.
- [OWNER-ratified 2026-10-18, agentic-mbse `.project/completed/20261020_l6-subset-profile/spec.md:146`] a subset-contract finding never labels a model generated-ready; [delegated by owner, same spec :127] dropped String values are warnings.

What ships:
- `check` exit codes: 0 when `generate` would build, 1 when it would refuse (including environment failure, as now), 2 usage error. Remove exit 3, the `Readiness` READY/NOT_READY concept, the interim rule, `readiness()` and the readiness line. No wording anywhere calls a model "ready" or "clean".
- The screen section stays exactly as the Phase 8 display ruling has it, presented as warnings/information under the generator's answer: actionable findings in full, admitted as a count, omitted/excluded per rule; "not assessed" stated plainly with its reason; disagreements stated. It never changes the exit code.
- The unbound String library default loss stays filed under RG-2 (2a `rg2-string-policy.md`); `check` has no special case for it.
Update spec (criteria that mention ready/not ready/exit 3, the outcome-words section), design (D8 → removed, with a one-line "out, because the generator alone decides (owner, Align Q1) and the epic criterion is generate's seam"), plan (Phase 10 rewritten to this and checked off), CLAUDE.md and `docs/architecture/reference/02-orchestration.md`, product-lens (design_review-F1/F2 closed: no readiness claim exists, so nothing can over-claim or settle RG-2). Tests: replace readiness tests with tests that `check`'s exit code equals `generate`'s outcome on every 2a case and that no output line says ready/clean. Exit check as before (0 byte / 0 record differences, base 9 failures, mypy, ruff, TEAx lane receipt if src changed). Commit per logical change. Report briefly.
