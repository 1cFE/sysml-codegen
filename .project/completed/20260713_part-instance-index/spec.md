# Spec: Part-Instance Index — Subtype Closure and Cardinality Expansion

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12 17:26 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC — Item 4

---

## Problem

Constraint lowering (Item 5) must find every concrete part instance so every modeled
assertion executes. Some instances belong to part definitions that own **only constraints,
no calculations**. Today's instance discovery cannot see them.

Two facts in the current code cause the miss:

- Instance discovery is calc-driven. `find_instance_paths_for_partdef` derives instance
  paths solely from virtual `CalcUsage` qualified names (`pipeline_builder.py:388-395`). A
  model with zero calculations yields zero instances, so a constraint-only definition has no
  discovered instances at all.
- Even the lower-level path finder matches by exact type. `_find_instantiation_paths`
  (`usage_extractor.py:313`) looks a usage up under the exact PartDef QN it carries and does
  no subtype closure. A plain subtype that inherits its base's assertion (`part def
  SpecializedLeaf :> ConstrainedLeaf`) is keyed under the subtype, so a lookup on the base
  never finds it.

S3 proved this live against a calc-free fixture: the current calc-independent base-owner
lookup found eight of nine concrete occurrences and missed exactly the plain subtype; the
downstream helper found nothing (S3 findings §1–2). Without a fix, a constraint-only
definition's assertions would silently never execute — the "silence is never an outcome"
failure the concept exists to stop (concept Design Principle 5; Edge Cases "a part
definition owns constraints but no calculations").

This item builds the production instance index from part structure alone. It is pure
part-structure analysis and consumes no constraint fact schemas, which is why it can land
before Items 1–2. Item 5 consumes the index; this item does not lower or wire anything.

## Success Criteria

- [ ] On the promoted S3 fixture (a model with **zero calculations**), the index finds
      **9/9** expected concrete occurrences — two direct, two nested, one retyped inherited
      feature, one plain subtype, three fixed-multiplicity members — with zero unexpected,
      including the plain subtype the current lookup misses.
- [ ] Two same-named multiplicity members under **different owning definitions with different
      counts** each expand to the correct number of occurrences — the collision case the S3
      probe asserted away (`probe_instance_index.py:74-77`). This requires extending the
      promoted fixture to contain the collision shape.
- [ ] A parameterized, variable, ordered, or unbounded multiplicity **blocks with a named
      diagnostic** naming the offending owner and feature — never a warn-and-drop and never a
      silently reduced instance set.
- [ ] Index entries and their ordering are **byte-identical across repeated live loads** of
      the same model.
- [ ] The existing corpus regenerates **byte-identically**: adding the index does not perturb
      calc-driven discovery or any generated artifact.

## Known Requirements

- **[INHERITED]** (concept "Concrete Lowering"; S3 result) The index is derived from
  `PartUsage` structure and `PartDefinition` heritage alone, independent of calc templates.
  It projects a source owner over its **subtype closure**, so a plain subtype instance that
  inherits the owner's assertion is found. The subtype-closure walk reuses the existing
  `_supertype_closure` / `user_partdef_lookup` heritage facts (`usage_extractor.py:197,256`) —
  S3 confirmed no new SysIDE facts are needed.
- **[INHERITED]** (S3 carry-forward (1)) Fixed-multiplicity expansion is keyed by **owning
  definition + feature** (`owning_part_def_qn` + `part_usage_name` on the extracted
  `MultiplicityData`), not by bare leaf usage name. Leaf-name keying provably collides when
  two definitions own a same-named multiplicity member.
- **[INHERITED]** (concept first-scope restriction; S3 §"First-scope restriction") Only a
  **fixed, finite, literal** cardinality expands to concrete occurrences. Parameterized,
  variable, ordered, and unbounded multiplicities are outside the first executable scope and
  must block.
- **[INHERITED]** (concept Design Principle 5) A non-finite cardinality, or an expected
  concrete instance that cannot be formed, **blocks generation with a named diagnostic** that
  states the offending owner and feature. There is no path on which an instance is quietly
  omitted.
- **[HARD]** The index consumes the existing extraction facts only: `MultiplicityData`
  (`count`, `count_attribute_name`, `owning_part_def_qn`, `part_usage_name`, `default_value`)
  and the live `PartUsage` / `PartDefinition` heritage already exposed. No new SysIDE facts
  are added.
- **[HARD]** The "fixed finite literal" test is **not** `count is None`. A parameterized
  multiplicity (`[module_count]`) carries a non-`None` `count` — the attribute's cached lower
  bound — **plus** a non-`None` `count_attribute_name` (`hierarchy_resolver.py:234-245`; test
  `test_hierarchy_resolver.py:850-896`). The S3 probe gated only on `count is None`
  (`probe_instance_index.py:70-73`), which would let a parameterized count expand silently.
  Production must treat a present `count_attribute_name` (and any ordered/unbounded marker) as
  non-finite and block it, expanding only a genuinely fixed literal count.
- **[HARD]** Retyped and redefined paths are **deduplicated**: `_build_part_usage_index`
  keys a retyped usage under both its subtype and its preserved user supertype
  (`usage_extractor.py:284-289`), so the same concrete occurrence can be reached twice.
  Each concrete occurrence appears once in the index (the probe's set-dedup over closure
  paths, `probe_instance_index.py:100-106`).
- **[INFERRED]** The index emits **one distinct entry per concrete occurrence** — each
  fixed-multiplicity member as its own identified occurrence — so Item 5 can wire each sibling
  independently (S3 carry-forward (3): three occurrences are three modules, not copies). The
  index carries the identity; the wiring is Item 5's.
- **[HARD]** The index is **additive**. It is a new part-structure analysis that does not
  alter calc-driven discovery — `_find_instantiation_paths`, `find_instance_paths_for_partdef`,
  and template expansion (`usage_extractor.py:416`) keep their current output. In particular,
  subtype-closure projection is **not** retrofitted onto calc discovery in this item, because
  that would change generated output and break the byte-identity criterion.
- **[INHERITED]** (S3 result; concept "Concrete Lowering") The index is what constraint
  lowering uses instead of virtual calculation usages — "do not use virtual calculation
  usages as the index" (S3 §1). Delivered as a production, callable index with its own tests;
  the S3 fixture is promoted into the test corpus.

## Non-Goals

- Constraint expansion, actual resolution, `constraint_id` minting, and catalog construction
  — Item 5 consumes this index.
- Wiring fixed-multiplicity siblings to their own channels — Item 5 (S3 carry-forward (3)).
- Changing virtual-calc instance discovery for calculations; it stays as-is and is not
  migrated onto the new index here.
- Any constraint fact schema (`ConstraintUsageFact`, executable profile) — Items 1–2. This
  item consumes none.
- Snapshot changes: the constraint-facts snapshot section, its version bump, and live/snapshot
  ID **re-derivation** parity are Item 5 / the snapshot-rejection item. See the surfacing note
  below.
- Expanding non-fixed multiplicities. Their cardinality and stable per-occurrence identity are
  undefined at lowering and stay blocked until separately probed (S3 open follow-up).

## Open Questions / Deferred to design

- **Per-occurrence identity/path encoding.** The probe's `owner__leaf[index]` spelling and its
  path format were explicit probe mechanics, not proposed production syntax
  (`probe_instance_index.py:99`; S3 §2). Design chooses the production encoding of a concrete
  occurrence and of each multiplicity member.
- **Diagnostic taxonomy and seam.** The exact named-diagnostic identifier, message text, and
  whether it is raised at extraction time or at lowering preflight are design detail. The
  requirement is only that it names the owner and feature and blocks.
- **Module placement and public surface.** Whether the index is a new function in
  `usage_extractor.py`, a new module, or an orchestration seam, and its return type (the shape
  of an index entry), is a design decision.
- **Interaction shapes beyond the fixture.** S3 exercised fixed `[3]` at a single level.
  Nested-under-multiplicity, multiplicity-under-subtype, and multiplicity-of-multiplicity
  compositions are design/test-coverage questions; block-or-expand behavior for any shape the
  fixture does not cover should be pinned in design.

### Surfacing note (do not resolve silently)

The concept's Required Invariant states `constraint_id`s and catalog ordering are identical
across **live and snapshot** generation. This item's determinism criterion is narrower —
**byte-identical across repeated live loads** — because `constraint_id` minting and the
snapshot constraint-facts round-trip are Item 5's. S3 carry-forward (2) is explicit that its
snapshot leg proved *carriage* stability, not *re-derivation*; recomputing IDs from snapshot
facts through the real lowering path is S4/Item 5's burden. This spec deliberately scopes
snapshot ID parity out and flags the boundary rather than claiming it here.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 4)
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  ("Concrete Lowering"; Design Principle 5; Appendix B S3 result and carry-forwards)
- **Spike (S3):** `.project/active/spike-concrete-expansion-instance-index/findings.md`
  (§1–2, plus the committed `probe_instance_index.py` and `model.sysml` — the fixture is
  promotable)
- **Required Reading (from epic):** concept "Concrete Lowering" instance-index sentences +
  S3 result and carry-forwards; S3 findings §1–2
- **Design:** `.project/active/part-instance-index/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
