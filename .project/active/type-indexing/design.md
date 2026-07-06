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

**Key form (doc 10).** `core/identifier_types.py:22` defines `SysMLQN` as the **`::`-separated** QN
form. The index keys and `usage_type_map` values here are produced by `build_element_qualified_name`,
whose default yields the **`__`-separated** (EQN) form — and the one behavioral consumer compares them
against `redef.owning_part_qn`, which is also `__`-form (`graph_builder.py:1053,1056` splits on `__`).
So these keys **must stay `__`-form `str`** — `SysMLQN` is the wrong wrapper and would mislabel the
separator. Doc-10 discipline asks for "unique-by-construction, no ambiguous string keys" (satisfied:
PartDef QNs are globally unique); it does **not** mandate the `SysMLQN` NewType at these sites, and the
established convention at both sites is already the bare `__`-form string.

**Warning convention.** `modeling-assumptions.md:344-350` numbers validation messages V1–V7. Item 3
lands first and claims **V8** (anonymous-return diagnostic). So this item's next free numbers are
**V9** (collision tiebreak) and **V10** (incomparable multi-typing).

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
  + V10 warning if incomparable), because literal-default resolution needs exactly one PartDef per usage.

The collision tiebreak is not new machinery — it is a rule applied at the existing `seen_qns` dedup:
when two *different* owners produce the same virtual QN, keep the most-specific owner and emit V9.

Nothing else moves. No backtracker, no generation, no template-detection change.

## Key Bets

- **B1. A usage's declared type is reachable as an owned `FeatureTyping` target via `usage.heritage`,
  and `heritage` yields owned typings — not typings inherited up the supertype chain.** The whole fix,
  and the plain-subtype Non-Goal, rest on this. *If false → either we can't find the declared type at
  all, or (if heritage climbs the chain) a plain `part x : Subtype` resolves through its own typing up to
  a supertype, silently contradicting the Non-Goal and changing baseline output.* **Gated by probe Q2.**

- **B2. Two halves. (a) For a retyped usage the user supertype is present in `usage.types`. (b) For a
  plain `part x : Subtype` usage, user supertypes are *absent* — `.types` carries only the declared
  type.** Half (a) makes superset indexing preserve supertype flow for retyped usages; half (b),
  **B2-plain, is the load-bearing bet for baseline invariance** — it is what stops superset indexing from
  adding a supertype key to the plain subtype-typed usages that existing baselines very likely already
  contain. *If (a) false → the preservation contract breaks. If (b) false → every plain `part x : Subtype`
  in the 4 baselines gains a supertype key and output shifts; the Non-Goal also leaks.* Half (a) confirmed
  by the research live probe; **half (b) is gated by probe Q1's plain-usage shape (`plain_hif`) — it is
  probed, not assumed.**

- **B3. No existing baseline model carries a *retyping* (`:>>`) shape.** *If false → a baseline's retyped
  usage gains its subtype key and output could shift.* Verified statically in spec-review. **Necessary but
  not sufficient for baseline invariance** — B2-plain is the bet that actually covers the common plain
  subtype-typed usage; B3 only covers the retyping shape. The live zero-diff re-capture (Validation) is
  the backstop that proves both together.

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
  `heritage`/`Specialization` walk. The walk needs the PartDef *element* for a QN string: build a
  **`{qn: PartDefElement}` lookup once** from `elements_of_type(model,"PartDefinition")` and pass it into
  `most_specific` — not an O(partdefs) scan per comparison. Incomparable (neither in the other's closure)
  → deterministic first-in-stable-order (sorted by QN) + V10. For 3+ owners on a chain, reduce
  **pairwise**, which converges to the chain sink. *Rejected: relying on `usage.types` ordering to rank
  specificity* — that ordering is the unstable thing we are removing.

- **D3. Collision tiebreak lives at the `seen_qns` dedup, comparing template owners' specificity.**
  Replace the `set` with a `dict[str, CalcUsageData]` (`__`-form QN → winning virtual) so a second arrival
  can be compared, not blindly dropped. The specificity comparison uses the **stored virtual's**
  `owning_part_def_qn` (`_create_virtual_calc_usage`, line 266) vs the incoming one — do not re-derive it.
  Same owner re-arriving (idempotent multi-path) stays silent; different owners → keep most-specific + V9.
  *Rejected: a separate post-pass that regroups virtual instances by QN* — more code, same result, and it
  would re-derive owner specificity the dedup already has in hand.

- **D4. New/changed keys and map values stay plain `__`-form `str` (not `SysMLQN`).** `SysMLQN` is the
  `::`-form (`identifier_types.py:22`); these keys are `__`-form and the consumer compares them `__`-form
  (`graph_builder.py:1053,1056`), so `SysMLQN` would mislabel the separator and the runtime form must not
  change to `::`. Doc-10's ask (unique-by-construction, no ambiguous keys) is met by PartDef-QN
  uniqueness — it does not mandate `SysMLQN` here. *Rejected: typing them `SysMLQN`* — factually wrong
  separator, and it would break the `__`-split consumer. *Rejected: coining a new `__`-form NewType* —
  out of scope for a 1-day item; the bare `__`-form string is the established convention at both sites.

- **D5. One fixture model holds shapes 1–5; shape 6 is the existing 4 baselines (no new fixture).**
  Shapes 1–4 compose in a single Facility/Variant retype design; shape 5 (plain-subtype negative) is a
  sibling plain usage in the same design. *Rejected: one file per shape* — five near-identical models to
  maintain, and the shapes are clearer read together. Exact SysML is a plan call.

## Architecture

Data flow, unchanged except at the two picks and the dedup:

```
elements_of_type(PartUsage) ─┐
                             ├─► _build_part_usage_index ──► index: str(__QN) → [PartUsage]  (FIX 1: all user types)
user PartDef QN set ─────────┘                                     │
                                                                   ▼
templates (is_template) ──► _expand_template_calc_usages ──► _find_instantiation_paths
                                                                   │
                                        seen dedup (FIX 3: tiebreak + V9) ──► virtual CalcUsages

PartDefinition.owned_members ──► extract_hierarchy_data ──► usage_type_map (FIX 2: most-specific + V10)
                                                                   │
                                            graph_builder._find_literal_redefinition (unchanged consumer)
```

The shared heritage-walk helper sits under both FIX 1 and FIX 2. FIX 3 is local to expansion.

## Required Invariants

- **INV-1.** For every PartUsage, `index` contains an entry under each user-model PartDef in the **set
  union** (owned FeatureTyping targets ∪ user PartDefs in `usage.types`), and under no library type. Build
  the per-usage key set as a `set` — the declared type is *both* an owned FeatureTyping target and a
  `usage.types` member, so naive concatenation would list the usage twice under that key.
- **INV-2.** For a plain (non-retyped) usage the key set is exactly its one declared type — byte-identical
  to today. This rests on **B2-plain** (plain `.types` excludes user supertypes) and is what keeps
  baselines invariant.
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
- **`user_partdef_types(usage, user_qn_set) → list[str]`** — new shared helper. Maps `usage.types`
  to `__`-form QNs, keeps those in `user_qn_set`. Used by the index only.
- **`most_specific(qns, qn_to_partdef) → (winner, incomparable: bool)`** — new shared helper.
  Specialization-chain comparison (D2), driven by a prebuilt `{qn: PartDefElement}` lookup (built once, not
  per call). Used by `usage_type_map` (V10) and the collision tiebreak (V9).
- **`_build_part_usage_index`** — FIX 1. Builds `user_qn_set` (and the `qn_to_partdef` lookup) once from
  `elements_of_type(model,"PartDefinition")`, then keys each usage under the **set union** of the two
  helpers' results. Return type → `dict[str, list[Any]]` (`__`-form keys).
- **`extract_hierarchy_data` (usage_type_map block, lines 526-533)** — FIX 2. Replaces
  `next(iter(member.types))` with `most_specific(owned_feature_typing_targets(member) targets)`; V10 on
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
  it in the sandbox; `uv run` needs an approval the non-interactive sandbox can't grant). It answers,
  against the synthetic model in `probe/model.sysml`:
  - **Q1** — `usage.types` order and membership. For `Variant.driver` (retyped) expect
    `['IFE Driver', …, 'HIF Driver']`, declared type last (research confirmed on fusion-tea). For the added
    plain `plain_hif : 'HIF Driver'` expect `.types` to **exclude** `IFE Driver` — this is the direct test
    of **B2-plain**, on which baseline invariance rests. Locks B2 (both halves).
  - **Q2** — heritage FeatureTyping targets, owned-only check. Compare `Facility.driver` (one owned typing
    → `IFE Driver`) against `Variant.driver` (its own typing → `HIF Driver`, *not* also `IFE Driver` via
    inheritance). If heritage climbs the chain, **B1 is false → hard stop** (see below). Locks B1.
  - **Q2b (multi-typing)** — the added `multi : 'IFE Driver', 'Other Driver'` usage (two unrelated user
    typings): print its heritage FeatureTyping targets to confirm multiple owned typings exist and in what
    order. This locks D2's incomparable branch and the V10 warning — otherwise written blind.
  - **Q3** — whether any accessor gives owned typings directly (`owned_relationships`/`declared_type`).
    **Promoted to gating iff Q2 shows heritage climbs the chain** — it becomes the only concrete owned-only
    mechanism at that point. Otherwise informational.
  - **Q4** — does `elements_of_type(model,"PartDefinition")` exclude the standard library (no `Part`)? If
    yes, the `user_qn_set` intersection is the whole filter (cheap, unique-by-construction). If it includes
    library defs, fall back to source-document filtering (type defined under a loaded user-model path).
    Decides the D1 user-filter mechanism.
- **B1-false is a hard stop, not a fallback.** If Q2 shows heritage is not owned-only and Q3 finds no
  owned-only accessor, there is no in-budget path — **report and halt the item pending a new approach**;
  do not improvise a heritage filter. The precedent (`_get_calc_def_name`) plus the research make B1 likely
  true, so this branch is contained, but it is a stop.
- **Warning texts (V-style), dedup, placement.** Both are appended to the existing `warnings` lists and
  logged (`logger.warning`), matching `usage_extractor.py:314-315`.
  - **V9 (collision tiebreak, `_expand_template_calc_usages`):**
    `"Template collision on '{virtual_qn}': owners '{owner_a}' and '{owner_b}' both define calc "
    `'{calc_name}'; kept most-specific owner '{winner}'."` Dedup by `(owner_a, owner_b, calc_name)` so a
    usage instantiated N times warns **once**, not N times. *Known limitation:* a 3-owner chain colliding
    on one QN reduces pairwise to the right winner, but this pair-keyed dedup may emit more than one line;
    out of the pinned 2-owner fixture matrix — do not build for it.
  - **V10 (incomparable multi-typing, `usage_type_map`):**
    `"Usage '{owning_qn}.{name}' has multiple incomparable owned types {sorted_qns}; resolved defaults "
    `"against '{winner}' (first in stable order)."` Dedup is natural — one entry per `(owning_qn, name)`.
- **`most_specific` edge cases.** Zero targets → skip (usage keyed only by `usage.types` user entries; map
  gets no entry, as today). One target → return it, no comparison, no warning. Two+ comparable → the sink
  of the chain. Two+ incomparable → sorted-first + warning.
- **Do not touch** the `no PartUsage instantiations — dropped` warning (line 318-326) — it stays as the
  correct signal for a genuinely uninstantiated template (agentic-mbse Level-6 check depends on it).

## Potential Risks

- **Heritage climbs the chain (B1 false).** Highest risk; fully gated by probe Q2 before any code. This is
  a **hard stop**: if Q2 shows heritage is not owned-only and Q3 finds no owned-only accessor, report and
  halt — do not improvise a heritage filter (there is no defined mechanism to tell an owned FeatureTyping
  from an inherited one in the `heritage` iterable).
- **`elements_of_type` includes library defs (Q4).** Would make the naive intersection admit `Part`.
  Mitigation: source-document filter fallback, decided at the probe, before implementation.
- **A baseline's plain subtype-typed usage gains a supertype key (B2-plain false).** The real
  baseline-invariance risk (not B3): superset indexing adds a supertype key to any plain `part x : Subtype`
  whose `.types` includes the supertype. Gated by probe Q1's `plain_hif` shape *and* caught by the live
  re-capture as a non-empty `git diff`; investigate before committing rather than force-recapture.
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
4. **Baseline zero-diff (runtime re-run — L3-3; backstops B2-plain + B3).** Re-run
   `capture_extraction_snapshots.py` and `capture_pipeline_baselines.py` on the 4 pipeline baselines with a
   live license; **`git diff` on their snapshot/baseline files must be empty.** Then `test_factory_purity`
   (offline) confirms generated graphs are byte-identical. Inspection is not accepted as proof.
5. **Unit test for `most_specific`** on comparable and incomparable pairs (guards D2/V10 without a license).

## Docs / Matrix Plan

- **`modeling-assumptions.md` §5** — add retyping to the Redefinition Types framing: a `:>>` retype to a
  subtype pulls the subtype's template calcs while supertype templates continue to flow; a calc *replacing*
  an inherited one must reuse its name (same-QN redefinition). Add **V9, V10** to the Validation table
  (V8 belongs to Item 3).
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
  fixture shape matrix (D5); warning texts and dedup keys; REQ tags EXT-13/14, LVP-08; V9/V10.
- **Open until the probe runs:** the exact heritage accessor (raw `heritage` vs owned-only, Q2/Q3) and the
  user-package filter mechanism (intersection vs source-document, Q4). Both are gated, both cheap to settle.
- **De-risk first:** run `probe/probe.py` (Q1, Q2, Q2b, Q3, Q4) before writing any fix — B1 (heritage
  owned-only) and B2-plain (plain `.types` excludes supertypes) are the load-bearing bets, and D2's
  incomparable branch (Q2b multi-typing) is otherwise written blind. Do not write the helper until Q2
  confirms heritage is owned-only; **a false B1 is a hard stop**, not a fallback.

---
Next Step: After approval → `/_my_plan`.
