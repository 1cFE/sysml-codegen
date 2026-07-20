# Design: Lifecycle Item 2 — Shared Producer Resolution and Gate A

**Status:** Implemented — all phases complete; candidate ready for independent audit (`evidence.md`)
**Owner:** Reid W
**Created:** 2026-07-19
**Revised:** 2026-07-19
**Branch:** `constraint-exec-epic`
**RED predecessor:** sysml-codegen `287afc47ab06826de27c38e203ffffb45398f972` (Item 1 certified)
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 2, register row 2
**Complexity:** HIGH
**Decision records:** `.project/adr/` does not exist in this tree. None to honor or supersede.

---

## Review Resolution

Rev 1 was returned **Needs-rework** on the ladder-unification half; the Gate A half was approved in
mechanism. Every finding was re-verified first-hand before acting on it.

| Finding | Verdict | Revision |
|---|---|---|
| **C1** key form 12 does not cover the calc leaf-unique fallback | **Confirmed.** `test_matcher_fixes_item7.py:79-86` resolves `magnet_holder.magnet_vol` → `Lib__MagnetPartDef__magnet_vol`; key form 12 would build `{owner_def_qn}__magnet_holder__magnet_vol`. `CalcUsageData.owning_part_def_qn` is `str \| None = None` (`usage_extractor.py:125`). | Exact-twin argument withdrawn. Deletions narrowed per D2/D11; the fallback survives as a declared key form. |
| **C2** Strategy 2 is a successor to tier 1, not a twin | **Confirmed.** `graph_builder.py:1240-1245` — the leaf match is the `else` of `if target_partdef_qn is not None`. Mutually exclusive by construction. D7's re-keying fails identically. | Same. Strategy 2's leaf tier survives, re-typed to refuse on collision. |
| **C3** `core/` cannot hold the resolver's context | **Confirmed.** `core/__init__.py` declares the layer invariant `resolution → extraction, analysis, core`. Three of six required types live above `core`. | D1 re-derived: the resolver lives in `resolution/`. |
| **C5** the table undercounts by ~2x | **Confirmed.** Real inventory is ~24 lookups plus 7 scan arms. Appendix A rebuilt from code. | Table rebuilt; climb and side effects given explicit non-row homes. |
| **M1** result type cannot carry what minting needs | **Confirmed.** `group_deriver` is absent at two of three mint sites. | D8 downgraded honestly: the resolver owns the QN and the default, not `EntryPoint` construction. |
| **M2** three QN formulas unreconciled | **Confirmed.** | One rule stated that reproduces all three byte-for-byte (D9). |
| **M3** I9 has no mechanism | **Confirmed.** | I9 restated as a property of tier-2 resolution, not of the mint point. |
| **M4** `ResolutionContext` name collision | **Confirmed** (`input_resolver.py:40`). | New type named `ProducerContext`. |
| **M5** `kind == "PartUsage"` is an open-vocabulary string compare | **Confirmed.** `constraint_extraction.py:193-200` sets `kind=type(element).__name__`. | D10 hardened: allowlist + `None` guard + explicit raise, no silent fall-through. |
| **M6** B1's stated premise is factually wrong | **Confirmed.** Nine usage-owned constraints exist in `catf_mfe_model`; all are excluded upstream as `unassessed_form`. | B1 restated on true ground; Phase 2 gains package-owner fixture coverage. |
| **M7** `_expand_package_owner` misquoted | **Confirmed.** | Quote corrected (`or owner_qn`). |
| **m1–m4** | Confirmed. | Line refs corrected to `:303-420`; positional-discrimination note carried into D12; the scan-abort and conditional-warning facts recorded. |

One finding produced a **new** discovery the review did not have, which changes D8 materially: see
PC-3 below on V11 scope.

---

## Overview

One typed producer-resolution procedure replaces the calculation, constraint, and aggregation
ladders' three separate orderings, guards, and terminal policies. Gate A is fixed separately and
upstream, in constraint owner classification.

The rev-1 claim that unification is *free* — that every guess had an exact twin already in the tree
— was false. Unification is still right, but it buys one ordering rather than a clean sweep of
deletions. This revision says so plainly and narrows the deletions to what the requirements
actually forbid.

---

## Surfaced premise conflicts

Three. The owner is not reachable, so each is recorded loudly with dependent conclusions marked.

### PC-1 — Gate A is an owner-classification defect, and the fix touches an Item 1 seam

*(Approved in mechanism by the design review, which confirmed the diagnosis first-hand against the
adapter. Retained here with M6's correction and M7's exact quote.)*

A constraint declared inside a concrete `PartUsage` reports its owner as the enclosing **package**.
The adapter carries the usage on `owner.owner` and the package on `owner.owning_definition` —
observed at `tests/fixtures/catf_mfe_model/extraction_snapshot.json:658-668`.
`constraint_lowering.py:1184` reads only `owning_definition`, so `prepare_constraint_usages` routes
the constraint to `_expand_package_owner` (`constraint_lowering.py:458-461`), which returns
`((sanitize_qualified_name(usage.identity.qualified_name or owner_qn), ""),)` — the constraint's own
QN as owner instance path, and an empty occurrence scope.

Both design-attribute key forms then key off the wrong root. For `part the_host { attribute gain = 40.0; }`
in package `gate_a`, extraction emits `gate_a__the_host__gain` correctly
(`parameter_groups.py:140,189-190`; shape confirmed real at
`tests/fixtures/chain_override_probe/extraction_snapshot.json:263-272`), but the occurrence-scoped
form builds `gate_a__the_host__positive__gain` (overshoots by the constraint's own name) and the
owner-def form builds `gate_a__gain` (undershoots by the usage). The target-QN form cannot help: for
a self-named actual the reference target is the constraint's own formal
(`tests/fixtures/plant_values/extraction_snapshot.json:328`). Resolution reaches
`terminal_disposition(strict=True)` and generation fails.

**The conflict.** Delivering SR-R20 requires a `part_usage` owner branch — touching
`prepare_constraint_usages`, an Item 1 seam SR-R06 says not to rework.

**B1, restated on true ground (M6).** Rev 1 argued "no existing constraint is usage-owned." That is
false: nine exist, all in `catf_mfe_model` (snapshot lines 478, 660, 1067, 1339, 1654, 1699, 2869,
2914, 2959). They cannot move bytes because all 65 catf constraints are `plain_usage` form and land
`unassessed_form`, so `is_excluded_usage` short-circuits at `constraint_lowering.py:761` *before*
owner dispatch — pinned by `test_constraint_migration_mapping.py:104-117`. The correct claim is
therefore stronger, not weaker: **no *admitted* usage-owned constraint exists today, so the new
branch has zero currently-passing cases to preserve.** That is what makes it extension rather than
rework.

### PC-2 — the entry-point backfill is not post-build mutation

*(Confirmed independently by the review.)* `_build_agg_input_source` is reachable only from the Step
6.7 loop at `graph_builder.py:331-337`; `ComputationGraph` is constructed at `:436`. The backfill
runs strictly before the graph exists. D-1 is not implicated, and SR-R16's stated basis is wrong.

The real defect survives: the backfill at `:1333` reads
`new_entry_points.get(ep_qn) or entry_points.get(ep_qn)`, so it can shadow an entry point created by
the *calculation* path, not just an earlier aggregation. The mutation is cross-source and
order-dependent. That — invariant I5 — is the ground the deletion stands on. SR-R16's text should be
amended to its true basis when the spec is next touched.

### PC-3 — V11's scope is narrower than "one mint point" implies (new)

Discovered while rebuilding the table. `_fallback_entry_points` has exactly one writer:
`dependency_backtracker.py:635`, on the calculation ladder's Step-4 fall-through. Nothing in
`graph_builder.py` or `input_resolver.py` ever adds to it. It reaches `ComputationGraph` at
`graph_builder.py:440` (field `resolution/models.py:551`, `exclude=True`) and is read only by
`collect_uncovered_params` (`:800-845`) and `collect_unwired_fallthrough` (`:848-875`). V11 itself is
the hard abort raised on a non-empty collector result, at `cli/__init__.py:278-291` and again on the
extended graph at `constraint_lowering.py:1542-1544`.

**Consequence: aggregation-minted entry points are invisible to V11 today.** A naive "one mint
point" would either start feeding them in — turning currently-green fixtures red — or would not,
making the unification asymmetric in a way the design must state rather than hide.

**This design takes the second branch and declares it.** The mint point records V11 membership only
for the calculation-binding consumer, preserving today's exact scope (invariant I10). Widening V11
to aggregation is a real question, but it is a *coverage-scope* decision, which SR-R07 assigns to
Item 3 (Gate B). Item 2 must not decide it silently by refactor. Flagged for Item 3.

### PC-4 — the calculation consumer cannot express the reference as written (new, implementation)

Discovered building SR-A02's fixture. `ProducerRequest.reference` is specified as the reference as
written, never pre-split. The constraint consumer has that — `FeatureReferenceFact.source_name`.
The calculation consumer does not: binding extraction resolves the reference to its referent's
qualified name and discards the written name. For a self-named binding `in gain = gain` the
referent is the calc usage's *own formal*, so the reference arrives as
`SharedProducer::the_rig::scaler::gain`. `raw_expression` does not carry it either — live it holds
the debug rendering `'FeatureReferenceExpression -> …'`, and it is empty in all 247 bound bindings
across every committed snapshot, on both routes.

**Consequence.** Key form 15 (occurrence-materialized QN) is structurally unreachable from the
calculation consumer, and rows 16-20 all key on the target QN or a leaf name. So one usage-owned
attribute read by both a calc input and a constraint actual yields **two** entry points, not one.
That is I9 falsified and SR-A02 undeliverable by table unification. Pinned as a recorded
known-incomplete state by `tests/fixtures/shared_producer/` (see its `PROVENANCE.md`).

**Resolution (orchestrator ruling, agent-grade, 2026-07-19).** Preserve byte identity and I10; do
not infer the written reference from the formal name. The exact structural recovery
(`referent_qn == {usage_qn}::{param_name}` → the written reference was `param_name`) was measured:
it newly resolves **22 self-named bindings across six existing fixtures**, all single-consumer, so
it fixes no wrong value — each per-consumer entry point already carries the correct modeled
default — while renaming entry-point identity across six generated surfaces and shrinking
`fallback_entry_points` membership ahead of Item 3's vacuity proof. *Rejected on that basis.* The
correct fix is carrying the written reference through extraction and the snapshot format, which is
a coordinated `agentic-mbse` + codegen change **folded into Item 4**, whose versioned-schema and
skew machinery is what it needs. SR-A02 completes there, on real data.

### Residual — `param_group` on LocalTerm mints

An entry point minted by the aggregation LocalTerm path carries `param_group=None`, before and
after Item 2: `group_deriver.classify` does not claim that QN shape. The parameter still emits,
via the group rebuild that follows aggregation module construction, so nothing is dropped. Item 2
fixed the missing *default*, not the field — populating it is a classification question in
`group_deriver`'s domain, ruled out of scope (orchestrator, 2026-07-19). Recorded here so Item 4
or Item 10 picks it up consciously if it matters there. Pinned by
`test_localterm_entry_point_is_rendered_in_a_parameter_group`.

### Residual tension worth a reviewer's eye

D11 restricts name-based key forms to the lenient consumers. SR-R14 says strictness differs *only*
at terminal miss, so a policy-restricted key form is technically a second fork. The restriction is
byte-preserving — the constraint ladder's eleven existing lookups are *all* exact, so it forbids
nothing the constraint consumer does today — and it is declared as data on one table rather than as
three code paths. But it does refine SR-R14's text, and I would rather surface that than let it pass
as an implementation detail.

---

## Related Artifacts

- **Stage brief:** `briefs/design.md` · **Spec:** `spec.md` · **Review:** `design-review.md`
- **Normative architecture:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  — invariants 19-26 (`:172-195`), D-1 (`:284-289`), D-2 (`:290-298`)
- **Predecessor:** `.project/active/constraint-lifecycle-occurrence-demand/{design,evidence,audit}.md`

---

## Research Findings

Full lookup inventory in Appendix A. Load-bearing findings only here.

- **The three ladders make ~24 distinct lookups plus 7 non-registry scan arms**, not twelve. The
  calculation chain path alone is `5 + (S+1)` registry calls for a consumer scope of `S` segments.
- **Almost all of them are exact keyed lookups.** All four `OutputRegistry` accessors are bare
  `dict.get` with no case folding (`core/output_registry.py:172-196`). Correction to rev 1:
  `register_alias` (`:125-138`) is *first-wins with a DEBUG line*, not a raise site — only the
  scoped, SysML-QN, and scoped-alias namespaces raise on collision.
- **Exactly four behaviors actually guess.** The calculation bare-name multi-candidate first-pick
  (`dependency_backtracker.py:846-856`), `_find_literal_redefinition`'s warn-and-return-first
  collision arm (`graph_builder.py:1257-1267`), `ChainRedefinitionFollow`'s case-insensitive
  first-`break` match (`input_resolver.py:171-179`), and the calculation dotted-arm first-hit scan
  (`dependency_backtracker.py:790-793`).
- **The name-based forms that are *not* guesses carry real coverage.** The leaf-unique fallback
  (`:795-813`) returns `None` unless `len(cands) == 1` — pinned by
  `test_def_owned_leaf_ambiguous_refuses` (`test_matcher_fixes_item7.py:89-95`). The bare-name unique
  arm (`:842-843`) is likewise unambiguous. Both refuse exactly as SR-R12 requires; what they do is
  name-based *candidate identification*, which SR-R12 does not forbid.
- **The scope climb is not an ordered rung.** It collects every hit into a set and returns only on
  `len(climbed) == 1` (`:715-723`), and its key set is a strict superset of rungs 1 and 2 — the
  `i = len(segments)` and `i = 0` iterations rebuild those exact keys, so two of its `S+1` calls are
  guaranteed-dead re-queries.
- **The self-reference guard is not uniform, in three separate ways.** It is absent from
  `_resolve_to_design_attribute` entirely, absent from `resolve_actual` entirely, and on the
  aggregation side lives at the driver rather than per-lookup — so a rejection skips to the next
  *strategy*, abandoning that strategy's remaining keys (`input_resolver.py:263-271`).
- **Three different lenient entry-point QN formulas exist** (`dependency_backtracker.py:76`;
  `input_resolver.py:281-282`; `graph_builder.py:1524-1525`), and `group_deriver` is available at
  only one of the three mint sites.
- **`resolution/` is the correct layer.** `core/__init__.py` declares
  `resolution → extraction, analysis, core`; `supplied_values.py:39-42` already imports this exact
  type set at module level.
- **Item 1's seams are pre-graph and copy-on-write** and are untouched by this design.

---

## Core Concept

**Separate the tier from the key form.** A tier is a claim about what class of thing may produce a
value — contract invariant 19 names two: a real producer channel, then a real design attribute under
exact qualified identity. A key form is one way of asking "is it here?" The ladders drifted not
because they try many key forms — they try about two dozen, and nearly all are exact — but because
each invented its own list, its own guard placement, and its own terminal behavior.

So the design is one ordered table of key forms, partitioned into the two tiers, declared as data in
one place. A consumer supplies a request and reads a result. It cannot add, reorder, or skip a key
form, and the guard and the terminal fork are applied once, by the table, for everyone.

**What unification buys, stated honestly.** Rev 1 claimed each guess had an exact twin already in the
tree, so the guesses could be deleted at no coverage cost. Review falsified that for two of three,
and re-verification confirmed it: an exact tier that runs *before* a guess and falls through to it is
a predecessor, not a replacement. The calculation leaf fallback reaches attributes owned by unrelated
part defs whose QN contains no consumer segment at all; `_find_literal_redefinition`'s leaf tier
fires only where `usage_type_map` has no entry, including the whole of `plant_value_shapes`, whose
map is empty (`supplied_values.py:256`).

So the deletions narrow to what SR-R12 actually forbids — **guessing among candidates**, not
name-based candidate *identification*. Four behaviors guess and die. The deterministic
unique-or-refuse forms survive as declared key forms, restricted to the lenient consumers, which is
where they already live. What unification still buys is real and is the point: one declared order, one
guard applied uniformly at every lookup instead of at three different granularities, one terminal
fork, one QN rule, and one place where drift becomes visible.

Gate A is separate and upstream — not a missing key form but a missing *scope*, because a constraint
owned by a concrete `PartUsage` is misclassified as package-owned.

---

## Key Bets

All `[INFERRED]`, agent-grade, challengeable.

- **B1.** No *admitted* usage-owned constraint exists today, so a `part_usage` owner branch added
  ahead of the package branch preserves every currently-passing case and is extension, not rework.
  *If false → Gate A leaves Item 2; Phases 0 and 2 park.* (Restated per M6; the nine
  `catf_mfe_model` usage-owned constraints are excluded upstream as `unassessed_form`.)
- **B2.** Every lookup in the three ladders is either an exact keyed lookup, a deterministic
  unique-or-refuse name-based form, or one of the four named guesses. *If false → a consumer
  silently loses coverage at cutover, surfacing as a byte-identity diff.* (Rev 1's B2 claimed
  exact-twin coverage and was falsified; this is the weaker claim that survived re-verification.)
- **B3.** A constraint actual never legitimately reads a channel produced by its own constraint
  module. *If false → the uniform guard refuses a valid model and SR-R13 is wrong.*
- **B4.** The QN rule in D9 reproduces all three existing formulas byte-for-byte. *If false →
  entry-point identity moves and every generated baseline shifts.* This is the largest
  byte-identity risk in the plan and Phase 5 gates on it.
- **B5.** Raising lenient terminal misses to one uniform warning needs no severity schema.
  *If false → SR-R15 defers to Item 4 and Item 2 records the asymmetry.*

### Verdicts on the spec's five flagged bets

| Spec bet | Verdict |
|---|---|
| Two positive rungs only (SR-R11) | **Confirmed as two tiers, not two rungs.** ~24 lookups exist; the tier count is the contract's real claim. |
| Uniform self-reference guard (SR-R13) | **Confirmed, and the drift is worse than the spec knew** — the guard is absent from two paths and misplaced on a third. |
| Entry points written once (SR-R16) | **Challenged on its basis** (PC-2); requirement survives on order-dependence, narrowed by PC-3. |
| Aggregation joins the shared request (SR-R10) | **Confirmed for the table and the guard; partially challenged for the mint point** — V11 scope must stay calculation-only (PC-3). |
| Lenient visibility without a schema (SR-R15) | **Confirmed.** Note per m4 that today's Strategy-2 warning is conditional on collision, so the volume increase is larger than rev 1 implied. |

---

## Key Decisions

- **D1. The procedure lives in `resolution/producer_resolution.py`.** `core/__init__.py` declares
  `resolution → extraction, analysis, core`, and `resolution/` is the lowest layer that may legally
  see all six required types; `EntryPoint` and `InputSource` already live there, and
  `supplied_values.py:39-42` is precedent for importing the rest at module level.
  `analysis/constraint_lowering.py` consumes it via a deferred import, the pattern already in use at
  `constraint_lowering.py:1396`. This is not a clean layering: `resolution/` already reaches up into
  `analysis/` for `DesignAttributeData`, and now two `analysis/` modules reach back down into
  `resolution/` for the resolver — a second deferred edge, on top of the one Item 1 left. The
  placement is the least-bad of the three considered, not a tidy one. *Rejected: `core/` (rev 1's choice — C3 showed three of six types
  live above it, so the strict-leaf property that was the entire justification would be destroyed);
  a new leaf package (same defect, plus it would require relocating types across three layers).*
- **D2. One ordered key-form table, declared as data, with a `policies` attribute per form.** Each
  entry declares its tier, its key expression, and which terminal policies may reach it. Ordering
  and admissibility are readable in a test. *Rejected: an `if` chain (order implicit, the exact
  failure that let three ladders drift); a single table with no policy attribute (would either
  expose name-based forms to the strict constraint consumer, changing its behavior, or force
  deleting forms that carry live coverage).*
- **D3. Consumer identity, scope, formal name, and terminal policy are request fields.** One
  predicate serves all three consumers. *Rejected: a `consumer_kind` enum branched on inside the
  resolver — a consumer-specific ladder in disguise.*
- **D4. The guard is applied by the table at every lookup, and a rejection continues the table.**
  This fixes all three of the current asymmetries at once. *Rejected: preserving per-ladder guard
  placement (that asymmetry is the drift).*
- **D5. Ambiguity within a key form yields no result and records the tied candidates.** The strict
  error names them (SR-A04); the lenient path warns. *Rejected: raising from inside a key form
  (would make lenient consumers strict by accident).*
- **D6. The scope climb is a declared *tier-1 terminal search*, not a table row.** It runs after the
  tier-1 rows are exhausted, keeps its collect-then-require-unique semantics, and skips the two
  iterations that duplicate rows 1 and 2. *Rejected: modeling it as an ordered row (C5 — loses the
  ambiguity guard that is its whole justification and re-queries dead keys).*
- **D7. `ChainRedefinitionFollow` survives as a lenient-only key form, made case-sensitive and
  refusing on multiple matches.** Its recursion and cycle guard are real mechanism; only the
  case-insensitivity and the first-`break` are indefensible. *Rejected: rev 1's re-keying to
  `usage_type_map` (C2 — loses untyped usages, cannot build a key past recursion hop one, needs
  `owning_part_qn` that is not in scope, and breaks `plant_value_shapes`, whose map is empty);
  deleting it outright (aggregation loses chain-redefinition coverage).*
- **D8. The resolver owns the entry-point QN and its modeled default. It does not construct
  `EntryPoint`.** `group_deriver` is available at only one of the three mint sites, and pulling
  `ParameterGroupDeriver` into the resolver's context would drag `analysis` into a type that
  `analysis` must import. Consumers construct `EntryPoint` from the resolver's QN and default,
  keeping `param_group` classification where it already is. "One mint point" is therefore **one QN
  and default authority**, which is weaker than rev 1 claimed and is stated as such. *Rejected:
  growing the result type to carry all seven `EntryPoint` fields (M1 — forces `group_deriver` into
  the context); leaving QN derivation with consumers (the three formulas stay unreconciled).*
- **D9. One entry-point QN rule, chosen to reproduce all three existing formulas.** The rule is
  `f"{consumer_eqn}__{param_name}"`, where `param_name` is the consumer's declared formal name when
  it has one, and the flattened reference (`ref.replace(".", "_")`) when it does not. This
  reproduces `dependency_backtracker.py:76` (calc bindings have formals),
  `input_resolver.py:281-282` (aggregation terms have none, so the flattened reference is used), and
  `graph_builder.py:1524-1525` (a LocalTerm's bare attribute name flattens to itself) without moving
  a byte. *Rejected: keying always on the reference (moves every calculation entry point); keying
  always on a leaf (`input_resolver.py:276-279` documents that this collides sibling part-usage
  inputs).*
- **D10. Gate A is fixed by owner classification, with a hardened predicate.** A `part_usage` branch
  is taken when `owner.owner` is non-`None` and its `kind` is in a declared allowlist. Because
  `kind` is `type(element).__name__` — an open set fixed by the syside runtime, not by agentic-mbse
  (`constraint_extraction.py:193-200`) — and because the replay route reads JSON with no live object
  to test structurally, the branch **raises on an unrecognized non-`None` owner kind** rather than
  falling through to the package branch. *Rejected: `SysideAdapter.is_instance` (unavailable on the
  snapshot route); a bare `== "PartUsage"` compare (M5 — fails closed and silently on any syside
  rename or subclass).*
- **D11. Name-based key forms are declared lenient-only.** They are unreachable from the constraint
  consumer, which is exactly where they are unreachable today — all eleven of `resolve_actual`'s
  lookups are exact. This is byte-preserving on both sides and is surfaced as a refinement of
  SR-R14 (see the residual tension above). *Rejected: exposing them to strict consumers (changes
  constraint behavior and violates contract invariant 20's spirit); deleting them (C1, C2 — real
  coverage loss).*
- **D12. `_is_calc_def_owned` stays at the point of use, not at map construction.** Rev 1 moved it to
  map construction; C1's last point is right that this is not obviously behavior-neutral for the
  constraint consumers reading the same map today unfiltered. Applying it only inside the
  leaf-unique key form preserves both behaviors exactly. *Rejected: rev 1's map-construction filter
  (silently changes what constraint tier-2 forms can see).*

---

## Data Contracts

Names are proposals; the plan may refine names but not ownership or semantics.

### `ProducerRequest` (frozen)

| Field | Type | Meaning |
|---|---|---|
| `consumer_eqn` | `str` | Producing-module EQN of the asker. Sole input to the guard and to D9's QN rule. |
| `reference` | `str` | The reference as written. Never pre-split by the caller. |
| `param_name` | `str \| None` | The consumer's declared formal name, where it has one. Drives D9. |
| `consumer_scope` | `str` | Dotted scope the reference is read in. |
| `instance_path` | `str \| None` | Occurrence instance path, for the occurrence-scoped and direct-channel forms. |
| `owner_def_qn` | `str \| None` | Owning-definition QN, for the def-scoped design-attribute form. |
| `policy` | `STRICT \| LENIENT` | Read once, after the table. Also gates which key forms are admissible (D11). |
| `diagnostic_context` | `str` | Consumer-supplied context for error and warning text. |

### `ProducerResolution` (frozen)

| Field | Type | Meaning |
|---|---|---|
| `outcome` | `MODULE_OUTPUT \| DESIGN_ATTRIBUTE \| ENTRY_POINT` | What resolved. |
| `identity` | `str` | Channel, design-attribute QN, or minted entry-point QN. |
| `default_value` | `str \| None` | Modeled default, for `DESIGN_ATTRIBUTE` and `ENTRY_POINT`. |
| `simple_name` | `str \| None` | Supplied for `ENTRY_POINT` so the consumer can build the `EntryPoint` (D8). |
| `records_v11` | `bool` | True only for the calculation-binding consumer's lenient miss (PC-3, I10). |
| `key_form` | `str \| None` | Which form produced it. Makes precedence observable (SR-A03). |
| `attempted` | `tuple[str, ...]` | Forms tried, in order. Required strict-error context. |
| `ambiguous_candidates` | `tuple[str, ...]` | Identities that tied within a form. |

### `ProducerContext`

Named to avoid the existing `ResolutionContext` at `input_resolver.py:40` (M4), which is deleted with
`resolve_input`. Holds the `OutputRegistry`, `canonical_channels`, the by-QN design-attribute map,
the design-attribute list (for name-based forms), `redefinitions`, `usage_type_map`, and the calc-def
QN set used by D12's filter. Built once per run.

### Exact APIs

| API | Ownership |
|---|---|
| `resolve_producer(request, context) -> ProducerResolution` | `resolution/producer_resolution.py`. The only positive-resolution entry point in the tree. |
| `KEY_FORMS: tuple[KeyForm, ...]` | Same module. Ordered, tier-partitioned, policy-annotated. |
| `terminal_disposition(...)` | Moves here from `dependency_backtracker.py:38-77`. Called only by `resolve_producer`. |

Negative ownership: no consumer constructs a registry key, splits a reference, or calls
`terminal_disposition`.

---

## Architecture

### The key-form table

Rebuilt from the code (Appendix A). Tier 1 exhausts before tier 2. `L` marks lenient-only (D11).

**Tier 1 — real producer channel**

| # | Key form | Origin |
|---|---|---|
| 1 | scoped, consumer-scope prefixed | calc `:651`, constraint `:176`, agg A `:86` |
| 2 | scoped, de-indexed occurrence scope | constraint `:184` |
| 3 | scoped, bare reference | calc `:657`, agg A `:98` |
| 4 | alias, consumer-scope prefixed | constraint `:192`, agg A `:89` |
| 5 | alias, de-indexed / bare | constraint `:200`, agg A `:101`, calc `:689` |
| 6 | structured scoped alias, scope-prefixed | calc `:678-680`, constraint `:223` iter 1 |
| 7 | structured scoped alias, de-indexed scope | constraint `:223` iter 2 |
| 8 | structured alias, unscoped | calc `:682-684`, constraint `:232` |
| 9 | structured alias, de-indexed prefix | constraint `:234` |
| 10 | SysML QN, sanitized | calc `:735-737`, agg B `:128` |
| 11 | direct channel construction, membership-checked | agg E `:215-218` |
| 12 `L` | leaf recombined with parent part (scoped, then alias) | calc `:544`, `:546` |
| 13 `L` | leaf recombined with consumer scope (scoped, then alias) | calc `:554`, `:556` |
| 14 `L` | chain-redefinition follow — case-sensitive, refuses on multiple (D7) | agg C `:171-188` |

**Tier-1 terminal search (not a row, per D6):** the scope climb. Iterates ancestor prefixes
`i = S-1 … 1`, collecting distinct non-self-referential channels, returning only on exactly one.
Gated on `reference.count(".") >= 2`. The `i = S` and `i = 0` iterations are omitted as exact
duplicates of rows 1 and 3.

**Tier 2 — real design attribute under exact qualified identity**

| # | Key form | Origin |
|---|---|---|
| 15 | occurrence-materialized QN | constraint `:259-260` |
| 16 | sanitized target QN | calc `:824-827`, constraint `:268-269` |
| 17 | owner-def QN | constraint `:284-285` |
| 18 `L` | dotted arm: `(first-segment, leaf)` pair, refusing on multiple | calc `:790-793`, re-typed to refuse |
| 19 `L` | leaf-unique across files, calc-def-owned filtered (D12) | calc `:802-813` |
| 20 `L` | bare-name unique arm only | calc `:834-843` |

Rows 12, 13, 18, 19, 20 and the chain-follow in 14 are the name-based forms restricted to lenient
consumers. Every one either already refuses on multiple candidates or is re-typed here to do so.

**Guard.** Every tier-1 hit is tested with one predicate — `channel.rsplit("__", 1)[0]` against
`request.consumer_eqn` — before it is returned. A rejection skips the candidate and continues the
table, fixing all three current asymmetries (D4).

### Terminal miss

Read `request.policy` once, after the table and the climb.

- **STRICT** raises `CodeGenerationError` naming usage, formal, reference as written, `attempted`
  forms, and any tied candidates. Today's error carries only three strings and names no attempted
  classes; SR-R14 requires them.
- **LENIENT** derives the entry-point QN by D9's rule and its modeled default, sets `records_v11`
  per I10, and emits one warning. The consumer builds the `EntryPoint` (D8).

### Consumer convergence

- **Calculation** (`dependency_backtracker.py`): `_resolve_binding_via_registry` becomes a request
  builder (`policy=LENIENT`, `param_name` = the calc formal) and a result reader. It adds the
  returned QN to `_fallback_entry_points` when `records_v11` is set, preserving V11 scope exactly.
  The four dispatch methods and `_resolve_to_design_attribute` are deleted; their surviving forms
  are rows 12, 13, 18, 19, 20.
- **Constraint** (`constraint_lowering.py`): `resolve_actual` becomes a request builder with
  `policy=STRICT`. Its eleven lookups become rows 1-11 and 15-17; no name-based form is reachable,
  matching today exactly.
- **Aggregation** (`input_resolver.py`, `graph_builder.py`): `resolve_input`, `AGG_STRATEGIES`, and
  the old `ResolutionContext` are deleted. `_build_agg_input_source` and the LocalTerm path build
  lenient requests; the register/backfill pair goes, and the LocalTerm path gains the warning it
  never had.

### Gate A path

`prepare_constraint_usages` gains a `part_usage` owner branch ahead of the package branch, taken when
`owner.owner` is non-`None` with an allowlisted kind, raising on an unrecognized kind (D10). It
returns a real owner instance path and occurrence scope from `usage.owner.owner.qualified_name`,
after which key form 15 builds `gate_a__the_host__gain` and hits. No new key form.

**Fixture shape constraint.** The Gate A fixture must use the def-typed constraint form with an
explicit self-named actual (`assert constraint viability : 'Viability Threshold' { in gain = gain; }`),
mirroring `tests/fixtures/plant_values/library.sysml:107`. The *inline* form has no formal bindings
(`formal_bindings` is `None` at `constraint_lowering.py:1187`) and never reaches resolution — an
inline fixture would silently fail to certify Gate A, the exact substitution risk SR-R21 guards.

---

## Required Invariants

- **I1 — one authority.** `resolve_producer` is the only positive-resolution path. No consumer
  builds a registry key or splits a reference.
- **I2 — declared order and admissibility.** `KEY_FORMS` is one ordered sequence; a test reads it as
  data and pins both order and per-form policy admissibility.
- **I3 — refuse, never guess.** No key form takes an arbitrary first pick among multiple candidates.
  Name-based *identification* is permitted; guessing among what it finds is not.
- **I4 — one terminal fork.** Strict and lenient differ only after the table and the climb, plus the
  declared admissibility in I2.
- **I5 — identity-determined defaults.** An entry point's default is a function of its identity and
  the reference that mints it, not of consumer iteration order. No backfill.
- **I6 — uniform guard.** One predicate, applied at every tier-1 lookup for every consumer, skipping
  the candidate and continuing.
- **I7 — visible lenient miss.** Every lenient terminal miss emits one warning.
- **I8 — Item 1 seams unchanged.** `resolve_logical_demand`, `select_group_source`, and
  `enrich_graph_design_attributes` are not modified. `prepare_constraint_usages` gains one branch;
  its three existing branches are unchanged.
- **I9 — convergence is a tier-2 property. FALSIFIED for the self-named shape at implementation
  time; see PC-4.** The claim was that two consumers of one design attribute converge because both
  resolve *positively* to the same QN through tier 2. That holds only when both consumers can
  express the same reference, and they cannot: the calculation consumer has no access to the
  reference as written. The constraint consumer still converges on the source QN; the calculation
  consumer still mints per-consumer. SR-A02 is **not delivered by Item 2** and is referred to Item 4
  (PC-4). Lenient-miss entry points remain per-consumer by construction.
- **I10 — V11 scope is preserved, not widened.** Only the calculation-binding consumer's lenient
  miss sets `records_v11`. Aggregation entry points stay outside `fallback_entry_points`, exactly as
  today. Widening is Item 3's (PC-3).

---

## Forced differences

Every difference from today's generated bytes, with the requirement that forces it. Anything not
listed here is a byte-identity failure, not an accepted change.

| # | Difference | Forced by |
|---|---|---|
| 1 | A colliding leaf-name literal redefinition refuses instead of returning the first value, so `literal_default` is `None` and the term's compilability flips to `MANUAL_REQUIRED`. **This changes a compilability verdict, not just a diagnostic.** | SR-R12, SR-R17, inventory row 4 |
| 2 | Every lenient terminal miss emits one WARNING; previously only the multi-hop-chain shape did, and every other miss was DEBUG or silent. | SR-R15 / I7 |
| 3 | The strict terminal error names the key forms attempted and any tied candidates. | SR-R14 |
| 4 | The aggregation LocalTerm mint carries its modeled default; it was unconditionally defaultless. Reachable only on `agg_localterm_probe`, a new fixture, so no pre-existing baseline moves. | SR-R16, orchestrator ruling 4 |
| 5 | Two minters of one entry-point QN carrying different defaults leave it defaultless and warn, rather than the later writer backfilling over the earlier. | SR-R16 / I5, review note 4 |

No committed fixture's generated bytes moved under any of these: differences 1 and 5 have no corpus
population, 2 and 3 are diagnostics, and 4 is confined to the new fixture. The byte-identity gate is
green across every pre-existing fixture.

## Deletion Inventory

Narrowed per C1, C2, and Recommendation 1(b). Each row says what dies and what survives.

| # | Deleted | Survives as |
|---|---|---|
| 1 | The three ladders' separate orderings, guard placements, and terminal behaviors — `_resolve_chain_dispatch`, `_resolve_reference_dispatch`, `_resolve_reference_via_registry` (`dependency_backtracker.py:519-744`), `resolve_actual`'s sequence (`constraint_lowering.py:172-290`), `AGG_STRATEGIES` / `resolve_input` (`input_resolver.py:228-290`) | rows 1-20 plus the climb, in one table |
| 2 | The calculation bare-name **multi-candidate first-pick and same-file tiebreak** (`dependency_backtracker.py:846-856`) | row 20 keeps the `len(candidates) == 1` arm only |
| 3 | The dotted arm's **first-hit-wins scan** (`:790-793`) | row 18, re-typed to refuse on multiple |
| 4 | `_find_literal_redefinition`'s **warn-and-return-first collision arm** (`graph_builder.py:1257-1267`) | the leaf tier survives, refusing when `len(set(hits)) > 1` |
| 5 | `ChainRedefinitionFollow`'s **case-insensitivity and first-`break`** (`input_resolver.py:171-179`) | row 14, case-sensitive and refusing on multiple |
| 6 | The **register/backfill pair** (`graph_builder.py:1322-1342`) and the **silent** LocalTerm mint (`:1524-1540`) | one QN-and-default authority (D8/D9); LocalTerm gains a warning |
| 7 | The old `ResolutionContext` (`input_resolver.py:40`) | `ProducerContext` (M4) |

Retained-with-reason, recorded as SR-R41 deviations: the leaf-unique fallback (`:795-813`), the
bare-name unique arm, the dotted pair form, the `usage_type_map`-less leaf tier, and the
chain-redefinition follow — all because C1 and C2 showed no exact form covers their populations, and
all already satisfy or are re-typed to satisfy I3.

**Helpers (SR-R42).** `_get_parent_part_for_usage` (`:486-494`) moves to the resolver with rows 12
and 13. `_consumer_scope_dotted` (`:496-506`) moves as the `consumer_scope` derivation.
`_is_calc_def_owned` moves with row 19 per D12. `_deindexed_scope` moves with rows 2, 5, 7, 9.
`_reference_dotted` and `occurrence_scope` stay in `constraint_lowering.py` — both have surviving
callers (`supplied_values.py:453`; the owner-expansion path this design extends).

**Tests (SR-R43).** Private-mechanics tests of deleted dispatch internals are deleted. But rev 1
misclassified `test_matcher_fixes_item7.py:79-137` (C1): `test_def_owned_leaf_unique_resolves` and
`test_leaf_unique_ignores_calc_io_collision` pin **observable** resolution outcomes, and under the
narrowed deletions they now have somewhere to migrate — rows 19 and 20 preserve their behavior.
Likewise `test_silent_failure_family3.py:73-96` migrates with its assertion changed from
warn-and-first-wins to refusal. The six precedence pins at `test_constraint_resolver.py:303-420`
(m1: `:303`, not `:305` or `:283`) are the migration guard, addressed in Phase 3.

---

## Non-Goals

- Item 3's Gate B coverage scope — **including whether V11 should widen to aggregation entry
  points (PC-3)**. Item 4's diagnostic severity schema. Item 5's relocated whole-tree proof.
- Reworking Item 1's three resolution seams or reopening its deviations.
- General typed-path or part-index refactors (`[CONSTRAINT-ARCH-UNIFY]` scope item 3).
- Public late fill, placeholder completion, post-build graph or default mutation (D-1).
- The stellarator acceptance and WI-027 passthrough removal (register row 12).
- Whether `Compilability.MANUAL_REQUIRED` remains the right label.

---

## Potential Risks

- **R1 — Gate A leaves the item (PC-1/B1).** *Control:* phase order puts it first.
- **R2 — a surviving name-based form's population is not what Appendix A says (B2).** *Control:*
  per-consumer cutover in separate phases, each gated on full suite plus byte identity.
- **R3 — D9's QN rule moves entry-point identity (B4).** The largest byte-identity risk; rev 1 had
  no risk entry for it (M2). *Control:* Phase 1 pins the rule against all three current formulas in
  unit tests *before* any consumer is cut over, and Phase 5 gates on byte identity.
- **R4 — the guard's new uniformity changes resolutions.** Applying it to `_resolve_to_design_attribute`
  and `resolve_actual`, where it is absent today, can newly refuse something. *Control:* Phases 3
  and 4 gate on byte identity; any refusal is enumerated with the requirement forcing it.
- **R5 — warning volume.** I7 converts DEBUG lines to warnings, and per m4 the Strategy-2 warning is
  today conditional on collision, so the increase is larger than rev 1 implied. Existing suites
  assert DEBUG silence (`test_dependency_backtracker.py:121,142`;
  `test_output_registry_construction.py:1009`). *Control:* migrated as recorded behavior changes.
- **R6 — the strict error's added context changes pinned bytes** (`test_constraint_resolver.py:255,266`).
  *Control:* recorded as intended under SR-R14.
- **R7 — the climb's extraction from the table changes ordering.** It now runs after all tier-1 rows
  rather than mid-sequence. *Control:* `test_res08_consumer_scope_paths.py:82` plus byte identity.
- **R8 — m3's latent abort.** `_find_literal_redefinition` returns `None` for the whole scan on the
  first non-numeric literal (`graph_builder.py:1250-1251`) rather than skipping it. Whatever
  replaces it must not reproduce this by accident; if it is fixed, that is a behavior change to
  enumerate, not a silent improvement.

---

## Validation Approach

New defect tests are authored once and run unchanged at RED coordinate `287afc4` and at candidate
GREEN, with no conditional (SR-R50/R51). RED must fail for the named defect.

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run --frozen pytest -q -rs tests/                                 # Item 1 baseline 3009p/26s
uv run --frozen pytest -q -rs tests/conformance/test_baselines.py    # byte-identity gate
uv run --frozen mypy src/                                            # baseline 76 errors, must not grow
uv run --frozen ruff check src/                                      # clean
```

Real generated execution runs in the agentic-mbse venv:

```bash
TEAX_SIMKIT_PATH=../teax/packages/teax-simkit PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
  /home/reid/1cfe/agentic-mbse/.venv/bin/python -m pytest -q -rs -o addopts= -m execution tests/execution/
```

Generated baselines are generator-owned bytes: never hand-edited or reformatted (SR-R31). Item 1's
acceptance file and `constraint_occurrence_demand/` fixtures are frozen controls (SR-R32).

---

## Phased Implementation Plan

Test-first, RED before GREEN on public fixtures. Each phase has a stop condition that halts the item
rather than working around it.

**Phase 0 — Gate A fixtures and the RED surface.** ✅ **Complete** (see Implementation Notes). Author `tests/fixtures/gate_a/` (usage-owned
literal attribute on a concrete `PartUsage`, def-typed constraint with a self-named actual, no
passthrough) **and** a genuinely package-owned constraint fixture — one declared directly in a
package body, which no fixture in the repo exercises today (M6). Author unchanged RED nodes for
SR-A01, SR-A04, SR-A05, SR-A06. Run at `287afc4`.
*Validation:* each node fails for its own named defect; Gate A must fail at
`terminal_disposition(strict=True)`, not at parse or setup.
*Stop condition:* Gate A fails anywhere other than the predicted terminal raise → PC-1's diagnosis
is wrong; stop and re-diagnose before writing resolver code.

**Phase 1 — the resolver, unconsumed.** ✅ **Complete.** Add `resolution/producer_resolution.py` with the request,
result, `ProducerContext`, the `KEY_FORMS` table, the climb, and `terminal_disposition` moved in. No
consumer wired. Unit tests pin the table order and policy admissibility as data (I2), refusal
behavior (I3), the guard (I6), both terminal policies (I4), and — critically — **D9's QN rule
against all three current formulas** (R3).
*Validation:* full suite unchanged; mypy and ruff clean.
*Stop condition:* D9's rule cannot reproduce one of the three formulas → B4 is false; stop and
re-derive before any cutover.

**Phase 2 — Gate A.** ✅ **Complete** (see Implementation Notes). Add the hardened `part_usage` owner branch (D10). Wire nothing else.
*Validation:* SR-A01 GREEN with generated TEAx execution returning the pinned verdict, and changing
the literal changing it (SR-R22); the package-owner fixture still routes to the package branch; an
unrecognized owner kind raises rather than falling through. Full suite and byte identity green.
*Stop condition:* any baseline byte moves — an existing constraint was silently reclassified, which
B1's extension argument does not cover. Stop and surface.

**Phase 3 — constraint consumer.** ✅ **Complete** — six precedence pins unchanged. Cut `resolve_actual` over; delete its ordering. No name-based
form is admissible to it, so its behavior should be unchanged. Address the six precedence pins per
SR-R33.
*Validation:* full suite; SR-A03, SR-A04, SR-A06 GREEN; byte identity.
*Stop condition:* a precedence pin changes with no requirement to point at.

**Phase 4 — calculation consumer.** ✅ **Complete** — V11 membership unchanged. Cut `_resolve_binding_via_registry` over; delete inventory rows
1-3 and move the helpers. Preserve V11 population via `records_v11` (I10).
*Validation:* full suite; SR-A09 GREEN on the calculation route; byte identity; the migrated
`test_matcher_fixes_item7` coverage passes against rows 19 and 20.
*Stop condition:* a byte-identity diff not explained by an enumerated forced difference, or any
change in `fallback_entry_points` membership.

**Phase 5 — aggregation consumer.** ✅ **Complete** — EP-key manifest zero-diff. Cut `_build_agg_input_source` and the LocalTerm path over;
delete inventory rows 4-7. Carries R3 and R8.
*Validation:* full suite; SR-A05, SR-A07, SR-A09 GREEN across all three routes; byte identity —
with particular attention to `plant_value_shapes` (empty `usage_type_map`) and `catf_mfe`; generated
execution.
*Stop condition:* a default or an entry-point QN moves without an enumerated cause.

**Phase 6 — sweep and evidence.** ✅ **Complete** — see `evidence.md`. Deletion proof by source search (SR-A12); docstrings amended to
describe the one procedure, not to prohibit removed behavior (SR-R44); every retained path recorded
as an SR-R41 deviation with its reason. Live and same-checkout replay parity on the Gate A fixture,
replay labeled non-certifying (SR-A10, SR-R08). LC-I09 coordinates per acceptance row (SR-R52).
*Validation:* SR-A11, SR-A13.

---

## Implementation Notes

### Phase group 1 (Phases 0, 2, and Phase 1's de-risk pins) — 2026-07-19

Scope executed: Gate A's owner-classification fix with live coverage of both branches, plus
D9's QN-rule de-risk pins. The ladder cutover phases (3–5) were not started.

**Files changed**

| File | Change |
|---|---|
| `src/sysml_codegen/analysis/constraint_lowering.py` | `_concrete_usage_owner` (D10 allowlist classifier) and `_expand_part_usage_owner`; the `package` dispatch arm now discriminates between them |
| `src/sysml_codegen/resolution/producer_resolution.py` | New. Holds D9's `entry_point_qualified_name` only — no consumer wired |
| `tests/fixtures/gate_a/` | New. Usage-owned literal on a concrete `PartUsage`, def-typed constraint, self-named actual |
| `tests/fixtures/gate_a_package_owner/` | New. The genuinely package-owned control (M6) |
| `tests/conformance/test_gate_a_owner_classification.py` | New. Three live nodes plus the D10 refusal |
| `tests/unit/test_producer_qn_rule.py` | New. Nine D9 pins |
| `tests/execution/test_gate_a_execution.py` | New. SR-A01/SR-R22 under real simkit |
| `scripts/capture_extraction_snapshots.py`, `tests/conformance/conftest.py` | Both fixtures registered |

**Phase 0 — stop condition cleared, PC-1 confirmed first-hand.** Live extraction of `gate_a`
reports `owner.owner = IdentityFact(kind='PartUsage', qualified_name='GateA::the_host')` with
`owning_definition = package GateA`, and extraction emits the attribute as
`GateA__the_host__gain` — exactly PC-1's prediction. The live build fails at
`dependency_backtracker.py:62`, `terminal_disposition(strict=True)`, on
`GateA__the_host__viability.gain` — the predicted terminal raise, not parse or setup. Re-verified
by stashing the production fix and re-running: both Gate A nodes fail there, the D10 node fails
`DID NOT RAISE`, and the package-owner control passes on both sides as a preservation pin should.

**Phase 2 — Gate A live GREEN.** `owner_instance_path` is `GateA__the_host`; the self-named
actual resolves to `DESIGN_ATTRIBUTE GateA__the_host__gain`; generated simkit execution returns
`satisfied` with the literal at 40.0 and flips to `violated` at 5.0 (SR-R22). No passthrough
calculation in the model. Byte identity held with zero baseline movement, so no existing
constraint was silently reclassified — Phase 2's stop condition never fired and B1 survives.

**Phase 1 de-risk — B4 holds, with one leg unfalsifiable today.** D9's rule reproduces the
calculation formula (pinned by calling the real `terminal_disposition`) and the aggregation-term
formula (by calling the real `resolve_input`), and reproduces all 23 entry points the corpus
actually mints, all in `fusion_tea`. **The third leg has no corpus coverage:** the aggregation
LocalTerm mint (`graph_builder.py:1524-1525`) is never reached by any committed fixture. The five
aggregations carrying local terms (all in `solar_battery_model`) resolve every one positively. So
that leg is pinned structurally, and **Phase 5 owes it live coverage before cutting the LocalTerm
path over** — a byte-identity gate cannot protect a population of zero.

**Deviations from the design**

1. *Fixtures carry an unrelated calc.* `pipeline_builder.py:753` refuses a model with no calc
   definition at all, which the design's fixture sketch did not anticipate. Each fixture carries
   a `Doubler` calc on a separate part that neither produces nor consumes the constrained
   attribute. It is not the passthrough SR-A01 forbids, and being unrelated it cannot mask the
   defect by minting the attribute's entry point itself — confirmed by the RED re-run.
2. *The new branch sits inside the `package` arm, not ahead of it.* The design said "ahead of the
   package branch". Discriminating only within that arm is what makes the extension argument
   hold: a `PartUsage` nested inside a part def also reports `owner.owner` as a `PartUsage`, and
   an unconditional check ahead of the dispatch would have pulled those out of `_expand_part_owner`
   — reworking an existing branch, which B1 does not cover and I8 forbids. Same routing outcome,
   narrower blast radius.
3. *`owner_kind` still records the owning-definition kind.* `PreparedConstraintUsage.owner_kind`
   and `ConcreteConstraint.owner_kind` document `OwningDefinitionFact.kind`, so a usage-owned
   constraint keeps `"package"` there and only `owner_instances` changes. Minting a new
   `"part_usage"` value would have moved a vocabulary that reaches `resolution/models.py:374`, the
   constraint report, and `_exclusion_for`, for no requirement in scope.
4. *`LibraryPackage` is in the package-owner allowlist.* `library package` is a real syside type
   and `is_instance("Package")` accepts it, so a library-package-owned constraint reports
   `owner.owner.kind == "LibraryPackage"`. Omitting it would have made D10's raise fire on a shape
   that works today.

**Validation**

- Full suite `3025 passed, 32 skipped` (Item 1 baseline 3009/26; +13 new nodes, the rest from
  the two fixtures joining parametrized corpus sweeps). Zero failures.
- Byte identity: `tests/conformance/test_baselines.py` 17 passed; `git status` clean over
  `tests/fixtures/baseline_outputs/` and over every pre-existing fixture snapshot.
- `mypy src/` 76 errors — the baseline exactly, not grown. `ruff check src/` clean.
- `-O`: all 13 new nodes pass. Two failures elsewhere
  (`test_expression_compiler.py` ×2) are pre-existing — they pin a bare `assert` that `-O`
  strips, and they reproduce with production stashed. Out of scope; the new refusals raise
  `CodeGenerationError`, so they survive `-O`.
- Real simkit execution lane: 17 passed, including the new Gate A node.

**Open for later phases.** The Gate A fixture pair is snapshot-captured, so SR-A10's live/replay
parity leg is available to Phase 6. SR-A02's two-consumer convergence is not covered — `gate_a`
deliberately has no calculation consumer of `gain`, so that acceptance row needs its own shape.

---

## Next-Stage Handoff

**Fixed.** The tier / key-form framing; `resolution/` as the home; the request and result field sets;
the narrowed deletion inventory; D9's QN rule; V11 scope preservation; the phase order.

**Open.** Type and function names; rendered prose of the strict error and ambiguity refusal; the
exact `gate_a` fixture names; whether `MANUAL_REQUIRED` stays the right label (Item 4).

**De-risk first.** Two, in order. PC-1's diagnosis, via Phase 0's stop condition — cheap and
empirical. Then D9's QN rule, via Phase 1's unit pins, because it is the one decision that can move
every generated baseline and it is checkable before any consumer is touched.

**Not to start.** Any deletion before Phase 3. Any change to Item 1's three resolution seams. Any
widening of V11 scope (PC-3 — that is Item 3's).

**Decision records.** None filed; every decision here is mechanism choice within an owner-settled
contract. `.project/adr/` does not exist; if acceptance judges D1, D9, or D11 to meet the density
bar, create it via `.project/scripts/adr.sh new` rather than hand-minting ids.

---

## Appendix A — Faithful lookup inventory

Rebuilt from code per C5. Counts are lookup *calls*, not table rows.

**Calculation — `_resolve_chain_dispatch` (`:643-725`): 5 + (S+1) calls.**
`ScopedKey(f"{consumer_scope}.{source_path}")` `:651` scoped · `ScopedKey(source_path)` `:657` scoped
· `ScopedAliasKey((f"{consumer_scope}.{prefix}", leaf))` `:678-680` · `ScopedAliasKey((prefix, leaf))`
`:682-684` · `ScopedKey(source_path)` `:689` alias · climb loop `:716-721`, key
`f"{prefix}.{source_path}"` for `prefix` = descending ancestor joins, collecting into `climbed` and
returning only on `len == 1` `:722-723`.

**Calculation — `_resolve_reference_dispatch` (`:727-743`) + `_resolve_reference_via_registry`
(`:519-560`): 5 calls over 3 keys.** `sysml_qn_lookup(sanitize_qualified_name(source_path))` `:735-737`
· then the path is discarded to a bare `leaf` at `:533-538` and recombined:
`ScopedKey(f"{parent_part}.{leaf}")` scoped `:544` then alias `:546`;
`ScopedKey(f"{consumer_scope}.{leaf}")` scoped `:554` then alias `:556`. Consequence worth recording:
`Pkg::PartA::x` and `Pkg::PartB::x` construct identical keys — the reference's own owner is never
consulted.

**Calculation — `_resolve_to_design_attribute` (`:756-856`): 7 scan arms**, mutually exclusive on
reference shape. Dotted: `(parts[0], parts[-1])` pair, first-hit `:790-793`; leaf-unique with
calc-def filter, refuses unless unique `:802-813`. `::`: exact QN `:824-827`. Bare: collect `:834-837`
· unique `:842-843` · same-file tiebreak `:846-849` · **`candidates[0]` with a warning** `:852-856`.

**Constraint — `resolve_actual` (`:143-300`): 11 calls, all exact, none refusing.** scoped occ `:176`
· scoped de-indexed `:184` · alias occ `:192` · alias de-indexed `:200` · scoped-alias iter 1 `:223`
· scoped-alias iter 2 `:223` · structured alias `:232` · structured alias de-indexed `:234` ·
occurrence-materialized QN membership `:259-260` · target QN membership `:268-269` · owner-def QN
membership `:284-285`.

**Aggregation — `AGG_STRATEGIES` order A, C, B, E: 8 calls (+2 per chain hop).** A: scoped-prefixed
scoped `:86-87` then alias `:89`; unscoped scoped `:98-99` then alias `:101`. C: redefinition scan
`:173-179` (case-insensitive last-segment, `break` = first-pick) then constructed-channel membership
`:185-188`, repeating per recursion hop `:191` under the `visited` guard `:162-169`. B:
`sysml_qn_lookup` `:128`. E: constructed-channel membership `:215-218`.

**Structural notes.** The climb's `i = S` and `i = 0` iterations rebuild rows 1 and 3 byte-identically
and are guaranteed misses when reached. The constraint scoped-alias loop `:219` does not dedupe:
when `occ_scope == deindexed_scope`, the discriminator `scope_candidate == deindexed_scope` is true
on both iterations and the identical lookup fires twice — the merged table discriminates
positionally (m2, carried into D2). `_find_literal_redefinition` aborts the entire scan on the first
non-numeric literal (`graph_builder.py:1250-1251`) rather than skipping it (m3, carried into R8), and
its collision warning fires only when `len(set(strategy2_hits)) > 1` (m4, carried into R5).

**Side effects with no table row.** `_fallback_entry_points.add` (`:635`) — the V11 population,
handled by `records_v11` under I10. `_calc_def_qns` lazy memo (`:870-875`). Self-reference DEBUG
logging (`:749-752`), which can fire repeatedly inside the climb.

## Appendix B — Item 1 seam facts consumed

`ResolvedDemand` has four fields (`supplied_values.py:158-172`); provenance selection is call-site
policy via `select_group_source` (`:330-360`). `enrich_graph_design_attributes` (`:495-600`) is
copy-on-write, running at live Step 5.65 (`pipeline_builder.py:843-859`) and replay
`graph_rebuild.py:107-114`, both before graph construction. `PreparedConstraintUsage` carries seven
fields including `predicate_source_key` (Item 1 deviation 1). `prepare_constraint_usages` (`:714-788`)
dispatches on `usage.owner.owning_definition.kind` into `_expand_part_owner`, `_expand_calc_owner`,
`_expand_package_owner` — the dispatch point this design extends with a `part_usage` branch.

---

**Next Step:** re-review of the revised ladder half (round 2 of two). After approval →
`/_my_implement` against the phased plan above (no separate `plan.md`).
