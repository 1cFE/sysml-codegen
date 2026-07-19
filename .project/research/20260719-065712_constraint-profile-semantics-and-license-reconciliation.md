---
date: 2026-07-19T06:57:12-07:00
researcher: Codex
topic: "Constraint profile R-1/R-2 intent and SysIDE license reconciliation"
tags: [research, constraints, executable-profile, polarity, licensing]
status: complete
last_updated: 2026-07-19
---

# Research: Constraint Profile Semantics and License Reconciliation

## Research Question

Did prior owner decisions already determine R-1 non-numeric ordering and R-2 negated-assertion
semantics, and why did Item 4 report an unavailable SysIDE license when a license exists?

## Summary

- R-1 is already determined by the owner-ratified numerical-profile contract: every ordering root
  is a numerical claim, and an ordering whose meaning cannot pass through the retained IEEE-double
  runtime is malformed and blocks generation. Boolean, String, and enumeration ordering therefore
  BLOCK; defining host-language ordering would reverse the selected scope.
- R-2 was presented as a false choice. Negation is already in the owner concept's first scope. The
  established architecture preserves the positive predicate body and usage polarity separately,
  derives expected truth from polarity, and applies polarity once when producing verdict and margin.
  The consistent repair is to make polarity explicit in `UsageDecision`, not fold it into IR and
  not block negated assertions.
- The recent license skips were caused by test invocation. `uv run` and the test configuration do
  not automatically load `.env`. Explicitly loading the new repo-local `.env` makes SysIDE import
  and all licensed Item 4 tests pass.

## Decision Provenance

### R-1: non-numeric ordering

The owner-stated purpose is numerical validity evaluation. Non-numerical statements remain visible
but are outside execution, while malformed or unprovable numerical claims error
(`.project/active/numerical-constraint-profile/spec.md:19-31,65-73`). The owner also ratified the
IEEE-double runtime and the structural classifier: an ordering/arithmetic root is a numerical claim;
if it is not fully admitted, it BLOCKs (`spec.md:78-105`; `spec-review.md:155-174`;
`design.md:133-147`).

The exact Boolean/String/enum ordering rows were not separately owner-originated. Their BLOCK result
is the direct application of that ratified rule. Admitting them would require a new typed runtime,
explicit Boolean and enum ordering definitions, typed schemas, compiler support, snapshot/evidence
changes, and a deliberate scope amendment. Python comparison behavior is not modeled semantics.

### R-2: assertion negation

The original owner concept includes negation in first scope and requires assertion polarity to
survive live extraction, snapshots, and execution unchanged
(`.project/concepts/constraint-execution-and-design-space-studies.md:81-87,141-147,231-237`). It
also states the separate-polarity model directly: assertion membership owns expected truth; normal
expects true and negated expects false (`constraint-execution-and-design-space-studies.md:295-303`).
The completed profile and owner-ratified numerical profile both include negated assertion polarity
(`../agentic-mbse/.project/completed/20260713_executable-profile/spec.md:139-146`;
`.project/active/numerical-constraint-profile/spec.md:35-39,90-93`).

The current dataflow implements that split:

1. Extraction selects the source predicate body and independently captures `is_negated`
   (`../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:666-693`).
2. The profile selects and walks the positive body, but currently omits polarity from its decision
   (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:717-783`). This omission is R-2.
3. Lowering verifies the same source IR, guards polarity, stores positive `predicate_ir`, and derives
   `expected_value = not is_negated` (`src/sysml_codegen/analysis/constraint_lowering.py:970-987,
   1083-1104`).
4. Models enforce that expected value derives from polarity
   (`src/sysml_codegen/resolution/models.py:387-438,454-482`).
5. The compiler returns the raw predicate value, compares it to false for a negated assertion, and
   flips only the simple-margin sign (`src/sysml_codegen/generation/predicate_compiler.py:232-302`).
   Execution pins a negated assertion as satisfied with raw `actual_value is False` and positive
   sign-flipped margin (`tests/execution/test_constraint_execution.py:509-544`).

Folding negation into IR would break the same-source-IR invariant and change `actual_value` from the
raw modeled predicate to its assertion-level negation. Blocking negation would reverse the original
scope. The profile should instead consume/carry known polarity and derived expected truth, and
codegen should verify and consume that decision-carried value rather than independently re-reading
unclassified usage metadata. Polarity remains applied once at verdict/margin derivation.

## License Findings

There was a real expired license earlier in 2026, followed by a renewed key used by `fusion-tea`.
The recent Item 4 skip had a different cause: plain `uv run pytest ...` did not load the new
sysml-codegen `.env`, and `tests/conftest.py` has no automatic dotenv loader.

Secret-safe successful commands used an explicit environment file or exported `.env` without
printing its value. Results on 2026-07-19:

- SysIDE import: passed.
- Item 4 relocation file: 3/3 passed, including live A/live B/replay A.
- Item 4 focused suite: 407/407 passed normally and 407/407 under optimized Python.
- Full licensed repository suite, independently run during this investigation: 2,950 passed,
  26 skipped, 10 deselected.

Preferred command pattern:

```bash
UV_CACHE_DIR=/tmp/sysml-codegen-license-uv-cache \
  uv run --env-file .env pytest ...
```

The repo-local `.env` is gitignored but currently mode `0664`; mode `0600` is preferable for a
secret file.

## Recommendations

1. Record R-1 as BLOCK for Boolean/String/enum ordering under the existing malformed-numerical
   diagnostic family. This applies the existing contract; it is not a new semantics choice.
2. Amend the Item 1 spec to replace the R-2 binary with the established third option: preserve
   source predicate IR, carry polarity explicitly in the profile decision, and apply it once
   downstream.
3. Add positive/negated x inline/definition-typed live and codec tests, plus a codegen invariant
   proving decision polarity, catalog polarity, expected truth, verdict, and margin agree.
4. Use `uv run --env-file .env` for licensed codegen gates and correct Item 4 audit/tracking from
   license-free certification to full certification.

## Open Questions

- Exact R-1 diagnostic code and repair wording are design details.
- The profile decision may carry only polarity or both polarity and derived expected truth. The
  design must keep one authoritative application path and reject missing/contradictory values.
- Whether to reduce `.env` permissions to `0600` is an operational action for the owner.
