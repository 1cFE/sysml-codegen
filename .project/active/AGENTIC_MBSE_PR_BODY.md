Companion to [1cFE/sysml-codegen#3](https://github.com/1cFE/sysml-codegen/pull/3) — Item 12 of the UPSTREAM-FINDINGS epic. sysml-codegen changed what SysML it accepts across eleven items; this PR moves agentic-mbse's teaching and checking surfaces in lockstep so the validated-subset contract is enforceable again.

## What's here (9 commits)

- **A-2** (`6dbdf1b`): the sysml-conventions calc-def stencil teaches inline `return`, not the expression-losing body-assignment form.
- **Phase 1** (`9db5ede`): the four non-fileable checks — L2 self-named dead-end FAIL (covered self-named bindings are now a *supported* plant idiom per codegen Items 9/10; only a binding with no covering feature anywhere fails), L6 anonymous-return FAIL, L6 constraint-non-executability WARN, L6 calc-bearing-part-def-no-instantiation FAIL (retyping counts as instantiation). Each with a negative fixture and a negative-of-the-negative.
- **Phase 2** (`87f9bc8`): adr002 operator corrections (`^` dropped, function-invocation WARN), two L6 false-positive families fixed (calc-def-internal derived expressions; quoted names), body-assignment WARN.
- **Phase 3** (`f68d1cb`): MODELING_GUIDE / pattern docs D1–D8 incl. the new `docs/patterns/plant-idiom.md` (reference shapes = sysml-codegen's ife_plant/spec_chain fixtures), retyping, quoted names, the no-loops rule, bare-`:>>` idiom, EXPOSE surfacing.
- **Phase 4** (`08cd595`): backlog filings (C7/C8 deferred checks, the syside vendor-note draft with the evaluation-time-recursion finding).

## Post-review fixes (3 commits)

A review of the branch found three checks still flagging shapes sysml-codegen accepts — the same "fires on a supported subset" defect class the epic exists to remove. All three are fixed here, each verified against codegen's own extraction code and fixtures (not assumed):

- **Findings 2/3 + F6** (`49c7b7a`): `check_supported_operators` and `check_static_function_invocations` now skip calc-def-owned attributes, so a calc-def-internal `a ^ b` / `sqrt(a)` in a flat layout no longer false-FAILs/WARNs. **F6 is now fixed, not just filed** — `check_static_expressions` exempts a design computed attribute whose refs all resolve to same-part owned siblings (a codegen FORMULA, Item 5 / REQ-CA-06), while still firing on calc-output-in-arithmetic, self-reference (REQ-CA-07), and dotted paths. Both directions fixtured; three pre-Item-5 tests that encoded the old blanket rule were updated to the relaxed contract.
- **Teaching reconciliation** (`9cf6b3c`): the F6 relaxation left several shipped surfaces contradicting the validator — some using the exact accepted shape (`= radius * 2.0`) as their "this FAILs" example. Reconciled across adr002-calculations.md, common-mistakes.md, the sysml-conventions skill, and MODELING_GUIDE/MODELING_PROCESS (templates + tracked install copies). Stance: calc defs stay recommended for real calculations; inline FORMULA is a convenience for simple arithmetic and unit conversions.
- **Follow-up specs** (`7f77510`): a C4 instantiation-check docstring/test-gap (the check is correct — a base reached only via plain subtype IS dropped by codegen per REQ-EXT-13/14 — but its docstring is wrong and the path untested) and the reconciliation record.

## Acceptance

- agentic-mbse suite: **1222 passed / 1 skipped**; slow corpus: **33 passed** (re-verified independently, incl. the changed V2 contract).
- Cross-repo: `run_all_checks` over sysml-codegen's fixture corpus — plant-idiom and `quoted_owner_formula` FORMULA fixtures now pass L1–L6 fully; no L1–L5 regression anywhere; the L6 false positive on `quoted_owner_formula` (F6) is resolved. Remaining failures are pre-existing check classes on deliberate trap fixtures.
- Traceability: every impact item recorded across the epic is implemented or filed — tables in sysml-codegen's `.project/active/validation-sync/close-out.md`. Two review follow-ups (C4 docstring/test gap; optional full inline-FORMULA teaching) are specced in agentic-mbse's `.project/active/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
