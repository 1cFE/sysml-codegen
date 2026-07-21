# agentic-mbse PR #11 description (FINAL — Item 13 composed proof complete)

**Status: FINAL.** The composed 41-case public lifecycle proof (register row 17) is complete —
**41/41** cells pass at the pinned set. Items 1–12 certified; Item 13 complete. Merge pending human.

Landed pin: agentic-mbse **`4c18d61`**.

**⚠️ Merge order — this PR merges FIRST.** sysml-codegen PR #9 pins the schema/profile versions
added here (`constraint-facts/v2`, `executable-profile/v4`) in `_upstream_pins.py` and fails its
`test_upstream_pins` if it merges first. teax's PR is independent; fusion-tea / stellarator stay
local.

**Note on ancestry:** `4c18d61`'s history includes `4ed2a07` ("Add modeling workflow orchestrator"),
a separate workstream retained in the candidate by owner direction (Item 0 evidence). Flagged for
the reviewer.

## What this delivers (agentic-mbse third of the lifecycle program)

- **Neutral constraint facts.** Production `ConstraintFacts` schemas + extraction — the neutral
  substrate sysml-codegen's lowering consumes.
- **ExpressionIR.** One production expression tree serving constraint predicates and calc
  expressions byte-identically.
- **Executable profile — `executable-profile/v4`.** Eligibility gates + named diagnostics: every
  supported assertion shape lowers; unsupported constructs block generation with a named
  diagnostic, never silence. Unit-safety derived per arithmetic node.
- **Versioned diagnostic severity (`constraint-facts/v2`).** `ExtractionDiagnosticFact` carries a
  versioned `severity` field + closed `kind` vocabulary; unclassified trust-affecting diagnostics
  fail closed; both consumer sinks covered.

## Evidence

- **Composed proof (register row 17):** 41/41 Appendix C cells pass at the pinned set (rerun 22 /
  compose 19), 16 negative mutations fail at their boundary, 6 full-tree byte checks pass. See
  sysml-codegen `.project/active/constraint-lifecycle-composed-proof/{release-readiness.md,
  evidence-coordinate-register.md}`.
- **Companion gates at `4c18d61`:** profile/skew/constraint-facts/version suite green (344 passed
  in the composed run). Case 37 fact-consumer behavioral tests exercised here.
- **Downstream coordinated pin verified:** codegen `test_upstream_pins.py` matches every entry
  against the value imported from `agentic_mbse`.
- Per-item artifacts under sysml-codegen `.project/active/constraint-lifecycle-*`.

## Scope honesty

This is the shared-semantics third of the lifecycle program. The composed public proof across all
repositories (Item 13) is complete and passes 41/41; this description reflects that final state.
Consumer-repo delivery (fusion-tea, stellarator) is a separate human decision.
