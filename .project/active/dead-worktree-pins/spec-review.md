# Spec Review: Dead Worktree Pins

**Spec:** `.project/active/dead-worktree-pins/spec.md`
**Contract:** `/home/reid/agentic-project-init/claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/dead-worktree-pins/spec-review.md`
**Date:** 2026-08-15

---

## Reality Check

**Concerns.** This is the right work item, and both cleanup regressions reproduce at codegen
`9ce5548`: the execution lane gives `76 passed, 12 errors`, and `paths` prints
`304 rows checked, 0 problems` while its configured companion root is absent. The core repairs are
directionally right. The spec is not safe as the design contract yet because it misreads the
coverage of `paths` and uses that error to add a broader reporting requirement.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The Problem and final Success Criterion conflate one helper with the whole
`paths` gate. Only `check_removed_symbols` filters to the 12 executed rows carrying `removes`
blocks (`scripts/check_ledger_4a.py:179-213`). `check_paths` still walks all 304 rows for duplicate
paths, exact diff-set equality, carried-row presence, row state, deleted responsibility, surface
coverage, data coverage, blockers, disposition vocabulary, and recorded reasons
(`scripts/check_ledger_4a.py:534-594`). Therefore the statements that the other 292 rows were
“never in that check” and that the headline overstates coverage by 24× are false as claims about
`paths` (`spec.md:25-30`, `:103-111`). The true statement is narrower: 12 rows carry an executed
removed-symbol claim, and the two companion claims are currently skipped because the configured
checkout is missing.

**L1-2 · Question to the user:** The reporting criterion is explicitly about a condition that
predates this cleanup (`spec.md:103-111`), while the owner-graded scope says “JUST FOR THE FIXES”
(`spec.md:118-119`). Its cited support does not settle that expansion: ADR-009 governs constraint
report headline vocabulary (`docs/architecture/modeling-assumptions.md:704-740`), and the
product-lens extrapolation is agent-grade (`product-lens.md:16-23`). **Do you want the ledger CLI’s
output redesigned in this repair item?** I recommend removing that criterion from this item. If
you do want it here, it needs to be recorded as an owner decision and rewritten around the actual
dimensions `paths` checks, not the 24× claim.

**L1-3 · Question to the user:** The “surfaced premise conflict” is no longer an active conflict.
The cited origin now says the repairs were reverted and the defects are live
(`.project/CURRENT_WORK.md:205-213`), and HEAD agrees. The sibling item already preserves the
revert history. **Do you want that historical correction to constrain design?** If not, ask the
spec agent to shrink `spec.md:59-73` to the current checked fact or remove it. Keeping the full
resolved contradiction works against the capture rule to amend a correction instead of accreting
its history.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** “Passed by absence” is the wrong opposite of “verified.” For an executed
delete row, a missing row path is the intended proof; both the checker and the spec say so
(`scripts/check_ledger_4a.py:21-24`, `spec.md:134-137`). The defect is that a missing *repository
root* is indistinguishable from that valid row-level result. The owner-approved startup root check
closes that ambiguity. If reporting changes remain, they must distinguish a missing configured
checkout from two valid verification outcomes: a deleted path proved absent and a surviving path
parsed for removed declarations.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** The spec omits the required pointer to its product-lens ledger. The
generation contract requires that pointer (`_my_spec.md:141-153`), and it matters here because the
ledger is the source of the disputed reporting expansion (`product-lens.md:33-48`). Add
`.project/active/dead-worktree-pins/product-lens.md` to Related Artifacts so downstream agents can
see that the added obligation is agent-originated and challengeable.

**L3-2 · Rewrite request:** The scope boundary around checker ceilings is internally inconsistent.
The Problem calls the companion replacement skip the sixth documented ceiling (`spec.md:43-45`),
but Non-Goals says the five pre-existing ceilings remain (`spec.md:161-162`). The live checker
numbers six (`scripts/check_ledger_4a.py:35-66`). Ask the spec agent to say plainly which modes may
change. If this remains a `paths`-only repair, `replacements` and all six recorded ceilings should
be explicitly outside the change.

### Lens 4 — Hygiene

No separate hygiene finding. The material structural omission is L3-1.

### Lens 5 — Reader Comprehension

No separate finding. Correcting L1-1 and resolving L1-2 removes the main obstacle to understanding
the work item on one read.

---

## Engagement Summary

**Overall take:** The narrow repair is real, correctly owned, and mostly specified well. The spec
then expands into a ledger-reporting redesign based on a false equation: “12 removed-symbol rows”
does not mean “only 12 of 304 rows are checked.” Correct that model before design.

**Here's what I need you to weigh in on:**

1. **[L1-1, L2-1]** Have the spec agent correct the checker model: all 304 rows are checked across
   several dimensions; 12 is only the removed-symbol subset, and valid row-path absence is itself
   verification once the repository root is known to exist.
2. **[L1-2]** **Resolved:** keep the item narrow. Retain the companion-root hard failure and remove
   the broader output redesign from this item.
3. **[L1-3]** **Resolved:** shrink the resolved CURRENT_WORK contradiction to one current-fact
   note; the full history already has a durable home.
4. **[L3-1, L3-2]** Restore the product-lens pointer and make the mode boundary explicit before the
   spec moves downstream.

---

## Resolutions

- **[L1-2] `[OWNER 2026-08-15]`:** “Keep in narrow.” The item stays limited to repairing the dead
  path pins, failing on a missing configured repository root, and keeping regression checks. The
  broader ledger-output redesign is not part of this work.
- **[L1-3] `[OWNER 2026-08-15]`:** “shrink it to a one current-fact note.” Replace the resolved
  premise-conflict section with one note stating the current fact: the defects are live at HEAD,
  and the `88 passed` result was reached only with the reverted repair applied. The full correction
  history stays in its existing durable homes.

---

**Verdict:** Revise
**Next Steps:** The owner’s resolutions are recorded. Re-run `my-spec` (or return to the spec agent)
and point it at this review. The reviewer does not edit the spec.
