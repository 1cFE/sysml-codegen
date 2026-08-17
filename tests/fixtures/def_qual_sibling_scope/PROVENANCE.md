# Provenance — definition-owned qualified reference, sideways reach (F-4)

Promoted for self-binding-replacement Phase 2 from the spike fixture
`.project/active/self-binding-replacement/spike/fixtures/s6_qual_sibling_scope/` (findings row 6
and F-4, reproduced at `0f89673`). Package renamed `S6QualSiblingScope` →
`def_qual_sibling_scope`; the shape is otherwise unchanged.

## Owner class

**Definition-owned.** `'Unit'::cost` resolves to a feature owned by `part def 'Unit'`, so the
reference takes `_resolve_leaf`'s route, not the exact usage-owner anchoring.

## Measured behavior (spike row 6 / F-4, reconfirmed on the shipped route)

`'Unit'::cost` is written inside `part def 'Power Block'`, which contains no `'Unit'`. The
**positional fallback** — lineage miss, then a descendant search from each lineage anchor —
finds the single occurrence under the *sibling* subtree and resolves to
`plant.bop.the_unit.cost` = 7.0, silently. Adding a second `'Unit'` anywhere under `plant`
converts this into a loud `SI_OCCURRENCE_AMBIGUOUS`.

This fixture pins **what the route does**, not that the author meant the sibling: owner
qualification does not mean "mine", and no route checks intent here. The guidance must carry
that caution for the definition-owned fallback (design D11 / Required Invariant 3).

**Durable disposition:** this silently-resolving candidate is owned by
`[DEF-OWNED-SIDEWAYS-REACH]` in `.project/backlog/BACKLOG.md` (filed 2026-08-16 at the
self-binding-replacement audit's direction) — an owner ruling on loud-refusal versus supported
fallback, then the bounded implementation. If that ruling lands on refusal, this fixture's
expected outcome changes with it.

Kept test: `tests/conformance/test_definition_owned_reference_positions.py`.
