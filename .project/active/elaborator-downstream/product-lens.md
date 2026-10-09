## spec — 2026-08-16 — rev `.project/active/elaborator-downstream/spec.md`
Epic: ELABORATE-FIRST
Point (re-derived): Preserve one semantic source occurrence as exactly one runtime source for
every and only its bound consumers, or refuse unsupported forms before generation; certify the
downstream impact without reopening the owner-excluded Stellarator migration. [source:
`.project/backlog/epic_elaborate_first_architecture.md`, Mission invariant and Item 8, grade:
owner; 0002 exact anchoring, grade: agent/ratified]
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
`.project/product/0001-design-search-free-variation.md` and
`.project/backlog/epic_elaborate_first_architecture.md`, grade: owner; 0002, grade:
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


## audit — 2026-10-09 — rev cc5291ea0c5802fb534d5f81caaa07ae996ee526

Point (re-derived): Preserve parser-resolved math without model workarounds, publish supported binding patterns, and converge the historical fixture to the owner's corrected shape. Account for retained certification obligations at their original authority grades. [source: product 0003/0004 first-capture owner quotes; epic owner-verbatim 2026-08-15; downstream spec-review Resolution L2-2; LC-SI catalog; grade: owner for behavior/guidance/convergence, INHERITED for complete acceptance coordinates]

Falsifier: The fixture retains its duplicate driver, generated consumers use invented semantics, guidance teaches unsupported self-binding, or certification closes while retained evidence gaps have no disposition or owning item.

Findings:

- audit-F1 [DO] Incomplete acceptance-coordinate evidence is acknowledged but lacks an explicit remaining-work disposition and owning item. — LC-SI-23 [INHERITED], lifecycle requirements:560; lifecycle contract:928–932 — disposition: pending Item 8 certification finding A1; record ownership and a bounded disposition before claiming reconciliation discharged. This does not require the owner-descoped joined-study proof or establish a behavioral defect.

Smells: None established in the retained implementation/test scope.

Gate: DISPOSE-and-proceed (audit-F1 is lower-authority; the audit separately assesses the retained reconciliation deliverable).


## audit-recheck — 2026-10-09 — rev cc5291ea0c5802fb534d5f81caaa07ae996ee526

Point (re-derived): Preserve the owner-required source behavior, supported authoring guidance, fixture convergence, and honest retained assurance reconciliation. [source: same source-first audit oracle above; grade: owner for behavior/guidance/convergence, INHERITED for complete acceptance coordinates]

Falsifier: Bounded reconciliation claims complete lifecycle certification, silently relaxes retained source semantics, or labels owner-descoped proof PASS.

Findings: None within retained bounded Item 8 reconciliation.

Authority bound: LC-SI-23 [INHERITED] remains PARTIAL; complete acceptance-coordinate certification is not claimed. Existing Item 8 completion authority and original SC15 supply the ownership context. Completing reconciliation does not discharge or waive that broader inherited requirement.

Gate: CLEAR for retained bounded reconciliation.

Resolves:

- audit-F1: FIXED — authority: existing owner single-completion-authority ruling, original SC15, and current spec Completion authority — basis: Rechecking the durable sources shows ownership already exists; the missing-ownership finding was overstated and is withdrawn. Explicit PARTIAL coordinate evidence is a bounded disposition, not a behavioral defect or a new proof task. No new deferral or external owner is created.
