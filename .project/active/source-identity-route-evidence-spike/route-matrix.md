# Source-Identity Route Matrix (SOURCE-IDENTITY Item 2)

**Date**: 2026-08-05 · **Branch**: `nested-override-tripwire` @ `fa9e0d0`
**Evidence**: kept tests `tests/conformance/test_source_identity_routes.py` (11, license-free),
census `probes/raw/census.json`, licensed parity `probes/raw/parity_*.json`,
Item-1 referent probes (`../source-identity-binding-semantics-spike/`).

Axes per the epic: owner kind, declaration site, occurrence override, written reference
form, consumer type, consumer count, live/relocated-snapshot route, off-default mutation.
Cells are **observed behavior at HEAD**, not desired behavior. "Route parity" is proven
for the starred fixtures (live = snapshot = relocated, entry-point topology + watched
binding states); unstarred rows are snapshot-route observations.

## Observed cells

| # | Owner kind / declaration site | Supplied via | Written form | Consumers | Route taken | Observed public topology | Fixture (parity) |
|---|---|---|---|---|---|---|---|
| 1 | PartDef attr, occurrence `:>>` | override literal | bare self-named | 2 calcs + 1 constraint | Path A (calc), exact-identity (constraint) | **3 fields**: 1 converged DESIGN_ATTRIBUTE + 2 stamped USAGE_LITERAL copies | fusion_tea `gain` ★ |
| 2 | PartDef attr, occurrence `:>>` | override literal | bare self-named | 2 calcs | Path A | **2 fields**, no converged sibling | fusion_tea `thermal_efficiency`, `availability` ★ |
| 3 | PartDef attr, def default | def default | bare self-named | 2 calcs, one occurrence | Path B | **2 fields**; def-declared source never public | ife_plant `bank_energy` ★ |
| 4 | PartDef attr, def default | def default | bare self-named | 1 calc | Path B | per-consumer field; def default backfilled into it | ife_plant `gain` ★, self_named_binding_trap |
| 5 | PartUsage-owned attr | usage literal | bare self-named | calc + constraint | row 16 | **converges** (SR-A02 control) | shared_producer ★ |
| 6 | Cross-part attr | value at source | dotted `driver.efficiency`, renamed formals | 2 calcs | SVM source-QN collapse | **converges** (control) | fusion_tea ★ |
| 7 | Parent-part attr, consumed cross-owner | override literal | bare self-named | agg/constraint + child-part calc | Path A (calc) | **2 fields**; consumer-owner+leaf reconstruction names nothing | solar_battery `pack_count` ★ |
| 8 | Authored usage literals | literal | none (`written_reference is None`) | one each | literal arm | distinct fields — correct; distinguishable from stamped | fusion_tea `num_units`, `target_factory_cost` ★ |
| 9 | Renamed stamped reference | override literal | bare, formal ≠ attribute | 1 calc | Path A | referent name survives the stamp (`rep_rate` ← `pulse_rate_ref`) | fusion_tea ★ |
| 10 | Two occurrences of one PartDef | def defaults | bare self-named | per-occurrence calcs | Path B | per-occurrence fields (occurrence distinctness holds; whether an un-overridden def default is one source or one per occurrence is an Item-3 ruling) | ife_plant `chamber_a`/`chamber_b` ★; fusion_tea driver pair |
| 11 | Unbound formals | library default | none | 8 usages | Case-1 mint | 8 per-usage LIBRARY_DEFAULT fields — **distinct class**, per-usage by ADR-001 design | solar_battery `fab_factor` ★ |
| 12 | Deep chain, same owner | override | mixed (incl. renamed) | 3 calcs | Path A | 3 stamped copies; reconstruction candidates unresolved | deep_cross_scope_probe |
| 13 | Aggregation terms, unresolved reference | — | dotted | aggregation | lenient terminal mint | per-term entry points (I7 warnings) — same terminal-mint family, aggregation consumer | solar_battery `permitting.*` ★ |

## Authoring-form columns resolved by Item 1 (licensed referent probes)

| Form | Referent | Bearing on this matrix |
|---|---|---|
| bare self-named `in R = R` | calc's **own formal** — degenerate self-binding, normatively required, silent | The input to rows 1-4, 7, 10, 12; ~47% of external usage bindings |
| bare renamed `in r_in = R` | outer attribute (def-level) | Resolves correctly today; collision is the entire cause of degeneracy |
| owner-qualified `'Plant'::R` | **def-level** attribute | Occurrence must be recovered from context — the same def-vs-occurrence gap as Path B's index miss; zero external corpus use |
| feature chain `plant.R` | **redefining feature at the occurrence** (`owned_redefinitions` edge names the def attribute) | The only written form whose referent carries occurrence identity |
| `#(i)` indexed | value semantics only; extractor silently drops the index segment | Additional stage-0 identity-loss site; zero prevalence |
| `[i]` indexed | load error (quantity/unit bracket) | Already rejected by the language |

## Blocked / not-observed cells (exact missing evidence)

- **Off-default mutation execution legs** — runtime proof that mutating one copy leaves
  siblings frozen. Deliberately not run here;
  `tests/runtime/test_fusion_tea_acceptance.py:113-125` already demonstrates the one-copy
  perturbation as a wrong-oracle PASS. Item 6 owns mutation-based acceptance.
- **Nested-occurrence override cell** — `tests/fixtures/nested_occurrence_override_probe/`
  ships without a snapshot (capture halts by design); coordinate pinned in its
  PROVENANCE.md and the tripwire verdict. Needs a live leg; absorbed into Item 4
  acceptance.
- **Shadowing / specialization referent cells** — no fixtures exist; measured ambiguity
  count of zero in the census is not proof of none.
- **Constraint/aggregation consumers of the qualified and chain forms** — Item 1 probed
  referents only for calc bindings; the cross-consumer sweep for those written forms
  needs new fixtures (calc-side behavior is rows 5-6, 13).
