# Provenance — definition-owned qualified reference, inside the def, two occurrences

Promoted for self-binding-replacement Phase 2 from the spike fixture
`.project/active/self-binding-replacement/spike/fixtures/s4b_qual_two_occ/` (findings row 4b).
Package renamed `S4BQualTwoOcc` → `def_qual_two_occ_inside`; the shape is otherwise unchanged.

## Owner class

**Definition-owned.** `'Plant'::availability` resolves to a feature owned by `part def 'Plant'`,
not by a part usage, so the reference takes `_resolve_leaf`'s route — the exact usage-owner
anchoring landed by `qualified-reference-occurrence-anchoring` (`98970c9`) does not apply here.

## Measured behavior (spike row 4b, reconfirmed on the shipped route)

The binding is authored inside `part def 'Plant'` and two occurrences exist. The consumer's own
scope lineage owns the slot, so each occurrence resolves to **its own** attribute: two modules,
`plant_a` reading 0.11 and `plant_b` reading 0.99, no diagnostic. This is the position that
falsified the earlier "refused when more than one occurrence exists" wording (spike F-1).

Kept test: `tests/conformance/test_definition_owned_reference_positions.py`.
