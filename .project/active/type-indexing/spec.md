# Spec: Part-Usage Type Indexing (SC-3)

**Status:** Draft (revised after spec-review 2026-07-05)
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM
**Branch:** upstream-findings-epic
**Epic:** UPSTREAM-FINDINGS — Item 4

---

## Problem

When a modeler retypes a part usage to a subtype — `part :>> driver : 'HIF Driver'`,
where `HIF Driver` specializes `IFE Driver` — the subtype's template calcs are
silently dropped. The generated pipeline is missing modules the model clearly asks
for, with no warning.

The cause is that two places pick a part usage's type by **list position** instead
of by the declared type:

- `usage_extractor.py` `_build_part_usage_index` (line ~163) does
  `next(iter(usage.types))` — the *first* type in the list.
- `hierarchy_resolver.py` `extract_hierarchy_data` (lines 527–531) does the same
  `next(iter(member.types))` to build `usage_type_map`, which literal-value
  propagation uses to resolve redefinition defaults.

For a **plain** usage (`part driver : 'HIF Driver'`) the declared type is first and
user supertypes are absent, so first-type happens to be right. For a **retyped**
usage the declared type is **last** — a live probe on the fusion-tea model shows
`usage.types = ['IFE Driver', Part, …, 'HIF Driver']`. So the index keys the usage
under `IFE Driver` (a supertype), the subtype `HIF Driver` never appears as a key,
and `HIF Driver`'s template calcs find no instantiation path and are dropped. The
hierarchy resolver has the mirror bug: it resolves the retyped usage's redefinition
defaults against the wrong PartDef.

This blocks the fusion-tea MFE epic, whose generic-plant → specialized-instance
structure *is* this retyping shape. Their current `hif_driver_instance` workaround
abandons the redefined slot, defeating the reuse the epic is built around. It also
survived 1,500+ conformance tests because zero fixtures use retyping and the one
unit test mocked a single-element `types` list — the exact shape that hides the bug.

Retyping is not forbidden by the supported-subset contract; the template-instantiation
convention (`modeling-assumptions.md` §5) lists LITERAL/CHAIN/deep-path redefinitions
and is simply silent on type-redefinition. This item makes retyping a supported,
tested pattern.

## Success Criteria

- [ ] A retyping fixture where `part :>> driver : 'HIF Driver'` (with `HIF Driver :> IFE Driver`)
      instantiates the **HIF-owned** template calcs — verified end-to-end through the
      pipeline on the new fixture. (fusion-tea models at `~/1cfe/fusion-tea` are readable
      for reference shapes.)
- [ ] The retyped usage still instantiates any **supertype-owned** template calcs it
      instantiated before — supertype-template flow is preserved, *except* where a same-QN
      collision triggers the tiebreak below (see Collision & Multi-Type Policy).
- [ ] The `usage_type_map` fix resolves a retyped usage's redefinition defaults against the
      correct (declared) PartDef, so the type-aware literal-default branch of
      `_find_literal_redefinition` (`graph_builder.py`, REQ-LVP-01 Strategy 1) matches.
- [ ] The 4 pipeline baselines (`attr_expr_probe`, `catf_mfe`, `chain_spike`,
      `solar_battery`) produce a **zero-diff** result when re-run through generation after
      the fix — proven by an actual runtime re-run, not by inspection. (No existing model
      carries a retyping shape, so all-types indexing adds no consequential keys — but this
      must be *shown*, since reasoning-by-inspection is exactly what let SC-3 survive 1,500
      tests.)
- [ ] The same-named collision case (supertype and subtype own a template calc that
      resolves to the same virtual QN) is covered by a test asserting **both** the
      deterministic winner (most-specific owner) **and** the warning naming both candidates.
- [ ] The differently-named case (supertype and subtype own differently-named template
      calcs) is covered by a test asserting **both instantiate** — this is the intended,
      faithful outcome, not a defect.
- [ ] New lookup keys are unique by construction and consumer-scope-prefixed (R1 / doc 10);
      no ambiguous string keys are introduced.
- [ ] `docs/architecture/reference/25-hierarchy-resolver.md`, `01-extraction.md` (as
      touched), `modeling-assumptions.md` §5, and the verification matrix are updated with
      the REQ tags below.
- [ ] "agentic-mbse impact" recorded (see final section).

## Known Requirements

### Indexing (the fix)

- **[HARD]** The type used for indexing MUST be the usage's **owned FeatureTyping target(s)**
  — determined by walking heritage for `FeatureTyping` relationships — never a position in
  `usage.types`. Mechanism precedent already in-repo: `_get_calc_def_name`'s heritage walk
  (`extractor.py:316-326`). Note the precedent itself picks the *first* FeatureTyping in
  heritage; that is a design-time probe, not a settled fact (see below).

- **[HARD]** A usage may carry **more than one** owned FeatureTyping (SysML permits it).
  `_build_part_usage_index` MUST index the usage under **all** owned FeatureTyping targets
  **plus every user-model PartDefinition in `usage.types`**, filtered to user packages.
  - Indexing under the declared type alone is wrong — it would drop the supertype template
    flow that models rely on today (baseline invariance depends on it — see next).
  - Indexing under library types (`Part`, ISQ base types, etc.) is wrong — those are not
    user PartDefs and must be filtered out.
  - For the probe case the resulting user-package key set is `{'IFE Driver', 'HIF Driver'}`.

- **[HARD]** **Supertype-template flow on retyped usages is preserved.** This is the epic's
  stated mechanism ("index under every user-model PartDefinition in `usage.types`") *and*
  baseline invariance depends on it — existing models rely on that flow today. It is a
  contract, not a "don't regress" nicety. Its one exception is the same-QN collision tiebreak
  (below). (This is distinct from the deferred supertype-chain walk for *plain* subtype
  usages — see Non-Goals; those two are different mechanisms.)

### usage_type_map (the mirror fix)

- **[HARD]** `extract_hierarchy_data`'s `usage_type_map` (`hierarchy_resolver.py:527-531`)
  MUST resolve `(owning_qn, usage_name) → type_qn` using the usage's **most-specific owned
  FeatureTyping target**, not `next(iter(member.types))`. If a usage has multiple owned
  FeatureTypings that are not comparable by specialization, pick deterministically
  (first-in-a-stable-order) and emit a warning naming the ambiguity. Unlike the index, this
  map is single-valued per usage by design.

- **[HARD]** The one consumer whose *behavior* changes is the type-aware branch of
  `_find_literal_redefinition` (`graph_builder.py`, REQ-LVP-01 Strategy 1 — "type-aware match
  via `target_partdef_qn`"). Design MUST confirm no other reader of `usage_type_map` relied
  on the old first-type value; the review's trace found the rest are serialization/threading
  (REQ-LVP-06 is only the threading requirement, not the behavioral consumer).

### Collision & Multi-Type Policy (consolidated)

Because a retyped usage is indexed under both its supertype and its subtype, template
expansion runs for both owners. Two cases, one policy each:

- **[NEED] Same-named templates on both types (same virtual QN).** The subtype's template
  calc and the supertype's share an instance name, so both resolve to the same virtual QN
  (`{path}__{calc_instance_name}`). This is a genuine override/redefinition. Resolve it with
  a **deterministic most-specific-owner tiebreak** (the subtype wins) **plus a warning**
  naming both candidate owners and the winner. This tiebreak is the single, explicit
  exception to the supertype-preservation contract above.

- **[NEED] Differently-named templates on both types.** They produce different virtual QNs;
  **both instantiate, full stop.** No warning. There is no signal that distinguishes "two
  legitimately distinct calcs" from "the subtype's differently-named calc was meant to
  replace the supertype's," so a warning here would be pure noise. Rationale: retyping *adds*
  the subtype's calcs while supertype templates continue to flow; a modeler who intends to
  replace a calc uses the **same name** (redefinition), which is exactly the same-QN case
  above.

### Discipline

- **[HARD]** Existing baselines MUST remain byte-identical, proven by a runtime re-run.
  Any regeneration goes through the `scripts/capture_*.py` scripts with a reviewed diff —
  never hand-edited (R3).

- **[HARD]** New behavior lands with a **real SysML fixture** (retyping shape) plus an
  extraction snapshot and conformance tests — no mocks. Mocks masked this exact bug because
  their `types` lists had one element (R1). The new fixture needs a live-license snapshot
  capture (license is live; fine).

- **[INFERRED]** The fix is confined to `usage_extractor.py` and `hierarchy_resolver.py`
  (plus fixture/snapshot/test/doc files). It touches no backtracker or generation code, and
  the only graph-builder interaction is that the corrected `usage_type_map` feeds the
  existing `_find_literal_redefinition` branch. This keeps it independent of the
  concurrently-in-flight Items 2 and 3.

## Fixture Matrix (shapes pinned; exact SysML is a design/plan call)

The fixture(s) MUST cover these shapes so design cannot quietly skip the contested ones.
Whether they live in one fixture or several is a design/plan decision.

1. **Retyped usage, subtype-owned template** — `part :>> x : Subtype`, subtype owns a
   template calc → the subtype's calc instantiates (the happy path).
2. **Supertype-owned template, flow preserved** — the same retyped usage also instantiates a
   supertype-owned template calc (locks the preservation contract).
3. **Same-named collision** — supertype and subtype each own a same-named template calc →
   same virtual QN → most-specific-owner tiebreak fires, with the warning (locks the tiebreak
   and its exception to preservation).
4. **Differently-named, both instantiate** — supertype and subtype own differently-named
   template calcs → both appear in output, no warning (locks the L2-1 resolution as the
   *intended, tested* outcome).
5. **Plain subtype-typed usage — out-of-scope negative** — `part x : Subtype` (plain, not
   retyped): the supertype-owned template MUST NOT reach it (needs the deferred
   supertype-chain walk). This locks the Non-Goal against future drift.
6. **Baseline invariance** — the existing 4 pipeline baselines re-run zero-diff.

## Non-Goals

- **Supertype-chain template inheritance for plain subtype-typed usages.** A template owned
  by a supertype does not reach a *plain* `part x : Subtype` usage, because a plain usage's
  `types` list does not contain its user supertypes (only the declared type). Making that
  work needs a supertype-chain walk over the specialization hierarchy — recorded as a note
  for the MFE epic, out of scope here. This item only preserves the supertype flow that
  *retyped* usages already get (their `types` list includes both), which is a different
  mechanism than a deliberate chain walk.

- **Cross-part channel wiring** for retyped nested parts (SC-5 stage 2 / Item 10). Item 10
  depends on this item's index fix but is separate work.

- **Any change to the template-detection or virtual-instance machinery** beyond the indexing
  key set and the collision tiebreak.

## Open Questions / Deferred to design

- **Owned-FeatureTyping node shape (design-time probe).** "Owned FeatureTyping target" is
  asserted as the right pick, but two node-shape facts must be confirmed by a live probe
  (same probe-first discipline as Items 1–3), because the precedent `_get_calc_def_name`
  picks first-in-heritage — itself position-based:
  1. Behavior when a usage has **multiple** owned FeatureTypings — the index handles all of
     them (requirement above), but `usage_type_map`'s most-specific pick needs the probe to
     confirm how to order/compare them.
  2. Confirm `heritage` yields **owned** typings only, not typings inherited from the
     supertype chain. If heritage climbs the chain, a plain `part x : Subtype` could resolve
     through the subtype's own FeatureTyping up to a supertype and quietly contradict the
     Non-Goal. This probe gates whether the Non-Goal holds as written.

- **User-package filter mechanism.** How to decide a PartDefinition in `usage.types` is
  "user-model" vs standard-library — e.g. intersect against the set of user PartDef QNs
  already enumerated by `elements_of_type(model, "PartDefinition")`, or test the type's
  source document against the user model paths. Design picks the one that is
  unique-by-construction and cheapest. (Verify whether `elements_of_type` already excludes
  library elements, which would make the intersection trivial.)

- **Fixture packaging.** Whether the six pinned shapes live in one fixture or several, and
  the exact SysML text. The shapes are fixed (above); the packaging is a design/plan call.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 4; cross-cutting R1/R2/R3)
- **Spec review:** `.project/active/type-indexing/spec-review.md` (Revise verdict; rulings applied)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` — SC-3 section
    (authoritative; corrects the register's "node-type naming" root cause to first-type-in-list)
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` — SC-3 finding
  - `docs/architecture/modeling-assumptions.md` — §5 Template Instantiation Convention
  - `docs/architecture/reference/25-hierarchy-resolver.md`
  - `docs/architecture/reference/10-output-registry.md` — typed registries / NewType keys
- **Code touched:**
  - `src/sysml_codegen/extraction/usage_extractor.py` — `_build_part_usage_index`
  - `src/sysml_codegen/extraction/hierarchy_resolver.py` — `extract_hierarchy_data` `usage_type_map`
  - Precedent: `src/sysml_codegen/extraction/extractor.py:316-326` — `_get_calc_def_name` heritage walk
  - Behavioral consumer of `usage_type_map`: `src/sysml_codegen/resolution/graph_builder.py` —
    `_find_literal_redefinition` (REQ-LVP-01 Strategy 1)
- **Design:** `.project/active/type-indexing/design.md` (to be created)

---

## Proposed REQ tags (renumbered per review; design confirms and places them in the matrix)

`REQ-EXT-01..12` are taken at HEAD (incl. Item 3's in-flight 10/11/12); `REQ-LVP-01..07` are
shipped. Next free tags:

- **REQ-EXT-13** — `_build_part_usage_index` SHALL index each PartUsage under all of its owned
  FeatureTyping targets and every user-model PartDefinition in `usage.types` (filtered to user
  packages), never by list position.
- **REQ-EXT-14** — When two template calcs from different owners in a retyped usage's type set
  resolve to the same virtual QN, expansion SHALL keep the most-specific owner's (deterministic
  tiebreak) and emit a warning naming both candidates and the winner. Differently-named
  templates SHALL both instantiate with no warning.
- **REQ-LVP-08** — `usage_type_map` SHALL resolve each `(owning_qn, usage_name)` to the usage's
  most-specific owned FeatureTyping target, not the first entry of `usage.types`; incomparable
  multi-typings resolve deterministically with a warning.

---

## agentic-mbse impact

sysml-codegen defines the executable subset; agentic-mbse teaches and audits it (R2). This
item's recorded impact, for Item 12 to execute (nothing here is urgent enough to do inline):

1. **Teach retyping as a supported pattern** (MODELING_GUIDE / sysml-conventions): a design
   may retype a part usage to a subtype (`part :>> driver : 'HIF Driver'`) to pull in the
   subtype's template calcs, and this now flows through generation. Document that the subtype
   should specialize the base part def (`part def 'HIF Driver' :> 'IFE Driver'`), and that a
   calc *replacing* an inherited one must reuse its name (same-QN redefinition), which is how
   the tiebreak recognizes intent.

2. **Record the "part def with template calcs but no instantiation" Level-6 check**
   (register A-1 row 4, updated for this item's retyping support). A calc-bearing part def
   that is never instantiated — plainly or by retyping — should FAIL the auditor, since its
   template calcs will be dropped. This item makes retyping count as an instantiation, so the
   check's definition of "instantiated" must include retyped usages. File for Item 12.

3. No inline agentic-mbse change is required by this item.

---

**Next Steps:** After approval, proceed to `/_my_design`.
