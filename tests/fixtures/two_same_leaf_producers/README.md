# Fixture: two_same_leaf_producers

The **ambiguous/defaulted producer** acceptance coordinate (Item 10, RED-first), snapshot
route. Contract acceptance row "Ambiguous/defaulted producer resolution".

Two parts (`SubsystemA`, `SubsystemB`) each own a `cost` design attribute; the consumer
`consumer` binds the **bare leaf** `cost`, which ties across `a.cost` / `b.cost` with no
exact-QN discriminator. Expected behavior: the resolver refuses to pick (`_unique_or_tie`)
and falls through to a synthesized entry point carrying both tied QNs; the
producer-completeness check (`resolution/producer_completeness.py`) names the ambiguity.

## Status

- **Resolver+check property: proven license-free** at the resolver+check boundary by
  `tests/conformance/test_producer_completeness_acceptance.py` (a genuine two-same-leaf tie
  through `resolve_producer` under capture → `AMBIGUOUS_PRODUCER`).
- **`extraction_snapshot.json`: CAPTURE PENDING.** The both-public-routes (live + relocated
  snapshot) fixture snapshot requires a licensed extraction capture. It is deferred to the
  licensed capture pass that also recaptures the stellarator (Item 10 Phase 3), to avoid a
  separate license round-trip. Register in `scripts/capture_extraction_snapshots.py` and run
  `uv run python scripts/capture_extraction_snapshots.py --fixtures two_same_leaf_producers`;
  then add the snapshot-route assertion (build the graph, run the completeness check, assert
  one `AMBIGUOUS_PRODUCER` on the bare-leaf consumer) on both routes.
