# Design: Part-Usage Type Indexing (SC-3)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM (1-day)
**Branch:** upstream-findings-epic
**Base commit:** 5a860e0
**Epic:** UPSTREAM-FINDINGS — Item 4

---

## Overview

A retyped part usage (`part :>> driver : 'HIF Driver'`) silently drops the subtype's
template calcs. Two extraction sites pick a usage's type by list position instead of by
its declared type. This design replaces both position picks with a heritage-walk over the
usage's **owned FeatureTyping** relationships, indexes the usage under all of its user-model
types, and adds a deterministic tiebreak (plus warning) for the one genuine collision case.

## Related Artifacts

- **Spec (contract):** `.project/active/type-indexing/spec.md`
- **Spec review:** `.project/active/type-indexing/spec-review.md`
- **Research (authoritative, SC-3 §):** `.project/research/20260705_upstream-findings-deep-research.md:123-131`
- **Ready-to-run probe:** `.project/active/type-indexing/probe/probe.py` + `probe/model.sysml`
- **Code touched:** `extraction/usage_extractor.py` (`_build_part_usage_index`, `_expand_template_calc_usages`),
  `extraction/hierarchy_resolver.py` (`extract_hierarchy_data` usage_type_map)
- **Precedent:** `extraction/extractor.py:316-326` (`_get_calc_def_name` heritage walk)
- **Behavioral consumer:** `resolution/graph_builder.py:1044-1046` (`_find_literal_redefinition`)
- **Docs:** `modeling-assumptions.md` §5 + Validation table; `reference/25-hierarchy-resolver.md`;
  `reference/01-extraction.md`; `verification-matrix.md`

---

## Research Findings

**The two bugs, confirmed at HEAD.**

- `_build_part_usage_index` (`usage_extractor.py:163`) does `next(iter(usage.types))` — indexes
  each PartUsage under only the *first* type in `usage.types`.
- `extract_hierarchy_data` (`hierarchy_resolver.py:527-531`) does the same `next(iter(member.types))`
  to build `usage_type_map[(owning_qn, name)] → type_qn`.

**The mechanism that makes retyping drop calcs.** Template expansion
(`_expand_template_calc_usages`, `usage_extractor.py:271-341`) walks, for each template CalcUsage,
`_find_instantiation_paths(owning_part_def_qn, index)`. The index is keyed by PartDef QN. If the
retyped usage is only keyed under `IFE Driver`, then a `HIF Driver`-owned template finds no path
and is dropped (the `no PartUsage instantiations — dropped` branch, line 318-326).

**The collision point already exists.** Expansion dedups virtual instances through a `seen_qns`
set (`usage_extractor.py:306,330-332`). Virtual QN is `{instantiation_path}__{calc_instance_name}`
(line 246-247). When a retyped usage is keyed under *both* types, an IFE-owned and a HIF-owned
template with the **same instance name** resolve to the **same** path and the **same** virtual QN —
they meet at `seen_qns`, where today it is silent first-template-wins. Differently-named templates
produce different QNs and both already survive. **This is the exact spot the tiebreak belongs.**

**The `usage_type_map` consumer trace (confirms L1-3).** `usage_type_map` is read in `graph_builder.py`
at 160/181/283 (threading) and at 1044-1046 inside `_find_literal_redefinition` (behavioral — the
type-aware `target_partdef_qn` match, REQ-LVP-01 Strategy 1). Only 1044-1046 changes an output. The
rest thread or serialize the value. Confirmed: no other reader depends on the old first-type value.

**NewType discipline (doc 10).** `core/identifier_types.py` defines `SysMLQN = NewType("SysMLQN", str)`
and friends (zero runtime cost). Index keys and `usage_type_map` values are PartDef qualified names —
i.e. `SysMLQN`. Current code types them as bare `str`.

**Warning convention.** `modeling-assumptions.md:344-350` numbers validation messages V1–V7. Next
free are **V8, V9**.

**Baseline diff harness.** `scripts/capture_extraction_snapshots.py` re-captures extraction snapshots
(live license); `test_factory_purity` rebuilds graphs offline from committed snapshots and compares
`model_dump` byte-for-byte. A live re-capture whose `git diff` is empty is the runtime zero-diff proof.

---

## Core Concept

A part usage's **declared type is the target of an owned FeatureTyping relationship on the usage
itself** — never a position in `usage.types`. `usage.types` is a flattened, order-unstable view that
mixes the declared type, library types (`Part`), and (for a retyped usage) inherited user supertypes.
The fix is to stop reading position and read the relationship.

Concretely, one shared primitive answers "what user-model PartDefs does this usage carry, and which is
its declared (most-specific) type?" by walking `usage.heritage` for `FeatureTyping` relationships (the
`_get_calc_def_name` precedent) and intersecting `usage.types` against the set of user PartDef QNs. The
two fix sites consume that primitive with different projections:

- **The index** (`_build_part_usage_index`) keys the usage under **all** user-model types it carries —
  owned FeatureTyping targets *plus* every user PartDef in `usage.types`. This is a superset that
  preserves the supertype-template flow retyped usages rely on today, and adds the subtype key that was
  missing. For plain usages the set is a single declared type — identical to today's behavior.
- **`usage_type_map`** picks the **single most-specific** owned FeatureTyping target (deterministic-first
  + V8 warning if incomparable), because literal-default resolution needs exactly one PartDef per usage.

The collision tiebreak is not new machinery — it is a rule applied at the existing `seen_qns` dedup:
when two *different* owners produce the same virtual QN, keep the most-specific owner and emit V9.

Nothing else moves. No backtracker, no generation, no template-detection change.

## Key Bets

- **B1. A usage's declared type is reachable as an owned `FeatureTyping` target via `usage.heritage`,
  and `heritage` yields owned typings — not typings inherited up the supertype chain.** The whole fix,
  and the plain-subtype Non-Goal, rest on this. *If false → either we can't find the declared type at
  all, or (if heritage climbs the chain) a plain `part x : Subtype` resolves through its own typing up to
  a supertype, silently contradicting the Non-Goal and changing baseline output.* **Gated by probe Q2.**

- **B2. For a retyped usage, the user supertype is present in `usage.types`; for a plain usage, user
  supertypes are absent (only the declared type).** This is what makes "index under all user types in
  `usage.types`" preserve supertype flow for retyped usages *without* leaking it to plain ones. *If false
  → the preservation contract and the Non-Goal both break: plain usages would start pulling supertype
  templates, changing baselines.* Confirmed by the research live probe; **re-confirmed by probe Q1.**

- **B3. No existing baseline model carries a retyping shape, so indexing under all user-model types adds
  no consequential keys to any current model.** *If false → the 4 baselines shift and the zero-diff SC
  fails.* Verified statically in spec-review; **proven by the live re-capture (Validation).**

- **B4. Same-named templates on both owners are the only case that collides on one virtual QN;
  differently-named templates never collide.** The tiebreak's correctness depends on this being the
  complete set of collisions. *If false → either a real collision escapes the tiebreak (silent
  double-pick) or the tiebreak fires on a non-collision.* Confirmed by the QN construction
  (`usage_extractor.py:246-247`); locked by fixture shapes 3 & 4.

## Key Decisions

- **D1. One shared helper for the heritage walk; two call sites keep their own projection.** A single
  function returns a usage's owned FeatureTyping targets (and a second returns the user-PartDef subset of
  `usage.types`); the index calls it and takes all, `usage_type_map` calls it and takes most-specific.
  *Rejected: duplicating the heritage walk in both files* — duplication is exactly what let the two sites
  drift into the same bug independently. *Rejected: threading one precomputed usage→type map across
  pipeline stages (a shared cache)* — the two passes run in different stages over different element sets
  (`elements_of_type(model,"PartUsage")` vs `PartDefinition.owned_members`) and need different
  projections; a shared cache adds cross-stage coupling the 1-day budget does not want. R1 compute-once
  applies to the *derivation logic*, which the helper centralizes — not to a runtime cache.

- **D2. Most-specific comparison is a specialization-chain walk over PartDef heritage.** Given two user
  PartDef QNs, A is more specific than B iff B is in A's supertype closure. Reuse the same
  `heritage`/`Specialization` walk. Incomparable (neither in the other's closure) → deterministic
  first-in-stable-order (sorted by QN) + V8. *Rejected: relying on `usage.types` ordering to rank
  specificity* — that ordering is the unstable thing we are removing.

- **D3. Collision tiebreak lives at the `seen_qns` dedup, comparing template owners' specificity.**
  Replace the `set` with a `dict[str, CalcUsageData]` (QN → winning virtual) so a second arrival can be
  compared, not blindly dropped. Same owner re-arriving (idempotent multi-path) stays silent; different
  owners → keep most-specific + V9. *Rejected: a separate post-pass that regroups virtual instances by QN*
  — more code, same result, and it would re-derive owner specificity the dedup already has in hand.

- **D4. New/changed keys and map values typed as `SysMLQN` (doc 10).** Zero runtime cost; matches the
  typed-registry discipline. *Rejected: leaving them bare `str`* — the SC calls for doc-10-clean keys and
  the NewType is free. Not a broad refactor: only the touched signatures.

- **D5. One fixture model holds shapes 1–5; shape 6 is the existing 4 baselines (no new fixture).**
  Shapes 1–4 compose in a single Facility/Variant retype design; shape 5 (plain-subtype negative) is a
  sibling plain usage in the same design. *Rejected: one file per shape* — five near-identical models to
  maintain, and the shapes are clearer read together. Exact SysML is a plan call.

## Architecture

Data flow, unchanged except at the two picks and the dedup:

```
elements_of_type(PartUsage) ─┐
                             ├─► _build_part_usage_index ──► index: SysMLQN → [PartUsage]   (FIX 1: all user types)
user PartDef QN set ─────────┘                                     │
                                                                   ▼
templates (is_template) ──► _expand_template_calc_usages ──► _find_instantiation_paths
                                                                   │
                                        seen dedup (FIX 3: tiebreak + V9) ──► virtual CalcUsages

PartDefinition.owned_members ──► extract_hierarchy_data ──► usage_type_map (FIX 2: most-specific + V8)
                                                                   │
                                            graph_builder._find_literal_redefinition (unchanged consumer)
```

The shared heritage-walk helper sits under both FIX 1 and FIX 2. FIX 3 is local to expansion.

## Required Invariants

- **INV-1.** For every PartUsage, `index` contains an entry under each user-model PartDef the usage
  carries (owned FeatureTyping targets ∪ user PartDefs in `usage.types`), and under no library type.
- **INV-2.** For a plain (non-retyped) usage the key set is exactly its one declared type — byte-identical
  to today. (This is what B2 buys and what keeps baselines invariant.)
- **INV-3.** `usage_type_map[(owning_qn, name)]` is the usage's most-specific owned FeatureTyping target;
  single-valued per usage.
- **INV-4.** Two templates share a virtual QN ⇔ same instantiation path ∧ same calc instance name. The
  tiebreak fires only on that, only when owners differ.
- **INV-5.** Every emitted virtual QN is unique in the output (dedup preserved); the tiebreak changes
  *which* template wins a shared QN, never the count of distinct QNs.

## Component Overview

- **`owned_feature_typing_targets(usage) → list[FeatureTyping target elems]`** — new shared helper
  (`usage_extractor.py`, importable by `hierarchy_resolver.py`). Walks `usage.heritage`, filters
  `FeatureTyping`, returns targets in heritage order. The single primitive both sites use.
- **`user_partdef_types(usage, user_qn_set) → list[SysMLQN]`** — new shared helper. Maps `usage.types`
  to QNs, keeps those in `user_qn_set`. Used by the index only.
- **`most_specific(qns, model) → (winner, incomparable: bool)`** — new shared helper. Specialization-chain
  comparison (D2). Used by `usage_type_map` (V8) and the collision tiebreak (V9).
- **`_build_part_usage_index`** — FIX 1. Builds `user_qn_set` once from
  `elements_of_type(model,"PartDefinition")`, then keys each usage under the union of the two helpers'
  results. Return type → `dict[SysMLQN, list[Any]]`.
- **`extract_hierarchy_data` (usage_type_map block, lines 526-533)** — FIX 2. Replaces
  `next(iter(member.types))` with `most_specific(owned_feature_typing_targets(member) targets)`; V8 on
  incomparable.
- **`_expand_template_calc_usages`** — FIX 3. `seen_qns` set → `dict` keyed by virtual QN; on a second
  arrival with a different owner, `most_specific` decides the keeper and V9 is emitted once per collision
  class.

## Non-Goals

- Supertype-chain template inheritance for **plain** `part x : Subtype` usages (needs a deliberate
  specialization walk; MFE-epic note). This design only preserves the supertype flow retyped usages
  already carry in `usage.types`.
- Cross-part channel wiring for retyped nested parts (Item 10).
- Any change to template detection, virtual-binding rewrite, backtracker, or generation.

## Implementation Notes

- **Probe first (de-risk #1).** Run `probe/probe.py` (a live-license run — the design could not execute
  it in the sandbox). It answers, against a synthetic retype model:
  - **Q1** — `usage.types` order for the Variant's retyped `driver`: expect `['IFE Driver', …, 'HIF Driver']`,
    declared type last (research confirmed on fusion-tea; re-confirm here). Locks B2.
  - **Q2** — heritage FeatureTyping targets on the retyped usage: **how many**, and are they **owned-only**?
    Compare the plain `Facility.driver` (expect one owned typing → `IFE Driver`) against `Variant.driver`
    (expect its own typing → `HIF Driver`, *not* also `IFE Driver` via inheritance). If heritage climbs the
    chain, B1 is false and the Non-Goal leaks — stop and revisit. Locks B1 and the multi-typing ordering
    for D2.
  - **Q3** — whether any accessor gives owned typings directly (`owned_relationships`/`declared_type`),
    which would simplify the helper. Nice-to-have, not gating.
  - **Q4 (add to probe)** — does `elements_of_type(model,"PartDefinition")` exclude the standard library
    (no `Part`)? If yes, the `user_qn_set` intersection is the whole filter (cheap, unique-by-construction).
    If it includes library defs, fall back to source-document filtering (type defined under a loaded
    user-model path). Decides the D1 user-filter mechanism.
- **Warning texts (V-style), dedup, placement.** Both are appended to the existing `warnings` lists and
  logged (`logger.warning`), matching `usage_extractor.py:314-315`.
  - **V9 (collision tiebreak, `_expand_template_calc_usages`):**
    `"Template collision on '{virtual_qn}': owners '{owner_a}' and '{owner_b}' both define calc "
    `'{calc_name}'; kept most-specific owner '{winner}'."` Dedup by `(owner_a, owner_b, calc_name)` so a
    usage instantiated N times warns **once**, not N times.
  - **V8 (incomparable multi-typing, `usage_type_map`):**
    `"Usage '{owning_qn}.{name}' has multiple incomparable owned types {sorted_qns}; resolved defaults "
    `"against '{winner}' (first in stable order)."` Dedup is natural — one entry per `(owning_qn, name)`.
- **`most_specific` edge cases.** Zero targets → skip (usage keyed only by `usage.types` user entries; map
  gets no entry, as today). One target → return it, no comparison, no warning. Two+ comparable → the sink
  of the chain. Two+ incomparable → sorted-first + warning.
- **Do not touch** the `no PartUsage instantiations — dropped` warning (line 318-326) — it stays as the
  correct signal for a genuinely uninstantiated template (agentic-mbse Level-6 check depends on it).

## Potential Risks

- **Heritage climbs the chain (B1 false).** Highest risk; fully gated by probe Q2 before any code. If true,
  the helper must use an owned-only accessor (probe Q3) instead of raw `heritage`, or filter heritage to
  direct/owned relationships. Design does not proceed past the probe on this point.
- **`elements_of_type` includes library defs (Q4).** Would make the naive intersection admit `Part`.
  Mitigation: source-document filter fallback, decided at the probe, before implementation.
- **A baseline model does carry a retyping shape after all (B3 false).** The live re-capture catches it as
  a non-empty `git diff`; investigate before committing rather than force-recapture.
- **Non-determinism in tie ordering.** Any deterministic pick must sort by QN string, never rely on
  `heritage`/`types` iteration order, or snapshots become machine-dependent.

## Integration Strategy

Confined to `usage_extractor.py` and `hierarchy_resolver.py` plus the shared helpers, a new fixture, its
snapshot, tests, and docs. The only cross-module behavioral effect is the corrected `usage_type_map`
feeding the existing `_find_literal_redefinition` branch — no signature change there. Independent of
in-flight Items 2 (snapshot, landed) and 3 (extractor.py member filter): different files, no overlap.

## Validation Approach

1. **New fixture (`tests/fixtures/retype_model/`, shapes 1–5).** Facility/Variant retype design.
   - Shape 1: Variant's retyped `driver` instantiates the HIF-owned template.
   - Shape 2: same usage still instantiates the IFE-owned (supertype) template.
   - Shape 3: IFE and HIF each own a same-named calc → one virtual QN → most-specific (HIF) wins + V9.
   - Shape 4: IFE and HIF own differently-named calcs → both instantiate, no warning.
   - Shape 5: a plain `part x : 'HIF Driver'` sibling — the IFE-owned template must **not** reach it.
2. **Snapshot capture (Item 2 CLI).** Add `retype_model` to `MODELS` in
   `scripts/capture_extraction_snapshots.py`; run it live; commit the versioned snapshot JSON.
3. **Conformance tests (no mocks — R1).** Extraction-level assertions on the committed snapshot: index
   key set = `{IFE Driver, HIF Driver}` for the retyped usage; virtual instances present per shapes 1/2/4;
   tiebreak winner + V9 text per shape 3; negative assertion per shape 5; `usage_type_map` for the retyped
   usage resolves to `HIF Driver`.
4. **Baseline zero-diff (runtime re-run — L3-3, B3).** Re-run `capture_extraction_snapshots.py` and
   `capture_pipeline_baselines.py` on the 4 pipeline baselines with a live license; **`git diff` on their
   snapshot/baseline files must be empty.** Then `test_factory_purity` (offline) confirms generated graphs
   are byte-identical. Inspection is not accepted as proof.
5. **Unit test for `most_specific`** on comparable and incomparable pairs (guards D2/V8 without a license).

## Docs / Matrix Plan

- **`modeling-assumptions.md` §5** — add retyping to the Redefinition Types framing: a `:>>` retype to a
  subtype pulls the subtype's template calcs while supertype templates continue to flow; a calc *replacing*
  an inherited one must reuse its name (same-QN redefinition). Add **V8, V9** to the Validation table.
- **`reference/25-hierarchy-resolver.md`** — document the `usage_type_map` most-specific rule (REQ-LVP-08)
  and its one behavioral consumer.
- **`reference/01-extraction.md`** — document the all-user-types index rule (REQ-EXT-13) and the collision
  policy (REQ-EXT-14), as touched.
- **`verification-matrix.md`** — add rows for REQ-EXT-13, REQ-EXT-14, REQ-LVP-08 mapped to the tests above.
- **agentic-mbse impact (carry-through, Item 12 — not inline):** teach retyping as a supported pattern;
  update the Level-6 "part def with template calcs but no instantiation" check so retyped usages count as
  an instantiation. Recorded verbatim in spec §"agentic-mbse impact".

## Next-Stage Handoff

- **Fixed:** the two fix sites and their projections (D1); tiebreak location and semantics (D3);
  fixture shape matrix (D5); warning texts and dedup keys; REQ tags EXT-13/14, LVP-08; V8/V9.
- **Open until the probe runs:** the exact heritage accessor (raw `heritage` vs owned-only, Q2/Q3) and the
  user-package filter mechanism (intersection vs source-document, Q4). Both are gated, both cheap to settle.
- **De-risk first:** run `probe/probe.py` (Q1–Q4) before writing any fix — B1 is the load-bearing bet and a
  five-minute live probe settles it. Do not write the helper until Q2 confirms heritage is owned-only.

---
Next Step: After approval → `/_my_plan`.
