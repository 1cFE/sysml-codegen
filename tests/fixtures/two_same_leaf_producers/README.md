# Fixture: two_same_leaf_producers

An authored ambiguity fixture retained as source-only provenance.

Two parts (`SubsystemA`, `SubsystemB`) each own a `cost` design attribute; the consumer
`consumer` binds the **bare leaf** `cost`, which ties across `a.cost` / `b.cost` with no
exact-QN discriminator. Expected behavior: the resolver refuses to pick (`_unique_or_tie`)
and falls through to a synthesized entry point carrying both tied QNs; the
exact graph validation names the ambiguity.

## Status

- **Resolver+check property: proven license-free** at the resolver+check boundary by
  `CUT-PROJ-01` (a genuine two-same-leaf tie
  through `resolve_producer` under capture → `AMBIGUOUS_PRODUCER`).
- The fixture is outside the accepted 37-path capture population. Exact ambiguity refusal is
  owned by `CUT-PROJ-01`; this directory preserves only the authored source referent.
