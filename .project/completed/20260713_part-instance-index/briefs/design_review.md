# Brief: Item 4 design review — Part-Instance Index

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design-review.md` in `.project/active/part-instance-index/`.

## Review target
`.project/active/part-instance-index/design.md` (spec: `spec.md` beside it; original briefs in `briefs/`).

## New evidence you must fold in
`.project/active/part-instance-index/b1-probe-evidence.md` — the orchestrator ran the live probe the design asked for. Bets B1 and B2 are now **confirmed facts** with one new edge case (`[3..3]` presents as equal literal bounds; the design must pin admit-or-block). Review the design's cardinality gate against this actual API surface (node-type dispatch on `upper_bound`; ordered/nonunique markers on the **usage**, not the multiplicity node) — the design was written before this evidence existed, so check its gate logic clause-by-clause against the table.

## What to probe hardest
1. The subtype-closure traversal: does the design's closure over SysIDE heritage match what the S3 probe proved (`_supertype_closure` exists in `extraction/usage_extractor.py`), and does it terminate/dedup correctly on diamond heritage?
2. Retyped-path dedup (D7 canonical-path rule): does it survive the S3 fixture's specialized/redefined containers without double-counting or dropping?
3. Occurrence identity (D5 `path[index]`): stable across loads? Consistent with S3's nine expected paths and with what Item 5 needs for per-occurrence channels (S3 carry-forward (3))?
4. The `[HARD]` byte-identity constraint: is the module genuinely additive (no import-time or call-path perturbation of existing discovery)?
5. Determinism (D6 integer-keyed sort): total order, no dict-iteration dependence?

Verdict format: must-fix list (each with why it's load-bearing), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code and the S3 fixture — do not take the design's word.
