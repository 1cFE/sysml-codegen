# Product-Lens Ledger: Calculation-Definition Gate Capability

## spec — 2026-08-13 — rev .project/completed/20260813_calcdef-constraint-gate-design/spec.md
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): Modeled physics constraints must make design search viable; for this
capability, each asserted calculation-definition constraint executes once per concrete
calculation occurrence, while usage-level coverage remains distinct from occurrence-level
results. [source: `.project/active/constraint-semantics-contract/rulings-20260812.md`
owner-stated frame and Q2/Q5, grades: owner; agent/ratified]

Falsifier: Two concrete calculations share one definition, one occurrence violates its gate, and
the generated package emits one collapsed check or reports full satisfaction without preserving
the failing occurrence.

Findings:

- None.

Gate: CLEAR

## audit — 2026-08-13 — rev .project/completed/20260813_calcdef-constraint-gate-design/design.md
Epic: CONSTRAINT-SEMANTICS

Point (re-derived): Modeled physics constraints must produce trustworthy design-search evidence;
for this capability, one asserted calculation-definition usage expands through exact graph
identity into one check per concrete calculation occurrence, while coverage remains usage-level
and results remain occurrence-level. [source:
`.project/active/constraint-semantics-contract/rulings-20260812.md` owner-stated frame and Q2/Q5,
grades: owner; agent/ratified]

Falsifier: Two sibling calculations use one definition, one occurrence fails, and the design
collapses them, reconstructs attachment from rendered names, loses the failed occurrence, or
permits full satisfaction without the complete occurrence population.

Findings:

- None. The design preserves one graph/catalog authority, exact occurrence identity, complete
  per-occurrence results, and fail-closed joins. No §4 audit smell fired.

Gate: CLEAR
