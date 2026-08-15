# Spec Brief — Lifecycle Item 10: Producer Completeness and Stellarator Rollup

**Stage:** spec
**Epic authority:** Item 10 (register row 12); ratified D-1/D-2 and invariants 19–26;
**required reading:** WI-027 spec/design/plan in
`../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/` and both
Gate B reports (epic Source Documents).

## Intent

- [INHERITED: D-1/D-2 — settled] Every model-derived consumed value resolves to ONE intended
  producer, proven independently of V11. Legitimate external typed design inputs preserved.
- The ambiguous/defaulted producer acceptance: two same-leaf candidates and a fallback/default
  shape must fail contextually or resolve only under exact QN — no guessed verdict while V11
  is clean. (Item 2's resolver already deleted the guessing behaviors — this item PROVES the
  property as its own acceptance, independent of V11's coverage.)
- Codegen compiles the stellarator's modeled cross-part capital aggregation through the SAME
  graph machinery as calculations/aggregations — no consumer mutation, no private bridge, no
  placeholder, no D7 passthrough calculations.
- WI-027 amended: supersession pointer to the later owner decision; D7 passthroughs removed;
  the stellarator generates publicly with UNCHANGED ordinary numerics (the five-constraint
  design point's ordinary values are the anchor).
- [OWNER] No LOC metrics; deletion of now-obsolete aggregation/resolver workarounds.

## Fresh ground truth (state as of Item 9 close)

- Chain: codegen 240d170, agentic-mbse 4c18d61, teax 07eb0ac, fusion-tea 2422e715.
- Stellarator repo: /home/reid/1cfe/fusion-tea-stellarator-mbse-demo at bceaf40a with the
  UNCOMMITTED Item 3 Gate B filing (two files). First action in that repo: commit that filing
  as its own commit (it is ratified record; Item 3's evidence names it) BEFORE any Item 10
  work dirties the tree.
- Item 2 landed the unified resolver (exact-QN, guesses deleted); Item 4 the written-qualifier
  carry; Item 8 the catalog authority. The stellarator's private bridge predates all of it —
  inventory what the bridge still compensates for at TODAY's chain before specifying.
- Gate A (usage-owned constraint actuals) works since Item 2 — the stellarator's five
  constraints may already be closer to public generation than WI-027's record assumes. Measure.

## Out of scope (firewall)

Public late fill or a permanent model placeholder; weakening exact-QN, final V11, or declared
external-input semantics; IFE work (done); Item 11 evidence semantics.

## Spec shape

Provenance-graded; the ambiguous/defaulted counterexample as a RED-first public coordinate
(the epic's de-risk note: drive it BEFORE the rollup); the stellarator inventory (what the
bridge/passthroughs still do, measured at the current chain); acceptance = public generation
+ five verdicts + unchanged ordinary numerical anchors (name them from WI-027); deletion
inventory; cross-repo phasing.
