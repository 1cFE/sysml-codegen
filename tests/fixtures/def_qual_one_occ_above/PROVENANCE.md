# Provenance — definition-owned qualified reference, above the def, one occurrence

Promoted for `[DEF-OWNED-SIDEWAYS-REACH]` from
`.project/active/self-binding-replacement/spike/fixtures/s9_qual_outside_one/` (findings row s9).
Package renamed `S9QualOutsideOne` → `def_qual_one_occ_above`; the shape is otherwise unchanged.

## Owner class

**Definition-owned.** `'Plant'::availability` resolves to a feature owned by `part def 'Plant'`,
so the reference takes `_resolve_leaf`'s route, not exact usage-owner anchoring.

## Expected behavior after the owner ruling

The consumer sits in the enclosing `'Fleet'`, outside the only `'Plant'` occurrence. The
occurrence is not on the consumer's lineage, so the route refuses with `SI_OCCURRENCE_MISSING`.
It does not select the occurrence because it is the only descendant.

The owner source and exact bound live at `[DEF-OWNED-SIDEWAYS-REACH]` in
`.project/backlog/BACKLOG.md`.

Kept test: `tests/conformance/test_definition_owned_reference_positions.py`.
