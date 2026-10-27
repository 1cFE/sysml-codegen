# Brief: design review, repeated-rollup-collision

Run as a fresh subagent by the orchestrating session on 2026-10-25. You did not write the spec or design.

## Task

Review `.project/active/repeated-rollup-collision/design.md` against `spec.md` beside it, following `~/.claude/commands/_my_design_review.md`. Work in `/home/reid/src/sysml-codegen` on branch `repeated-rollup-collision` (design at commit `71214b28`). Write `design-review.md` beside the design. Don't change `src/` and don't commit.

## Intent

[OWNER-VERBATIM] "yes file it and orchestrate a fix in sysml-codegen": several identical sub-assemblies, each rolling up its own children, should generate and compute the right numbers.

## Orchestrator decision to check, not assume [AGENT]

The design pulls in a fix for backlog `[SC11-IMPORT-REWRITE]` (import lines rewritten by substring in `registry.py:110-118`), because the named-parts criterion fails without it. The orchestrator accepted that scope. Judge whether the design's version (D6) is sound and contained.

## What matters most

- Engineering quality: is "projection decides identity, registry registers each module type once" one clear rule, or does it scatter special cases? Is the shape comparison (which fields count as per-copy) correct and complete, or could two copies that should differ be merged into one class and compute a wrong number? Look hard at that; a silent wrong number is the worst outcome here.
- Does single-copy output stay byte-identical, and is that proven by the plan's tests?
- Are the flipped fixtures (`unresolvable_attr_probe`, `elab_native_plural_scope`) and changed pins handled honestly (values checked before baselines are re-captured)?
- The D3 limit (differing copies under same-named parents) is acceptable to leave filed?
- Can the plan's execution-lane checks actually run (dc3's venv has `simkit`)?

Rank findings must-fix / should-fix / note. End with `ARTIFACT: <path>`.
