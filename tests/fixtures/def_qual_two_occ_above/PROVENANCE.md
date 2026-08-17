# Provenance — definition-owned qualified reference, above the def, two occurrences

Promoted for self-binding-replacement Phase 2 from the spike fixture
`.project/active/self-binding-replacement/spike/fixtures/s8_qual_outside_two/` (findings row 4d).
Package renamed `S8QualOutsideTwo` → `def_qual_two_occ_above`; the shape is otherwise unchanged.

## Owner class

**Definition-owned.** `'Plant'::availability` resolves to a feature owned by `part def 'Plant'`,
so the reference takes `_resolve_leaf`'s route, not the exact usage-owner anchoring.

## Expected behavior after the owner ruling

The consumer sits in the enclosing `'Fleet'`, **outside** every `'Plant'` occurrence, and two
occurrences are reachable below its anchor. Neither is on the consumer's lineage, so the route
refuses with `SI_OCCURRENCE_MISSING`. It does not count or select descendants.

This is the two-descendant counterpart to `def_qual_one_occ_above`; both outcomes are identical
because SysIDE's resolved structure is authoritative. The owner source and exact bound live at
`[DEF-OWNED-SIDEWAYS-REACH]` in `.project/backlog/BACKLOG.md`.

Kept test: `tests/conformance/test_definition_owned_reference_positions.py`.
