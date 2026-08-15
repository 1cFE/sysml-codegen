# Product-Lens Ledger: Atomic Cutover

## spec — 2026-08-10 — rev `.project/active/elaborator-cutover/spec.md`

Epic: ELABORATE-FIRST

Point (re-derived): sysml-codegen turns a SysML model into an executable TEAx computation graph;
each consumed modeled value must become exactly one runtime source for every and only its bound
consumers, while unsupported authored forms fail before generation. The resolved instance graph,
not a reconstructed string identity, must carry that answer through live and offline routes.
[source: `.project/backlog/epic_elaborate_first_architecture.md` “Critical Success Factor” and
owner-originated rulings; `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
invariants 54–60; grade: owner]

Falsifier: a corrected customer-scale model exposes duplicate public inputs, an off-default mutation
misses a bound consumer or changes an independent source, live and relocated-snapshot routes project
different graphs, an unsupported form projects, or a legacy front end remains a shipped alternate
authority after cutover.

Findings: none. The spec requires the customer-scale every-and-only mutation, public live/capture/
relocated parity, fail-closed diagnostics, one shipped authority, complete legacy deletion, real TEAx
execution, and the pending owner recapture checkpoint. It preserves the contract's capture-refusal
outcomes while requiring one recorded result for every inherited corpus path.

Smells: none.

Gate: CLEAR

## spec — 2026-08-10 — rev `.project/active/elaborator-cutover/spec.md` after P0/P1 review

Epic: ELABORATE-FIRST

Point (re-derived): one loaded semantic source occurrence must become exactly one runtime source
for every and only its bound consumers. Item 7 makes the resolved instance graph the only shipped
authority, carries runtime-source outcomes through live and portable snapshot routes, and rejects
unsupported authoring before capture or generation. [source:
`.project/backlog/epic_elaborate_first_architecture.md:61-84` and
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:735-768`; grade:
owner outcomes plus inherited contract]

Falsifier: the revised spec could still pass while a second projectable authority, public legacy
surface, or wrong oracle survives; Fusion Tea could gain a parallel corrected fixture; a
diagnostic cell could become a loadable snapshot; outer envelope metadata could change semantics
without an integrity failure; or the final corpus batch could land before owner disposition.

Findings: none. The revised contract grades owner outcomes as `[NEED]`, keeps ratified agent
strategy `[INFERRED]`, and cites genuinely inherited behavior. It pins the in-place C25/C2 Fusion
Tea migration, outcome-specific route matrix, closed API and deletion censuses, integrity-bound
envelope, measurable temporary real-TEAx evidence, two-repository quality gates, and one accepted
owner-reviewed recapture batch. Committed downstream packages and studies remain Item 8.

Smells: none.

Gate: CLEAR

## design-review-v3 — 2026-08-10 — rev `.project/active/elaborator-cutover/design.md`

Point (re-derived): one loaded semantic source occurrence must become exactly one runtime source
for every and only its bound calculation, constraint, and aggregation consumers. The resolved
instance graph must be the sole shipped authority, preserve that answer across live and portable
snapshot routes, and reject unsupported authored forms before capture or generation. [source:
`.project/backlog/epic_elaborate_first_architecture.md` “Owner-originated rulings” and “Success
Criteria”; grade: owner]

Falsifier: the design could pass while one modeled source becomes multiple public inputs, an
off-default mutation misses a bound consumer or changes an independent source, live and relocated
v6 routes disagree, an unsupported form produces a snapshot or projection, or a legacy/QN-based
front end remains callable as shipped authority.

Findings: none. DON'T: the corrected context, envelope, and paired-candidate coordinator protect
integrity and landing state without reconstructing semantic identity or retaining a second route.
DO: I1–I12, the closed deletion/caller census, strict v6 validation, C2/C25/C19 every-and-only
proofs, exact 37-path outcomes, and the owner acceptance gate cover the positive obligation.

Smells: none. Smell 2 does not fire: staged admission, projection receipts, and paired promotion own
guarantees that SysIDE, mutable projected graphs, and Git do not claim. Smell 7 does not fire: D1–D12,
the component-owner table, and the stable census rows explicitly assign every moved invariant.

Gate: CLEAR
