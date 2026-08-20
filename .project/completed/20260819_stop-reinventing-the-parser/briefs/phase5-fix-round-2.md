# Brief — fix round 2 (narrow): no fabricated provenance, then re-mint

The rev-2 re-audit (`audit.md`, rev-2 section, committed `3b2866c`) confirms every prior
blocker fixed and blocks on one remaining defect class: **the public catch-all fabricates
provenance**. Unclassified failures get the model-facing `SI_EVIDENCE_INCOMPLETE` plus an
invented location — first `.sysml` in the argument list, line 1. Measured consequences: a plain
syntax error at line 17 reports as an internal failure at `[model.sysml:1]` (because
`SysMLParsingError` is missing from the passthrough tuple at
`orchestration/exact_pipeline_context.py:288` while the sibling tuple has it), and a failure
caused by `zzz_broken.sysml` is cited against an innocent `aaa_fine.sysml`. Orchestrator
verified the tuple gap by reading the code.

The governing principle — record it in the phase record and hold every change to it: **a
diagnostic field is either measured or absent, never defaulted.** A fabricated citation is
worse than the silence it replaced, and inventing a plausible value instead of admitting
ignorance is this item's forbidden move applied to diagnostics. Totality means "a formed
diagnostic always crosses the boundary," not "all four fields are always non-empty."

Scope is exactly the auditor's remedy plus the re-mint. Trees: Codegen
`/tmp/stop-parser-rev2/worktrees/sysml-codegen` on top of `C_prod-r2` `2234845` — same
chain-reset discipline as last round (preserve the r2 evidence chain as `evidence-chain-r2`,
build from `C_prod-r2`, never on the evidence commit `4ea1e8c`). Agentic is **closed** at
`4433888` — nothing there is in scope. Tests first throughout.

## The fixes

1. **Passthrough tuple:** add `SysMLParsingError` at `exact_pipeline_context.py:288` (audit
   the sibling seams for the same asymmetry). A parse error must surface as the parse
   diagnostic it already is — kept test: syntax error at line 17 reports "SysML parsing
   failed" citing line 17, exactly as at `21e09af`.
2. **Distinct internal-defect code:** the catch-all stamps unclassified failures with an
   internal-failure code (naming per design D8's code ownership), never the model-facing
   `SI_EVIDENCE_INCOMPLETE`. The user must be able to tell "your model" from "our bug".
3. **No fabricated locations:** the catch-all reports only what it actually knows — cause
   chain and any true context; location and reference are **omitted** when unknown, never
   guessed. Kept tests: the wrong-file case (`zzz_broken` cited, `aaa_fine` never named) and
   an unclassified planted failure carrying the internal code, full cause chain, and no
   invented `file:line`.
4. **True provenance at the named raise sites:** repair the three rev-1 shapes never fixed
   (`SI_REDEFINITION_INVALID`, the item-def arm of `SI_CONSTRAINT_UNATTACHED`, the
   capture-arm staging path) and the three additional codes the audit names as sharing the
   gap — each raise site attaches its real authored context at the site, so those failures
   never reach the catch-all at all. Kept test per shape.
5. **Fix the totality test** so it enforces the principle: it must fail on a fabricated
   field (assert the reported location equals the planted failure's true site, or is absent),
   not merely on an empty one.

## Then

Rerun the affected focused/full gates from a fresh extraction (recorded, recomputable
commands — and explain any count delta in one sentence), re-mint the chain through the
committed runner (all 21 lanes → `C_prod-r3` / `F_final-r3` / `C_evidence-r3`; Agentic
identity unchanged), update plan.md (superseded-identities note for r2, new table) and the
run records, commit everything in reviewable units in both the worktree and the docs
checkout. Standing constraints unchanged: license via the `.env` source line, no PDF/paid
suites, `deep_cross_scope_probe` stop condition, nothing pushed, no user checkout touched,
mutation-check new kept tests, no self-certification — the independent auditor re-attacks
next. Final message: prose closure account per fix, new identity table, lane results, ending
`ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`.
