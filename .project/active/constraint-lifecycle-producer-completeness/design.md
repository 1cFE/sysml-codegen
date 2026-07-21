# Design: Producer Completeness and Stellarator Rollup (Lifecycle Item 10)

**Status:** Draft (phased plan folded in)
**Owner:** Reid W
**Created:** 2026-07-20
**Branch:** constraint-exec-epic
**Spec:** `./spec.md`
**Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`, Item 10 (register row 12)

---

## Overview

The spec collapsed this item to one codegen capability plus its cleanup: **teach codegen to compile
the modeled cross-part capital aggregation through the ordinary graph machinery**, then prove
producer completeness as its own property and retire the stellarator's private bridge.

The central design finding — the one that makes this small — is that **the aggregation path already
does what the rollup needs.** `_build_aggregation_module` (`graph_builder.py:1478-1757`) decomposes a
cross-part sum into terms and resolves each term through the Item-2 shared resolver
(`resolve_producer`, `producer_resolution.py:561-613`) to a real `MODULE_OUTPUT` channel that becomes
a wired `ModuleInput`. The capital rollup is refused today only because it arrives on the wrong front
door: it is written as an `=` computed attribute (a FORMULA), which is routed through
`calc_compat_renderer.render_calc_expression`, and that renderer refuses any feature chain
(`calc_compat_renderer.py:102-103`, "feature chain expression not supported in CalcDef output").
The `:>>` EXPRESSION-redefinition form of a cross-part sum is *already* decomposed into an aggregation
(`build_aggregation_expression`, `hierarchy_resolver.py:354-399`); the `=` FORMULA form is not.

So the renderer gap is not "make the renderer render chains." It is: **route a cross-part-chain-bearing
computed attribute into the same aggregation decomposition the `:>>` form already uses, so it compiles
like any aggregation — no special-case arm for "capital."** The design settles that routing, the
de-risk-first ambiguous/defaulted acceptance, the producer-completeness check, the stellarator cutover,
and the cross-repo phasing with stop conditions.

---

## Load-bearing assumptions (stated up front)

These carry the design. Each has a named verification and, where it can bite, a stop condition. If one
fails, it is a surface-to-orchestrator event, not a silent workaround.

1. **A1 — The aggregation path reproduces the harness rollup value bit-exactly.** The generated
   aggregation module sums the same per-account producer channels the two-pass harness sums in Python.
   Both are `powercore_capital + bop_capital + buildings.capital_cost + …`; the graph does the arithmetic
   codegen previously could not wire. *Verification:* the six ordinary anchors and oracle bit-exactness
   (rel < 1e-9). *Stop:* an anchor value moving is a STOP (§5), never a re-anchor.

2. **A2 — Chained aggregation resolves.** `direct_capital` references `powercore_capital`, which is
   *itself* a cross-part sum (`mfe_plant.sysml:389-392`; `bop_capital` `:395-397`). So
   `powercore_capital`/`bop_capital` must each
   compile to an aggregation producer, and `direct_capital`'s reference to them (a `LocalTerm`) must
   resolve to those aggregation output channels — an aggregation consuming aggregation outputs.
   `total_capital` = `direct_capital + contingency_capital + indirect_capital` chains one level deeper.
   *Verification:* a Phase-1 two-level fixture, both public routes, asserting the outer `LocalTerm` wires to a
   `module_output` source **structurally** (channel identity — not just value; A7). The producer-registration
   precondition A7 is the crux. *This is the highest-risk assumption* — see Risks R1. If nesting does not
   resolve through the ordinary `resolve_producer` ladder, surface it; do not add a rollup-specific
   resolution arm.

3. **A3 — The computed-attribute (FORMULA) expression is decomposable by the existing aggregation
   decomposition.** `decompose_aggregation_expression` (`aggregation.py:207-219`) classifies each AST
   node into `SumTerm` / `SingletonTerm` (cross-part dotted, e.g. `buildings.capital_cost`) / `LocalTerm`
   (bare local ref). The rollup expression is a flat `+`-fold of local refs and single-hop cross-part
   chains — exactly this grammar. *Verification:* Phase-1 confirms the FORMULA expression AST feeds the
   same decomposition the `:>>` EXPRESSION path uses; if the FORMULA AST shape differs, the adapter is at
   the extraction dispatch, not in the decomposer.

4. **A4 — The cross-part references key by exact QN, not by a guessed leaf.** Item 4's written-scope
   qualifier (`BindingInfo.stored_source_written_qualifier`, `usage_extractor.py:97-99`) is the
   disambiguation lever: a scope-qualified reference resolves under exact identity (resolver rows 16/17)
   rather than being re-anchored onto an owner-local same-named shadow. *Verification:* the ambiguous/
   defaulted acceptance (§2) proves the resolver refuses a leaf-name tie; the rollup references are
   dotted `part.capital_cost` forms that resolve via tier-1 scoped rows.

5. **A5 — Producer completeness is derivable from the resolver's own result, with no new resolution.**
   `ProducerResolution` already records `outcome`, `key_form`, and `ambiguous_candidates`
   (`producer_resolution.py:130-141`). The check reads these; it does not re-resolve. *Verification:* §3.

5b. **A5-amended (was "no re-resolution") — the completeness check reads a purpose-built capture sink, not
   a pre-existing record.** `ProducerResolution` objects are **ephemeral**: created and discarded at each
   `resolve_producer` call, and the final graph carries `InputSource` types + `fallback_entry_points`, not
   `outcome`/`key_form`/`ambiguous_candidates` (verified: no accumulator exists; `collect_uncovered_params`
   scans the graph, `graph_builder.py:841-886`). So the check requires **new plumbing** — a capture sink that
   records each `ProducerResolution` as it is produced, threaded through **every** `resolve_producer` call
   site (§3 enumerates them, aggregation paths included). The check reads the sink at finalization. It does
   not re-resolve — but the record it reads is one this item builds, not one that already sits somewhere.

6. **A6 — Legitimate external typed design inputs are exempt by declaration.** `availability`,
   `discount_rate`, `contingency_rate`, etc. are declared inputs with no producer and must stay ordinary
   typed entry channels. The completeness check must exempt them by their declared-input status, not by
   leniency (invariant 26; D-1). *Verification:* §3; the stellarator regen keeps its declared inputs.

7. **A7 — For chained aggregation, the inner producer's canonical channel is registered in
   `output_registry.canonical_channels` BEFORE the outer LocalTerm resolves** (the producer-registration
   precondition Major 2 surfaced). For `:>>` aggregations this already holds; for a FORMULA-routed inner
   aggregation (`powercore_capital`) it holds only if the new route registers the channel up front. *If it
   does not, the outer LocalTerm misses the sibling lookup (`graph_builder.py:1620-1622`) and silently mints
   an entry point (`:1681`) — the F4-cutover EP-key-collapse (`[[f4-cutover-fallback-divergence]]`), invisible
   to V11.* *Verification:* the two-level fixture asserts the outer input's source is `module_output`
   **structurally** (channel identity), per the multi-hop lesson (`[[multihop-expose-offline-parity]]`) —
   a value check alone passes on a defaulted minted EP. *Stop:* an outer LocalTerm resolving to an entry
   point is a STOP.

---

## Decision 1 — The renderer gap: cross-part feature-chains through the aggregation path

**Decision:** When a computed attribute (FORMULA) or CalcDef output carries cross-part feature-chain
references, route its expression through the existing aggregation decomposition
(`decompose_aggregation_expression` → `AggregationExpressionData`) and `_build_aggregation_module`, so
each term resolves via `resolve_producer` to a real channel. The rollup becomes a `ModuleKind.AGGREGATION`
producer like any other aggregation. **No special-case arm for "capital" anywhere** — the routing keys on
"the expression contains a cross-part feature chain," a structural property, not on the attribute's name
or role.

### ⚠ Decision-1 premise CORRECTED (2026-07-20, empirical) — the aggregation path did NOT resolve cross-part terms

The original premise — "each term resolves via `resolve_producer` to a real channel; the aggregation path
already resolves cross-part references" — was **false** and is corrected here. The routing (Step 4.7,
`_route_crosspart_formula_aggregations`) landed byte-clean and A7 (chained `LocalTerm` → `module_output`)
holds. But the cross-part **`SingletonTerm`s collapse**: building the canonical stellarator graph, all 13
`X.capital_cost` terms (`magnet`/`heating`/…) resolved to ONE def-level attribute
`mfe_magnet_cost__Magnet_Coil_Cost__capital_cost` via `key_form=leaf_unique` — the resolver **dropped the
`magnet.`/`heating.` part-usage qualifier and leaf-matched** `capital_cost`. Two root causes, both here:

1. **The per-child redefinitions are not captured.** Each child is `part magnet : 'Magnet System' { :>>
   capital_cost = magnet_cost.capital_cost; }`. These member `:>>` CHAIN redefinitions on part-def-level
   child usages are absent from `hierarchy_data.redefinitions` (0 of 22 are `capital_cost`), so
   `_chain_redefinition_follow` (row 13) has nothing to follow.
2. **A qualified reference silently drops its qualifier.** With row 13 missing, `X.capital_cost` falls to
   the name-based tier-2 rows (`_leaf_unique`/`_dotted_pair`), which strip `X.` and leaf-match — collapsing
   every child to one producer. This is the Item-4 written-qualifier lesson at the aggregation seam: a
   written scope qualifier must anchor exact identity, never be dropped to widen the candidate set.

**Fix mechanism (general, in `producer_resolution` / the aggregation term builder — no rollup-specific arm):**

- **(a) Follow the per-child redefinition per instance.** Capture the child part usages' member `:>>` CHAIN
  redefinitions so `_chain_redefinition_follow` resolves `magnet.capital_cost` to the magnet instance's own
  channel (its `magnet_cost` output), structurally — the written/structural derivation, per instance, with
  DIFFERENT per-child values (never a value coincidence — the F2 lesson).
- **(b) A qualified term REFUSES rather than leaf-matches.** A `part_usage.attr` reference must not resolve
  by dropping `part_usage.` and matching the bare leaf: the name-based rows (`_leaf_unique`/`_dotted_pair`)
  must not fire for a qualified reference. Where no per-child derivation exists, the term misses cleanly
  (terminal → distinct per-term entry point), never a qualifier-drop collapse. This is the same
  no-qualifier-drop rule the producer-completeness check enforces at generation.

This closes the epic's **WI-015 finding #4 root** (cross-part rollup "cannot be wired") — the wiring was
blocked by the dropped per-child redefinition plus the silent qualifier-drop, not by a fundamental limit.

**If any of the 13 terms' per-child `:>>` is structurally unavailable from extraction** (the AST does not
carry it), that term is a coordinated-pair (agentic-mbse) question — STOP and name it, do not shim.

**Why this is composition, not invention.** Every piece already exists:

- **Decompose:** `decompose_aggregation_expression` (`aggregation.py:207-219`) already classifies a
  `FeatureChainExpression` → `SingletonTerm(source_path)` (`aggregation.py:230-235`), a bare ref →
  `LocalTerm`, a `sum(...)` → `SumTerm`. The rollup's `+`-fold of local refs and single-hop chains is this
  grammar (A3).
- **Resolve + wire:** `_build_agg_input_source` (`graph_builder.py:1369-1458`) builds a
  `ProducerRequest(policy=LENIENT)` per term and calls `resolve_producer`; a `MODULE_OUTPUT` outcome
  yields a wired cross-part channel (`:1415-1419`). `SingletonTerm` wiring lives at `graph_builder.py:1584-1611`.
- **Emit:** `_build_aggregation_module` (`graph_builder.py:1478-1757`) produces a
  `PipelineModule(module_kind=ModuleKind.AGGREGATION)` with one `float` output channel.

**What actually changes (the two front doors that currently refuse/drop the rollup):**

1. **The FORMULA / CalcDef-output route** — `calc_compat_renderer.py:102-103` raises on any
   `chain_segments`. The computed-attribute extractor invokes it at `computed_attribute_extractor.py:303`;
   the CalcDef-output path at `expression_compiler.py:306`. This is the front door `direct_capital` /
   `total_capital` take (`= <cross-part sum>`). The change: before refusing, detect that the expression is
   a cross-part aggregation and hand it to the aggregation decomposition instead of the byte-for-byte calc
   renderer. The renderer keeps refusing genuinely uncompilable local expressions; it stops being the place
   a cross-part sum dies.
   **The FORMULA route must reuse the FULL aggregation construction, not just term decomposition (Minor 5).**
   Today the only caller of `decompose_aggregation_expression` is `build_aggregation_expression`, hard-gated
   to `:>>` EXPRESSION (`hierarchy_resolver.py:345`, gate `:376-378`/`:538-539`). The new route must build a
   **complete** `AggregationExpressionData` — decompose **plus** the neutral-node render and the
   `has_unsupported` guard (`_render_neutral_aggregation_node` / `_agg_operator_str`,
   `hierarchy_resolver.py:202-306`, guard at `:218`) — so an odd-operator chain FORMULA falls back to
   MANUAL_REQUIRED rather than miscompiling. Reuse `build_aggregation_expression`'s path (or an equivalent
   that keeps `has_unsupported`); do not hand-roll a decompose-only shortcut.
2. **The plain-usage `:>>` override drop** — `_keep_plain_usage_override` (`hierarchy_resolver.py:102-110`,
   `:152-153`) deliberately drops CHAIN/EXPRESSION plain-usage overrides, commented verbatim "Item 10's
   job." If any stellarator rollup arrives as a plain-usage `:>>` override (catf_mfe / ife_plant shape 4
   class), this gate opens to route it to the same aggregation builder. *Design confirms at Phase 1 which
   front door each of `powercore_capital` / `bop_capital` / `direct_capital` / `total_capital` takes* — the
   canonical forms are `=` computed attributes (`mfe_plant.sysml:389-424`), so door 1 is primary; door 2 is
   opened only if a plain-usage override shape is in the live set.

**The disambiguation lever (A4).** Each cross-part term resolves through the Item-2 ladder. Where a
reference names its own scope, Item 4's written qualifier (`source_written_qualifier`,
`usage_extractor.py:101-108`; consumed via `written_reference`, `:117-159`) forces resolution under exact
identity (row 16 `_occurrence_materialized_qn` misses → row 17 `target_qn`), never an owner-local shadow.
Compose this field; do not add a second disambiguation path.

**Rejected alternative — teach `calc_compat_renderer` to render a chain as `inputs.<flattened>`.** This
would invent a parallel producer-wiring path inside the renderer, duplicating what
`_build_agg_input_source` already does, and it would not give the term a real graph producer (it would mint
an input the bridge-era code would then have to fill). Rejected: it recreates the bridge in a new place.
The aggregation path is the one machinery; the renderer stays a pure local-expression renderer.

**Flag carried from investigation (Risks R2):** aggregation-term lenient misses currently mint entry points
whose V11 membership is recorded only for the calculation consumer, not aggregation terms
(`dependency_backtracker.py:619-624`, "widening to aggregation is a coverage-scope decision"). An
unresolved rollup term could therefore mint an entry point that `collect_uncovered_params`'s
`fallback_entry_points` set does not include — i.e., slip past V11. This is precisely why the
producer-completeness check (§3) is independent of V11: it must catch an unresolved rollup term directly,
by the resolver outcome, not rely on V11 membership.

## Decision 2 — The ambiguous/defaulted RED coordinate (de-risk-first)

**Decision:** Build the ambiguous/defaulted producer acceptance as a **public codegen fixture, RED-first,
BEFORE any rollup or stellarator work** (epic De-risking; Risks row "drive exact-QN and ambiguous/defaulted
counterexamples first"). It is license-free — a synthetic SysML fixture plus a conformance test — with no
stellarator dependency, so it de-risks the resolver-precedence property in isolation.

**Fixture shape (acceptance matrix row "Ambiguous/defaulted producer resolution",
contract `:437`):** a model with

- **two same-leaf candidate design attributes** — two attributes sharing a leaf name in different scopes
  (e.g. `a::cost` and `b::cost`); and
- **a consuming reference in the lenient name-based form** — a *bare-leaf* reference (no scope qualifier),
  so it reaches resolver rows 19–21 / `_dotted_pair` (`producer_resolution.py:419-424`) and actually ties.
  A scope-qualified (exact-QN) reference resolves cleanly and never ties, so it would not exercise the
  property; and
- **a defaulted-fallback shape** — a consumed formal with a fallback/default available.

**Where the named error comes from — the check, not the resolver.** At today's resolver a same-leaf tie in
LENIENT mode does **not** fail generation: `_unique_or_tie` refuses to *pick*, so the outcome falls through
to `Outcome.ENTRY_POINT` carrying `ambiguous_candidates` (`producer_resolution.py:640`), and
`_build_agg_input_source` mints an EP with a warning. So the acceptance's **named ambiguity/producer error is
Decision 3's completeness check firing on a non-empty `ambiguous_candidates`** — not a new resolver raise.
The exact-QN escape (a scope-qualified reference resolving cleanly) is the *other* admissible observation.

**Required observation:** either the completeness check **fails generation with a named ambiguity/producer
error** (the bare-leaf tie), OR the reference **resolves only under exact QN** (the written-qualifier path),
and **no verdict is ever produced from a guessed or defaulted binding while V11 is clean.**

**Reaching the resolver.** Confirm the consuming reference actually reaches `resolve_actual` — inline-form
fixtures can miss the resolver entirely (`[[gate-a-owner-classification-bug]]`: Gate A breaks in owner
classification, not the ladder; inline-form fixtures never reach `resolve_actual`). Author the fixture in a
form that reaches the resolver, and assert that it does.

**Both public routes** — live extraction and relocated snapshot replay — per the standing coordinate.

**Why RED-first matters here:** if the resolver cannot cleanly refuse the ambiguous case, the same
weakness would let a rollup term bind to the wrong same-leaf producer (`capital_cost` appears on every
subsystem). Proving the refusal first de-risks the rollup wiring in Decision 1.

## Decision 3 — Producer completeness as its own check (independent of V11)

**Decision:** Add a producer-completeness check that runs at graph-assembly finalization, separate from and
additive to `collect_uncovered_params` (`graph_builder.py:841-886`). It asserts: **every model-derived
consumed value resolved to exactly one intended producer under exact identity.** The check does not
re-resolve — but the record it reads does not exist today and this item builds it (A5-amended).

**The capture sink (new plumbing — stated honestly).** `ProducerResolution` objects are ephemeral (created
and discarded per `resolve_producer` call); the final graph carries `InputSource` types and
`fallback_entry_points`, not `outcome`/`key_form`/`ambiguous_candidates`. So Decision 3 adds a
**resolution-outcome capture sink**: a per-run accumulator (carried on `ProducerContext` or the
graph-build context) that records each `ProducerResolution` — the `(consumer, request, outcome, key_form,
ambiguous_candidates)` tuple — **as it is produced.** It is threaded through **every** `resolve_producer`
call site; missing any aggregation site reproduces the exact R2 blind spot the check exists to close.

**Enumerated hook points (all of them — verified call sites of `resolve_producer`):**

1. **Calc-consumer path** — `dependency_backtracker.py:596-631` (`resolve_actual` / the calc-binding
   resolution).
2. **Aggregation SumTerm / SingletonTerm path** — `_build_agg_input_source`, `graph_builder.py:1403`
   (the cross-part-term resolution — the rollup's own terms).
3. **Aggregation LocalTerm path** — `graph_builder.py:1663-1701` (the sibling/inner-producer resolution —
   the chained-aggregation seam A7 guards).

*If a fourth `resolve_producer` call site exists, Phase-2 step 1 grep-enumerates it and adds the hook; the
sink must cover 100% of resolution sites or the completeness claim is hollow.*

**What it reads (per captured resolution):** `ProducerResolution.{outcome, key_form, ambiguous_candidates}`
(`producer_resolution.py:130-141`); a same-leaf tie in LENIENT mode reaches the terminal as
`Outcome.ENTRY_POINT` carrying the tied QNs (`producer_resolution.py:640`), so the check *can* see it.

**What it asserts:**

- **Model-derived consumed value** (a reference to a model producer): `outcome` is `MODULE_OUTPUT` or an
  exact-QN `DESIGN_ATTRIBUTE` (`key_form` ∈ rows 16–18, the exact-identity forms), and
  `ambiguous_candidates` is empty. A value that resolved via a lenient name-based row (19–21) or landed as a
  synthesized `ENTRY_POINT` is a completeness failure — a named producer error.
- **Legitimate external typed design input** (A6): exempt by its **declared-input** status — a formal the
  model declares as an input with no producer, resolving to a legitimately declared typed entry channel.
  The exemption is by declaration, not by resolver leniency. External inputs remain ordinary typed entry
  channels (invariant 26; D-1).

**Why separate from V11:** V11 catches only a valueless *wired* fallthrough (a `KeyError` at load); a
defaulted fallback or an ambiguous first-match passes V11 while feeding the wrong value (invariant 26,
verbatim: "V11 is not a substitute"). And the aggregation-term coverage gap (R2) means an unresolved rollup
term may not even reach V11's membership set. Producer completeness closes both by reading the resolver
outcome directly.

**Relationship to the RED coordinate:** Decision 2's fixture is the acceptance that this check (and the
resolver's tie-refusal) works; Decision 3 is the always-on enforcement. Build the check so Decision 2's
fixture is one of its RED cases.

## Decision 4 — The stellarator cutover

**Decision:** Once Decision 1 lands, the stellarator generates through the ordinary public path with no
bridge and no harness rollup arithmetic. The cross-part sums are real aggregation producers, so the demo
package emits and executes single-pass (or otherwise bridge-free).

**Sequence in the stellarator repo (its own modeling-PM record; WI-027 amended):**

1. **Restore the canonical formulas in the staged twins.** The staged `mfe_plant.sysml:409/:434` convert
   `direct_capital` / `total_capital` to valueless plain inputs (the DEMO NOTE conversions). With codegen
   able to compile the cross-part sums, restore the canonical formulas (`mfe_plant.sysml:400-424`) in the
   twins, removing those two conversions. After this, the twins differ from canonical only where the demo
   legitimately must — ideally nowhere in the rollup region.
2. **Recapture the snapshot.** The committed snapshot carries zero constraint facts (captured 2026-07-18
   from a stripped state) and is snapshot-format v3, predating the Item 4 v4 amendment. Recapture from the
   current staged model, lowering-ON, no `--design-path-filter`. Confirm five constraint facts and the
   rollup aggregation producers are present.
3. **Generate publicly.** Run the supported CLI generation path — **not** `bridge_v11_generate.py`. There
   should be **zero** V11 offenders now (the three rollup keys are real producers), so nothing to bridge.
4. **Cut the runner over to bridge-free execution.** The two-pass runner exists only to compute the rollup
   in Python (glue-2) and overwrite the placeholders before the canonical pass. With the rollup in the
   graph, that arithmetic is obsolete: cut to a single canonical pass (or a bridge-free two-pass if another
   reason for two passes survives — confirm at implement). Removing glue-2 must not reintroduce any
   viability comparison in harness code (WI-027 MR-WI027-2 grep bar stays green).
5. **Verify the anchors and verdicts.** Six ordinary anchors byte/value-preserved, oracle bit-exact
   (rel < 1e-9); five verdicts all `satisfied`, `headline=all_satisfied`; WI-022 handwritten-impl sha256
   intact through `preserve_handwritten`; handshake diff empty.

**Deletion inventory (retired by this item — named before design, verified deleted at implement, not
shimmed):**

- `exploration/stellarator_e2e/bridge_v11_generate.py` — the private bridge (whole file).
- The three placeholder `BRIDGE_KEYS` (each `stellarator_09__stellaris__…` prefixed) and the
  `PLACEHOLDER = 1.0` fill; the "expected exactly 3 offenders" assert (`bridge_v11_generate.py:42-47,91-92`).
- The two-pass runner's glue-2 Python rollup arithmetic in `run_stellaris.py` (the `direct`/`total`
  computation that overwrites the three keys) and, if the second pass has no other purpose, the two-pass
  structure itself.
- **`handshake_1costingfe.py` — the second executable harness (Major 4).** It re-implements the identical
  two-pass glue: its own `patch_bop_wiring` (`:129`), PASS A / PASS B structure (`:373`/`:406`), its own
  glue-2 rollup (`powercore`/`bop`/`direct`/`total`, `:390-398`), overwriting the same three bridge keys via
  `set_params` (`:401-403`). MR-WI027-2's grep scope names "the handshake" explicitly. Removing glue-2 from
  `run_stellaris.py` while leaving this file orphans it or silently keeps a harness rollup — the exact
  consumer mutation this item retires. Retire its rollup glue (and its `patch_bop_wiring` copy); the
  handshake keeps only its comparison role against 1costingFE, edited only within the injection map
  (MR-WI027-5.2). Re-verify the MR-WI027-2 grep bar after removal.
- The two staged DEMO NOTE plain-input conversions (`mfe_plant.sysml:400-409`, `:430-434`).
- **Codegen side:** any aggregation/resolver workaround the cross-part capability obsoletes — confirm at
  Phase 1 whether opening the two front doors makes the `_keep_plain_usage_override` drop
  (`hierarchy_resolver.py:102-110`) a now-dead guard that can be deleted. **Do NOT touch
  `computed_attribute_extractor.py:381-395`** — that is the live D3-16 EXPOSE_PURE alias-disagreement warn
  branch for a *single-hop* cross-part EXPOSE_PURE, a different shape than the FORMULA cross-part sum this
  item handles; opening the front doors does not obsolete it (Minor 7 — verify before deleting anything
  here; a live guard dies if the cite is wrong). No compatibility wrapper or parallel producer route
  survives (epic simplification mandate; no LOC accounting).

**WI-027 amendment (artifact-level):**

- Add a supersession pointer: WI-027 D7 (passthrough calculations) is superseded by ratified D-2 (direct
  literal design-attribute actuals are valid). Point the WI-027 design at the contract.
- Remove the D7 passthroughs from the WI-027 record — **none exist in any model file** (measured: no
  `Scalar Value` def; the staged asserts read design attributes directly). This is a documentation
  correction, not model surgery.
- Record the bridge/placeholder/glue retirement and the public-generation result in the WI-027 record and
  SV-033.

## Decision 5 — Cross-repo phasing and stop conditions

**Phasing.** Codegen capability first (this repo, the one PR-wave landing unit); stellarator consumer second
(its own repo/record). Certification stays ordered behind the open predecessor (Item 9) per the register;
the codegen work may be built while Item 9 is open but not certified around it.

**Stop conditions (surface to orchestrator; do not work around):**

- **An anchor value moving is a STOP, not a re-anchor.** If any of the six ordinary anchors or any
  oracle-checked channel shifts, halt and surface. The rollup-as-aggregation must reproduce the harness
  arithmetic exactly (A1); a shift means the graph sum diverges from the intended sum — a real defect, not
  a new baseline.
- **Chained aggregation not resolving through the ordinary ladder (A2)** — surface; do not add a
  rollup-specific resolution arm.
- **A rollup term binding to the wrong same-leaf producer** — the producer-completeness check must catch it;
  if it resolves ambiguously and the check passes, the check is wrong. Surface.
- **A canonical `models/` viability-semantics edit becoming necessary** — barred; surface (the twins are the
  adaptation surface, not canonical).
- **Snapshot-format skew blocking recapture** — if v4 handling forces a schema change beyond recapture,
  surface (out of this item's scope; Item 4 owns the format).

---

## Phased plan (folded in)

**Phase 0 — RED-first ambiguous/defaulted acceptance (Decision 2).** Author the public fixture (two
same-leaf candidates + defaulted fallback) and the conformance test on both routes. Prove RED against a
resolver that could guess, then confirm GREEN: contextual failure or exact-QN-only resolution, no guessed
verdict while V11 clean. *Gate: the fixture is a RED case of the Phase-2 completeness check.*

**Phase 1 — Cross-part aggregation compilation (Decision 1).**
1. **Byte-identity enumeration FIRST (Major 3 — load-bearing for the frozen anchors).** `grep` every fixture
   carrying a chain-bearing computed attribute (surfaced set: catf_mfe, ife_plant, fusion_tea,
   deep_cross_scope, plant_values, d316_crosspart_expose, chain_override_probe, … ~15+). For **each**, record
   its current classification and confirm the routing change does not move it: a FORMULA-classified,
   chain-bearing attribute where compilation currently *fails* (no module today) is the only shape that may
   gain a module; an EXPOSE_PURE / EXPOSE_CHAIN_TENTATIVE / existing-aggregation shape **must not
   reclassify**. **Over-catching any EXPOSE_PURE / tentative / existing-aggregation shape is a named STOP**
   (§5) — the routing key must fire strictly on FORMULA-classified, chain-bearing attributes, *after* the
   EXPOSE confirm pass, only where compilation currently fails. Per-fixture generated-byte diff must be empty
   except the intended new aggregation module(s). (Baselines are format-exempt: `[[generated-baselines-format-exempt]]`.)
2. Confirm the front door each rollup attribute takes (`=` FORMULA vs `:>>` override) and that the FORMULA
   expression AST feeds `build_aggregation_expression`'s full construction incl. `has_unsupported` (A3, Minor 5).
3. Route cross-part-chain-bearing computed attributes / CalcDef outputs into the aggregation construction +
   `_build_aggregation_module`; open the `_keep_plain_usage_override` gate only if a plain-usage override
   shape is in the live set. Register the FORMULA-routed aggregation's canonical channel in
   `output_registry.canonical_channels` **before** outer resolution (A7).
4. Verify chained aggregation (`powercore_capital` → `direct_capital` → `total_capital`) resolves through
   the ordinary `LocalTerm` wiring (A2/A7). *Stop if the outer LocalTerm resolves to an entry point.*
5. Add the two-level fixture. **First check whether `spec_chain_twolevel` /
   `tests/conformance/test_spec_chain_twolevel.py` (already exists) covers or extends to the cross-part
   two-level rollup** before authoring a fresh fixture, so the suite does not grow a parallel one. The test
   asserts the outer input's source is `module_output` **structurally** (channel identity, A7) *and* the
   aggregation output equals the summed inputs (value), on both public routes.

**Phase 2 — Capture sink + producer-completeness check (Decision 3).**
1. Grep-enumerate every `resolve_producer` call site; add the capture-sink hook at each (the three named
   sites plus any fourth). Assert 100% coverage — a resolution site with no hook is a STOP.
2. Build the check reading the sink at graph finalization; exempt declared external inputs by declared-input
   status (A6), not leniency.
3. Make Phase 0's ambiguous fixture and an unresolved-rollup-term case its RED cases (the named ambiguity
   error is the check firing on `ambiguous_candidates`, Minor 6). Verify it does not reject the stellarator's
   legitimate declared inputs (`availability`, `discount_rate`, `contingency_rate`, …).

**Phase 3 — Stellarator cutover (Decision 4, stellarator repo).** Restore canonical formulas in the twins →
recapture → public generation (no bridge, zero offenders) → runner cutover → verify six anchors + five
verdicts + WI-022 hash + handshake. Execute the deletion inventory. Amend WI-027; fill SV-033.

**Phase 4 — Deletion verification and evidence.** Confirm every named workaround is deleted, not shimmed
(codegen and stellarator); no parallel producer route remains. Record evidence in
`.project/active/constraint-lifecycle-producer-completeness/evidence.md` and the WI-027 record.

---

## Risks

| Risk | Likelihood / impact | Mitigation |
|---|---|---|
| **R1 — Chained aggregation (A2) does not resolve through the ordinary ladder** | med / high | Phase-1 step 3 is a dedicated two-level fixture *before* the stellarator; a miss is a STOP and surfaces, not a rollup-specific arm. |
| **R2 — Unresolved aggregation term mints an entry point that slips past V11** (`dependency_backtracker.py:619-624`) | med / high | The producer-completeness check (§3) reads the resolver outcome directly, so an aggregation term that resolves to a synthesized `ENTRY_POINT` fails completeness regardless of V11 membership. |
| **R3 — The rollup graph sum diverges from the harness arithmetic** | low / high | A1 anchor bit-exactness; an anchor move is a STOP (§5). |
| **R4 — A same-leaf term binds to the wrong producer** (`capital_cost` on every subsystem) | med / high | Written-qualifier exact-QN keying (A4); Phase-0 ambiguity acceptance proves the refusal first. |
| **R5 — Snapshot v3→v4 recapture friction** | low / med | Recapture is in scope; a schema change beyond recapture is out of scope and surfaces (Item 4 owns format). |
| **R6 — Runner cutover reintroduces a harness viability rule** | low / med | WI-027 MR-WI027-2 grep bar stays green after glue-2 removal; adapters marked, swept at Phase 3. |

---

## Traceability

- **Renderer gap:** `calc_compat_renderer.py:102-103` (refusal), `:49` (`render_calc_expression`);
  FORMULA invocation `computed_attribute_extractor.py:303`; CalcDef-output invocation
  `expression_compiler.py:306`.
- **Aggregation path (the reused machinery):** `AggregationExpressionData`
  (`sysml-codegen/src/sysml_codegen/extraction/data_models.py:246`), `ScopedAggregationData` (`:296`);
  `SumTerm`/`SingletonTerm`/`LocalTerm` (`agentic-mbse/src/agentic_mbse/sysml/data_models.py:88-109`);
  `decompose_aggregation_expression` (`aggregation.py:207-219`); `build_aggregation_expression`
  (`hierarchy_resolver.py:354-399`); `_build_aggregation_module` (`graph_builder.py:1478-1757`);
  `_build_agg_input_source` (`graph_builder.py:1369-1458`); `SingletonTerm` wiring (`:1584-1611`);
  `LocalTerm` wiring (`:1614-1708`).
- **Item-2 resolver:** `producer_resolution.py` — `ProducerRequest` (`:97-127`), `ProducerResolution`
  (`:130-141`), `resolve_producer` (`:561-613`), `KEY_FORMS` (`:472-495`), exact-QN rows 16–18
  (`:370-416`), lenient rows 19–21 + `_unique_or_tie` (`:419-424`), `_terminal_miss` (`:616-641`).
  Design: `.project/active/constraint-lifecycle-shared-resolution/design.md`.
- **Item-4 written qualifier:** `BindingInfo.stored_source_written_qualifier` (`usage_extractor.py:97-99`),
  `source_written_qualifier` (`:101-108`), `_written_qualifier` (`:975-995`), `written_reference`
  (`:117-159`); consumed at `dependency_backtracker.py:605`; row-16 use `producer_resolution.py:370-403`.
  `.project/active/constraint-lifecycle-diagnostics-defaults/`.
- **Extraction gates:** `_keep_plain_usage_override` (`hierarchy_resolver.py:102-110`, `:152-153`);
  cross-part EXPOSE_PURE skip (`computed_attribute_extractor.py:381-395`).
- **V11 / completeness:** `collect_uncovered_params` (`graph_builder.py:841-886`), `UncoveredInput`
  (`:825-838`), `collect_unwired_fallthrough` (`:889-916`); aggregation-coverage flag
  (`dependency_backtracker.py:619-624`). Capture-sink hook points: calc consumer
  `dependency_backtracker.py:596-631`; aggregation SumTerm/SingletonTerm `graph_builder.py:1403`; aggregation
  LocalTerm `graph_builder.py:1663-1701`. Chained-aggregation seam: sibling lookup
  `graph_builder.py:1620-1622`, EP mint `:1681`. Full aggregation construction:
  `build_aggregation_expression` `hierarchy_resolver.py:345`, `has_unsupported` guard `:202-306`/`:218`.
  Second harness: `handshake_1costingfe.py:129,373,390-403,406`.
- **Contract:** invariants 19–26 (`constraint-execution-authoritative-lifecycle-contract.md:172-195`),
  D-1/D-2 (`:284-298`), acceptance rows "Ambiguous/defaulted producer resolution" (`:437`) and
  "Stellarator design point (D-1/D-2)" (`:462`).
- **Stellarator:** rollup canonical `mfe_plant.sysml:389-424`, staged plain inputs `:409/:434`;
  bridge `exploration/stellarator_e2e/bridge_v11_generate.py`; two-pass runner `run_stellaris.py`;
  WI-027 `../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/`.

---

**Next Steps:** Independent `/_my_design_review` in a fresh session, then `/_my_plan` (or proceed to
`/_my_implement` Phase 0 given the plan is folded in here).
