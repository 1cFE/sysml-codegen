# Design Review: Semantic Identity and Occurrence Foundation (SOURCE-IDENTITY Item 4)

**Design:** `.project/active/source-identity-occurrence-foundation/design.md`
**Spec:** `.project/active/source-identity-occurrence-foundation/spec.md`
**Review File:** `.project/active/source-identity-occurrence-foundation/design-review.md`
**Date:** 2026-08-07

---

## The Point

One semantic source occurrence must become exactly one runtime source across all of its
calculation, constraint, and aggregation consumers: one public input for an externally supplied
value or one producer channel for a computed value. Today the pipeline loses that identity before
resolution — 40 of 75 measured model-derived cells mint a consumer-local public input instead of
converging, and a nested `:>>` override's modeled `80.0` is silently lost to both its consumers.
Item 4 is the foundation slice: make the runtime source derivable from the modeled declaration
plus its concrete occurrence before any consumer selects a source, on both live and snapshot
routes, without inventing identity from a consumer's owner, parameter name, written leaf, or
current value. The resolver cutover that makes consumers converge is Item 5, by ratified
sequencing. Source: epic `[OWNER]` mission invariant; lifecycle contract invariants 54–60.

## Fundamental Assessment

**Sound.** This is the right piece of work and the right approach.

- **Right piece of work.** The design implements exactly the Item-4 scope the epic and ratified
  contract assign: extraction-owned identity, one occurrence authority, snapshot v6 transport,
  the absorbed C19 repair, and the assigned authoring diagnostics — with the Item-5 cutover
  explicitly left out. The product-lens re-derived the point independently from the epic and
  contract and it matches the design's own "The Point" at owner grade. Gate: **DISPOSED** (two
  low-grade transitional-scope watch items, both already mitigated inside the design; ledger
  block `design-review — 2026-08-07` in `product-lens.md`).
- **Neither design smell fires.** Smell 2 (consumer compensating for a producer guarantee): the
  design moves compensation the correct direction — out of `supplied_values`' string-scope
  heuristic and into the extraction-owned authority. Smell 7 (ownership change unstated): the
  transfer of identity ownership to one `SourceIdentityAuthority` is stated explicitly (D4, I5,
  Non-Goals) and cites invariant 60.
- **The complexity matches the problem.** The manifest/authority/typed-coordinate machinery is
  not invented ambition — it is what contract invariants 55 (extraction-owned identity), 58
  (versioned route parity), and 60 (one authority, one bridge) jointly require, plus immutability
  against the documented VBR-mutation failure mechanism. The genuinely simpler alternatives
  (per-route fields, additive optional v5 field, string paths) are each named and rejected for
  reasons that held up under checking.
- **The factual base held.** Every code citation in Research Findings verified against the code
  (one nuance recorded under Dimension 1). The load-bearing reuse claims are true:
  `PartInstanceIndex` has the structured/frozen/fail-closed behavior claimed, constraint
  preparation already consumes an `occurrences_of` protocol the authority can implement as a
  drop-in, `resolve_producer` has exactly the five call sites claimed, and the v6 bump follows
  the repo's documented v2→v5 "real version bump with a load-time shape gate" convention.

One framing note the lens asked the stage to carry (not a defect): **the customer-visible
fan-out defect persists after Item 4 by design.** The producer key table stays in control until
Item 5; C14/C26 stay pinned as current defects. Anyone reading Item-4 completion as "the bug is
fixed" would be wrong — the design says this plainly (I10, Non-Goals), and the plan should too.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Pass

Every success criterion and SIF requirement maps to a design element; I traced all of them:

- SC 1–2 (identity at the pre-resolution boundary, from extraction evidence, fail-closed) → D1,
  D3, D8, producer-boundary threading.
- SC 3 / SIF-07 (C19 `80.0` on both paths, tripwire silent, flat sibling preserved) → D7 and the
  C19 acceptance bullets; matches the contract's C19 cell exactly (referent, value_state 80.0,
  calc + constraint consumers).
- SC 4 / SIF-05/08 (C8 distinctness, C9/C10 ambiguity, atomic cycle/cardinality failures) → D5,
  I6, I7.
- SC 5 / SIF-11 (Appendix C coordinates) → the Validation Approach covers every assigned cell:
  C8, C9–C13, C15, C18–C21, C24, C25, 22a, C17 control, and C14/C26 as canonical identity plus
  explicit current-defect pins — precisely the spec's ratified Item-4/Item-5 seam.
- SC 6 / SIF-09/10 (v6, atomic 37-snapshot recapture, v5 fail-closed, in-place vs relocated
  parity) → D6, Implementation Notes, I9. The "exactly 37" count verified.
- SC 7 / SIF-06 (one bridge, no parallel walker *introduced*) → D4, I5 — the design uses the
  spec's corrected "introduced" phrasing, not the end-state phrasing the spec review fixed.
- SC 8 / SIF-12/13/14 (both diagnostics legs; oracle tests replaced, not deleted/xfailed) → D8,
  D9, and the extraction/readiness test bullets including the same-named-outer negative control.
- SC 9 / SIF-16 (recapture review; independent phasing of the agentic-mbse leg) → Recapture
  review bullets; Integration Strategy step 1.
- SC 10 (baselines unchanged unless reviewed) → Regression gates and Risk 4 mitigation.

Provenance carried faithfully: The Point is graded `[OWNER]` with its source; the design treats
the ratified `[AGENT]` items (atomic recapture, independent phasing) as fixed constraints with
their ratification recorded in the spec, and hardens no owner example. The owner's `80.0`
referent survives verbatim.

One accuracy nuance from verification (no direction change): Research Findings says `BindingInfo`
"keeps only mutable path/name hints" — it also carries two AST element fields
(`source_instance_elem`/`source_attribute_elem`, `usage_extractor.py:77`). The true and
load-bearing part of the claim stands: the type is mutable, deep chains lose middle-segment ASTs,
and the indexed first operand is silently dropped. Also `loader.py:684` cites the function head;
the version gate itself is at `loader.py:722-736`.

### 2. Pattern Consistency
**Assessment:** Pass

- Immutable frozen dataclasses are the established idiom across `resolution/` and `analysis/`
  (`ProducerRequest`, `PathStep`, `InstanceOccurrence`, `PreparedConstraintBatch`); D1's
  immutable value types follow it.
- A new focused module under `analysis/` matches the directory's structure;
  `part_instance_index.py` and `source_referent.py` are direct precedents for an
  authority/identity module.
- D6's version bump follows the repo's own documented convention ("a real version bump with a
  load-time shape gate — not an in-place edit", `snapshot/__init__.py:22-29`; v2→v5 precedent at
  commit 936315c) and the loader already has per-section shape gates to extend.
- Deterministic sorted serialization already exists (`serializer.py:124`, `:217-219`); the
  manifest's sorted-records requirement extends it rather than inventing a scheme.
- The authority implementing the existing `OccurrenceIndex` protocol
  (`part_instance_index.py:425-432`) makes it a drop-in for constraint preparation, which already
  consumes `occurrences_of` (`constraint_lowering.py:323`) — no new pattern needed at that seam.

### 3. Abstraction Quality
**Assessment:** Pass

Each new abstraction earns its existence:

- `SemanticSourceIdentity` (declaration + occurrence, coordinates excluded from equality) is the
  contract's identity definition made into a type; removing it re-creates the string-tuple
  identity the epic exists to kill.
- `SourceIdentityAuthority` is the invariant-60 requirement reified; without it, identity
  projection would scatter across the three consumer routes — the exact rejected D2 shape.
- The manifest gives snapshot transport and route-parity testing one comparable object; without
  it, I9 has nothing to compare.
- Responsibilities are cleanly cut: the authority "does not know channels, entry points, or
  resolver policy" keeps it out of Item 5's territory.

### 4. Duplication Avoidance
**Assessment:** Pass

The design is aggressively anti-duplication where it matters: one manifest not three ledgers
(D2), one walker (I5, `_find_instantiation_paths` named and banned for identity — and
`part_instance_index.py:196-202` already documents itself as the structured sibling that must
not call it), one union transcript instead of a constraint-only transcript plus a second table
(D4). The aggregation-scoping reroute replaces the calc-derived dotted-path derivation
(`pipeline_builder.py:692` via `find_instance_paths_for_partdef`) rather than paralleling it.
One watch item on that reroute is recorded under Dimension 7 (it is a live-path change, not an
attach-only change).

### 5. Data Structure Clarity
**Assessment:** Concerns

The identity side is explicit and well-typed (D1, D3, typed coordinates with duplicate
rejection). Two gaps:

- **"Value site" is load-bearing but never specified.** The manifest's second record kind
  ("modeled value sites", D2), the D3 coordinate list ("a captured value site"), the entire D7
  C19 join, and Risk 6's multiplicity semantics ("if the value site is zero, multiple, or
  disagrees across demand contexts") all depend on it — yet the design never says what a value
  site *is* (a definition default? an occurrence `:>>` override site? a usage literal?), what
  identifies one, or what its record carries. The term is design-coined: it appears nowhere in
  the contract or spec. A plan agent could build two different things from this. One paragraph
  defining the value-site record (kinds, identifying coordinate, fields, relation to the
  contract's `value_state` vocabulary) closes it.
- **The transcript's sealing point is ambiguous.** D4 says the authority "publishes the
  successful union query transcript only after finalization succeeds," but the Implementation
  Notes' ordering has supplied-value enrichment (where the C19 adapter queries) and constraint
  resolution running *after* finalization — and Risk 3's mitigation says the transcript records
  queries from "scoping, identity, value repair, or constraint preparation." Both cannot hold
  unless the transcript stays open past finalization and is sealed at capture time. One sentence
  stating when the transcript is sealed relative to those consumers removes a contradiction the
  plan would otherwise have to guess through.

### 6. Route Safety
**Assessment:** Pass

Read as pipeline-route behavior: the v5 rejection reuses the existing first gate (verified
pattern at `loader.py:722-736`), the frozen index fails closed on an absent queried owner
(verified, `part_instance_index.py:453-460`), D8 enumerates named machine-checkable failure
codes instead of warn-and-continue, and D6 explicitly rejects the silent-compatibility fallback.
No wildcard or reconstruct-on-miss behavior anywhere.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B4 are genuine bets, each with an honest "if false → stop/extend/review" consequence, and
D1–D9 each name their rejected alternative with a real reason. Two load-bearing beliefs are
**not** stated as bets:

- **Hidden bet: live records every occurrence query replay will make.** Replay answers
  constraint-preparation and C19 value-adaptation queries from the frozen union transcript, and
  the frozen index *raises* on an absent owner. That is only safe if the live pipeline's recorded
  query set is a superset of replay's — i.e., the query sequence is deterministic across routes.
  Probably true (replay runs the same deterministic code), but if false, valid snapshots fail
  closed at replay with `SI_SNAPSHOT_CORRUPT`-shaped errors. Risk 3 covers the opposite failure
  (transcript too big), not this one. State it as a bet or invariant, with the live/replay
  query-set parity test that retires it.
- **Hidden behavioral expansion: the index is built for every model.** Today the live pipeline
  builds `PartInstanceIndex` only when constraints exist (verified, `pipeline_builder.py:977`).
  The Architecture builds the authority "once after model load" unconditionally. Consequence: a
  constraint-free model with recursive containment or non-finite multiplicity that generates
  today will now abort atomically (I6). That is consistent with SIF-08 and arguably is
  "fail-closed readiness behavior" under I10 — but it is a runtime-result change beyond C19 that
  the design never names. One sentence claiming it under I10's fail-closed clause (plus the index
  cost on constraint-free models) makes the I10 boundary honest.

Also carried from the product-lens (both DISPOSE-and-proceed, already mitigated in-design):
transitional dual-liveness in `supplied_values.py` until Item 5 (design-review-F1), and the
C19 attach-vs-use boundary meeting in that same file (design-review-F2) — the plan must keep the
non-C19 ladder a pure value adapter and key the C19 join only on complete manifest records.

### 8. Reader Comprehension
**Assessment:** Concerns (one term)

The design reads well for its difficulty: The Point is plain and first, Core Concept gives the
mental model ("a fact produced once, not a successful lookup") before mechanism, Research
Findings pair each claim with its citation, and the ASCII diagram carries the shape. "Union
transcript" is decodable from D4 in one read. The one genuine comprehension blocker is the same
"value site" gap recorded under Dimension 5 — a load-bearing coined term with no definition
anywhere in the document or its authority chain. Fixing that fixes this dimension.

---

## Issues by Severity

### Critical
- None.

### Major
- **Undefined "value site" record**: the manifest's second record kind, the D7 C19 join, and
  Risk 6 all depend on a design-coined term with no definition, coordinate, or field shape —
  Data Structure Clarity / Reader Comprehension.
- **Unstated replay-query-coverage bet + ambiguous transcript sealing point**: replay fails
  closed on any query live didn't record, and D4's "publishes after finalization" contradicts
  post-finalization value-repair/constraint queries being in the transcript — Bets & Decisions /
  Data Structure Clarity.

### Minor
- **Unconditional index construction is a runtime-behavior expansion**: cycle/non-finite
  failures (and index cost) newly reach constraint-free models; claim it explicitly under I10's
  fail-closed clause — Bets & Decisions.
- **Aggregation-scoping reroute is a live-path change**: replacing calc-derived dotted paths
  with structured occurrences must reproduce today's scoped output; Risk 4's baseline gate
  catches drift but the design doesn't say why the output stays identical — Duplication
  Avoidance / Bets.
- **Two citation nuances**: `BindingInfo` also carries two AST element fields (the "only
  path/name hints" phrasing overstates); the loader version gate is at `loader.py:722-736`, not
  `:684` — Spec Compliance (accuracy note only).

---

## Recommendations

1. Define the value-site record: the kinds it covers (definition default, occurrence `:>>`
   override, usage literal), its identifying coordinate, its fields, and its relation to the
   contract's `value_state` vocabulary. One paragraph in D2 or Architecture.
2. State the transcript sealing point (open through supplied-value repair and constraint
   resolution, sealed at capture) and add the live/replay query-set parity claim as a bet or
   invariant with a named test in the Validation Approach.
3. Add one sentence claiming the unconditional index build under I10's fail-closed clause, so
   the "only C19 and fail-closed readiness may change runtime results" boundary is honest.
4. Add one sentence on why the aggregation-scoping reroute preserves current scoped output (or
   explicitly route any diff into the Risk-4 baseline review).
5. (Optional, cosmetic) Soften the `BindingInfo` "only path/name hints" phrasing and fix the
   loader line citation.

---

## Resolutions

The review recommendations remain agent-grade. The owner ratified their incorporation on
2026-08-07.

- **[AGENT] (ratified by owner, 2026-08-07) Major — undefined value site: incorporated.** D2 now
  defines the three modeled value-site kinds, their typed coordinate, their manifest fields, and the
  join back to extraction-owned values and provenance. D7/D8 name the zero/multiple join failures.
- **[AGENT] (ratified by owner, 2026-08-07) Major — replay coverage and transcript sealing:
  incorporated.** B5 states the load-bearing coverage bet. D4 separates manifest finalization from
  transcript sealing and keeps the recorder open through every live query-producing phase. I10 and
  the snapshot validation require overall replay-subset coverage plus exact equality for phases shared
  by live and replay.
- **[AGENT] (ratified by owner, 2026-08-07) Minor — unconditional occurrence authority:
  incorporated.** Architecture and I11 now claim the indexing cost and the intended fail-closed
  result when source identity queries cyclic or non-finite structure in a constraint-free model.
- **[AGENT] (ratified by owner, 2026-08-07) Minor — aggregation-scoping equivalence:
  incorporated.** The design keeps the existing extracted-calc-usage eligibility boundary, changes
  only the path authority, and adds an exact scoped-record equivalence test.
- **[AGENT] (ratified by owner, 2026-08-07) Minor — citation accuracy: incorporated.** The
  `BindingInfo` finding now acknowledges its two live AST pointers, and the loader version-gate cite
  points to `loader.py:722-736`.
- **[AGENT] (ratified by owner, 2026-08-07) Carry-forward boundary: incorporated.** The handoff now
  states that Item 4 does not fix the customer-visible fan-out defect: the legacy key table remains
  in control until Item 5, and C14/C26 remain current-defect pins.

---

**Overall:** Resolved — the Revise findings are incorporated in `design.md`.
**Next Steps:** The owner advanced the revised design to planning on 2026-08-07. The fundamental
approach needs no re-review unless a later change alters an invariant or decision.
