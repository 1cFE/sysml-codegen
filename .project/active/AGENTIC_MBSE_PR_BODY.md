Companion to [1cFE/sysml-codegen#3](https://github.com/1cFE/sysml-codegen/pull/3) — Item 12 of the UPSTREAM-FINDINGS epic. sysml-codegen changed what SysML it accepts across eleven items; this PR moves agentic-mbse's teaching and checking surfaces in lockstep so the validated-subset contract is enforceable again.

## What's here (6 commits)

- **A-2** (`6dbdf1b`): the sysml-conventions calc-def stencil teaches inline `return`, not the expression-losing body-assignment form.
- **Phase 1** (`9db5ede`): the four non-fileable checks — L2 self-named dead-end FAIL (covered self-named bindings are now a *supported* plant idiom per codegen Items 9/10; only a binding with no covering feature anywhere fails), L6 anonymous-return FAIL, L6 constraint-non-executability WARN, L6 calc-bearing-part-def-no-instantiation FAIL (retyping counts as instantiation). Each with a negative fixture and a negative-of-the-negative.
- **Phase 2** (`87f9bc8`): adr002 operator corrections (`^` dropped, function-invocation WARN), two L6 false-positive families fixed (calc-def-internal derived expressions; quoted names), body-assignment WARN.
- **Phase 3** (`f68d1cb`): MODELING_GUIDE / pattern docs D1–D8 incl. the new `docs/patterns/plant-idiom.md` (reference shapes = sysml-codegen's ife_plant/spec_chain fixtures), retyping, quoted names, the no-loops rule, bare-`:>>` idiom, EXPOSE surfacing.
- **Phase 4** (`08cd595`) + F6 (`1b7046a`): backlog filings (C7/C8 deferred checks, the syside vendor-note draft with the evaluation-time-recursion finding, and a third L6 false-positive family found in the cross-repo sweep).

## Acceptance

- agentic-mbse suite: **1218 passed / 1 skipped** (re-verified independently).
- Cross-repo: `run_all_checks` over sysml-codegen's fixture corpus — plant-idiom fixtures pass L1–L6 fully; no L1–L5 regression anywhere; remaining failures are pre-existing check classes on deliberate trap fixtures.
- Traceability: every impact item recorded across the epic is implemented or filed — tables in sysml-codegen's `.project/active/validation-sync/close-out.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
