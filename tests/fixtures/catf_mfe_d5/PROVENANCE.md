# Provenance — `catf_mfe_d5`

Authored 2026-08-11 for recovery plan **Gate 4C part 6**
(`.project/active/cutover-recovery/plan.md`), as the migrated variant of `catf_mfe_model`.

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. `catf_mfe_model` is
untouched: the ratified corpus row and every pin on its refused shape keep their subject.

**INCOMPLETE — the exact route does not yet accept this model.** It is committed at the
rename stage because that stage is finished and proved, not because it is usable coverage.

## What was done — the D-5 rename, complete and proved

`catf_mfe_model` is refused with 1× `SI_SELF_BINDING`:
`CATFMFEVacuum__catf_vacuum_pumping__pump_load.pumping_speed_total`. One formal,
`pumping_speed_total`, renamed to `pumping_speed_total_in` inside its `calc def` and on the
left side of its binding — `designs/catf_mfe/vacuum.sysml` and
`library/analyses/thermal_loads.sysml`.

**Strip check: 0 problems.** Removing the `_in` suffix reproduces `catf_mfe_model` byte for
byte, file for file, so the rename is the only edit. Pinned by
`tests/conformance/test_d5_variants.py`, and re-runnable without a license via
`python scripts/make_d5_variant.py --check catf_mfe_model catf_mfe_d5`.

## What blocks it — a different class the rename does not reach

With the self-binding gone, the elaborator refuses the model with
**152 × `SI_OCCURRENCE_MISSING`** (`ElaborationDiagnosticError`), of the form:

```
CATFMFERadialBuild__catf_radial_build__ht_shield__thickness:
    leaf declaration 146016c8-… has no feature slot
```

These are nested-occurrence resolutions, not bindings. No rename addresses them, and they
were previously invisible because the self-binding refusal fired first. Slice 3D met the same
error *code* on the customer model at 7 diagnostics and closed it with a product change
(`_enumeration_literal`); this is 152 diagnostics on deep part hierarchies, which is not
obviously the same sub-case.

**Surfaced to the orchestrator as a premise finding, not resolved here.**
