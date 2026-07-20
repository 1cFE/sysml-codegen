# Phase-0 Finding: codegen omits the EntryPoint module at zero entry channels

**Status:** Open codegen gap — routed, not shimmed (design A3 discipline; owner instruction
2026-07-20: "a codegen gap routes to a stop-and-report, not a shim").
**Found:** 2026-07-20, Item 9 Phase 0.
**Repos/revs probed:** codegen `589c8c4`, teax `0a49b89`.

## What Phase 0 set out to do

Author the "zero" acceptance coordinate — a minimal codegen-generated package with **zero entry
channels** — and confirm assumption **A3**: that codegen emits exactly one `EntryPoint` module even
when it has zero channel outputs (required because TEAx's `pipeline_validator.py:83-87` and
`MappingEntrySource.from_spec` (`entry_source.py:30`) both assume one entry module exists).

## What the real CLI actually produces (empirical)

Minimal zero-entry model (a no-input calc with a constant output, instantiated as a part usage so
the calc is retained):

```sysml
// zero_library.sysml
package zero_library {
    private import ScalarValues::*;
    calc def 'Constant Calc' { out attribute value : Real = 2.0 * 3.0; }
}
// zero_plant.sysml
package zero_plant {
    private import ScalarValues::*;
    private import zero_library::*;
    part def 'Zero Plant' { calc value_calc : 'Constant Calc' {} }
    part zeroPlant : 'Zero Plant';
}
```

`uv run sysml-codegen generate --models … --package-name zero_channel` (real live extraction,
licensed) succeeds (exit 0) and derives 1 module + 1 ExitPoint, but the generated
`pipelines/pipeline.yaml` has **no `entry_fusion` EntryPoint module** — the module registry log says
"No entry point groups to generate", and the pipeline is:

```yaml
modules:
  zero_plant__zeroplant__value_calc:
    module_type: zero_library.Constant_CalcModule
    outputs:
      root: RootModel[float] zero_plant__zeroPlant__value_calc__value
  exit_point:
    module_type: ExitPoint
    outputs:
      zero_plant__zeroPlant__value_calc__value: RootModel[float] …value.json
```

**Root cause:** the pipeline template gates the entry module behind the parameter-group count —
`templates/pipeline_yaml.jinja2:11` `{% if entry_points %}` — so zero entry channels means the
`entry_fusion` module is never emitted.

## The gap manifests in stock TEAx (empirical)

Loading that generated package through the stock TEAx entry-point validator rejects it:

```
$ entry_point_validate("…/zero_channel/pipelines/pipeline.yaml")
REJECTED: ValidationError -> Pipeline must declare exactly one EntryPoint module
```

Both the `PipelineSpecification` pydantic schema (`simkit/config/pipeline_schema.py`) and
`core/pipeline_validator.py:83-87` require exactly one EntryPoint; `MappingEntrySource.from_spec`
does a bare `next(m … is_entry)` (`entry_source.py:30`, `StopIteration` on none). So a
zero-entry-channel package is **not loadable** by stock TEAx.

## Decision (no shim)

- **Not fixed in TEAx.** No relaxing of `pipeline_validator`, no hand-authored fake-EntryPoint
  package. Shimming TEAx to accept a malformed pipeline would defeat the one-entry-module invariant
  the design deliberately preserves.
- **Routed to codegen's owner.** The minimal fix lives in codegen: emit `entry_fusion` with an empty
  `inputs:` block even when there are zero entry channels (drop or invert the `{% if entry_points %}`
  guard for the module header), so the package still declares exactly one EntryPoint whose expected
  channel set is empty. Then stock TEAx's already-multi-channel seam handles it
  (`MappingEntrySource.from_spec` builds an empty `expected_types`; `validate({})` passes). This is a
  codegen change, out of Item 9's TEAx scope; it belongs to a codegen item (candidate: Item 13's
  composed proof needs the end-to-end zero coordinate, or a dedicated codegen fixup).

## What Item 9 proves instead for "zero" (in scope, in repo)

The **zero bridge shape** — Item 9's actual layer — is proven at the TEAx unit level without a
generated package: a `CandidateBridge({})` builds the empty mapping `{}`, and
`MappingEntrySource(expected_types={}).validate({})` passes with nothing missing and nothing extra.
That is the "zero typed channel mapping validates completely" requirement
(contract acceptance `:457`) at the bridge boundary. The **end-to-end** zero package coordinate is
parked on the codegen gap above.

## Reproduction

Model preserved at `evidence/zero_entry_model/` in this feature dir. Regenerate with the licensed
`sysml-codegen generate` CLI as above.
