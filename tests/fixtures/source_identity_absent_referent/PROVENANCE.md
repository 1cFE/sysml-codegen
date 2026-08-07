# Provenance — genuine-miss coordinate (C18), pinned at the load boundary

Constructed for SOURCE-IDENTITY Item 4 Phase 2 against the contract's C18 key: an
aggregation-term reference whose target is genuinely absent from the model.

## Measured fact (licensed probe, 2026-08-07) — surfaced, not silently resolved

SysIDE **refuses to load** this model:

```
[ERROR] model.sysml:20: error (reference-error): No Feature named 'ghost_cost' found.
```

A genuinely absent chained target is a KerML name-resolution failure, and the adapter returns no
model on ERROR diagnostics. **The C18 premise that a loadable model can carry a genuinely absent
term target does not hold at the SysIDE boundary for this authored form.** Consequences:

- The live route can never reach extraction, projection, or policy with this shape — the
  language boundary already fails closed before any source exists, which trivially satisfies
  "no minted input, no same-named capture" for this form.
- The contract's published C18 outcome (`POLICY_DIAGNOSTIC` at the executable boundary) is
  therefore realizable only for an `ABSENT_REFERENT` that arrives by another route (e.g. term
  evidence whose resolved target is absent in snapshot data, or a form SysIDE resolves
  leniently). The authority keeps `ABSENT_REFERENT` as the honest policy input for exactly that
  (D2/I8), proven at the unit level in `tests/unit/test_source_identity.py`.
- Phase-5 acceptance mapping should reconcile the C18 cell against this measured boundary with
  the owner rather than inventing a lenient loader.

Consumers: `tests/conformance/test_source_identity_occurrences.py` pins the load refusal as this
fixture's exact behavior.
