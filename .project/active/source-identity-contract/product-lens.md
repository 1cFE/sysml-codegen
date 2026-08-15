## audit — 2026-08-07 — rev 5be8276
Point (re-derived): Every supported binding maps one semantic source occurrence to exactly one runtime source across all consumers: one public input for an externally supplied value or one producer channel for a computed value.   [source: `.project/backlog/epic_semantic_source_identity.md` (`[OWNER]` Mission invariant), grade: owner]
Falsifier: A public live-and-relocated-snapshot package exposes duplicate inputs for one modeled occurrence, or routes one computed value through anything other than its single producer channel across all bound consumers.
Findings:
- audit-F1 [DO] The claimed-complete 26-cell source-identity acceptance authority omits the computed-source topology: no cell proves that one computed value feeds multiple calculation, constraint, and aggregation consumers through one producer channel, so Items 4–6 could pass without proving half of the owner’s runtime-source invariant. — `.project/backlog/epic_semantic_source_identity.md` (`[OWNER]` Mission invariant) (owner) — disposition: BLOCK
Fired smells: none
Gate: BLOCKED (audit-F1)

## correction — 2026-08-07 — rev 5be8276 (worktree)
- audit-F1 resolved by citation: cell **C24** (computed source × 1 calc + 1 constraint + 1 aggregation → `RUNTIME_SOURCE` — one producer channel, no minted public input, upstream-mutation propagation) published in
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, Appendix C, cell C24, under the explicit D8 reopening in the same appendix (counts 26/32 → 27/33, changed together with `design.md` A.3/A.4/A.6/A.8). Certification: `BLOCKED(computed-source mixed-consumer fixture → Item 4)`; mutation legs → Item 6 — the topology can no longer pass unproven by omission.
- Gate: awaiting audit rerun (this entry records the correction, not a verdict).

## audit-rerun — 2026-08-07 — rev 5be8276 (corrected worktree)
Point (re-derived): Every supported binding maps one semantic source occurrence to exactly one runtime source across all consumers: one public input for an externally supplied value or one producer channel for a computed value.   [source: `.project/backlog/epic_semantic_source_identity.md` (`[OWNER]` Mission invariant), grade: owner]
Falsifier: A published acceptance population can pass without proving one computed value reaches all calculation, constraint, and aggregation consumers through one producer channel, or without proving the exact mixed-context customer source converges on one public input.
Findings:
- None.
Resolves:
- audit-F1: FIXED — authority: owner — basis: C24 publishes the owner-required computed-source topology with 1 calculation + 1 constraint + 1 aggregation, one producer channel, zero public inputs for the computed source, and an upstream-mutation obligation (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, Appendix C). C25 separately closes the audit's exact customer-context gap; the matrix now derives to 28 cells / 34 coordinates.
Fired smells: none. Authority state has one home in the contract's "Current conclusion"; downstream surfaces cite it.
Gate: CLEAR

## audit-rerun — 2026-08-07 — rev 5be8276 (corrected worktree, independent pass)
Point (re-derived): Every supported binding preserves one semantic source occurrence as exactly one runtime source across all consumers: one public input for an externally supplied value or one producer channel for a computed value. The exact customer composition must reject the original self-binding loudly, then make the approved explicit form converge on one shared input across live and relocated-snapshot execution. [source: `.project/backlog/epic_semantic_source_identity.md` (`[OWNER]` Mission invariant and customer criterion), grade: owner]
Falsifier: The published acceptance population can pass without proving the computed-source producer topology, or without proving the exact mixed usage/definition-authored customer topology and its shared off-default mutation.
Findings:
- None.
Verification:
- C24 publishes one computed source feeding 1 calculation, 1 constraint, and 1 aggregation through one producer channel with zero public inputs; live/snapshot parity and upstream-mutation evidence remain explicitly owed to Items 4 and 6.
- SRC-01/01b require the original customer self-binding to fail loudly. C25 covers the approved bare-renamed availability bindings across the actual usage-authored and definition-authored contexts, converging on one `hif_plant.availability` input whose mutation reaches both calculations.
Resolves:
- audit-F1: FIXED — authority: owner — basis: the prior `audit-rerun` contains a valid structured resolution citing C24 and its owner-required producer-channel topology. The earlier loose correction entry alone was not the resolution.
Fired smells: none. The retained 11-test suite passes but remains explicitly non-certifying; defect pins are not compatibility requirements, and route-specific controls are not used as universal proof.
Gate: CLEAR

## audit-rerun — 2026-08-07 — rev 5be8276 (corrected worktree, topology-split pass)
Point (re-derived): Every supported binding preserves one semantic source occurrence as exactly one runtime source across every calculation, constraint, and aggregation consumer: one public input for an externally supplied value or one producer channel for a computed value. The exact customer composition must reject the original self-binding loudly and make the approved explicit form converge on one shared input across live and relocated-snapshot execution. [source: `.project/backlog/epic_semantic_source_identity.md` (`[OWNER]` Mission invariant and customer criterion), grade: owner]
Falsifier: The published acceptance population can collapse producer-backed and literal-backed aggregation sources into one coordinate, leave a counted declaration or occurrence parametric, or pass while one semantic occurrence maps to duplicate or wrong-topology runtime sources.
Findings:
- None.
Verification:
- Appendix C now derives 29 cells / 35 coordinates. C17 fixes `permitting.capital_cost` to one producer channel with zero public inputs; C26 fixes the three literal-backed `permitting` cost features to three independent public inputs with zero producer channels. Current single-route evidence is recorded only as a C17 control and a C26 contradiction; full live/relocated mutation proof remains owed.
- C24 fixes one direct calculation-output declaration, `'Source Identity Producer'::result` on `source_identity_computed.producer_calc`; 22a fixes one concrete expression binding, `ExpressionBindingDesign::expr_probe::cost_calc::combined_input`. C25 and SRC-01/01b continue to carry the exact customer positive and negative obligations.
Resolves:
- audit-F1: FIXED — authority: owner — basis: Appendix C cell **C24 — feature chain to a computed value × single occurrence × mixed consumers (producer channel)** in `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` publishes the owner-required producer topology, with one channel, zero public inputs, and all three consumer types. This stable cell-name/path citation governs in place of the stale line-number locator in the earlier correction entry.
Fired smells: none. The lifecycle contract remains the sole normative scenario authority; projections cite it. Defect pins and route controls remain explicitly non-certifying, so neither baseline compatibility nor a selected route substitutes for the product obligation. The retained source-identity suite passes 11/11.
Gate: CLEAR
