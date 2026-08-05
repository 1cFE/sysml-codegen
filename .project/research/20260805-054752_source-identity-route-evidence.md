---
date: 2026-08-05T05:47:52-07:00
researcher: Claude
topic: "Source-identity routes and evidence sufficiency (SOURCE-IDENTITY Item 2 learning test)"
tags: [research, learning-test, source-identity, backtracker, snapshots, census]
status: complete
branch: nested-override-tripwire
commit: fa9e0d0
---

# Learning Test: Source-Identity Routes and Evidence Sufficiency

**Upstream artifact**: `.project/backlog/epic_semantic_source_identity.md`, Item 2.
**Kept tests**: `tests/conformance/test_source_identity_routes.py` (11 tests, license-free).
**Scope note**: this is the learning-test leg of Item 2 — the observable-behavior evidence.
It does not replace the item's spec/design/plan pipeline; cells that need live extraction,
new fixtures, or execution-mutation legs are named as blocked below. **Item 1 completed in
parallel the same day** (`.project/active/source-identity-binding-semantics-spike/findings.md`);
its results are cross-referenced where they bear on this evidence, and the remaining Item-2
close-out is the joint semantic synthesis of the two documents.

## Summary of Findings

1. **Identity destruction is persisted into every committed snapshot.** Snapshot capture
   (`src/sysml_codegen/snapshot/capture.py:48`) runs the full live pipeline — including the
   Step-3.5 virtual-binding rewrite, which mutates bindings in place — and then serializes
   the *mutated* `calc_usages`. The committed fusion_tea snapshot already contains
   `binding_type=literal, source_path=null` for the stamped `gain` bindings. The snapshot
   rebuild (`src/sysml_codegen/snapshot/graph_rebuild.py`) never re-runs the rewrite; the
   offline route depends on the baked-in stamp. Any repair that changes what capture
   persists forces a full corpus recapture, and "capture pre-rewrite state instead" is not
   a free fix — the rebuild has no rewrite step to re-apply it.

2. **The written-form evidence survives everything.** The stamp clears the resolved route
   (`source_path`) but not the written-form fields: `source_attribute_name` and
   `source_written_qualifier` survive the stamp and the snapshot round-trip, even for a
   renamed binding (`rep_rate` still records referent `pulse_rate_ref`). This makes
   **reference-derived literals distinguishable from authored literals on existing
   snapshots**: an authored literal has `written_reference is None`; a stamped one names
   its referent. That is the discriminator the Item-2 success criterion asked for, and it
   needs no schema change.

3. **Owner-local reconstruction is insufficient across the matrix.** Reconstructing the
   source as `consumer_owner_path + written leaf` works for same-owner cells (ife_plant:
   24/25 reconstruct to the def-declared source) but measurably fails for cross-owner
   references: solar_battery's `pack_count` lives on `battery_system`, is consumed by
   `battery_bos.cost_model`, and the owner-local candidate names nothing (kept test).
   Corpus-wide, over the 75 model-derived per-consumer entry points: 35 reconstruct
   (2 exact-occurrence, 33 def-default), 40 do not, 0 ambiguous — against *captured*
   attributes only (the materialized index would resolve more; treat 35 as a lower bound).
   **Provisional verdict for the Item-3 decision: exact reconstruction from current
   evidence cannot cover the matrix; an extraction-owned semantic source ID (or
   preserving the resolved referent through the rewrite) is required for exactness.**
   Either option touches snapshot content ⇒ `snapshot_format_version` bump or full
   recapture of all 37 snapshot fixtures, plus companion-repo (fusion-tea, stellarator)
   snapshots/packages. Item 1's probes (completed 2026-08-05) strengthen the verdict:
   SysIDE exposes the occurrence→definition bridge directly at extraction — the `:>>`
   node's `owned_redefinitions` yields a `Redefinition` edge with `.redefined_feature`
   (def attribute) and `.redefining_feature` (override site) — so an extraction-owned
   source ID is directly implementable from live evidence, not a reconstruction heuristic.

4. **The corpus census: 27% of the public entry surface is model-derived per-consumer
   minting.** 277 entry points across the 37 snapshot fixtures: 123 converged
   design-attribute fields, 58 library defaults (per-usage by ADR-001 design), 14 authored
   usage literals, 7 expression/other — and **75 per-consumer mints of model-derived
   values** (37 via the silent literal stamp, 38 via the warned lenient miss). Fan-out
   groups where one modeled source demonstrably maps to multiple public fields: fusion_tea
   `gain` (3 fields), `thermal_efficiency` (2), `availability` (2); ife_plant
   `bank_energy` (2); deep_cross_scope `baseline_value` (3); solar_battery `pack_count`
   (2, cross-owner). The census grouping keys on (owner, leaf), so cross-owner duplicates
   beyond `pack_count` are an explicitly unknown class until re-swept with scope search.

5. **Path B loses nothing at the binding — it lacks a bridge.** The lenient-miss route
   keeps the resolved self-reference and the written leaf; what fails is that the
   attribute index holds the *definition* QN (`IfePlantLib__Ife_Power_Plant__gain`) while
   demand is *occurrence*-relative (`IfePlantDesign__baseline_plant` + `gain`). This is
   the same occurrence→definition gap already filed as `[NESTED-OCCURRENCE-OVERRIDE]` —
   confirming the epic's decision to absorb that fix into Item 4 as one bridge, not a
   sibling fix.

6. **A fourth value authority masks the identity loss.** The per-consumer Path-B entry
   point is classified `USAGE_LITERAL` (no literal exists in the model) yet carries the
   def default (500.0): entry-point classification fails to find a value, and the
   parameter-group deriver's independently resolved value is backfilled at
   `src/sysml_codegen/resolution/graph_builder.py:620-630`. Value provenance and identity
   provenance travel entirely different routes and only coincide at capture — which is
   why every single-point run looks correct. Add this backfill to Item 5's
   superseded-route deletion candidates.

## Question / Goal

Item 2: map where semantic identity survives or is lost across the pipeline routes,
determine the minimum sufficient source evidence for a correct repair, and enumerate the
affected corpus — before any fix design.

## Identity Trace (stage by stage)

What each stage holds for a model-derived consumed value, verified on committed snapshots
and current code at `fa9e0d0`:

| Stage | Code | Identity in | Identity out |
|---|---|---|---|
| 0. Extraction | `extraction/usage_extractor.py:831-842` | AST referent | Self-named `in R = R` resolves to the calc's **own formal**; `source_path` = self-ref QN. Written-form fields (`source_attribute_name`, `source_written_qualifier`) captured from the CST. Outer-source identity is **never established** for this form. |
| 1. VBR (live Step 3.5) | `orchestration/pipeline_builder.py:336-379` | self-ref QN + written fields | Occurrence `:>>` matched by `(parent_path, leaf)` **name coincidence** → `binding_type=LITERAL`, `source_path=None`. Written fields survive (measured). Route identity destroyed. |
| 2. Snapshot capture | `snapshot/capture.py:48-70` | post-VBR bindings | **Stamp persisted.** Rebuild (`snapshot/graph_rebuild.py`) has no VBR step; offline route replays the stamped state. |
| 3. SVM enrichment (Step 5.65 / rebuild) | `resolution/supplied_values.py:502` | bindings + overrides | Skips bindings with no `source_path` → stamped literals invisible to source-QN collapse. Synthesizes occurrence attributes from demands (solar's converged `pack_count` field exists only as a synthesized attribute). Definition-relative captures vs occurrence-relative demands fail the tier match (`[NESTED-OCCURRENCE-OVERRIDE]`, tripwire warns). |
| 4. Backtracker | `analysis/dependency_backtracker.py:445-463, 571-631` | binding state | LITERAL arm mints `{usage_qn}__{param}` per consumer and **never calls the resolver**. REFERENCE arm reaches the 22-form table; row 16 (`owner + written`) hits only when the occurrence attribute exists in the enriched index; the `::`-qualified self-ref QN misses rows 17/19-21. |
| 5. Classification | `resolution/graph_builder.py:534-579` | EP name | Catch-all else → `USAGE_LITERAL` for both paths — reference-derived mints wear an authored-literal label. |
| 6. Value backfill | `resolution/graph_builder.py:620-630` | deriver's parallel resolution | Def-default value quietly attached to the per-consumer EP; value repaired, identity not. |

First stage at which identity is absent: **extraction (stage 0)** for self-named forms —
the outer-source link is never established, only reinterpreted downstream (constraint
route, row 16, SVM) or destroyed (VBR stamp). First stage at which it becomes
unrecoverable on the current offline route: **capture (stage 2)**.

## Route Matrix (observed cells)

All license-free, from committed snapshots; consumer type "calc" unless noted.

| Owner kind | Supplied via | Reference form | Consumers | Route | Observed topology | Fixture |
|---|---|---|---|---|---|---|
| PartDef attr, occurrence `:>>` | override literal | bare self-named | 2 calcs + constraint | Path A | **3 public fields** (1 converged + 2 stamped copies) | fusion_tea `gain` |
| PartDef attr, occurrence `:>>` | override literal | bare self-named | 2 calcs | Path A | **2 fields**, no converged sibling | fusion_tea `thermal_efficiency`, `availability` |
| PartDef attr, def default | def default | bare self-named | 2 calcs, same occurrence | Path B | **2 fields**; def-declared source never public | ife_plant `bank_energy` |
| PartDef attr, def default | def default | bare self-named | 1 calc | Path B | per-consumer field, def default backfilled | ife_plant `gain`, trap fixture |
| PartUsage-owned attr | usage literal | bare self-named | calc + constraint | row 16 | **converges** (control) | shared_producer |
| Cross-part attr | dotted `driver.efficiency` | dotted, renamed | 2 calcs | SVM collapse | **converges** on source QN (control) | fusion_tea |
| Parent-part attr, cross-owner | override literal | bare self-named | agg/constraint + child-part calc | Path A | **2 fields**; owner-local recon fails | solar_battery `pack_count` |
| Authored usage literals | literal | none | each its own | literal arm | distinct (correct); distinguishable from stamped | fusion_tea `num_units` etc. |
| Renamed reference, stamped | override literal | bare, renamed formal | 1 calc | Path A | referent name survives (`pulse_rate_ref`) | fusion_tea `rep_rate` |
| Two occurrences of one def | def defaults | bare self-named | per-occurrence calcs | Path B | per-occurrence fields (distinctness correct; def-default sharing is an Item-3 question) | ife_plant `chamber_a`/`chamber_b`; fusion_tea driver pair |
| Unbound formals | library default | none | 8 usages | Case-1 mint | 8 per-usage LIBRARY_DEFAULT fields — **distinct class**, per-usage by ADR-001 design | solar_battery `fab_factor` |
| Deep chain, same owner | override | mixed | 3 calcs | Path A | 3 stamped copies; recon candidates unresolved | deep_cross_scope |
| Aggregation terms, unresolved | — | dotted | agg | lenient mint | per-agg-term EPs (I7 warnings) — same terminal-mint family, aggregation consumer | solar_battery `permitting.*` |

**Blocked cells** (exact missing evidence named):
- Live vs relocated-snapshot parity for these routes — needs the syside license
  (`SYSIDE_LICENSE_KEY` via `~/1cfe/agentic-mbse/.env`); all observations above are
  snapshot-route. The forensics assert live/pin equivalence for fusion shapes; not
  independently re-proven here.
- Bracketed occurrence-index and owner-qualified/feature-chain written forms — no
  committed snapshot fixture here; Item 1's licensed probes covered them (2026-08-05):
  qualified names denote the *def-level* attribute, feature chains the *occurrence-level*
  redefining feature; `#(i)` is value-only and the extractor silently drops the
  IndexExpression segment (`_parse_chain_expression` records `source_path='R'`) — an
  additional identity-loss site at stage 0 with zero corpus prevalence; `[i]` fails to
  load. See the Item-1 findings and `authoring-form-table.md`.
- Nested-occurrence override cell — `tests/fixtures/nested_occurrence_override_probe/`
  ships **without a snapshot** (capture halts by design); its coordinate is pinned in its
  PROVENANCE.md and the tripwire verdict. Not reproducible license-free.
- Off-default mutation legs (execution proof that mutating one copy leaves siblings
  frozen) — runtime/TEAx legs, deliberately out of this item's license-free scope;
  `tests/runtime/test_fusion_tea_acceptance.py:113-125` already demonstrates the one-copy
  perturbation (as a wrong-oracle PASS).

## Evidence-Sufficiency Experiment

Attempted reconstruction `candidate = owner_path__written_leaf`, fallback
`owning_part_def_qn__written_leaf`, against captured design attributes, over all 75
model-derived per-consumer EPs in the corpus:

- **Exact occurrence hit: 2** (fusion_tea `gain` copies — the occurrence attribute exists
  because the constraint demand synthesized it).
- **Def-default hit: 33** (ife_plant class: the def-declared source is recorded; needs the
  occurrence→definition bridge to be usable).
- **Unresolved: 40** — three sub-classes: (a) cross-owner references (solar `pack_count`:
  true source one scope up; kept test), (b) dotted/deep tails where the middle segments
  are consumer-relative (`cost_model` chains in solar/issue22/alias_agg/chain_override),
  (c) no materialized occurrence attribute and no captured def attr (deep_cross_scope,
  fusion_tea driver-occurrence copies).
- **Ambiguous: 0** in this corpus — but shadowing fixtures don't exist yet; absence of
  measured ambiguity is not proof of none (Item 1 authors the shadow/specialization
  probes).

Caveat: run against **captured** attributes; the SVM-enriched index would convert some
"unresolved" to hits. The direction of the verdict does not change: cross-owner and
consumer-relative-tail cells cannot be recovered from owner-local written evidence at all.

**Verdict (falsifiable, final after Item-1 synthesis and licensed parity):** written-reference
plus occurrence-owner evidence is sufficient to *distinguish* reference-derived from authored
values and to reconstruct *same-owner* sources, but not to recover exact source identity across
the matrix. Preserving the existing resolved `source_path` is also insufficient for bare self-named
forms: Item 1 proves it normatively names the calculation formal, not the intended outer source.
The repair therefore requires an extraction-owned semantic source ID derived from the SysIDE
referent/redefinition edge and carried independently of the binding's supplied value and route.

Licensed live, committed-snapshot, and relocated-snapshot builds have identical entry-point topology
and watched binding state for `fusion_tea`, `ife_plant`, `shared_producer`, and
`solar_battery_model`; evidence is retained under
`.project/active/source-identity-route-evidence-spike/probes/raw/parity_*.json`. The fan-out is a
pipeline semantic, not snapshot-only drift. The source-ID blast radius is therefore:
`snapshot_format_version` bump with fail-closed old versions, coordinated capture/rebuild changes,
full recapture of the 37-fixture corpus (with timestamp-churn discipline), and companion Fusion Tea
and Stellarator snapshot/package regeneration.

## Corpus Census (initial)

Totals over 37 snapshot fixtures (all build license-free): **277 entry points** =
123 converged design-attribute + 58 library-default + 14 authored-literal +
7 expression/unattributed + **37 Path-A + 38 Path-B per-consumer mints**.

Same-owner fan-out groups (one modeled source, several fields): fusion_tea ×3
(`gain` w/ converged sibling, `thermal_efficiency`, `availability`), ife_plant ×1
(`bank_energy`), deep_cross_scope ×1 (`baseline_value`). Cross-owner: solar_battery
`pack_count` (found via the forensics pointer, pinned by test; the same-owner grouping
heuristic cannot find this class — the final Item-6 census must key on recovered source,
not consumer owner).

Explicit unknown classes (preserved, not forced): catf_mfe's 13 per-occurrence
`inner_radius` attributes (13 distinct layer occurrences, not per-consumer mints — whether
the model chains them is unread); the 6 EXPRESSION-binding EPs (`expression_binding_probe`)
plus `plant_value_shapes` `rated_cost__rate`; all 40 reconstruction-unresolved rows;
every cross-owner duplicate beyond `pack_count`.

Census artifacts: probe script and full JSON in this session's scratchpad were
throwaway; the reproducible artifact is the kept test file plus this table. The Item-6
final census re-runs against the corrected pipeline with zero silent unknowns allowed.

## Adjacent-Work Register (one owner per mechanism)

| Mechanism | Evidence this session | Disposition / owner |
|---|---|---|
| Item-10 per-child `:>>` capture + transitive instance routing (landed) | Not contradicted; VBR tier-2 path distinct from the fan-out stamp | **Reuse as substrate** — SOURCE-IDENTITY Item 4 audits, does not re-implement |
| `[NESTED-OCCURRENCE-OVERRIDE]` (absorbed into Item 4) | Overlap revalidated: Path B's miss is the *same* def-keyed-index vs occurrence-keyed-demand gap the materializer has; one bridge serves both | **Item 4 owns the one occurrence→definition bridge**; tripwire + probe fixture are acceptance evidence; no snapshot exists for the probe (live leg needed) |
| `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2 (one part-structure index) | Three walkers still present; Item 4 needs only occurrence-type threading into `enrich_graph_design_attributes` | **Sequencing stands as filed (BACKLOG 2026-08-04)**: Item 4 threads the existing occurrence index; builds no second walker; remainder stays in CONSTRAINT-ARCH-UNIFY |
| Queued fusion-tea producer-channel/aggregation-scoping finding (unfiled, owner gate) | Aggregation terms share the lenient terminal mint (solar `permitting.*` I7 warnings) — same family, aggregation consumer | **Item 2 final synthesis dispositions it** against the matrix; evidence here says same semantic family, so absorption is the likely ruling — owner decision pending |
| Parameter-group-deriver value backfill (`graph_builder.py:620-630`) | **Newly identified** parallel value authority; masks Path B identity loss | **Flag to Item 5's superseded-route deletion register** — not previously in any backlog entry |
| SVM occurrence-attribute synthesis (`supplied_values.py` enrichment) | Solar's converged `pack_count` field exists only as a synthesized attribute | Item 4/5: synthesis must derive from the single identity authority, not run as a parallel one |

## Log

1. Read both forensic reports; extracted the two-path mechanism and open questions.
2. Located harness: `build_pipeline_context_from_snapshot(snapshot_fixture(name))` —
   full pipeline, license-free, 37 fixtures with committed snapshots.
3. Probed fusion_tea/ife_plant/shared_producer/trap topologies; observed the three-field
   `gain` split and pure Path-B ife surface directly.
4. Found stamped literals **in the committed snapshot** (pre/post diff showed no pipeline
   mutation) → traced to `capture.py` running the full live pipeline before serializing;
   confirmed `graph_rebuild.py` has no VBR step.
5. Confirmed written-form survival on stamped bindings (`source_attribute_name`,
   `source_written_qualifier` serialized; `written_reference` computed on load), including
   the renamed `rep_rate`←`pulse_rate_ref` case; confirmed authored literals carry
   `written_reference=None` → discriminator.
6. Ran the whole-corpus census + reconstruction experiment (counts above); identified the
   cross-owner `pack_count` cell and the same-owner-grouping blind spot; classified
   catf's 13× `inner_radius` as per-occurrence attributes, not per-consumer mints;
   classified solar's 8× `fab_factor` as unbound-formal LIBRARY_DEFAULT (third mint site,
   distinct class).
7. Chased ife's 500.0 default: not classification (float fails on the self-ref QN), not
   SVM synthesis (zero synthesized attrs for ife) — it is the group-deriver backfill at
   `graph_builder.py:620-630`.
8. Wrote and ran the 11 kept tests; adjusted the cross-owner test after learning the
   converged `pack_count` attribute is SVM-synthesized (absent from the raw captured map).

## Tests Written

`tests/conformance/test_source_identity_routes.py` — all passing at `fa9e0d0`, all
license-free:

- `test_path_a_one_modeled_gain_is_three_public_fields` — defect pin, Path A topology.
- `test_path_a_stamp_is_persisted_into_the_snapshot` — capture persists the stamp.
- `test_path_a_written_evidence_survives_the_stamp` — evidence pin incl. renamed referent.
- `test_reference_derived_literal_distinguishable_from_authored_literal` — the
  discriminator (Item-2 success criterion).
- `test_path_b_lenient_miss_mints_per_consumer` — defect pin, Path B topology.
- `test_path_b_identity_evidence_present_but_unbridged` — the occurrence→definition gap.
- `test_path_b_value_backfill_masks_identity_loss` — value/identity split.
- `test_shared_producer_control_converges` — row-16 control.
- `test_dotted_cross_part_control_converges` — SVM-collapse control.
- `test_cross_owner_stamp_defeats_owner_local_reconstruction` — the cell that forces the
  explicit-source-ID verdict.
- `test_unbound_formals_are_a_distinct_per_usage_class` — LIBRARY_DEFAULT class boundary.

The defect pins are deliberate: Items 4-6 flip them consciously when the repair lands.

## Reproduction

```bash
uv run pytest tests/conformance/test_source_identity_routes.py -q   # no license needed
```

Every assertion reads committed snapshots under `tests/fixtures/`. The census numbers
reproduce by iterating `tests/fixtures/*/extraction_snapshot.json` through
`build_pipeline_context_from_snapshot` and grouping per-usage entry points by the binding
evidence described above.

## Remaining Questions / Follow-ups

1. **Def-default sharing across occurrences** (ife chambers): one source (the def
   default) or one per occurrence? Owner disposition, Item 3.
2. **Cross-owner duplicate sweep**: the census's same-owner grouping cannot enumerate the
   full cross-owner class; the Item-6 census must key on recovered source identity.
3. **catf_mfe 13× `inner_radius`**: read the model to classify chained-vs-independent
   layer radii before Item 6 counts them.
4. The `permitting.*` aggregation-term mints tie the queued fusion-tea aggregation-scoping
   finding to the same terminal-mint family — supports absorption, awaiting the owner.
5. Shadowing/specialization and qualified/chain constraint-consumer fixtures remain absent; the
   route matrix names these cells explicitly for later acceptance coverage.
