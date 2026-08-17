# Provenance: the usage-owned reference anchoring fixture family

These thirteen fixture roots are the durable conformance authority for exact owner anchoring
of one-segment references (`.project/completed/20260816_qualified-reference-occurrence-anchoring/`). They
are read by `tests/conformance/test_usage_owned_reference_anchoring.py`.

The research paths they came from are archived once that item closes (design decision D6), so
the copies here — not their sources — are the authority. No synchronization back to the
research paths is promised.

## The authored fixture

`usage_owned_reference_consumers/model.sysml` is written for this item (2026-08-15). It is the
combined cross-consumer fixture required by D7: one named source, `plant.comp_a.length` (3.0),
read from six consumer lanes authored inside the sibling `plant.comp_b` (7.0), which carries a
same-slot attribute of its own. The lanes are a typed alias, an alias-following calculation
input, a computed attribute, a calculation input, a typed constraint actual, an asserted inline
constraint predicate, and a direct scalar `sum()` term.

Every lane names `comp_a::length`, so every lane must reach `comp_a`'s node. Before the Phase-3
resolver repair all seven edges reach `comp_b.length` instead — one fixture, seven wrong edges,
no diagnostic.

## Copied from `.project/active/self-binding-replacement/spike/fixtures/` (bytes preserved)

Qualified (`::`) one-segment references. Their `SPIKE THROWAWAY` headers are part of the
preserved bytes and are stale on that point.

| Root | Shape | Role |
|---|---|---|
| `u1_usage_qual_self` | qualifier names the consumer's own enclosing usage | control — edge is already correct |
| `u2_usage_qual_two_owner_occ` | two occurrences of the qualifying usage, one per plant | control — each consumer already reaches its own occurrence |
| `u3_usage_qual_multi_occ` | qualifying usage arrayed `[2]` | control — ambiguity is correct and survives the repair |
| `u3b_usage_qual_single_occ` | the `[1]` counterpart of u3 | control — single occurrence already resolves |
| `u4_usage_qual_pkg_sibling` | package-scoped usage named from inside a part def | **affected** — `SI_OCCURRENCE_MISSING` today |
| `u5_usage_qual_named_sibling` | one of two named sibling usages | **affected** — `SI_OCCURRENCE_AMBIGUOUS` today |
| `u6_usage_qual_crossnamed` | consumer inside `comp_b` names `comp_a::length` | **affected** — silently wired to `comp_b.length` today |
| `u7_both_spellings` | both qualified spellings plus their dot-path controls | **affected** — both qualified inputs ambiguous today, dot-path controls correct |

## Copied from the Phase-1 bare-discriminator learning test (bytes preserved)

Source: `.project/completed/20260816_qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/`,
2026-08-15. The written reference in each is one bare segment; an `alias` or a subsetting
declaration is what makes SysIDE resolve it to the sibling's leaf.

| Root | Source candidate | Role |
|---|---|---|
| `usage_owner_bare_alias` | `c01-alias-parent-scope` | **affected** — the promoted bare discriminator; computes `14.0` where the model says `6.0` |
| `usage_owner_bare_alias_def_owned` | `c06-alias-to-definition-owned` | control — the alias resolves to a `PartDefinition`-owned leaf, so the owner branch must not activate |
| `usage_owner_bare_subset_def_owned` | `c08-subset-sibling-usage` | control — same guard through subsetting instead of aliasing |
| `usage_owner_bare_alias_arrayed` | `c12-arrayed-owner` | **affected negative** — the exact owner has two occurrences, so scalar owner selection must refuse rather than answer |
