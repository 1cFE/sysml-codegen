## spec — 2026-08-07 — rev .project/active/source-identity-occurrence-foundation/spec.md

Epic: SOURCE-IDENTITY

Point (re-derived): Every supported consumed modeled value must carry its exact
declaration-plus-concrete-occurrence identity so one semantic source occurrence produces exactly
one public input or producer channel for every and only its consumers. [source:
`.project/backlog/epic_semantic_source_identity.md`, grade: owner/HARD]

Falsifier: The spec permits a supported binding to reach source selection without extraction-owned
declaration-plus-occurrence identity, allows consumer-local reconstruction or guessing, or creates
a second occurrence-to-definition authority.

Findings: None.

Smells: None.

Gate: CLEAR

## spec — 2026-08-07 — rev 2 .project/active/source-identity-occurrence-foundation/spec.md

Epic: SOURCE-IDENTITY

Point (re-derived): Every supported consumed modeled value must carry its exact
declaration-plus-concrete-occurrence identity so one semantic source occurrence produces exactly
one public input or producer channel for every and only its consumers. [source:
`.project/backlog/epic_semantic_source_identity.md`, grade: owner/HARD]

Falsifier: The spec permits a supported binding or current-format snapshot to reach source
selection without extraction-owned declaration-plus-occurrence identity, allows consumer-local
reconstruction or guessing, or creates a second occurrence-to-definition authority.

Findings: None.

Smells: None.

Gate: CLEAR

## spec — 2026-08-07 — rev 3 .project/active/source-identity-occurrence-foundation/spec.md

Epic: SOURCE-IDENTITY

Point (re-derived): Every supported consumed modeled value must carry its exact
declaration-plus-concrete-occurrence identity so one semantic source occurrence produces exactly
one public input or producer channel for every and only its consumers. [source:
`.project/backlog/epic_semantic_source_identity.md`, grade: owner/HARD]

Falsifier: The spec permits source selection without extraction-owned
declaration-plus-occurrence identity, treats a retained Item-5 defect pin as correct topology,
defers schema/identity review of the Item-4 snapshot recapture, omits executable validation
oracles, or creates a second occurrence-to-definition authority.

Findings: None.

Smells: None.

Gate: CLEAR

## design-review — 2026-08-07 — rev .project/active/source-identity-occurrence-foundation/design.md @ 224bfa6

Point (re-derived, independent of the design's "The Point"):
Item 4 must give every supported model-derived consumed value ONE exact extraction-owned semantic
source identity — declaration identity plus concrete occurrence identity — that survives live
extraction AND relocated-snapshot replay before any consumer resolution, produced through exactly
one occurrence-to-definition bridge / identity authority; reconstruction from owner/leaf/name is
explicitly NOT an accepted authority; an older snapshot format lacking the evidence fails closed;
a self-binding is never read as an outer reference; and the nested-occurrence override (C19)
resolves so both consumers observe 80.0. This is the foundation slice of the [OWNER] mission
invariant "one semantic source occurrence -> exactly one runtime source across all consumers"; the
convergence/cutover itself is Item 5, by the epic's ratified sequencing.
  [source: .project/backlog/epic_semantic_source_identity.md (Item 4 + [OWNER] Mission invariant);
   .project/concepts/constraint-execution-authoritative-lifecycle-contract.md invariants 54-60,
   D-4 [OWNER-VERBATIM], D-16..D-19, Appendix C SRC-01/C19; grade: owner/HARD for the mission
   invariant and D-4; agent-ratified/INHERITED for the Item-4 foundation slice and invariants 55/58/60]

Falsifier (design-level observables that would show the point violated): the design would
(a) let identity be reconstructed from owner/leaf/name/value as the authority; (b) stand up a
second bridge, structural walker, or identity authority; (c) carry identity on only one route;
(d) add a silent snapshot compatibility shim instead of failing v5 closed; (e) leave C19
unresolved; or (f) let VBR/rescue/backtracking mutate the captured identity.

Findings:
- design-review-F1 [DO] Transitional dual-liveness in supplied_values.py: Item 4 stands up the
  single SourceIdentityAuthority (D4) and uses it for the C19 value-site match (D7), while the
  legacy string-scope precedence ladder stays live for every other outcome and full satisfaction
  of "one identity authority; superseded adapters derive from it or are deleted" is deferred to
  Item 5. — lifecycle contract invariant 60 / D-16..D-18 (INHERITED) — disposition:
  DISPOSE-and-proceed. The design already contains the guard (I4 immutability: VBR/rescue/
  backtracking cannot mutate extracted evidence or manifest identity; Item-5 deletion register).
  Plan must hold the line that the non-C19 legacy ladder stays a pure value adapter and never
  re-derives identity. Not a contradiction — the partial state is explicitly scoped and named.
- design-review-F2 [DO] Item 4 "foundation" changes one runtime result (C19 applies 80.0) inside
  an item whose I10/B4 promise is "topology unchanged except C19 + fail-closed forms," so the
  attach-but-ignore boundary (B4) and the use-for-C19 boundary (D7) meet in supplied_values. —
  epic Item 4 success criterion (nested fixture applies 80.0) + contract C19 (agent-ratified /
  INHERITED) — disposition: DISPOSE-and-proceed. In-scope and required by the epic; the design
  specifies the C19 join derives from the single manifest authority, not a fresh lookup. Watch:
  the C19 value-site join must key on complete source-identity/value-site records (design's own
  risk mitigation), never the old leaf/scope fallback.

Framing note (not a finding): the [OWNER] mission invariant — a bound parameter is never exposed
as an independently mutable input — remains VIOLATED for all non-C19 sources at the end of Item 4,
because the producer key table is deliberately left in control until the Item-5 cutover. This is
faithful to the epic's ratified evidence->authority->implementation->cutover sequencing, not a
design defect. The stage should register that the customer-visible fan-out defect persists after
Item 4 by design; C14/C26 are kept as explicit current-defect pins for Item 5 to flip.

Smells checked (design smells 2 and 7):
- Smell 2 (a consumer compensates for a producer/platform guarantee): DOES NOT FIRE against this
  design. The design moves compensation the correct direction — out of the consumer
  (supplied_values' failed string-scope tripwire) and into the producer (extraction-owned identity
  authority). Residual consumer-side compensation (the legacy ladder) is pre-existing, named, and
  scheduled for Item-5 deletion; it is not introduced here.
- Smell 7 (changes who owns an invariant without saying so): DOES NOT FIRE. The ownership transfer
  of source identity from the scattered owners (VBR stamp, SVM synthesis, backtracking fallback,
  parameter-group backfill, _find_instantiation_paths) to one SourceIdentityAuthority is stated
  explicitly (D4, I5, Non-Goals), cites invariant 60 and the adjacent-work register, and names
  _find_instantiation_paths as never consulted for identity. The identity-vs-selection split
  (authority owns identity now; legacy key table owns runtime selection until Item 5) is declared,
  not hidden.

Positive alignment (both directions checked, no owner/HARD contradiction found): D-4
[OWNER-VERBATIM] "never reinterpret a self-binding as an outer reference" is honored exactly (D8 +
Implementation Notes: self-binding is a formal-vs-referent semantic comparison, not param_name==leaf
or an outer-scope search; same-named outer features are diagnostic context only, SI_SELF_BINDING
fails closed). D-19 honored (never infer indexed form from the flattened source_path; capture
before FeatureChainExpression normalization). Invariant 55 honored (D3/I3: coordinates locate but
are excluded from identity equality/hash — the measured 40-of-75 reconstruction failure mode is
rejected as authority). Invariant 58 honored (D6: v6 bump, v5 fails closed at the existing first
gate, no shim; I9 route parity on the complete manifest). Invariant 60 honored at the identity
layer (D4: one authority, one walker). C19 obligation met (D7 + validation approach).

Gate: DISPOSED (design-review-F1, design-review-F2) — no owner/HARD contradiction; no BLOCK. Both
findings are low-grade transitional-scope watch items already mitigated within the design; neither
requires an ADR. The design faithfully discharges the Item-4 foundation slice of the point.

## audit-phase1-2 — 2026-08-07 — rev 224bfa6-dirty

Point (re-derived): Every supported binding must map one semantic source occurrence to exactly one
runtime source across all calculation, constraint, and aggregation consumers; a bound parameter
must not become an independently mutable input because of its consumer. [source:
`.project/backlog/epic_semantic_source_identity.md:111`, grade: owner/HARD]

Falsifier: The live `source_identity_mixed_consumers` C24 fixture cannot assign the calculation,
constraint, and aggregation consumers of `source_identity_computed.producer_calc.result` one equal
semantic identity, or any leg falls to a missing occurrence / independent runtime source.

Findings:
- audit-phase1-2-F1 [DO] C24's aggregation extraction drops the chain root and resolved member path,
  leaving only the calc-definition-owned leaf; `demand_from_term()` therefore raises
  `SI_OCCURRENCE_MISSING` on `computed_total` while the calculation leg identifies the source, so
  the published three-consumer source cannot enter one manifest. —
  `.project/backlog/epic_semantic_source_identity.md:111` (owner/HARD) — disposition: BLOCK
- audit-phase1-2-F2 [DON'T] `demand_from_binding()` constructs the occurrence member path from
  `authored_segments`, even though extraction defines that field as diagnostic spelling only; two
  supported spellings can therefore give one resolved referent and occurrence different semantic
  identities. — `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  invariants 55–56 (agent/ratified) — disposition: DISPOSE-and-proceed only after identity uses
  resolved structural segment evidence
- audit-phase1-2-F3 [DO] Structured aggregation scoping still runs the legacy calc-derived dotted
  path finder, renders the authority's occurrences back to strings, and joins the two by path text;
  the completed Phase-2 claim therefore retains two occurrence representations and makes identity
  attachment depend on their manual format agreement. —
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariant 60
  (agent/ratified) — disposition: DISPOSE-and-proceed only after the authority supplies the
  structured eligible occurrences directly

Smells:
- Smell 1, **two representations must be manually kept synchronized**, fires on the legacy dotted
  aggregation paths versus rendered `InstanceOccurrence.instance_path` join; it contributes to the
  blocking stage judgment rather than remaining a green equivalence check.
- Smell 4, **correctness depends on downstream knowledge of an internal representation**, fires on
  both the aggregation string join and the use of diagnostic authored segments in identity.
- Smell 6, **a test passes only because it selects one duplicate, one route, or one interpretation**,
  fires because C24 is asserted only on the calculation extraction route while calc/aggregation
  convergence is tested on C11; the actual C24 aggregation route raises `SI_OCCURRENCE_MISSING`.

Gate: BLOCKED (audit-phase1-2-F1)
