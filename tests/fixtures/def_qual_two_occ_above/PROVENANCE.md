# Provenance — definition-owned qualified reference, above the def, two occurrences

Promoted for self-binding-replacement Phase 2 from the spike fixture
`.project/active/self-binding-replacement/spike/fixtures/s8_qual_outside_two/` (findings row 4d).
Package renamed `S8QualOutsideTwo` → `def_qual_two_occ_above`; the shape is otherwise unchanged.

## Owner class

**Definition-owned.** `'Plant'::availability` resolves to a feature owned by `part def 'Plant'`,
so the reference takes `_resolve_leaf`'s route, not the exact usage-owner anchoring.

## Measured behavior (spike row 4d, reconfirmed on the shipped route)

The consumer sits in the enclosing `'Fleet'`, **outside** every `'Plant'` occurrence, and two
occurrences are reachable below its anchor. The route refuses:
`SI_OCCURRENCE_AMBIGUOUS: … consumer context contains 2 leaf occurrences`. Together with
`def_qual_two_occ_inside` this pins that the discriminator is the consumer's **position
relative to the occurrences**, not the occurrence count of the qualifying definition.

Kept test: `tests/conformance/test_definition_owned_reference_positions.py`.
