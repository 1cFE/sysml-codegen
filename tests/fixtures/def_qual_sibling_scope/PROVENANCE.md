# Provenance — definition-owned qualified reference, sideways reach (F-4)

Promoted for self-binding-replacement Phase 2 from the spike fixture
`.project/active/self-binding-replacement/spike/fixtures/s6_qual_sibling_scope/` (findings row 6
and F-4, reproduced at `0f89673`). Package renamed `S6QualSiblingScope` →
`def_qual_sibling_scope`; the shape is otherwise unchanged.

## Owner class

**Definition-owned.** `'Unit'::cost` resolves to a feature owned by `part def 'Unit'`, so the
reference takes `_resolve_leaf`'s route, not the exact usage-owner anchoring.

## Historical finding (spike row 6 / F-4)

`'Unit'::cost` is written inside `part def 'Power Block'`, which contains no `'Unit'`. The
old route searched descendants and selected `plant.bop.the_unit.cost` = 7.0 from the sibling
subtree. That fallback was removed by the owner ruling below.

**Owner ruling and durable disposition:** `[OWNER 2026-08-16]` rejected the lineage-miss
descendant fallback. SysIDE's resolved structure is authoritative; codegen must refuse rather than
invent an occurrence through positional search. `[DEF-OWNED-SIDEWAYS-REACH]` in
`.project/backlog/BACKLOG.md` records the owner-verbatim source, owner Reid W, the exact bound, and
the `_resolve_leaf`/tests/guidance implementation vehicle. This fixture now expects
`SI_OCCURRENCE_MISSING`; an explicit occurrence path remains supported for another subtree.

Kept test: `tests/conformance/test_definition_owned_reference_positions.py`.
