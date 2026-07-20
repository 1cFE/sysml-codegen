# Design Review: Producer Completeness and Stellarator Rollup (Lifecycle Item 10)

**Design:** `.project/active/constraint-lifecycle-producer-completeness/design.md`
**Spec:** `.project/active/constraint-lifecycle-producer-completeness/spec.md`
**Review File:** `.project/active/constraint-lifecycle-producer-completeness/design-review.md`
**Date:** 2026-07-20
**Verified against:** codegen HEAD `2314ed9` (the design commit; cited baseline `240d170` is one commit behind and the seams are unchanged), agentic-mbse `4c18d61`, stellarator repo `43a1d405`.

---

## Fundamental Assessment

**Sound.** The central move — route a cross-part-chain-bearing computed attribute into the *existing*
aggregation decomposition rather than teaching the calc renderer to render chains, with no "capital"
special-case — is the right call, and it is minimal. I verified the machinery it leans on actually exists
and behaves as claimed:

- `decompose_aggregation_expression` is form-agnostic: it dispatches purely on SysIDE AST node types and
  recurses through arbitrarily nested `OperatorExpression` trees, so a `+`-fold of local refs and
  single-hop cross-part chains decomposes correctly (`aggregation.py:222-326`; test
  `test_aggregation.py:98-116`). A bare cross-part chain becomes a `SingletonTerm`; a bare local ref a
  `LocalTerm`; `sum(part.attr)` a `SumTerm`.
- Operators are **preserved**, not flattened into a blind sum — `_render_neutral_aggregation_node` +
  `_agg_operator_str` translate the operator tree and mark an unknown operator `has_unsupported`
  (`hierarchy_resolver.py:202-306`, guard at `:218`). That `has_unsupported` guard is the safety net that
  makes a broad "contains a cross-part chain" routing key tolerable — an odd-shaped chain expression falls
  back rather than miscompiling — **provided the new route actually runs through it** (see Major 4).
- `ambiguous_candidates` survives to the terminal outcome: a same-leaf tie in LENIENT mode yields
  `Outcome.ENTRY_POINT` carrying the tied QNs (`producer_resolution.py:640`), so Decision 3 *can* read it.

This is composition, not invention, and it does not over-reach. Proceed to the detailed review — this is
not a rework.

Two things the "already does what the rollup needs" framing understates, both surfaced below: the
completeness check has no persisted record to read at finalization, and the chained-aggregation bet rests
on a producer-registration precondition the design never states.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec requirement maps to a design element, and provenance is carried faithfully — the `[INHERITED]`
invariants and D-1/D-2 are treated as constraints, the `[INFERRED]` single-pass cutover is held as design's
mechanism to confirm at implement (Decision 4 step 4 keeps the "or bridge-free two-pass" escape), and the
frozen anchors are marked STOP-not-rebaseline. Good capture discipline.

The gap is the **frozen-anchor / byte-identity requirement** (spec success criterion "ordinary numerics
bit-identical"). The design argues byte-safety analytically — a chain-bearing FORMULA produces no module
today, so rerouting it can only *add* a module, never change an existing one. I confirmed that mechanism:
a cross-part chain raises at `calc_compat_renderer.py:103` → caught at `computed_attribute_extractor.py:305`
→ `MANUAL_REQUIRED` → dropped with a warning at `graph_builder.py:318-334`, no module. So the analytic floor
holds for *existing FORMULA modules*. But the priority-1 enumeration the spec's frozen anchors demand is
**not in the design** (see Major 3): ~15+ fixtures carry dotted computed attributes, and the real exposure
is over-catching a shape that is EXPOSE_PURE / EXPOSE_CHAIN_TENTATIVE / an existing aggregation, not FORMULA.

### 2. Pattern Consistency
**Assessment:** Pass (with one duplication note)

The design reuses the aggregation path, the Item-2 resolver, and the Item-4 written qualifier rather than
inventing parallel mechanisms; the "rejected alternative" (teach the renderer to render chains) is correctly
rejected as bridge-in-a-new-place. One note: a `spec_chain_twolevel` fixture and
`tests/conformance/test_spec_chain_twolevel.py` **already exist** — Phase-1 step 4 should check whether that
fixture already covers (or extends to) the cross-part two-level rollup before authoring a fresh one, so the
suite doesn't grow a parallel fixture. (Minor, Duplication.)

### 3. Abstraction Quality
**Assessment:** Pass

No new abstractions are introduced where existing ones suffice. The completeness check is a new reader over
existing resolver output — the right level. The routing change is a dispatch decision, not a new layer.

### 4. Duplication Avoidance
**Assessment:** Concerns

The design's intent (delete workarounds, no parallel producer route) is right, but the **deletion inventory
is incomplete on the stellarator side** — it omits `handshake_1costingfe.py`, a second executable harness
that re-implements the two-pass glue and depends on the same three bridge keys (Major 4). Leaving it turns
"retire the harness rollup" into "retire one of two copies."

### 5. Data Structure Clarity
**Assessment:** Fail

This is the review's central finding (Major 1). Decision 3 / A5 reads `ProducerResolution.{outcome, key_form,
ambiguous_candidates}` "at graph finalization … no re-resolution." Those fields live **only** on the
ephemeral `ProducerResolution` object, which is created and discarded at each `resolve_producer` call site.
I verified there is **no accumulation** of these objects anywhere, and that the existing V11 check
(`collect_uncovered_params`, `graph_builder.py:841-886`) scans the *final graph* — `InputSource` types and
`fallback_entry_points` — which does **not** carry `key_form` or `ambiguous_candidates`. So the data the
check needs does not exist at finalization. The check requires a new capture sink, and the design neither
names it nor its hook points.

### 6. Route Safety
**Assessment:** Concerns

Two route hazards, both surfaced below: the chained-aggregation LocalTerm can silently collapse to an entry
point if the inner producer channel isn't registered in time (Major 2), and the routing key is broader than
the shape the aggregation path faithfully compiles unless the new route reuses `has_unsupported` (Major 4).
The renderer refusal itself (`calc_compat_renderer.py:102-103`) is a precise structural test —
`node.reference.chain_segments` non-empty — so the *key* is well-defined; the risk is where it's applied and
what it hands off to.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets (A1–A6) are genuine reality-claims with verifications, and R1 (chained aggregation) is
honestly flagged as highest-risk. But two **hidden bets** are load-bearing and unstated:

- **Hidden bet H1 (feeds Major 1):** "the resolver's outcome is *available* at finalization." It is not —
  the record is ephemeral. The check silently assumes a persistence layer the design never builds.
- **Hidden bet H2 (feeds Major 2):** "the newly-routed inner aggregation's output channel is registered in
  `output_registry.canonical_channels` before the outer aggregation's LocalTerm resolves." For `:>>`
  aggregations this holds; for a FORMULA-routed `powercore_capital` it holds only if the new route registers
  the channel up-front. If it doesn't, `direct_capital`'s LocalTerm misses the sibling lookup
  (`graph_builder.py:1620-1622`) and mints an EP (`:1681`) — the F4-cutover EP-key-collapse failure, silent.

### 8. Reader Comprehension
**Assessment:** Pass

The Overview leads with the plain finding ("the aggregation path already does what the rollup needs") before
mechanism, the two-front-doors framing is concrete, and terms are anchored to file:line. A tired engineer can
get the model. The one place the prose *misleads* rather than merely reads awkwardly is A5's "reads the
resolver's recorded result … no re-resolution," which reads as though the record already sits somewhere
readable — the source of Major 1. Fix the claim, not the sentence.

---

## Issues by Severity

### Critical
None. The foundation is sound; nothing here warrants rework.

### Major

1. **Decision 3 has no record to read at finalization (Dimension 5 / hidden bet H1).**
   `ProducerResolution` objects are ephemeral — created and discarded at each `resolve_producer` call
   (verified: no accumulator in the tree; `collect_uncovered_params` scans the graph, not resolutions; the
   graph carries `InputSource` types, not `outcome`/`key_form`/`ambiguous_candidates`). The check as
   described cannot run "at finalization reading records" — the records don't survive. It requires new
   plumbing: capture every `ProducerResolution` as produced, threaded through **all** resolution call sites —
   the calc-consumer path (`dependency_backtracker.py:596-631`), the aggregation SumTerm/SingletonTerm path
   (`_build_agg_input_source`, `graph_builder.py:1403`), and the aggregation LocalTerm path
   (`graph_builder.py:1663-1701`). **If the accumulator misses the aggregation call sites, the check
   reproduces the exact R2 blind spot it exists to close.** "No re-resolution" is fine as a principle but
   must not hide this wiring. Name the sink, its per-request hook points (all of them), and state explicitly
   that it covers aggregation terms.

2. **Chained aggregation (A2/R1) rests on an unstated producer-registration precondition; the fixture must
   assert wiring, not just value (Dimension 6 / hidden bet H2).** The outer LocalTerm resolves via a
   sibling-channel lookup against `output_registry.canonical_channels` (`graph_builder.py:1620-1622`), a
   pre-built set. For a FORMULA-routed inner aggregation (`powercore_capital`/`bop_capital`), the new route
   must register the output channel in that same registry *before* the outer resolves. If it doesn't, the
   LocalTerm mints `{module_eqn}__powercore_capital` (`:1681`) — the F4-cutover EP-key-collapse, silent, and
   not caught by V11 (R2). A2's verification points only at the consumer seam (1614-1708) and misses the
   producer-registration precondition. The two-level fixture must assert the outer input's source is
   `module_output` (structural), because a value check alone can pass on a defaulted minted EP. See
   `[[f4-cutover-fallback-divergence]]` — the trap is a known real divergence, not hypothetical.

3. **The cross-fixture byte-identity enumeration priority 1 demands is absent (Dimension 1/6).** The
   analytic "nothing moves" argument holds for existing FORMULA *modules*, but the exposure is over-catching
   an attribute that today is EXPOSE_PURE / EXPOSE_CHAIN_TENTATIVE / an existing aggregation, not FORMULA. The
   routing key must fire strictly on FORMULA-classified, chain-bearing attributes, *after* the EXPOSE confirm
   pass, only where compilation currently fails — and must not touch the EXPOSE/tentative/aggregation shapes.
   Commit, at Phase 1, to enumerating every fixture with a chain-bearing computed attribute (catf_mfe,
   ife_plant, fusion_tea, deep_cross_scope, plant_values, d316_crosspart_expose, chain_override_probe, … all
   surfaced by grep), and confirm each currently produces no module (or is EXPOSE_PURE and stays so) and none
   reclassify. This enumeration is load-bearing for the frozen anchors.

4. **Deletion inventory omits `handshake_1costingfe.py` (Dimension 4).** It is a second executable harness
   in `exploration/stellarator_e2e/` with its own `patch_bop_wiring` (`:129`), its own PASS A/PASS B two-pass
   structure (`:373`/`:406`), its own glue-2 rollup (`powercore`/`bop`/`direct`/`total`, `:390-398`), and it
   overwrites the identical three bridge keys via `set_params` (`:401-403`). MR-WI027-2's scope explicitly
   names "the handshake." If Phase 3 removes glue-2 from `run_stellaris.py` and the staged conversions but
   leaves this file, it is orphaned/broken or silently keeps a harness rollup — the exact consumer mutation
   this item retires. Add it (and its `patch_bop_wiring` copy) to the inventory.

### Minor

5. **A3 — "same decomposer handles both `=` and `:>>`" is architecturally true but not demonstrated, and the
   new route must reuse the *full* construction.** Today the only caller of `decompose_aggregation_expression`
   is `build_aggregation_expression`, hard-gated to the `:>>` EXPRESSION form
   (`hierarchy_resolver.py:345`, gate at `:376-378`/`:538-539`); no FORMULA path feeds it. The new route must
   build a **complete** `AggregationExpressionData` — decompose **plus** the neutral-node render and the
   `has_unsupported` guard — not just sum decompose terms. If it bypasses `has_unsupported`, an odd-operator
   chain FORMULA miscompiles instead of falling back. State that the FORMULA route reuses
   `build_aggregation_expression`'s path (or an equivalent that keeps `has_unsupported`).

6. **The ambiguous/defaulted fixture (Decision 2) under-specifies the *consuming reference* form, and locates
   the "named error" wrongly.** At today's resolver a same-leaf tie in LENIENT mode does **not** fail
   generation — it yields `Outcome.ENTRY_POINT` with `ambiguous_candidates` populated
   (`producer_resolution.py:640`) and `_build_agg_input_source` mints an EP with a warning. So "fails
   generation with a named ambiguity error" is **not** the resolver's behavior; it must come from Decision
   3's new check firing on `ambiguous_candidates`. And a scope-qualified (exact-QN) reference resolves cleanly
   and never ties — so to exercise the property the consuming reference must be the lenient name-based form
   that reaches rows 19-21 / `_dotted_pair`. Pin the exact reference form, and confirm the reference actually
   reaches `resolve_actual` (see `[[gate-a-owner-classification-bug]]`: inline-form fixtures can miss the
   resolver entirely). State that the named error is the check's, not the resolver's.

7. **Traceability mis-cite that could delete a live guard.** The deletion inventory and Traceability cite
   `computed_attribute_extractor.py:381-395` as a "cross-part EXPOSE_PURE skip" candidate for deletion. That
   range is the **EXPOSE_PURE alias-disagreement warn branch (D3-16)** for a *single-hop* cross-part
   EXPOSE_PURE — a different shape than the FORMULA cross-part sum this item handles. Opening the two front
   doors does **not** obsolete it. Correct the cite so implement doesn't delete a live guard.

8. **Cosmetic line-number drifts (fix so implement lands on the right lines).** Canonical `powercore_capital`
   is `mfe_plant.sysml:389-392` (design: 389-401); `bop_capital` `:395-397`. BRIDGE_KEYS carry a
   `stellarator_09__stellaris__` prefix the design drops. `dependency_backtracker.py` R2 flag is `619-624`
   (design: 620-623). `SumTerm`/`SingletonTerm`/`LocalTerm` are `data_models.py:88-109` (design: 89-110).
   None change the argument.

---

## Recommendations

1. **Close Major 1:** add a resolution-outcome capture sink; name it; enumerate its hook points at every
   `resolve_producer` call site including both aggregation paths; state that Decision 3 reads it and that it
   covers aggregation terms. Rewrite A5 to say "captured as produced," not "already recorded."
2. **Close Major 2:** state the producer-registration precondition for FORMULA-routed aggregations, and make
   the two-level fixture assert the outer LocalTerm wires to a `module_output` source (structural), on top of
   the value check.
3. **Close Major 3:** add a Phase-1 enumeration of every fixture with a chain-bearing computed attribute,
   with the per-fixture "currently no module / EXPOSE_PURE stays" confirmation, before touching the routing.
4. **Close Major 4:** add `handshake_1costingfe.py` (and its `patch_bop_wiring`/glue) to the deletion
   inventory; verify against the MR-WI027-2 grep bar after removal.
5. **Minors 5–8:** specify the full aggregation-construction reuse (has_unsupported); pin the ambiguous
   fixture's consuming reference form and locate the named error in the check; fix the `:381-395` mis-cite;
   correct the line drifts.

---

## Resolutions

All four Majors and minors 5–8 incorporated into `design.md` (2026-07-20):

- **Major 1 (capture sink):** Decision 3 rewritten with a resolution-outcome capture sink threaded through
  all three enumerated `resolve_producer` call sites (calc consumer, aggregation SumTerm/SingletonTerm,
  aggregation LocalTerm), read at finalization; A5 amended to "captured as produced," H1 now explicit (A5b).
- **Major 2 (registration precondition + structural assertion):** new A7 states the
  `output_registry.canonical_channels` registration precondition; A2 verification now asserts the outer
  LocalTerm wires to a `module_output` source structurally; R1 references it; STOP added.
- **Major 3 (byte-identity enumeration):** Phase 1 step 1 is now the per-fixture enumeration across the
  ~15+ chain-bearing-computed-attribute fixtures; over-catching EXPOSE_PURE/tentative/existing-aggregation
  is a named STOP.
- **Major 4 (second harness):** `handshake_1costingfe.py` (patch_bop_wiring/two-pass/glue-2) added to the
  deletion inventory with the MR-WI027-2 grep re-verify.
- **Minor 5:** FORMULA route reuses the full `build_aggregation_expression` construction incl.
  `has_unsupported`. **Minor 6:** ambiguous fixture's consuming reference pinned to the bare-leaf lenient
  form; named error located in the check, not the resolver; reach-`resolve_actual` confirmation added.
  **Minor 7:** `:381-395` mis-cite corrected to a "do NOT touch — live D3-16 guard." **Minor 8:** line
  drifts fixed (powercore :389-392, bop :395-397, R2 flag :619-624, terms :88-109, BRIDGE_KEYS prefix).

Proceeding directly to implementation (audit verifies).

---

**Overall:** Approve-with-revisions.
The approach is sound, minimal, and correctly composes existing machinery — no rework. The four Major items
are gaps to close in the design (and pin at implement), not flaws in the foundation: name the completeness
check's capture sink and its aggregation hook (Major 1), state the producer-registration precondition and a
structural wiring assertion for chained aggregation (Major 2), commit to the cross-fixture byte-identity
enumeration (Major 3), and add the second harness to the deletion inventory (Major 4). The minors sharpen the
FORMULA-route construction, the ambiguous-fixture shape, and the traceability cites.

**Next Steps:** Once resolutions are recorded here, re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
