# Phase 5 audit fix round — green-checkpoint record

**Date:** 2026-08-18  
**Codegen base:** `1332b01fa4eb57d1832dfd000daeca94780a9cc0`  
**Agentic input:** `443388823f0db46c14df1728d3843d0a74ee7590`

This checkpoint closes the compatibility failures exposed by the first full declared-extraction
run after the audit fixes. It is the resumable boundary before Fusion repinning and the 21-lane
evidence remint.

## Corrections in this checkpoint

- The five tests that previously expected an unsupported invocation to survive acquisition now
  require the pre-graph public refusal with exact code, authored expression, root-relative source
  file and line, rendered provenance, and the upstream semantic-evidence cause. The alias-cycle
  and graph-codec responsibilities those fixtures also carried remain covered on invocation-free
  models.
- The established empty-model `CodeGenerationError` is routed through unchanged. The catch-all
  converts only failures that do not already have a public refusal type.
- Diagnostic source-context helpers no longer appear as construction authorities imported from
  the exact-context module.
- Gate 4A ledger rows `L-288` and `L-291` now record the Phase 5 audit retirement of the dead
  classifier-only tests. The extraction validation performs a complete collection sweep over all
  retained replacement-proof citations.

The full-suite skip count changes from 34 to 9 because retiring the dead computed-attribute golden
test removes exactly its 25 parametrized “no computed attributes” skips; the nine retained skips
are the calc-compat golden cases.

## Validation boundary

Before this checkpoint, the declared extraction returned 2,508 passed, 13 failed, 9 skipped and 94
deselected. Every failure was assigned to one of the corrections above. The checkpoint is not an
evidence result: the next required action is a fresh declared extraction, a complete default suite,
and the full ledger citation-collection sweep. The 21-lane runner must not start until both are green.
