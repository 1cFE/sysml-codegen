## spec — 2026-08-16 — rev `.project/active/elaborator-downstream/spec.md`
Epic: ELABORATE-FIRST
Point (re-derived): Preserve one semantic source occurrence as exactly one runtime source for
every and only its bound consumers, or refuse unsupported forms before generation; certify the
downstream impact without reopening the owner-excluded Stellarator migration. [source:
`.project/backlog/epic_elaborate_first_architecture.md`, Mission invariant and Item 8, grade:
owner; P-002 exact anchoring, grade: agent/ratified]
Falsifier: The item can pass while a bound consumer reads the wrong source, an affected July
output or consumer lacks a status, or Stellarator migration becomes a completion gate.
Findings:
- spec-F1 [DO] The July census acceptance gate names cost/LCOE consumers but not recirculation or
  other decision-relevant outputs affected by frozen design-point values, so the report could pass
  without naming every affected consumer. — `.project/backlog/epic_elaborate_first_architecture.md`,
  Item 8 scope 2 and success criteria (agent/ratified) — disposition: amended the census gate to
  cover every affected decision-relevant output and downstream consumer, including recirculation.
Smells: none fired. The owner-amended Stellarator boundary is preserved without contradiction.
Gate: DISPOSED-and-proceed (spec-F1 amended in the spec)

## spec — 2026-08-16 — rev `.project/active/elaborator-downstream/spec.md`
Epic: ELABORATE-FIRST
Point (re-derived): Enable trustworthy design search by preserving each modeled source occurrence
as exactly one runtime source for every and only its bound consumers, refusing unsupported forms
before generation, and reporting downstream impact honestly. [source:
`.project/product/P-001-design-search-free-variation.md` and
`.project/backlog/epic_elaborate_first_architecture.md`, grade: owner; P-002, grade:
agent/ratified]
Falsifier: The item can pass while a public mutation misses a bound consumer, changes an unrelated
source, or an affected July output lacks a truthful disposition.
Findings: none.
Smells: none fired.
Gate: CLEAR
Resolves:
- spec-F1: FIXED — authority: agent/ratified — basis: The revised impact-report criteria cover
  every affected decision-relevant output and consumer, explicitly including LCOE, cost, and
  recirculation, while preserving the 2,294-of-2,301 verdict bound and naming unknown external use.
