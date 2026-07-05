# Spec: Part-Usage Type Indexing (SC-3)

**Status:** Draft
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
- `hierarchy_resolver.py` `extract_hierarchy_data` (lines 526–533) does the same
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
      instantiated before (accidental supertype-template flow is preserved, not lost —
      see Non-Goals for why this is deliberate, not a full inheritance walk).
- [ ] The same first-type bug is fixed in `usage_type_map`, so literal-value propagation
      resolves a retyped usage's redefinition defaults against the correct (declared) PartDef.
- [ ] The 4 pipeline baselines (`attr_expr_probe`, `catf_mfe`, `chain_spike`,
      `solar_battery`) are **byte-identical** — no existing model has a retyping shape,
      and all-types indexing adds no consequential keys for them.
- [ ] The virtual-QN collision case (supertype and subtype own a template calc that
      produces the same virtual QN) is covered by a test with a deterministic, documented
      outcome — a most-specific-owner tiebreak, or at minimum a clear warning.
- [ ] New lookup keys are unique by construction and consumer-scope-prefixed (R1 / doc 10);
      no ambiguous string keys are introduced.
- [ ] `docs/architecture/reference/25-hierarchy-resolver.md`, `01-extraction.md` (as
      touched), `modeling-assumptions.md` §5, and the verification matrix are updated with
      REQ tags for the new behavior.
- [ ] "agentic-mbse impact" recorded (see final section).

## Known Requirements

- **[HARD]** The type used for indexing MUST be the usage's **owned FeatureTyping target**
  (the declared type), determined by walking heritage for the `FeatureTyping` relationship —
  never a position in `usage.types`. Mechanism precedent already in-repo:
  `_get_calc_def_name`'s heritage walk (`extractor.py:316-326`), which picks the
  `FeatureTyping` target from `elem.heritage`.

- **[HARD]** `_build_part_usage_index` MUST index each usage under **every user-model
  PartDefinition in `usage.types` plus the owned FeatureTyping target**, filtered to user
  packages. Indexing under the declared type alone is wrong — it would drop the retyped
  usage's *supertype* template flow that models rely on today. Indexing under library types
  (`Part`, ISQ base types, etc.) is wrong — those are not user PartDefs and must be filtered
  out. For the probe case the resulting key set is `{'IFE Driver', 'HIF Driver'}`.

- **[HARD]** `extract_hierarchy_data`'s `usage_type_map` (`hierarchy_resolver.py:526-533`)
  MUST resolve to the FeatureTyping (declared) target, not `next(iter(member.types))`. This
  map keys `(owning_qn, usage_name) → type_qn` and feeds literal-value propagation
  (REQ-LVP-06); a single declared type per usage is correct here (unlike the index, which is
  multi-key by design).

- **[HARD]** Existing baselines MUST remain byte-identical. Regeneration, if any is needed,
  goes through the `scripts/capture_*.py` scripts with a reviewed diff — never hand-edited
  (R3).

- **[NEED]** When supertype and subtype own **differently-named** template calcs, both
  instantiate. If that risks double-counting (the subtype's calc was meant to replace the
  supertype's), the modeler is warned rather than silently given both. (Diagnostics follow
  the V1–V6 pattern — a clear, actionable message, nothing dropped silently.)

- **[NEED]** When supertype and subtype own template calcs that resolve to the **same**
  virtual QN, the outcome is deterministic and tested — the most-specific owner wins, or a
  warning names the collision. The reader/modeler can predict which module is generated.

- **[HARD]** New behavior lands with a **real SysML fixture** (retyping shape) plus an
  extraction snapshot and conformance tests — no mocks. Mocks masked this exact bug because
  their `types` lists had one element (R1). The new fixture needs a live-license snapshot
  capture (license is live; fine).

- **[INFERRED]** The fix is confined to `usage_extractor.py` and `hierarchy_resolver.py`
  (plus fixture/snapshot/test/doc files). It touches no backtracker, graph-builder, or
  generation code. This keeps it independent of the concurrently-in-flight Items 2 and 3.

## Non-Goals

- **Supertype-chain template inheritance for plain subtype-typed usages.** A template owned
  by a supertype does not reach a *plain* `part x : Subtype` usage, because a plain usage's
  `types` list does not contain its user supertypes (only the declared type). Making that
  work needs a supertype-chain walk over the specialization hierarchy — recorded as a note
  for the MFE epic, out of scope here. This item only preserves the supertype flow that
  *retyped* usages already get accidentally (their `types` list happens to include both).

- **Cross-part channel wiring** for retyped nested parts (SC-5 stage 2 / Item 10). Item 10
  depends on this item's index fix but is separate work.

- **Any change to the template-detection or virtual-instance machinery** beyond the indexing
  key set and the collision tiebreak.

## Open Questions / Deferred to design

- **Collision resolution mechanism.** Whether to implement a deterministic most-specific-owner
  tiebreak (subtype wins over supertype for a colliding virtual QN) or ship a warning-only
  floor for this item's budget (1 day). The success criterion is satisfied either way;
  design picks based on how cheaply the most-specific-owner comparison falls out of the
  heritage data already in hand.

- **User-package filter mechanism.** How to decide a PartDefinition in `usage.types` is
  "user-model" vs standard-library — e.g. intersect against the set of user PartDef QNs
  already enumerated by `elements_of_type(model, "PartDefinition")`, or test the type's
  source document against the user model paths. Both are viable; design picks the one that
  is unique-by-construction and cheapest. (Note: verify whether `elements_of_type` already
  excludes library elements, which would make the intersection trivial.)

- **Fixture design.** Whether to author a minimal synthetic retyping fixture (a base part
  def with a template calc, a subtype adding its own template calc, and a design that
  retypes a usage to the subtype) or lift a reduced shape from the fusion-tea IFE models.
  A minimal synthetic fixture that also carries the collision case is the likely choice, but
  design/plan settles the exact SysML.

- **Whether the collision-case shape lives in the same fixture** as the happy-path retyping
  or a second dedicated fixture. Deferred to design/plan.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 4; cross-cutting R1/R2/R3)
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
- **Design:** `.project/active/type-indexing/design.md` (to be created)

---

## Proposed REQ tags (for design to confirm and place in the verification matrix)

- **REQ-EXT-10** — `_build_part_usage_index` SHALL index each PartUsage under its owned
  FeatureTyping target and every user-model PartDefinition in `usage.types` (filtered to
  user packages), never by list position.
- **REQ-EXT-11** — When two template calcs from different owners in a retyped usage's type
  set resolve to the same virtual QN, expansion SHALL produce a deterministic result
  (most-specific owner) or a warning; it SHALL NOT silently pick one.
- **REQ-LVP-07** — `usage_type_map` SHALL resolve each `(owning_qn, usage_name)` to the
  usage's FeatureTyping (declared) target, not the first entry of `usage.types`.

---

## agentic-mbse impact

sysml-codegen defines the executable subset; agentic-mbse teaches and audits it (R2). This
item's recorded impact, for Item 12 to execute (nothing here is urgent enough to do inline):

1. **Teach retyping as a supported pattern** (MODELING_GUIDE / sysml-conventions): a design
   may retype a part usage to a subtype (`part :>> driver : 'HIF Driver'`) to pull in the
   subtype's template calcs, and this now flows through generation. Document that the subtype
   should specialize the base part def (`part def 'HIF Driver' :> 'IFE Driver'`).

2. **Record the "part def with template calcs but no instantiation" Level-6 check**
   (register A-1 row 4, updated for this item's retyping support). A calc-bearing part def
   that is never instantiated — plainly or by retyping — should FAIL the auditor, since its
   template calcs will be dropped. This item makes retyping count as an instantiation, so the
   check's definition of "instantiated" must include retyped usages. File for Item 12.

3. No inline agentic-mbse change is required by this item.

---

**Next Steps:** After approval, proceed to `/_my_spec_review`, then `/_my_design`.
