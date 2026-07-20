# Spec: Lifecycle Remediation Item 2 — Shared Producer Resolution and Gate A

**Status:** Implementation In Progress — phase group 1 complete (Phases 0, 2, D9 de-risk pins)
**Owner:** Reid W
**Created:** 2026-07-19
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 2, register row 2
**RED predecessor:** sysml-codegen `287afc47ab06826de27c38e203ffffb45398f972` (Item 1 certified),
agentic-mbse `515e08bbcd70aa9d23212765161bd02b3e3d8f23`,
TEAx `d545701f575133350474108c96202a2ac5244462`

---

## Surfaced premise conflict (read before design)

**[OWNER] vs [INHERITED] — unresolved in the epic text.** Epic Item 2 scope point 5 still reads
"target the adversarial review's estimated 300–500 line reduction"
(`.project/backlog/epic_constraint_execution_lifecycle_remediation.md:339`). The owner retired every
numeric LOC gate epic-wide on 2026-07-19 (epic commit `a1435e1`; contract Simplification constraint;
LC-I08: "Do not create or require LOC baselines, budgets, per-file caps, net-negative targets,
counting tools, or code-growth deviation reviews").

This spec follows the owner correction: **no LOC target, budget, or gate appears anywhere below.**
Simplification is judged structurally per SR-R40. The stale epic line should be amended when the
owner next touches the epic. No dependent conclusion in this spec rests on it.

---

## Problem

Three independently ordered resolvers answer the same question — *which real thing produces this
consumed value?* — and they have already drifted apart in ordering, in candidate identification, and
in what they do when nothing matches.

- **The calculation ladder** (`analysis/dependency_backtracker.py:562-744`, design-attribute tail at
  `:756-857`) has scope-climb, self-reference rejection, and structured-alias rungs the others lack.
  Its terminal miss is lenient: `terminal_disposition(..., strict=False)`
  (`dependency_backtracker.py:38-77`) invents the entry-point QN `{usage_qn}__{param}` and logs at
  DEBUG for most shapes. Worse, before it ever gets there, its bare-name design-attribute arm
  (`:823-855`) resolves an **ambiguous first-pick** — it logs "Ambiguous design attribute" and
  returns `candidates[0]`.
- **The constraint ladder** (`analysis/constraint_lowering.py:143-301`) has a base-def default rung
  the calculation ladder lacks, no self-reference guard, and no scope climb. Its terminal miss is
  strict: `terminal_disposition(..., strict=True)` raises.
- **The aggregation ladder** (`resolution/input_resolver.py:228-290` driving four strategies, choke
  point `resolution/graph_builder.py:1271-1351`) identifies candidates by **case-insensitive leaf
  name** (`input_resolver.py:176-177`; `graph_builder.py:1246-1248`). On a leaf collision it warns
  and returns the first value anyway (`graph_builder.py:1258-1266`). It never raises; on a miss it
  mints an entry point at DEBUG, then a second writer registers or **backfills a default onto an
  already-created `EntryPoint`** (`graph_builder.py:1326-1345`), and the LocalTerm path
  (`:1490-1533`) invents a `DESIGN_ATTRIBUTE` entry point with no default and no warning at all.

Two consequences make this a lifecycle defect rather than tidy-up debt.

**Gate A does not work.** A literal-valued design attribute owned by a concrete `PartUsage` is a
valid constraint actual under owner decision D-2, and today it does not resolve. The stellarator
consumer worked around it with passthrough calculations, which D-2 supersedes. The one inline
fixture that looks like it covers this (`tests/fixtures/constraint_inline/model.sysml:16-21`)
declares the attribute on the **part def**, so it certifies a weaker shape than the real failure.

**A green V11 does not mean the graph is right.** Contract invariant 26 states this directly: a
defaulted fallback or ambiguous first-match binding passes V11. Every one of the leniency seams
above produces exactly that — a plausible verdict from a guessed binding, with the graph reporting
clean.

## Success Criteria

- [ ] **[NEED]** One production resolver serves calculation, aggregation, and constraint consumers;
      the three consumer-specific ladders no longer exist. Source: owner-ratified contract invariant
      20 ("Positive resolution may not fork into consumer-specific ladders") and register row 2.
- [ ] **[NEED]** A direct literal design attribute owned by a concrete `PartUsage`, referenced by a
      self-named actual, resolves under its real qualified name with no passthrough calculation, on
      the public live route. Source: owner D-2, 2026-07-19 (quoted at LC-D08).
- [ ] **[NEED]** No verdict is ever produced from a guessed or defaulted binding while V11 is clean:
      an ambiguous or unresolved constraint actual fails generation contextually, and lenient
      calculation behavior never resolves by leaf-name guess or ambiguous first-pick. Source:
      contract invariant 26 and the "Ambiguous/defaulted producer resolution" acceptance row.
- [ ] **[NEED]** The superseded mechanisms are deleted rather than shimmed — no wrapper, flag,
      compatibility alias, or parallel resolver survives. Source: owner simplification constraint,
      2026-07-19, as corrected (structural judgement, no line counts).

## Known Requirements

### A. Scope and authority

- **SR-R01 [INHERITED]** Calculation inputs and constraint actuals use one shared positive-resolution
  procedure: a real producer channel first, then a real design attribute under its exact qualified
  identity. Source: contract invariant 19, LC-D06.
- **SR-R02 [INHERITED]** Strictness changes only the terminal miss policy. Constraint resolution
  never invents a value, parses display text, or reaches the calculation fallback. Source: contract
  invariant 20, LC-D07.
- **SR-R03 [INHERITED]** A direct literal-valued design attribute is a valid actual. It must be
  available during graph construction and must reuse the same QN-keyed typed entry point as any
  calculation consumer. Requiring a passthrough calculation is a workaround, not conformance.
  Source: contract invariant 21, LC-D08, owner D-2.
- **SR-R04 [INHERITED]** Modeled defaults remain overridable typed parameters and never become study
  variables automatically. An omitted constraint formal accepts a modeled default only when the
  model declares it. Source: contract invariants 19 and 22, LC-D09.
- **SR-R05 [INHERITED]** No late-fill, leaf-name guess, ambiguous first-pick, or post-build
  graph/default mutation seam is supported. Source: contract invariant 26, owner D-1.
- **SR-R06 [INHERITED]** Item 2 builds on the Item 1 seams and does not rework them:
  `prepare_constraint_usages` / `PreparedConstraintBatch`
  (`analysis/constraint_lowering.py:706-789`), and `resolve_logical_demand` / `select_group_source` /
  `enrich_graph_design_attributes` (`resolution/supplied_values.py:330-600`). Item 1's recorded
  deviations are facts on the ground — notably `ResolvedDemand` has four fields
  (`supplied_values.py:158-175`) and provenance selection is call-site policy (Item 1 evidence.md §6
  deviation 2). Source: Item 2 stage brief; Item 1 certified at `287afc4`.
- **SR-R07 [INHERITED]** Item 3 owns the Gate B coverage-scope decision; Item 4 owns diagnostic
  severity schema and default fidelity, including the Item 1 audit's tier-2 disposition asymmetry;
  Item 5 owns relocated whole-tree portability. Source: epic Items 3–5 and the Item 2 stage brief.
- **SR-R08 [INFERRED]** Item 2's relocated Gate A leg uses the same-checkout replay route as
  regression evidence only, explicitly labeled non-certifying, if full relocation is not yet
  available. Basis: LC-I09 defines the certifying snapshot route as relocated replay; Item 5 owns it.
  This mirrors Item 1's OD-R08 disposition.

### B. The one resolution procedure

- **SR-R10 [INFERRED]** There is exactly one typed resolution request and one typed resolution
  result. Every consumer — calculation binding, constraint actual, and aggregation term — constructs
  the request and reads the result. Consumer identity enters the request as declared data (at
  minimum: consuming module/usage identity, the reference as written, the consumer's scope, and the
  terminal-miss policy), never as a separate code path. Basis: contract invariant 20's
  no-consumer-ladders rule; `[CONSTRAINT-ARCH-UNIFY]` scope item 2
  (`.project/backlog/BACKLOG.md:815-820`).
- **SR-R11 [INFERRED]** The ladder is one ordered, declared sequence of rungs, in this order:
  1. a real producer channel that already exists in the graph's canonical channel set;
  2. a real design attribute matched under exact qualified identity.

  Every rung is declared in one place, in order, and the order is observable in a test. A consumer
  may not add, reorder, or skip a rung. Basis: contract invariant 19 states the two positive tiers;
  the ordering-in-one-place rule is the mechanism that makes drift detectable.
- **SR-R12 [INFERRED]** No rung resolves by leaf name, case-insensitive name, suffix match, or
  arbitrary first-pick among multiple candidates. Where more than one candidate satisfies a rung
  under non-exact identity, the rung produces no result rather than a guess. Basis: contract
  invariant 26; the offending sites are named in SR-R41.
- **SR-R13 [INFERRED]** The self-reference guard applies uniformly: a rung may not resolve a
  consumer's input to a channel produced by that same consumer. Today this guard exists on the
  calculation ladder (`dependency_backtracker.py:745-755`) and the aggregation driver
  (`input_resolver.py:263-271`) but not on the constraint ladder. Basis: a self-producing input is a
  cycle in every consumer's graph; the asymmetry is drift, not intent.
- **SR-R14 [INHERITED]** Terminal miss is the only place strict and lenient differ.
  - **Strict** (constraint actuals) raises a contextual generation error naming the usage, the
    formal, the actual as written, and the resolution classes attempted. It synthesizes nothing.
  - **Lenient** (calculation inputs, aggregation terms) yields an ordinary declared typed entry
    point under a deterministic QN.

  Source: LC-D07, contract invariant 20. The existing shared switch
  (`dependency_backtracker.py:38-77`) is the surviving seam; the constraint error text at
  `constraint_lowering.py:292-301` is the surviving strict shape.
- **SR-R15 [INFERRED]** A lenient terminal miss is visible. It emits a diagnostic at a severity a
  build log actually shows, uniformly for every consumer. Today calculation multi-hop chains warn
  while every other lenient miss logs at DEBUG (`dependency_backtracker.py:614-639`;
  `input_resolver.py:277-290`), and the aggregation LocalTerm fallback emits nothing at all
  (`graph_builder.py:1517-1533`). Exact severity vocabulary and codes are Item 4's; Item 2 owes
  uniform visibility, not a schema. Basis: contract invariant 26's "no silent" posture and the Item
  4 boundary in SR-R07.
- **SR-R16 [INFERRED]** An entry point minted by a terminal miss is created once, with its modeled
  default resolved at creation. No second writer registers a duplicate or backfills a default onto
  an entry point created earlier. The register/backfill pair at `graph_builder.py:1326-1345` and the
  silent LocalTerm mint at `:1517-1533` are the seams this retires. Basis: owner D-1 (no post-build
  graph/default mutation) and contract invariant 26.
- **SR-R17 [INFERRED]** Modeled-default discovery uses exact owning-definition identity. The exact
  tier already exists (`graph_builder.py:1226-1244`, keyed on `usage_type_map`); the leaf-name
  Strategy 2 and its warn-and-return-anyway collision arm (`:1246-1266`) do not survive SR-R12. A
  formal with no modeled default and no resolution reaches the terminal-miss policy for its
  consumer — it does not acquire an invented default. Basis: SR-R04 and contract invariant 22.

### C. Gate A

- **SR-R20 [NEED]** A literal-valued design attribute declared on a concrete `PartUsage` and
  referenced by a self-named actual resolves through the shared design-attribute rung under its real
  qualified name, on the public live route, with no passthrough calculation in the model. Source:
  owner D-2, quoted in LC-D08: "100% Option A. I am BLOW AWAY this wasn't already a requirement and
  this is a design gap. That is the whole fucking ethos of the graph-building."
- **SR-R21 [INFERRED]** The Gate A fixture pins the real failure shape, not a weaker equivalent: the
  attribute is **usage-owned** on a concrete `PartUsage` (not declared on the part def) and the
  actual is **self-named**. `tests/fixtures/constraint_inline/model.sysml:16-21` is def-owned and
  therefore does not certify Gate A. Basis: correction re-review edit E11
  (`.project/research/20260719-134700_...-correction-rereview.md:99-104`), which names exactly this
  substitution risk.
- **SR-R22 [INFERRED]** The value the Gate A attribute carries reaches generated execution and moves
  the verdict. Certification observes a real evaluated verdict, not only that resolution returned a
  non-null channel or entry point. Basis: Item 1's OD-R35 lesson — distinct wrappers can hide a
  collapsed value.
- **SR-R23 [INFERRED]** Gate A resolution produces the same QN-keyed typed entry point a calculation
  consumer of the same attribute would get. Two consumers of one attribute converge on one entry
  point; they do not mint two. Basis: contract invariant 21's "same QN-keyed typed entry point".

### D. Preservation and parity

- **SR-R30 [INHERITED]** Live and supported snapshot routes agree on decisions, diagnostics, retained
  producers, graph/catalog values, fingerprints, and generated bytes. Source: contract invariant 35.
- **SR-R31 [INFERRED]** Existing generated output is byte-identical across the change except where a
  named requirement above forces a difference. Every forced difference is enumerated with the
  requirement that causes it, before the baselines are regenerated. Generated baselines under
  `tests/fixtures/baseline_outputs/` are generator-owned bytes and are never hand-edited or
  reformatted. Basis: the standing byte-identity gate and the format-exemption rule for generated
  fixtures.
- **SR-R32 [INFERRED]** Item 1's public acceptance file and fixtures are frozen controls. Item 2
  neither modifies them nor re-anchors their SHA-256. Basis: Item 2 stage brief; Item 1's Phase 0
  overlay digest is its RED/GREEN anchor (Item 1 evidence.md §6 deviation 10).
- **SR-R33 [INFERRED]** The precedence pins in `tests/unit/test_constraint_resolver.py:283-420` state
  the constraint ladder's current conflict ordering. They are the migration's protection: each pin
  either survives unchanged, or its change is recorded as an intended precedence correction with the
  requirement that forces it. A pin is never deleted merely because the code it pinned moved. Basis:
  `[CONSTRAINT-ARCH-UNIFY]` scope item 2 names these pins as the migration guard.
- **SR-R34 [INFERRED]** The affected regression union includes constraint lowering and resolution,
  dependency backtracking, aggregation and input resolution, entry-point classification, parameter
  groups, graph building, snapshot parity and portability, generated-output byte identity, and real
  generated execution. Compatible full and licensed public-live suites run at one candidate
  coordinate. Basis: the changed surfaces named in SR-R41 and LC-I05.

### E. Deletion and simplification

- **SR-R40 [INHERITED]** Named superseded mechanisms are removed rather than shimmed; no duplicate
  authority or parallel route remains. Simplification is judged structurally — one authority, no
  duplicate route, no new shim around a superseded mechanism. Line counts are not proof. Source:
  owner simplification constraint as corrected 2026-07-19 (contract), LC-I08.
- **SR-R41 [INFERRED]** These specific production paths are deleted, not wrapped:
  1. the calculation ladder's own ordering and dispatch —
     `_resolve_binding_via_registry`, `_resolve_chain_dispatch`, `_resolve_reference_dispatch`,
     `_resolve_reference_via_registry` (`dependency_backtracker.py:519-744`);
  2. the calculation ambiguous-first-pick design-attribute arm
     (`dependency_backtracker.py:823-855`) and the leaf-unique fallback at `:787-802`;
  3. the constraint ladder's own ordering — `resolve_actual`'s rung sequence
     (`constraint_lowering.py:143-301`), keeping its strict terminal disposition and its error
     context;
  4. the aggregation strategy chain as a separate algorithm — `AGG_STRATEGIES` and `resolve_input`
     (`input_resolver.py:228-290`), including `ChainRedefinitionFollow`'s case-insensitive leaf match
     (`:176-177`);
  5. `_find_literal_redefinition`'s Strategy 2 leaf-name tier and its warn-and-guess collision arm
     (`graph_builder.py:1246-1266`);
  6. the entry-point register/backfill pair (`graph_builder.py:1326-1345`) and the silent LocalTerm
     mint (`:1490-1533`).

  Basis: each is a rung or terminal behavior that SR-R11–SR-R17 replace. A path retained for a
  reason discovered in design is recorded as a deviation with that reason, not silently kept.
- **SR-R42 [INFERRED]** String-surgery helpers that exist only to serve a deleted ladder go with it.
  The candidates are `_consumer_scope_dotted`, `_get_parent_part_for_usage`, `_is_calc_def_owned`
  (`dependency_backtracker.py:486-507, 858-877`) and, on the constraint side, whichever of
  `occurrence_scope` / `_deindexed_scope` / `_reference_dotted`
  (`constraint_lowering.py:103-140`) the one procedure no longer needs. Helpers with a surviving
  consumer stay; design names which. Basis: SR-R40's no-orphan-shim rule.
- **SR-R43 [INFERRED]** Tests that exist only to pin a deleted ladder's private behavior are deleted
  with it, subject to SR-R33. Coverage of an *observable* behavior migrates to the one procedure; it
  is not dropped. Basis: register row 2's "duplicate tests/helpers are deleted".
- **SR-R44 [INFERRED]** Load-bearing docstrings and comments describing the three ladders are amended
  or deleted, not supplemented with prohibition prose about the removed behavior. Basis:
  capture-fidelity correction law.

### F. Evidence discipline

- **SR-R50 [INFERRED]** New defect-specific tests are authored once and run unchanged at the SR-R51
  RED coordinate and at the candidate GREEN, with no baseline/candidate conditional. RED must fail
  for the intended defect; a setup, license, import, or unrelated assertion failure does not count.
  Basis: Item 1's OD-A11 discipline, which the stage brief names as the template.
- **SR-R51 [INFERRED]** The RED coordinate is the Item 1 certified candidate recorded in this spec's
  header. Item 1's own tests are green there by construction; Item 2's RED comes only from its new
  nodes. Basis: epic dependency (Item 2 depends on Item 1) and Item 1 evidence.md header.
- **SR-R52 [INFERRED]** Every acceptance row below records its LC-I09 evidence coordinate: revision
  and lock set, fixture ID, owner kind, source form, polarity, anonymity, actual presence and source,
  occurrence/override shape, open predecessor rows, and route. Same-checkout replay is labeled
  non-certifying per SR-R08. Source: LC-I09.

## Mandatory Acceptance Cases

Requirements above are the single normative decision home. Each row is an `[INFERRED]` proof
instrument citing the requirements it tests; it creates no second grade or precedence rule.

| ID | Governing requirements | Case and required observation |
|---|---|---|
| SR-A01 | SR-R20–SR-R23 | **Gate A.** Public live source: a literal-valued attribute declared on a concrete `PartUsage` (not on its part def), referenced by a self-named constraint actual, with no passthrough calculation anywhere in the model. Generation succeeds, the attribute resolves under its real QN, and generated TEAx execution returns the pinned verdict. Changing the literal changes the verdict. |
| SR-A02 | SR-R23 | The same usage-owned attribute consumed by both a constraint actual and a calculation input yields **one** QN-keyed typed entry point, not two, with one modeled default and one group assignment. **NOT DELIVERED BY ITEM 2 — referred to Item 4** (design PC-4): the calculation consumer cannot express the reference as written, so it cannot reach the shared design-attribute key form. Pinned as a recorded known-incomplete state by `tests/fixtures/shared_producer/`. |
| SR-A03 | SR-R11, SR-R33 | Resolver precedence is observable in one place. A fixture where a producer channel and an exact-QN design attribute both match resolves to the channel. Every surviving pin in `tests/unit/test_constraint_resolver.py:283-420` passes, or its change is listed with the requirement that forced it. |
| SR-A04 | SR-R12, SR-R14 | **Ambiguity fails, it does not guess.** A model with two same-leaf candidate design attributes under different owners: the constraint consumer fails generation with a named ambiguity/producer error carrying usage, formal, actual, and attempted classes; the calculation consumer does not silently bind one of them. Under exact QN the same model resolves. No verdict is produced from a guessed binding while V11 is clean. |
| SR-A05 | SR-R12, SR-R17 | Aggregation over a part whose leaf name collides with an unrelated PartDef leaf resolves by exact owning-definition identity or not at all. The pre-change warn-and-return-first-value behavior (`graph_builder.py:1258-1266`) is unreachable. |
| SR-A06 | SR-R14, SR-R15 | Terminal-miss policy is the only fork. One fixture reference, unresolvable, observed from a constraint consumer (strict: contextual raise, nothing synthesized) and from a calculation consumer (lenient: one deterministic typed entry point plus a visible diagnostic). Both use the same resolution request shape. |
| SR-A07 | SR-R16, SR-R05 | An entry point minted by a lenient terminal miss is written once. Mutating or re-registering it after graph construction has no supported seam: the register/backfill pair is absent from the tree and the LocalTerm path emits a visible diagnostic rather than a silent defaultless entry point. |
| SR-A08 | SR-R04, SR-R17 | A constraint formal omitted from the actual bindings takes a modeled default **only** when the model declares it, and an override changes the verdict. A formal with no modeled default reaches strict terminal miss rather than acquiring one. |
| SR-A09 | SR-R13 | A consumer whose reference resolves, by name, to its own output channel is refused on every route — calculation, constraint, and aggregation — rather than resolving on the constraint route only. |
| SR-A10 | SR-R30, SR-R31, SR-R08 | Live and same-checkout replay of the Gate A fixture agree on resolved producer, entry-point identity and default, catalog values, and generated bytes. Existing baselines are byte-identical except for the enumerated forced differences. Replay is labeled non-certifying; the relocated leg remains open for Item 5. |
| SR-A11 | SR-R50, SR-R51 | New unchanged RED nodes covering Gate A (SR-A01), ambiguity refusal (SR-A04), leaf-collision refusal (SR-A05), and the terminal-miss fork (SR-A06) run at the SR-R51 coordinate and each fails only for its named defect. The identical test bytes pass at candidate GREEN. |
| SR-A12 | SR-R41–SR-R44 | Deletion proof: a source search shows each SR-R41 path absent with no wrapper, flag, alias, or dead fallback; orphaned helpers per SR-R42 are gone or their surviving consumer is named; amended docstrings describe the one procedure. Any retained path is recorded as a deviation with its reason. |
| SR-A13 | SR-R34, SR-R52 | The affected regression union, compatible full suite, and licensed public-live suite pass at one candidate coordinate, with the LC-I09 coordinate recorded per row. |

## Explicit Agent Bets

Non-normative reviewer index. These remain challengeable.

| Bet | Requirement | Default and rationale |
|---|---|---|
| Two positive rungs only | SR-R11 | Contract invariant 19 names exactly two tiers. Any further rung the current ladders have (scope climb, structured alias, occurrence-scoped materialized QN) must justify itself as a *form of exact identity*, not as an additional guess tier. Design decides which survive and states each as a declared rung. |
| Uniform self-reference guard | SR-R13 | The constraint ladder's missing guard is drift, not a deliberate allowance. If design finds a constraint shape that legitimately reads its own channel, this bet loses. |
| Entry points written once | SR-R16 | The backfill seam is read as post-build default mutation under D-1. If design shows the backfill happens strictly before the graph is complete and no other writer can observe the intermediate state, the requirement weakens to "one writer", not "no backfill". |
| Aggregation joins the shared procedure | SR-R10 | The contract names calculation and constraint explicitly; the epic names aggregation as the third ladder. Treating aggregation as a consumer of the same request is the agent reading, ratified by the epic row, not owner-originated. |
| Lenient visibility without a schema | SR-R15 | Uniform visibility is Item 2's; severity codes and sinks are Item 4's. If the two cannot be separated, SR-R15 defers to Item 4 and Item 2 records the asymmetry rather than inventing a schema. |

## Non-Goals

- **[INHERITED]** Public late fill, placeholder completion, and post-build graph/default mutation.
  Source: owner D-1, epic Item 2 out-of-scope.
- **[INHERITED]** General typed-path or part-index refactors not required to unify the resolver.
  `[CONSTRAINT-ARCH-UNIFY]` scope item 3 (the three concrete-instance walkers,
  `.project/backlog/BACKLOG.md:821-828`) is not absorbed here. Source: epic Item 2 out-of-scope.
- **[INHERITED]** Item 3's Gate B coverage-scope decision, Item 4's diagnostics and default fidelity
  (including the Item 1 audit's tier-2 disposition asymmetry), and Item 5's relocated whole-tree
  proof. Source: SR-R07.
- **[INFERRED]** Reworking the Item 1 seams named in SR-R06, or re-opening Item 1's recorded
  deviations. They are inputs, not scope.
- **[INFERRED]** The stellarator five-constraint acceptance and the WI-027 passthrough removal.
  Item 2 makes them possible; register row 12 (Item 10) owns them.

## Open Questions / Deferred to design

- **[INFERRED]** Where the one procedure lives and what its request/result types are called. SR-R10
  fixes its inputs and its observable contract, not its module or class names.
- **[INFERRED]** Which of the current ladders' extra rungs (calculation scope-climb
  `dependency_backtracker.py:699-723`; structured scoped-alias on both sides; the constraint
  occurrence-scoped materialized-QN rung `constraint_lowering.py:243-262`; the de-indexed occurrence
  key) survive as declared rungs of the one ladder. SR-R11 and SR-R12 fix the test each must pass:
  declared, ordered, and exact-identity rather than a guess.
- **[INFERRED]** The error class hierarchy and exact rendered prose for a strict miss and for an
  ambiguity refusal. SR-R14 and SR-A04 fix the required context, not the wording.
- **[INFERRED]** How aggregation's `Compilability.MANUAL_REQUIRED` outcome is expressed once
  `_find_literal_redefinition`'s leaf tier is gone. SR-R17 fixes that no default may be invented; it
  does not decide whether MANUAL_REQUIRED remains the right label.
- **[INFERRED]** Whether the Gate A fixture is new or an extension of an existing constraint fixture.
  SR-R21 fixes the shape it must have; SR-R32 forbids reusing Item 1's frozen controls.

---

## Related Artifacts

- **Stage brief:** `.project/active/constraint-lifecycle-shared-resolution/briefs/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — Item 2,
  register row 2.
- **Normative architecture:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — invariants 19–26,
  owner decisions D-1/D-2, acceptance rows "Literal design-attribute actual (D-2)" and
  "Ambiguous/defaulted producer resolution".
- **Lifecycle requirements:** `.project/active/constraint-execution-lifecycle-contract/spec.md` —
  LC-D06–D09, LC-I08–I09.
- **Primary defect research:**
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`.
- **Gate A shape pin:**
  `.project/research/20260719-134700_constraint-execution-lifecycle-contract-correction-rereview.md`
  edit E11; census C-3 in
  `.project/research/20260719-111228_constraint-execution-lifecycle-evidence-census.md`.
- **Absorbed backlog row:** `.project/backlog/BACKLOG.md` `[CONSTRAINT-ARCH-UNIFY]` scope items 1–2.
- **Predecessor item:** `.project/active/constraint-lifecycle-occurrence-demand/{spec,evidence,audit}.md`
  — Item 1 seams, §6 deviations, residual items.
- **Design:** `.project/active/constraint-lifecycle-shared-resolution/design.md` (to be created).

---

**Next Steps:** Independent `my-spec-review` in a fresh session, then `my-design`.
