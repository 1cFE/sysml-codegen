# Design: Lifecycle Item 2 — Shared Producer Resolution and Gate A

**Status:** Draft — ready for independent design review
**Owner:** Reid W
**Created:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Design commit:** `3d205d116788c22439a67ccf9f6c7ba3b6b80c4d`
**RED predecessor:** sysml-codegen `287afc47ab06826de27c38e203ffffb45398f972` (Item 1 certified)
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 2, register row 2
**Complexity:** HIGH
**Decision records:** `.project/adr/` does not exist in this tree. No prior decision records to honor or
supersede. This design files none (see Next-Stage Handoff).

---

## Overview

One typed producer-resolution procedure replaces the calculation, constraint, and aggregation
ladders. Consumers differ only in the request they build and in what happens at terminal miss.

Gate A is fixed as part of this, but not by the ladder. Investigation found Gate A's break one hop
upstream of every ladder, in constraint owner classification. That finding reshapes the item and is
surfaced below before anything depends on it.

---

## Surfaced premise conflicts

Two, both raised under the surfacing duty (`claude-pack/rules/capture-fidelity.md` law 4). The owner
is not reachable in this session, so they are recorded loudly here with dependent conclusions
marked, not resolved silently. **A design reviewer should rule on PC-1 before the plan is executed.**

### PC-1 — Gate A cannot be fixed inside the resolver, and the fix touches an Item 1 seam

`[OWNER] SR-R20 / D-2` vs `[INHERITED] SR-R06` and design brief constraint 1.

The spec reads Gate A as a design-attribute-rung defect. It is not.

**Epistemic status of what follows.** A live generation run on a Gate A model was attempted and
blocked by session permissions, so this diagnosis rests on two things, not three: committed
extractor snapshots (real captured extractor output, not inference) and direct reading of the
dispatch code, both of which were verified first-hand rather than taken from a subagent report. It
has *not* been confirmed by a live failing run. Phase 0's stop condition exists to close exactly
that gap before any code is written.

Evidence:

- A constraint declared inside a concrete `PartUsage` reports its owner as the enclosing **package**.
  The adapter's owner fact carries the usage on `owner.owner` and the package on
  `owner.owning_definition` — observed in `tests/fixtures/catf_mfe_model/extraction_snapshot.json:658-668`,
  where a constraint on part usage `catf_physics` records
  `owner.owner = PartUsage CATFMFEPhysics::catf_physics` and
  `owner.owning_definition = package CATFMFEPhysics`.
- `constraint_lowering.py:1184` reads only `usage.owner.owning_definition.qualified_name`. The
  usage segment is discarded.
- Owner-kind dispatch in `prepare_constraint_usages` therefore routes this constraint to
  `_expand_package_owner` (`constraint_lowering.py:458-461`), which returns
  `((sanitize_qualified_name(usage.identity.qualified_name), ""),)` — the **constraint's own QN** as
  the owner instance path, and an empty occurrence scope.

Both design-attribute rungs then key off the wrong root. For `part the_host { attribute gain = 40.0; }`
in package `gate_a`, extraction emits the attribute correctly as `gate_a__the_host__gain`
(`parameter_groups.py:140,189-190`; the usage-owned shape is confirmed real at
`tests/fixtures/chain_override_probe/extraction_snapshot.json:263-272`). But:

| Rung | Key built | vs extracted QN |
|---|---|---|
| 7, occurrence-scoped (`constraint_lowering.py:258-265`) | `gate_a__the_host__positive__gain` | overshoots by the constraint's own name segment |
| 9, base-def default (`:283-290`) | `gate_a__gain` | undershoots by the `the_host` segment |

Rung 8 (`:267-274`) cannot help: for a self-named actual the reference target resolves to the
constraint's own formal, not to the attribute (`tests/fixtures/plant_values/extraction_snapshot.json:328`).
So resolution reaches `terminal_disposition(strict=True)` and generation fails.

The needed key is exactly *owner-usage QN + attribute name*. **The data is present** on
`usage.owner.owner.qualified_name`; it is simply never threaded into resolution.

**The conflict.** Delivering SR-R20 requires a `part_usage` owner kind in owner classification —
i.e. touching `prepare_constraint_usages`, an Item 1 landed seam that SR-R06 and brief constraint 1
say to build on and not rework.

**Recommendation, and what this design assumes.** Treat it as *extension*, which constraint 1
permits ("extend or consume them; do not rework them"): add a new `part_usage` branch ahead of the
package branch, leaving all three existing branches byte-for-byte unchanged. No existing Item 1
behavior changes — a constraint that is genuinely package-owned still takes the package branch.
This design proceeds on that reading (bet **B1**). If a reviewer rules it rework, Gate A leaves
Item 2 and the item reduces to ladder unification only; Phases 0 and 2 below are the parked
dependent conclusions.

### PC-2 — the entry-point backfill is not post-build mutation

`[INFERRED] SR-R16` characterizes the register/backfill pair at `graph_builder.py:1326-1345` as a
post-build graph/default mutation seam under owner D-1. That characterization is factually wrong.

Traced call order: `_build_agg_input_source` is reachable only from `_build_aggregation_module`
(`graph_builder.py:1412-1416`, `:1471-1475`), itself called only from `build_computation_graph`'s
Step 6.7 loop at `:331-337`. The `ComputationGraph` object is not constructed until `:436`. The
backfill therefore runs strictly *before* any graph exists. D-1 is not implicated.

The spec anticipated this and set the fallback condition: the requirement weakens to "one writer"
if "no other writer can observe the intermediate state." That condition is also false — the
backfill exists *precisely because* a later aggregation observes an earlier one's entry point via
`entry_points.get(ep_qn)` after the per-iteration `entry_points.update(new_eps)` at `:336`.

**What survives is a different and still-real defect**, restated as invariant I5 below: an entry
point's default depends on aggregation iteration order rather than on the entry point's identity.
The design deletes the backfill on that ground — order-dependence, not D-1 — and the deletion
holds. SR-R16's requirement text should be amended to its true basis when the spec is next touched.
No conclusion below rests on the D-1 framing.

---

## Related Artifacts

- **Stage brief:** `.project/active/constraint-lifecycle-shared-resolution/briefs/design.md`
- **Spec:** `.project/active/constraint-lifecycle-shared-resolution/spec.md`
- **Normative architecture:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  — invariants 19-26 (`:172-195`), owner decisions D-1 (`:284-289`) and D-2 (`:290-298`)
- **Lifecycle requirements:** `.project/active/constraint-execution-lifecycle-contract/spec.md` —
  LC-D06-D09, LC-I08-I09
- **Predecessor:** `.project/active/constraint-lifecycle-occurrence-demand/{design,evidence,audit}.md`
  — Item 1 seams and its §6 recorded deviations (rigor template for this document)
- **Primary defect research:** `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`
- **Gate A shape pin:** `.project/research/20260719-134700_...-correction-rereview.md` edit E11

---

## Research Findings

Facts established by reading the three ladders and Item 1's seams. Full rung-by-rung inventories are
in Appendix A; only the load-bearing findings are here.

- **The ladders try many keys, not two.** The calculation chain path alone tries five key forms
  (`dependency_backtracker.py:648-690`) plus a scope climb (`:713-723`); the constraint path tries
  six registry forms and three design-attribute forms (`constraint_lowering.py:176-290`);
  aggregation tries four strategies (`input_resolver.py:228-233`). Contract invariant 19's "two
  tiers" is a statement about *what class of thing* may produce a value, not about how many keys may
  be tried. This distinction is the design's organizing idea.
- **Almost every key form is already an exact keyed lookup.** All `OutputRegistry` accessors are
  typed dict lookups with no case folding (`core/output_registry.py:172-196`), and the registry
  raises on scoped/QN/scoped-alias collision (`:76-83, 93-100, 158-166`).
- **Exactly three key forms are guesses, and each has an exact twin already in the tree.**
  - `ChainRedefinitionFollow`'s case-insensitive last-segment part match
    (`input_resolver.py:171-179`) — exact twin: `_find_literal_redefinition`'s `usage_type_map` tier
    (`graph_builder.py:1226-1241`).
  - `_find_literal_redefinition`'s Strategy 2 leaf tier and its warn-and-return-first arm
    (`graph_builder.py:1242-1267`) — same exact twin, one tier above it in the same function.
  - The calculation bare-name ambiguous first-pick (`dependency_backtracker.py:831-856`) and the
    leaf-unique fallback (`:795-813`) — exact twin: the constraint ladder's `owner_def_qn` rung
    (`constraint_lowering.py:283-290`).
- **The calculation leaf guess exists only to cover def-owned attributes.** A design attribute owned
  by a part *def* extracts with `parent_part == ""` (documented at `dependency_backtracker.py:795-797`),
  so the exact dotted arm at `:790-793` can never match it. The constraint ladder solved the same
  problem exactly, one module away.
- **The scope climb is exact and already ambiguity-guarded.** It varies only the ancestor prefix,
  preserving the whole source path, and collects every distinct hit into a set, returning only when
  `len(climbed) == 1` (`dependency_backtracker.py:713-723`). It is a search over declared scopes,
  not a fuzzy match.
- **The constraint ladder has no self-reference guard.** Confirmed absent across `resolve_actual`
  (`:143-300`) and `_resolve_formal` (`:791-823`); it never receives module identity. The other two
  guards compare the same thing — producing-usage EQN vs consumer EQN
  (`dependency_backtracker.py:745-754`; `input_resolver.py:263-271`).
- **Lenient miss visibility is inconsistent by accident, not design.** `terminal_disposition`
  warns only for multi-hop chains (`dependency_backtracker.py:66-71`) and otherwise logs DEBUG;
  the aggregation LocalTerm fallback (`graph_builder.py:1524-1540`) logs nothing at all and mints a
  `DESIGN_ATTRIBUTE` entry point with a `None` default.
- **`core/` is a strict leaf package.** It imports nothing from `analysis/`, `resolution/`,
  `extraction/`, `orchestration/`, or `snapshot/`. `analysis/` and `resolution/` are a mutual cycle
  managed by deferred imports (`constraint_lowering.py:1396`; `supplied_values.py:45,453`).
- **Item 1's seams are pre-graph and copy-on-write.** `enrich_graph_design_attributes` returns a new
  map and mutates nothing (`supplied_values.py:495-600`); it runs at live Step 5.65
  (`pipeline_builder.py:843-859`), ~115 lines before `build_computation_graph` at `:973`. Nothing in
  this design disturbs that ordering.

---

## Core Concept

**Separate the tier from the key form.** A tier is a claim about what kind of thing may produce a
value — contract invariant 19 names exactly two: a real producer channel, then a real design
attribute under exact qualified identity. A key form is one way of asking "is it here?" The three
ladders drifted not because they tried many key forms, but because each invented its own list, in
its own order, and two of the lists included key forms that guess.

So the design is one ordered table of key forms, partitioned into the two tiers, declared in one
place. A consumer supplies a request — who is asking, what reference, in what scope, under which
terminal policy — and reads a typed result. It cannot add, reorder, or skip a key form. Every key
form is an exact keyed lookup; where more than one candidate satisfies one, it yields nothing rather
than a guess.

**The unification is what makes the deletions safe, and that is the real argument for it.** Each of
the three guessing key forms has an exact-identity twin that already exists — in a *different*
ladder. The calculation side guesses by leaf name to reach def-owned attributes; the constraint side
already reaches them exactly through the owner-def QN. The aggregation side matches part names
case-insensitively; the type-aware `usage_type_map` tier sitting directly above it answers the same
question exactly. Merging the ladders lets each guess be *deleted* rather than merely banned,
because the merged table already contains its exact replacement. A ban would have cost coverage;
the merge does not.

Gate A is separate and upstream. It is not a missing rung — it is a missing *scope*: a constraint
owned by a concrete `PartUsage` is misclassified as package-owned, so every design-attribute key
form is built from the wrong root. The resolver cannot fix that from inside; owner classification
must carry the usage identity the adapter already provides.

---

## Key Bets

Beliefs about reality. All are `[INFERRED]` agent-grade and challengeable.

- **B1.** Adding a `part_usage` owner branch ahead of the existing package branch is an *extension*
  of Item 1's `prepare_constraint_usages`, not a rework, because no existing branch's behavior
  changes. *If false → Gate A (SR-R20, owner D-2) cannot be delivered in Item 2 at all; Phases 0 and
  2 leave this item and the epic needs a new home for them.* This is PC-1 and is the single most
  load-bearing bet in the document.
- **B2.** Every key form the three ladders use is either (a) an exact keyed lookup, (b) an
  ambiguity-guarded search over declared scopes, or (c) one of the three named guesses whose exact
  twin already exists elsewhere in the tree. *If false → some consumer silently loses coverage at
  cutover, appearing as a byte-identity diff or a newly unresolved input on an existing fixture.*
- **B3.** A constraint actual never legitimately reads a channel produced by its own constraint
  module. *If false → the uniform self-reference guard refuses a valid model, and SR-R13 is wrong.*
- **B4.** An entry point's modeled default is determined by the entry point's identity plus the
  reference that mints it — not by which consumer happens to mint it first. *If false → unifying the
  mint point changes existing defaults, and the backfill was load-bearing rather than a patch over
  order-dependence.*
- **B5.** Raising every lenient terminal miss to one uniform `logger.warning` at a single call site
  requires no severity schema and no diagnostic sink, so Item 4's boundary holds. *If false → SR-R15
  defers wholesale to Item 4 and Item 2 records the asymmetry instead (the spec's own fallback).*

### Verdicts on the spec's five flagged bets

| Spec bet | Verdict | Evidence |
|---|---|---|
| Two positive rungs only (SR-R11) | **Confirmed in substance, reframed** | Two *tiers* is right; "two rungs" is not. Nine-plus key forms exist and most are exact. See Core Concept and Appendix A. |
| Uniform self-reference guard (SR-R13) | **Confirmed** | Guard genuinely absent on the constraint ladder; the other two compare identical predicates. No constraint shape found that reads its own verdict channel. |
| Entry points written once (SR-R16) | **Challenged on its stated basis; requirement survives on a new one** | Not post-build mutation (PC-2). Real defect is order-dependent default assignment. |
| Aggregation joins the shared request (SR-R10) | **Confirmed, with one addition** | Aggregation's strategies are the same key forms plus `DirectChannelConstruction` (`input_resolver.py:201-222`), which becomes a declared tier-1 key form. Its chain-redefinition *follow* survives re-keyed; only the case-insensitive match dies. |
| Lenient visibility without a schema (SR-R15) | **Confirmed** | After unification there is exactly one lenient terminal-miss call site; uniformity is a one-line property, not a schema. |

---

## Key Decisions

- **D1. The procedure lives in `core/producer_resolution.py`.** `core/` is a strict leaf, so a
  shared module there is cycle-free by construction, and it already owns `OutputRegistry` and the
  identifier types the key forms are built from. `terminal_disposition` moves there from
  `dependency_backtracker.py:38-77`, retiring the current `analysis → analysis` import at
  `constraint_lowering.py:38`. *Rejected: `resolution/` (analysis↔resolution is already a managed
  cycle; a third participant makes it worse); leaving it in `analysis/dependency_backtracker.py`
  (the resolver would outlive the backtracker's ladder and shouldn't be housed in it).*
- **D2. One ordered key-form table, partitioned into two tiers, declared as data.** A module-level
  sequence of key-form descriptors, consulted in order. Ordering is observable by reading the
  sequence in a test. *Rejected: a chain of `if` blocks (order is then implicit and untestable as
  data — the exact failure mode that let three ladders drift).*
- **D3. Consumer identity, scope, and terminal policy are request fields.** The self-reference guard
  and the entry-point QN both derive from request data, so one predicate serves all three consumers.
  *Rejected: a `consumer_kind` enum branched on inside the resolver (that is a consumer-specific
  ladder wearing a different hat, banned by contract invariant 20).*
- **D4. Terminal policy is a two-valued field, not a flag threaded through the key forms.** It is
  read exactly once, after the table is exhausted. No key form sees it. *Rejected: passing `strict`
  into each key form (brief constraint 5 forbids collapsing the semantics into threaded flags).*
- **D5. Ambiguity within a key form yields no result and records why.** The result carries the
  attempted key forms and, where a key form found multiple candidates, their identities — so the
  strict error can name them (SR-A04) and the lenient path can warn usefully. *Rejected: raising
  from inside a key form (it would make lenient consumers strict by accident).*
- **D6. The scope climb survives as a declared, ambiguity-guarded key form.** Its candidates are
  exact scoped-key lookups on the full source path; only the ancestor prefix varies, and it already
  refuses on `len(climbed) != 1`. *Rejected: deleting it (it is the only resolver for ancestor-scope
  channels, pinned by `test_res08_consumer_scope_paths.py:82`); keeping it calculation-only (that is
  the drift SR-R11 exists to end).*
- **D7. The chain-redefinition follow survives, re-keyed to `usage_type_map`.** The recursion and its
  cycle guard are real mechanism; only the case-insensitive part match is the guess. Re-keying it to
  the same exact identity `_find_literal_redefinition` tier 1 uses makes it a declared exact key
  form. Recorded as an SR-R41(4) deviation with this reason. *Rejected: deleting the whole strategy
  (aggregation loses chain-redefinition coverage and existing baselines move); keeping the
  case-insensitive match (SR-R12).*
- **D8. One mint point for lenient entry points.** The entry-point QN and its modeled default are
  computed together, from the request, at the single lenient terminal-miss site. The register/
  backfill pair and the silent LocalTerm mint both collapse into it. *Rejected: keeping the backfill
  as a one-writer reconciliation (it encodes order-dependence, invariant I5); refusing on default
  disagreement (would be a new failure on existing green fixtures — see Risk R3).*
- **D9. Gate A is fixed by owner classification, not by a new rung.** A `part_usage` branch reads
  `usage.owner.owner` and produces a real owner instance path and occurrence scope, after which the
  existing exact design-attribute key forms hit unchanged. *Rejected: adding a Gate-A-specific
  design-attribute key form (it would key off the constraint's own QN — a fourth guess, and it would
  leave the occurrence scope wrong for the tier-1 key forms too).*
- **D10. `_is_calc_def_owned` survives as a map-construction filter.** The by-QN design-attribute map
  excludes calc-def-owned entries, preserving today's guard that a calc def's `out attribute` never
  becomes a `DESIGN_ATTRIBUTE` entry point. Named here per SR-R42's "design names which."
  *Rejected: deleting it with the leaf fallback it currently serves (the cross-wiring it prevents is
  real and independent of the fallback).*

---

## Data Contracts

Names below are the design's proposal; the plan may refine names but not ownership or field
semantics.

### `ProducerRequest` (frozen)

| Field | Type | Meaning |
|---|---|---|
| `consumer_eqn` | `str` | Producing-module EQN of the asking consumer. Sole input to the self-reference guard. |
| `reference` | `str` | The reference as written — dotted chain, `::` path, or bare name. Never pre-split by the caller. |
| `consumer_scope` | `str` | Dotted scope the reference is read in (`""` at top level). |
| `instance_path` | `str \| None` | Occurrence instance path where one exists; drives the occurrence-scoped and direct-channel key forms. |
| `owner_def_qn` | `str \| None` | Owning-definition QN, for the def-scoped design-attribute key form. |
| `policy` | `TerminalPolicy` | `STRICT` or `LENIENT`. Read once, after the table. |
| `diagnostic_context` | `str` | Consumer-supplied context for error and warning text (usage, formal). |

### `ProducerResolution` (frozen)

| Field | Type | Meaning |
|---|---|---|
| `outcome` | `MODULE_OUTPUT \| DESIGN_ATTRIBUTE \| ENTRY_POINT` | What resolved. `ENTRY_POINT` only from a lenient terminal miss. |
| `identity` | `str` | Canonical channel, design-attribute QN, or minted entry-point QN. |
| `default_value` | `str \| None` | Modeled default; set only for `DESIGN_ATTRIBUTE` and `ENTRY_POINT`. |
| `key_form` | `str \| None` | Which key form produced it. Makes precedence observable (SR-A03). |
| `attempted` | `tuple[str, ...]` | Key forms tried, in order. Required context for the strict error. |
| `ambiguous_candidates` | `tuple[str, ...]` | Identities that tied within a key form, if any. Feeds SR-A04. |

### `ResolutionContext` (built once per run, not per request)

Holds the `OutputRegistry`, the by-QN design-attribute map (filtered per D10), `redefinitions`,
`usage_type_map`, and `canonical_channels`. Consumers construct it once and pass it alongside each
request.

### Exact APIs

| API | Ownership |
|---|---|
| `resolve_producer(request, context) -> ProducerResolution` | `core/producer_resolution.py`. The only positive-resolution entry point in the tree. |
| `KEY_FORMS: tuple[KeyForm, ...]` | Same module. Module-level, ordered, tier-partitioned. |
| `terminal_disposition(...)` | Moves here from `dependency_backtracker.py:38-77`. Called only from `resolve_producer`. |

Negative ownership: no consumer module may construct a registry key, split a reference, or call
`terminal_disposition`. Those are the resolver's alone.

---

## Architecture

### The key-form table

Consulted in order. Tier 1 exhausts before tier 2 begins.

**Tier 1 — real producer channel**

| # | Key form | Identity | Origin |
|---|---|---|---|
| 1 | scoped, consumer-scope prefixed | exact `ScopedKey` | calc `:648-653`, constraint `:176-182`, agg A |
| 2 | scoped, de-indexed occurrence scope | exact `ScopedKey` | constraint `:183-190` |
| 3 | scoped, bare reference | exact `ScopedKey` | calc `:657` |
| 4 | alias, both scope variants | exact `ScopedKey` | constraint `:192-206` |
| 5 | structured scoped alias | exact `ScopedAliasKey` tuple | calc `:674-686`, constraint `:216-240` |
| 6 | SysML QN, sanitized | exact `SysMLQN` | calc `:735-739`, agg B |
| 7 | direct channel construction | constructed channel, membership-checked | agg E `:201-222` |
| 8 | chain-redefinition follow, `usage_type_map`-keyed | exact type QN (re-keyed per D7) | agg C `:139-195` |
| 9 | scope climb | exact scoped key per ancestor, refuses unless unique | calc `:713-723` |

**Tier 2 — real design attribute under exact qualified identity**

| # | Key form | Identity | Origin |
|---|---|---|---|
| 10 | occurrence-materialized QN | `{owner_instance_path}__{dotted→__}` | constraint `:258-265` |
| 11 | sanitized target QN | exact QN equality | calc `:818-829`, constraint `:267-274` |
| 12 | owner-def QN | `{owner_def_qn}__{dotted→__}` | constraint `:283-290` |

Every tier-1 hit passes the self-reference guard before it is returned: the channel's producing
usage EQN (`channel.rsplit("__", 1)[0]`) must not equal `request.consumer_eqn`. A guard rejection
skips the candidate and continues the table — it is not a terminal condition.

Deleted rather than migrated: the calculation leaf-unique fallback and bare-name first-pick, the
aggregation case-insensitive part match, and `_find_literal_redefinition`'s Strategy 2. Each is
covered by key form 12, 8, or 8 respectively.

### Terminal miss

Read `request.policy` once, after the table.

- **STRICT** raises `CodeGenerationError` naming the usage, the formal, the reference as written,
  the `attempted` key forms, and any `ambiguous_candidates`. Synthesizes nothing. This extends the
  context carried by today's error (`dependency_backtracker.py:56-65`), which carries only three
  strings and names no attempted classes — SR-R14 requires the classes.
- **LENIENT** mints exactly one entry point at the single mint point (D8): QN derived from
  `consumer_eqn` and the reference, modeled default resolved at creation, and one
  `logger.warning` carrying `diagnostic_context`.

### Consumer convergence

- **Calculation** (`dependency_backtracker.py`): `_resolve_binding_via_registry` becomes a request
  builder — `consumer_eqn = usage.qualified_name`, `consumer_scope = _consumer_scope_dotted(usage)`,
  `policy = LENIENT` — and a result reader mapping `MODULE_OUTPUT`/`ENTRY_POINT` onto
  `BindingResolution`. `_resolve_chain_dispatch`, `_resolve_reference_dispatch`,
  `_resolve_reference_via_registry`, and `_resolve_to_design_attribute` are deleted.
- **Constraint** (`constraint_lowering.py`): `resolve_actual` becomes a request builder with
  `policy = STRICT`, mapping the result onto `ConcreteConstraintInput`. Its rung sequence
  (`:172-290`) is deleted; its strict terminal shape and error context move into the resolver.
- **Aggregation** (`input_resolver.py`, `graph_builder.py`): `resolve_input` and `AGG_STRATEGIES`
  are deleted. `_build_agg_input_source` and the LocalTerm path both build requests with
  `policy = LENIENT` and share the one mint point; the register/backfill pair goes with them.

### Gate A path

`prepare_constraint_usages` gains a `part_usage` owner branch, taken when
`usage.owner.owner.kind == "PartUsage"`, before the package branch. It returns
`((sanitize_qualified_name(usage.owner.owner.qualified_name), occurrence_scope(...)),)` — a real
owner instance path and a real occurrence scope. Key form 10 then builds `gate_a__the_host__gain`
and hits the extracted attribute. No new key form is introduced.

**Fixture shape constraint, discovered during investigation:** the Gate A fixture must use the
def-typed constraint form with an explicit self-named actual
(`assert constraint viability : 'Viability Threshold' { in gain = gain; }`), mirroring
`tests/fixtures/plant_values/library.sysml:107`. The *inline* form
(`assert constraint positive { gain > 0.0 }`, as in `constraint_inline/model.sysml`) has no formal
bindings — `formal_bindings` is `None` at `constraint_lowering.py:1187` — and never reaches
resolution at all. An inline-form fixture would silently fail to certify Gate A, a second instance
of the substitution risk SR-R21 was written to prevent.

---

## Required Invariants

- **I1 — one authority.** `resolve_producer` is the only positive-resolution path in the tree. No
  consumer constructs a registry key or splits a reference.
- **I2 — declared order.** `KEY_FORMS` is a single ordered sequence; a test reads it as data and
  pins the order.
- **I3 — exact identity.** No key form matches by leaf name, case-insensitively, by suffix, or by
  arbitrary first pick. Multiple candidates within one key form yield no result.
- **I4 — one fork.** Strict and lenient differ only after the table is exhausted. No key form reads
  `policy`.
- **I5 — identity-determined defaults.** An entry point's default is a function of its identity and
  the reference that mints it, not of consumer iteration order. One mint point; no backfill.
- **I6 — uniform guard.** The self-reference predicate is one expression, applied to every tier-1
  hit for every consumer.
- **I7 — visible lenient miss.** Every lenient terminal miss emits one warning. None is silent.
- **I8 — Item 1 seams unchanged in behavior.** `resolve_logical_demand`, `select_group_source`, and
  `enrich_graph_design_attributes` are not modified. `prepare_constraint_usages` gains one branch;
  its three existing branches are unchanged.
- **I9 — convergent entry points.** Two consumers of one design attribute reach one QN-keyed entry
  point (SR-A02).

---

## Deletion Inventory

Per SR-R41, with the exact-twin that makes each deletion safe.

| # | Deleted | Covered by |
|---|---|---|
| 1 | `_resolve_binding_via_registry` ordering, `_resolve_chain_dispatch`, `_resolve_reference_dispatch`, `_resolve_reference_via_registry` (`dependency_backtracker.py:519-744`) | key forms 1,3,5,6,9 |
| 2 | leaf-unique fallback (`:795-813`), bare-name first-pick (`:831-856`) | key form 12 |
| 3 | `resolve_actual`'s rung sequence (`constraint_lowering.py:172-290`) | key forms 1-12 |
| 4 | `AGG_STRATEGIES`, `resolve_input`, case-insensitive leaf match (`input_resolver.py:171-179, 228-290`) | key forms 1,6,7,8 |
| 5 | `_find_literal_redefinition` Strategy 2 and collision arm (`graph_builder.py:1242-1267`) | its own tier 1 (`:1226-1241`) |
| 6 | register/backfill pair (`:1322-1342`), silent LocalTerm mint (`:1524-1540`) | the one mint point (D8) |

**Helpers (SR-R42).** `_consumer_scope_dotted` and `_get_parent_part_for_usage`
(`dependency_backtracker.py:486-506`) have no caller outside the deleted ladder;
`_get_parent_part_for_usage` is deleted, and `_consumer_scope_dotted` moves to the resolver as the
`consumer_scope` derivation. `_is_calc_def_owned` survives per D10. On the constraint side,
`_reference_dotted` survives — the public wrapper `reference_dotted` is consumed by
`supplied_values.py:453` — and `_deindexed_scope` moves to the resolver with key forms 2 and 4.
`occurrence_scope` survives; it is called from `prepare_constraint_usages`' expansion path
(`constraint_lowering.py:441,455`), which this design extends.

**Tests (SR-R43).** Private-mechanics tests of deleted internals are deleted with them: the seven in
`test_output_registry_construction.py:927-1081`, four in `test_dependency_backtracker.py:62-113`,
six in `test_matcher_fixes_item7.py:79-137`, six `_find_literal_redefinition` tests in
`test_factory_aggregation.py`, and the strategy-ordering assertions at
`test_input_resolver.py:244,384`. Their *observable* content migrates to the resolver's own tests —
notably the ambiguity-refusal and collision-warning behaviors in `test_silent_failure_family3.py:73-96`,
which become refusals under I3. The six precedence pins at `test_constraint_resolver.py:305-420`
are the migration guard and are addressed in Phase 3 (SR-R33).

---

## Non-Goals

- Item 3's Gate B coverage scope, Item 4's diagnostic severity schema and default fidelity, Item 5's
  relocated whole-tree proof (SR-R07).
- Reworking Item 1's `resolve_logical_demand` / `select_group_source` /
  `enrich_graph_design_attributes`, or reopening its recorded deviations.
- General typed-path or part-index refactors — `[CONSTRAINT-ARCH-UNIFY]` scope item 3 stays out.
- Public late fill, placeholder completion, post-build graph or default mutation (D-1).
- The stellarator five-constraint acceptance and WI-027 passthrough removal (register row 12).
- Deciding whether `Compilability.MANUAL_REQUIRED` remains the right label. Its only behavioral
  effect is suppressing `auto_impl_context` (`graph_builder.py:1574-1577`); the design preserves
  today's setting sites and leaves the naming question to Item 4.

---

## Potential Risks

- **R1 — Gate A leaves the item (PC-1).** If B1 is ruled rework, Phases 0 and 2 park. *Control:*
  phase order puts Gate A first precisely so this is discovered before the deletions begin.
- **R2 — a key form's coverage is not what the inventory says (B2).** A cutover silently loses an
  existing resolution. *Control:* per-consumer cutover in separate phases, each gated on the full
  suite plus byte identity, so the blast radius of any single cutover is one consumer.
- **R3 — unifying the mint point changes an existing default (B4).** The backfill exists because
  some first mint lacks a default. *Control:* Phase 5 runs the byte-identity gate before any
  deletion is committed; any moved default is enumerated per SR-R31 with the requirement forcing it,
  or the phase stops.
- **R4 — key form 8's re-keying loses aggregation coverage.** `usage_type_map` may not cover a pair
  the case-insensitive match reached. *Control:* the ~22 `resolve_input` observable tests in
  `test_input_resolver.py` and the ten in `test_graph_builder_aggregation.py` migrate unchanged in
  content and must pass.
- **R5 — warning volume.** I7 converts many DEBUG lines to warnings; existing suites assert DEBUG
  silence (`test_dependency_backtracker.py:121,142`; `test_output_registry_construction.py:1009`).
  *Control:* these are observable-behavior tests and are migrated with their assertions updated, and
  the change is recorded — it is a behavior change, not a test fix.
- **R6 — the strict error's added context changes pinned bytes.** Two call sites pin the current
  text (`test_constraint_resolver.py:255,266`). *Control:* recorded as an intended change under
  SR-R14, which requires the attempted classes the current text omits.

---

## Validation Approach

Evidence discipline follows Item 1: new defect tests are authored once and run unchanged at the
RED coordinate `287afc4` and at candidate GREEN, with no conditional (SR-R50/R51). RED must fail for
the named defect — a setup, license, or import failure does not count.

Commands (license per `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`):

```bash
uv run --frozen pytest -q -rs tests/                      # full suite; Item 1 baseline 3009p/26s
uv run --frozen pytest -q -rs tests/conformance/test_baselines.py   # byte-identity gate
uv run --frozen mypy src/                                 # baseline 76 errors, must not grow
uv run --frozen ruff check src/                           # clean
```

Real generated execution runs in the agentic-mbse venv, not this repo's:

```bash
TEAX_SIMKIT_PATH=../teax/packages/teax-simkit PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
  /home/reid/1cfe/agentic-mbse/.venv/bin/python -m pytest -q -rs -o addopts= -m execution tests/execution/
```

Generated baselines under `tests/fixtures/baseline_outputs/` are generator-owned bytes: never
hand-edited, never reformatted (SR-R31). Item 1's acceptance file and its
`constraint_occurrence_demand/` fixtures are frozen controls and run unmodified (SR-R32).

---

## Phased Implementation Plan

Folded in per brief constraint 6. Each phase is test-first, RED before GREEN on public fixtures, and
has a stop condition that halts the item rather than working around it.

**Phase 0 — Gate A fixture and the RED surface.** Author `tests/fixtures/gate_a/` with a
usage-owned literal attribute on a concrete `PartUsage`, a def-typed constraint with a self-named
actual, and no passthrough calculation. Author the unchanged RED nodes for SR-A01 (Gate A), SR-A04
(ambiguity refusal), SR-A05 (leaf-collision refusal), SR-A06 (terminal-miss fork). Run at `287afc4`.
*Validation:* each node fails for its own named defect, verified from the failure text — Gate A must
fail at `terminal_disposition(strict=True)`, not at parse or setup.
*Stop condition:* if Gate A fails anywhere other than the predicted terminal raise, the PC-1
diagnosis is wrong; stop and re-diagnose before writing any resolver code.

**Phase 1 — the resolver, unconsumed.** Add `core/producer_resolution.py` with the request/result
types, the `KEY_FORMS` table, and `terminal_disposition` moved in. No consumer wired. Unit tests pin
the table order as data (I2), exact-identity refusal (I3), the guard (I6), and both terminal
policies (I4).
*Validation:* full suite unchanged (nothing consumes it yet); mypy and ruff clean.
*Stop condition:* if any key form cannot be expressed without reading `policy`, D4 is wrong — stop
and re-derive the fork boundary.

**Phase 2 — Gate A.** Add the `part_usage` owner branch to `prepare_constraint_usages`. Wire nothing
else.
*Validation:* SR-A01 turns GREEN with generated TEAx execution returning the pinned verdict, and
changing the literal changes the verdict (SR-R22). Full suite and byte identity green — no existing
fixture should move, since no existing constraint is usage-owned.
*Stop condition:* any baseline byte moves. That would mean an existing constraint was silently
package-classified and is now reclassified — a behavior change PC-1's "extension not rework"
argument does not cover. Stop and surface.

**Phase 3 — constraint consumer.** Cut `resolve_actual` over to the resolver; delete its rung
sequence. Address the six precedence pins per SR-R33: each survives unchanged or its change is
recorded with the requirement forcing it.
*Validation:* full suite; SR-A03, SR-A04, SR-A06 GREEN; byte identity.
*Stop condition:* a precedence pin changes without a requirement to point at.

**Phase 4 — calculation consumer.** Cut `_resolve_binding_via_registry` over; delete deletion-
inventory items 1 and 2 and the orphaned helpers.
*Validation:* full suite; SR-A09 GREEN on the calculation route; byte identity.
*Stop condition:* a byte-identity diff not explained by an enumerated forced difference.

**Phase 5 — aggregation consumer.** Cut `_build_agg_input_source` and the LocalTerm path over;
delete inventory items 4, 5, 6. This is the phase carrying R3 and R4.
*Validation:* full suite; SR-A05, SR-A07, SR-A09 GREEN across all three routes; byte identity;
generated execution.
*Stop condition:* a default moves without an enumerated cause.

**Phase 6 — sweep and evidence.** Deletion proof by source search (SR-A12); docstrings and comments
amended to describe the one procedure, not to prohibit the removed behavior (SR-R44). Live and
same-checkout replay parity on the Gate A fixture, replay labeled non-certifying (SR-A10, SR-R08).
Record LC-I09 coordinates per acceptance row (SR-R52) and any deviation with its reason.
*Validation:* SR-A11 (identical test bytes pass at GREEN), SR-A13 (full and licensed-live suites at
one coordinate).

---

## Next-Stage Handoff

**Fixed.** The two-tier / many-key-form framing; the resolver's home in `core/`; the request and
result field sets; the deletion inventory and its exact-twin justifications; the phase order.

**Open.** Type and function names; the rendered prose of the strict error and the ambiguity refusal
(SR-R14 fixes required context, not wording); whether `MANUAL_REQUIRED` stays the right label
(Item 4); the exact `gate_a` fixture package and attribute names.

**De-risk first.** PC-1. A reviewer's ruling on B1 decides whether Phases 0 and 2 belong to this
item at all, and nothing else in the plan depends on it — the ladder unification stands either way.
Phase 0's stop condition is the cheapest empirical check on the diagnosis.

**Not to start.** Any deletion before Phase 3. Any change to Item 1's three resolution seams.

**Decision records.** None filed. Every decision here is mechanism choice within an owner-settled
contract (invariants 19-26, D-1, D-2) and is cited, not re-decided. `.project/adr/` does not exist;
if the acceptance review judges D1 or D9 to meet the density bar, create it via
`.project/scripts/adr.sh new` rather than hand-minting ids.

---

## Appendix A — Full key-form provenance

Every key form in the merged table, traced to the ladder it came from, with the exact predicate.

**Calculation** (`dependency_backtracker.py`): chain path tries consumer-scoped `ScopedKey`
(`:648-653`), bare `ScopedKey` (`:657`), structured `ScopedAliasKey` scoped-then-unscoped
(`:674-686`), `alias_lookup` (`:689`), then scope climb gated on `source_path.count(".") >= 2`
(`:713-723`). Reference path tries sanitized `SysMLQN` (`:735-739`) then
`_resolve_reference_via_registry` (`:519-560`), which discards the path and recombines the *leaf*
with the consumer scope — the one name-fragment key form on this side besides the climb, subsumed by
key forms 1 and 3 once the reference is not pre-split. Design-attribute tail: dotted exact
`(name, parent_part)` (`:790-793`), leaf-unique fallback (`:795-813`, deleted), `::` exact QN
(`:818-829`), bare-name with first-pick (`:831-856`, deleted).

**Constraint** (`constraint_lowering.py`): occ-scoped `scoped_lookup` (`:176-182`), de-indexed
`scoped_lookup` (`:183-190`), occ `alias_lookup` (`:192-198`), de-indexed `alias_lookup`
(`:199-206`), scoped structured alias over both scope candidates (`:216-231`), unscoped structured
alias (`:232-240`), occurrence-materialized QN (`:258-265`), sanitized target QN (`:267-274`),
owner-def QN (`:283-290`), strict terminal (`:292-300`).

**Aggregation** (`input_resolver.py:228-233`): `ScopedRegistryLookup` (`:70-109`, scoped then
unscoped, each `scoped_lookup` then `alias_lookup`), `ChainRedefinitionFollow` (`:139-195`, exact
`attribute_name` but case-insensitive last-`__`-segment part match at `:171-179`, first-wins with no
collision warning, cycle-guarded at `:162-169`), `SysMLQNLookup` (`:115-133`),
`DirectChannelConstruction` (`:201-222`, constructs `{instance_path}__{prefix→__}` and requires
membership in `canonical_channels`).

**Note on rung-5 aliasing.** The constraint scoped-alias loop discriminates on
`scope_candidate == deindexed_scope` — a value comparison, not a position index. When `occ_scope`
contains no brackets the two are equal and the first iteration takes the de-indexed branch. Harmless
today because the prefixes coincide, but the merged table should discriminate positionally.

## Appendix B — Item 1 seam facts consumed

`ResolvedDemand` has four fields, not five (`supplied_values.py:158-172`); provenance selection is
call-site policy via `select_group_source` (`:330-360`). `enrich_graph_design_attributes`
(`:495-600`) is copy-on-write and runs at live Step 5.65 (`pipeline_builder.py:843-859`) and replay
`graph_rebuild.py:107-114`, both before graph construction. `PreparedConstraintUsage` carries seven
fields including `predicate_source_key` (Item 1 deviation 1). `prepare_constraint_usages`
(`:714-788`) dispatches on `usage.owner.owning_definition.kind` into `_expand_part_owner`,
`_expand_calc_owner`, `_expand_package_owner` — the dispatch point this design extends with a
`part_usage` branch (PC-1, D9).

---

**Next Step:** independent `/_my_design_review` in a fresh session, ruling on PC-1 first. After
approval → `/_my_implement` against the phased plan above (no separate `plan.md`).
