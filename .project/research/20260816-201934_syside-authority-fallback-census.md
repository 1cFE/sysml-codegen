---
date: 2026-08-16T20:19:34-07:00
researcher: Claude
topic: "SysIDE-authority fallback census"
status: superseded
superseded_by: ".project/research/20260816-205035_premise-audit-fallback-census.md"
baseline: "codegen 26e19f9; agentic-mbse 8b105b3"
---

# Superseded census: site-location record only

This report's original interpretation was wrong. It treated the missing written `::` path as if
SysIDE had also discarded the exact resolved Feature and its owner. SysIDE retains that exact
referent, and its owner can be a `PartUsage`. The original CATF reading and aggregate blast-radius
claims were also wrong. Git history retains the original text; it is not repeated here as current
ground truth.

The corrected analysis is
`.project/research/20260816-205035_premise-audit-fallback-census.md`. The active contract is
`.project/active/stop-reinventing-the-parser/spec.md`.

## Surviving site-location map

The old labels survive only so existing references can be followed. Their current disposition is in
the active spec.

| Old label | Current spec row or disposition |
|---|---|
| L-01 — definition-owned lineage miss searches descendants | A3 |
| L-02 — nearest-anchor occurrence and calculation selection | A1, A2, A4 |
| L-03 — expression index segment dropped | A5 |
| L-04 — model-wide sole candidate supplies multiplicity | A6 |
| L-05 — redefinition endpoint silently skipped | B7 |
| L-06 — live SysIDE type-test failure falls back to class name | B1 |
| L-07 — operator expression tested by Python class name | B2 |
| L-08 — operand-iteration failure swallowed | B3 |
| L-09 — feature-reference name ladder can return nothing | B4 |
| L-10 — standard-library origin inferred from name prefix | B5 |
| L-11 — Python type inferred from simple type name | B6 |
| L-12 — unmapped output type warns and omits wrapper | B9 |
| L-13 — output-alias first-wins silence | Explicit follow-up outside the lanes |
| L-14 — parameter groups named after source files | Kept rendering policy |
| U-1 — source file inferred from a sole glob result | B10 |
| U-2 — resolved reference with no leaf may be skipped | B8 |

## Facts retained

- The exact-ID graph, snapshot, and projection architecture remains the public route.
- SysIDE supplies exact semantic declarations but not the concrete occurrence identities codegen
  needs. Contextual occurrence materialization remains codegen's job.
- Nearest-ancestor, descendant, sole-candidate, and first-match election can invent a runtime source.
- The expression path can discard an authored index and silently compute a different expression.
- Adapter and extraction failures must preserve exact evidence or fail by name.

No count or corpus blast-radius claim from the original report is retained. The active spec requires
a reproducible remeasurement in unique semantic sites.
