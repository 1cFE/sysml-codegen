# Provenance — `gate_a_d5`

Authored 2026-08-11 for recovery plan **Gate 4C part 7** (`.project/active/cutover-recovery/plan.md`),
as the exact-route execution specimen for row **L-194** (`tests/execution/test_gate_a_execution.py`).

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. `gate_a` itself — corpus
row, ratified `expected-collapse`, refused with 2× `SI_SELF_BINDING` — is untouched and still
carries the refused shape and its v5 `extraction_snapshot.json`.

## Why it exists

Gate A's subject is a literal-valued design attribute owned by a **concrete PartUsage**, read by a
self-named constraint actual. The execution lane has to observe a real verdict move when that
literal moves, and the exact route refuses `gate_a` itself.

## The one difference against `gate_a`

**D-5 binding form**, applied by `scripts/make_d5_variant.py` and proved by the strip check in
`tests/conformance/test_d5_variants.py`: removing the `_in` suffix reproduces `gate_a/model.sysml`
byte for byte. Two formals renamed:

| Declaring block | formal | binding after |
|---|---|---|
| `calc def Doubler` | `seed` → `seed_in` | `in seed_in = seed;` |
| `constraint def 'Viability Threshold'` | `gain` → `gain_in` | `in gain_in = gain;` |

**The recipe was widened to reach `constraint def`.** The first attempt renamed only the
*binding's* left side inside `assert constraint viability`, leaving the declaration saying `gain`
and the binding saying `gain_in`. That model is inconsistent and the exact route refused it at
generation with `cross_scope_binding_disagreement`, not at admission. `_DEFINITION_BLOCK` in
`scripts/make_d5_variant.py` now matches `constraint def` as well as `calc def`, including
single-quoted names. This is the same recipe applied to the block form that was missing from it,
and the strip check still proves the rename is the sole edit.

## What the exact route produces

Generated entry points, read off the package `run_codegen` writes:

```
GateA__the_host__gain                    40.0
GateA__the_host__viability__threshold    10.0
GateA__the_other__seed                    3.0
```

`GateA__the_host__gain` under its **real** qualified name is the whole Gate A claim: before the
owner-classification fix, resolution asked for `GateA__the_host__viability__gain` — the
constraint's own QN as the root — and generation failed at the strict terminal miss.

## Hand-derived verdicts

`gain >= threshold` with the modelled `40.0` and the defaulted `10.0` is satisfied, margin `30.0`.
Overriding `GateA__the_host__gain` to `5.0` in the generated inputs gives `5.0 >= 10.0` — violated,
margin `-5.0`.
