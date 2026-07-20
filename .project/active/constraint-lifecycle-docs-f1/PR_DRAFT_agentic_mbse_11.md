# DRAFT — agentic-mbse PR #11 description (Item 6 reconciliation)

**Status: DRAFT for Item 13.** Not pushed, not applied to the PR. Reflects Items 1–5 as
landed **locally** on `constraint-exec-epic`. **No release-readiness claim** — final
certification and the actual PR update are Item 13's, after the composed 41-case proof.

Landed pin this describes: agentic-mbse `4c18d61`.

---

# CONSTRAINT-EXEC lifecycle: neutral constraint facts, ExpressionIR, executable profile v4, versioned diagnostics

**⚠️ Merge order: this PR merges FIRST.** sysml-codegen's `constraint-exec-epic` PR pins the
schema and profile versions added here (`constraint-facts/v2`, `executable-profile/v4`) in
`_upstream_pins.py` and fails its `test_upstream_pins` if it merges first. teax's PR is
independent; fusion-tea's `main` push comes last.

## What this delivers (agentic-mbse third of the lifecycle program)

- **Neutral constraint facts.** Production `ConstraintFacts` schemas and extraction — the
  neutral substrate sysml-codegen's lowering consumes.
- **ExpressionIR.** One production expression tree serving constraint predicates and calc
  expressions byte-identically.
- **Executable profile — now `executable-profile/v4`.** Eligibility gates + named
  diagnostics: every supported assertion shape lowers; unsupported constructs block
  generation with a named diagnostic, never silence. Unit-safety is derived per arithmetic
  node (mixed-unit / derived-unit blocks are named).
- **Versioned diagnostic severity (`constraint-facts/v2`, lifecycle Item 4, `4c18d61`).**
  `ExtractionDiagnosticFact` carries a versioned `severity` field and a closed `kind`
  vocabulary; unclassified trust-affecting diagnostics fail closed; both consumer sinks are
  covered.

## Evidence

- Item artifacts under sysml-codegen `.project/active/constraint-lifecycle-*`. Item 4
  round-3 audit **Pass with notes** at codegen `caa149c` / agentic-mbse `4c18d61`.
- Downstream coordinated pin verified: codegen `test_upstream_pins.py` matches every entry
  against the value imported from `agentic_mbse`.

## Scope honesty

This is the shared-semantics third of an in-progress lifecycle program, not a finished
release. The composed public proof across all repositories is Item 13 and has not run.
