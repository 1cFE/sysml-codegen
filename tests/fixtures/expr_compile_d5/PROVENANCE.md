# Provenance — `expr_compile_d5`

Authored 2026-08-11 for recovery plan **Gate 4C** (`.project/active/cutover-recovery/plan.md`),
as the exact-route replacement specimen for row **L-201** (auto-implementation
classification, stub fallback, backlog contents, expression ground truth).

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run.

## Why it exists

The repointed nodes drove `solar_battery_model`, `catf_mfe_model` and `chain_spike_model` —
corpus rows 33, 5 and 7, all ratified `expected-collapse`. More to the point, **no fixture
the exact route accepts emits a stub**: every one of them auto-implements completely, so the
classification claim ("some calc defs compile, some do not, and the ones that do not become
stubs listed in the backlog") had no specimen left at any authority.

`OpaqueCalc` supplies the missing half: an `out` attribute with no expression, so there is
nothing to compile and the generator must emit `raise NotImplementedError` rather than invent
a body.

## Hand-derived values

| Calc | inputs | output | value |
|---|---|---|---:|
| `ProductCalc` | `width_in=6.0`, `height_in=2.5`, `margin_in=4.0` | `area` | 15.0 |
| `ProductCalc` | as above | `padded_area` | 19.0 |
| `RatioCalc` | `numerator_in=19.0`, `offset_in=5.0`, `divisor_in=4.0` | `ratio` | 6.0 |
| `PowerCalc` | `base_in=3.0`, `exponent_in=2.0`, `scale_in=0.5` | `scaled_power` | 4.5 |
| `OpaqueCalc` | — | `correlated_value` | stub, no value |

`RatioCalc`'s numerator is `product.padded_area`, so 19.0 is the upstream value the pipeline
supplies; each impl is executed in isolation with that value fed in.
