# Provenance — `catf_mfe_d5`

> **Sources collapsed (REPO-CLEANUP Move C, 2026-08-25).** The `.sysml` fork this record
> describes (26 of 28 files byte-identical to `catf_mfe_model`, a four-line rename diff)
> left HEAD; `scripts/make_d5_variant.py catf_mfe_model catf_mfe_d5` regenerates it
> byte-for-byte when a source tree is needed. The committed
> `instance_graph_snapshot.json` stays — it needs a license to regenerate and keeps every
> repointed test license-free — and this record stays as the account of the rename.

Authored 2026-08-11 for recovery plan **Gate 4C part 6**
(`cutover-recovery/plan.md` (git history)), as the migrated variant of `catf_mfe_model`.

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. `catf_mfe_model` is
untouched: the ratified corpus row and every pin on its refused shape keep their subject.

**The exact route accepts this model.** Elaborating the committed
`instance_graph_snapshot.json` and projecting it yields **43 modules** and a constraint
catalog of **65 authored usages / 0 concrete entries / 9 excluded / 56 non-reaching**
(measured 2026-08-13, CONSTRAINT-SEMANTICS Item 5 Phase 0). All 65 usages are bare
`constraint`; the model asserts nothing, so it executes no gate.

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

## What used to block it — closed

An earlier revision of this file recorded a second refusal behind the rename:
**152 × `SI_OCCURRENCE_MISSING`** on deep part hierarchies, surfaced as a premise finding
rather than resolved. That refusal no longer reproduces — the nested-occurrence resolution
it named was fixed in the product, and the model builds. The record is kept in this file's
git history.
