# Findings: Source-Identity Routes and Evidence Sufficiency (SOURCE-IDENTITY Item 2)

**Date**: 2026-08-05 · **Branch**: `nested-override-tripwire` @ `fa9e0d0`
(continued on `source-identity-epic`)
**Upstream artifact**: `.project/backlog/epic_semantic_source_identity.md`, Item 2
**Invoked as**: `/_my_learning_test` + licensed follow-up. The item's spec/design/plan
deliverables were consciously skipped in favor of the evidence shape — same call as
Item 1, noted here so the Item-3 reader knows why those files are absent.

**Deliverables in this folder**: `route-matrix.md`, `identity-trace.md`,
`corpus-census.md`, `adjacent-work-register.md`, `probes/` (census + parity, raw JSON).
**Kept tests**: `tests/conformance/test_source_identity_routes.py` (11, license-free,
passing; defect pins deliberately flip in Items 4-6).
**Narrative/discovery log**:
`.project/research/20260805-054752_source-identity-route-evidence.md`.
**Joint input**: Item 1's `../source-identity-binding-semantics-spike/`
(authoring-form table + standards rulings), completed the same day.

## Summary of Findings

1. **Where identity dies** (identity-trace.md): for the bare self-named form, outer-source
   identity is *never established* at extraction (normatively required self-binding —
   Item 1); the VBR stamp then destroys the route (`LITERAL`, `source_path=None`) by
   leaf-name coincidence; **snapshot capture persists the stamp** (capture runs the full
   live pipeline; the rebuild has no VBR step). Value provenance travels separately from
   identity through four authorities — VBR stamp, SVM ladder, resolver design-attribute
   tier, and a newly identified group-deriver backfill
   (`graph_builder.py:620-630`) — which agree at capture and diverge under mutation.

2. **Live = snapshot = relocated, everywhere probed** (`probes/raw/parity_*.json`): on
   fusion_tea, ife_plant, shared_producer, and solar_battery_model the three routes
   produce identical entry-point topology and identical watched-binding states, fan-out
   included. The defect is a pipeline property; relocation adds nothing.

3. **Evidence-sufficiency verdict — explicit extraction-owned semantic source ID.**
   Falsifiable basis:
   - The written-form fields survive the stamp and the snapshot round-trip (even for
     renamed bindings), so *distinguishing* reference-derived from authored literals
     needs no new evidence (`written_reference is None` ⇔ authored — kept test).
   - But owner-local reconstruction (consumer owner + written leaf, fallback owning-def
     QN) measurably cannot recover cross-owner sources (solar `pack_count` — kept test)
     or consumer-relative dotted tails; corpus-wide it recovers 35/75 model-derived
     mints against captured attributes.
   - Item 1 closes the feasibility question from the other side: SysIDE exposes the
     occurrence→definition bridge directly at extraction (`owned_redefinitions` →
     `.redefined_feature` / `.redefining_feature`), so extraction can emit exact
     declaration-plus-occurrence identity rather than a reconstruction heuristic.

   **Blast radius of the selected option**: new snapshot content ⇒
   `snapshot_format_version` bump with fail-closed old versions (per the epic), full
   recapture of the 37-fixture snapshot corpus (timestamp-churn discipline per the
   byte-identity gate memory), a `graph_rebuild` change (today it depends on the
   baked-in stamp), and companion-repo regeneration (fusion-tea, stellarator).
   The rejected alternative — reconstruction from current fields — is recorded above
   with its measured failure cells; a hybrid (persist pre-VBR bindings) is *not* free
   either: the rebuild would need a VBR step it doesn't have, with license-gated parity
   risk.

4. **The affected corpus is enumerated with explicit unknowns** (corpus-census.md):
   277 entry points, of which **75 (27%) are model-derived per-consumer mints**
   (37 stamped Path A, 38 lenient-miss Path B). Six proven duplicate groups (one modeled
   source → several fields). Unknown classes preserved: cross-owner duplicates beyond
   `pack_count` (the sweep key can't see them), catf's 13 per-occurrence `inner_radius`
   attributes, EXPRESSION-binding EPs, the 40 reconstruction-unresolved rows, and the
   multi-occurrence def-default question. The unbound-formal population (e.g. solar's
   8× `fab_factor`) is a *distinct, currently-legitimate* class (ADR-001 per-usage
   LIBRARY_DEFAULT), for Item 3 to ratify or overturn.

5. **Adjacent work has one owner per mechanism** (adjacent-work-register.md):
   `[NESTED-OCCURRENCE-OVERRIDE]` absorption into Item 4 is revalidated as structural
   (Path B's miss is the same def-vs-occurrence gap the materializer has; one bridge
   serves both); `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2 sequencing stands; the queued
   fusion-tea aggregation-scoping finding is evidenced as the same terminal-mint family
   (recommend absorption; owner files it); the group-deriver backfill and SVM synthesis
   are flagged to Item 5's deletion/derivation register; the `#(i)` extractor drop goes
   to Item 3's disposition table.

## What this hands Item 3 (decision inputs, no decisions made)

- The full route matrix and census name every supported-or-broken cell observed at HEAD,
  with the two controls (row-16 shared_producer, SVM dotted collapse) showing the
  convergence machinery that already exists.
- Item 1's cross-form finding matters jointly with Path B's mechanism: the two
  spec-correct written forms denote **different elements** (qualified → def-level;
  chain → redefining feature at the occurrence), and this spike shows the pipeline's
  failure is precisely the unbridged def-vs-occurrence split. Whichever form the owner
  ratifies as "the enclosing part's attribute", the repair must carry
  **declaration + concrete occurrence** — def-level identity alone reproduces Path B's
  gap.
- Open ruling flagged for the checkpoint: multi-occurrence def-default sharing (one
  source or one per occurrence); the unbound-formal class; the aggregation-scoping
  finding's filing.

## Item-2 success criteria status

| Criterion (epic) | Status |
|---|---|
| Every required matrix cell observed or explicitly blocked with missing evidence named | **Met** — route-matrix.md, blocked list includes mutation legs, nested-occurrence live leg, shadowing/specialization fixtures |
| Identity trace records source occurrence + every derived identity per stage | **Met** — identity-trace.md, pinned by kept tests |
| Falsifiable evidence-sufficiency verdict + schema/version blast radius | **Met** — explicit source ID selected; blast radius stated above |
| Census accounts for all entry points in the fixture corpus, explicit unknown class | **Met** — 277/277 classified, five unknown classes preserved |
| Adjacent-work register: one owner/disposition per mechanism, no second bridge/authority | **Met** — seven mechanisms, no new authority proposed |
| Kept tests/probes fail on both fan-out paths and distinguish independent literals from shared-source references | **Met** — 11 kept tests pin both paths + the discriminator |

Residual risk, stated plainly: the corpus contains no shadowing or specialization
referent fixtures, so the verdict's "0 ambiguous" is absence of evidence there; Item 4's
foundation tests must author those cells. The mutation execution legs are deliberately
deferred to Item 6's public acceptance.
