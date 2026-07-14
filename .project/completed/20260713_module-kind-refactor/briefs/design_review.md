# Brief: Item 6 design review — module_kind Refactor

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design-review.md` in `.project/active/module-kind-refactor/`.

## Review target
`.project/active/module-kind-refactor/design.md` (spec + spec-review + briefs beside it).

## What to probe hardest
1. **Byte-identity claims.** The design asserts str-Enum serializes as `.value` and round-trips — verify against the actual `ComputationGraph` serialization path and a committed baseline. Check the claimed per-module baseline diff (two flag keys out, `module_kind` + `output_schema_type` in) is exactly what `model_dump`/`model_dump_json` will produce, including key ordering effects on committed JSON.
2. **The generated-package byte-identity gate.** Walk the four seams' before/after dispatch shapes: for each, confirm the existing-kind branch is behaviorally identical (same template variables, same dedup behavior, same python-path derivation) — a subtle behavioral drift here defeats the whole gate.
3. **`extra='ignore'` claim**: verify PipelineModule's model_config; if it is actually `extra='forbid'`, stale test kwargs raise instead of dropping silently and the design's backstop reasoning changes.
4. **Fail-loud guard reachability**: is `CodeGenerationError` the right existing error family, and do all four seams actually have a raise path (no seam where the kind is silently filtered before dispatch)?
5. **Migration order**: can the tree really pass the suite at each stage boundary, or does the lockstep step need to be atomic? Say which.

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
