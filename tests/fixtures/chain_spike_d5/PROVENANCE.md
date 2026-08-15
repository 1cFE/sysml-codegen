# Provenance — `chain_spike_d5`

Authored 2026-08-11 for recovery plan **Gate 4C part 6**, as the migrated variant of
`chain_spike_model` — refused by the exact route with 3× `SI_SELF_BINDING`.

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. `chain_spike_model` is
untouched and still carries its refused shape.

Stage 1 only: 3 formals renamed to `<name>_in` inside their `calc def`s and on the left side of
their bindings. The aggregation stage is a no-op here — the model has no colliding rollup — so
the proof is the strongest form, **strip check byte-identity: 0 problems**. Re-runnable without
a licence via `python scripts/make_d5_variant.py --check chain_spike_model chain_spike_d5`.

The exact route accepts it: 3 modules, 3 entry points. It exists so the generation-layer
conformance family can be exercised on the exact route for the third model those tests
parametrise over.
