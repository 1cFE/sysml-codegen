# P-002 — One modeled source occurrence becomes exactly one runtime source

**Grade:** `[AGENT] (ratified by owner, 2026-08-16)` — an agent-originated promise the owner
approved. Challenge it by re-deriving against the reasoning recorded here, not by asking the owner.
**Serves:** [P-001](P-001-design-search-free-variation.md).
**Landed:** repair `98970c9`, evidence remediation `c2fa657`, item
`qualified-reference-occurrence-anchoring`.

## The promise

When a reference names a value that a part usage owns, the generated pipeline reads **that usage's**
value — not a same-named value on a sibling that happens to share a feature slot. Changing one
modeled source occurrence changes every consumer bound to it, and no consumer bound to anything
else.

Where the exact owner cannot be selected, elaboration **refuses by name** rather than choosing a
candidate. A confident wrong number is the failure mode P-001 cannot tolerate, so a named refusal is
the correct outcome, not a degradation.

## Why it needed building

Feature slots are shared across a whole redefinition family, so `comp_a::length` and
`comp_b::length` resolve to one slot. The shipped resolver discarded the exact leaf's owner and
re-found that slot by walking the **consumer's** occurrence lineage. A consumer authored inside
`comp_b` that named `comp_a::length` therefore bound `comp_b.length` — silently, with no diagnostic,
at the same slot. The measured case computed `14.0` where the model said `6.0`.

The repair runs the sequence in the order the model states it: owner declaration, owner occurrence,
then leaf slot at that occurrence.

## The bound — read this before relying on the promise

**The promise covers every shared-resolver lane that can reach the one-segment branch. One lane
cannot, and is not evidenced.**

Deep literal overrides do call the shared resolver
(`src/sysml_codegen/elaboration/elaborate.py:1050`), so the lane is real. But it fires only on a
chain, and a chain carries two or more segments, so it never reaches the one-segment branch the
repair sits in. A bounded search measured 51 live sites across 15 authored candidates plus a census
of every tracked chained-redefinition root and found zero one-segment sites.

That is empirical, not a proof. The evidence and its dated
`deep override affected-shape coverage unproven` gap live in the item's
`spike/deep-override-authorability/findings.md`, retained through archival.

**What this means in practice:** if a future change lets the deep-override lane produce a
one-segment chain, this promise does not yet cover it and the gap must be reopened rather than
assumed closed.

## Known inconsistency, dispositioned

For an arrayed owner, `sum(comp_a::length)` refuses with `SI_OCCURRENCE_AMBIGUOUS` while
`sum(comp_a.length)` resolves to one input per occurrence. Direct one-segment references are
deliberately scalar (design decision D4): a direct reference names one owner, so fanning it out
would invent a cardinality the model never authored.

Nothing that worked was lost — before the repair, `sum(comp_a::length)` silently summed the
*sibling's* value. **[OWNER, 2026-08-16]** accepted for the delivering item, with a bounded
follow-up filed at `[ANCHORING-ARRAYED-DIAGNOSTIC]` in `.project/backlog/BACKLOG.md`, scoped to the
diagnostic message first.

## Evidence

- `tests/conformance/test_usage_owned_reference_anchoring.py` — the durable authority for this
  guarantee; 15 of its nodes fail on the pre-repair resolver.
- `tests/conformance/test_elaboration_public_mutation.py` — asserts the consumers reached by a
  mutated source are **every** input port in the graph, so an unintended consumer fails wherever it
  binds.
- The item's `verification/` ledgers — 139 roots compared with identity, 0 changed.
