# Provenance — `constraint_occurrence_demand_overrides_d5`

Authored 2026-08-11 for recovery plan **Gate 4C part 7** (`.project/active/cutover-recovery/plan.md`),
as the exact-route execution specimen for row **L-193**
(`tests/execution/test_constraint_occurrence_demand_execution.py`), and behind it **L-113** /
**L-114**.

**Not a corpus fixture.** `constraint_occurrence_demand/overrides` is not a corpus fixture either —
it carries no v5 `extraction_snapshot.json` and has no `v6_recapture_batch/batch.json` record. It is
untouched, and still carries the refused shape.

## Why it exists

Lifecycle-remediation Item 1 (OD-A11): two sibling instances of one `part def` carry distinct
literal `:>>` overrides, and occurrence-stable usage identity is what keeps them apart. The claim
only holds if the two siblings reach *different* verdicts from their own values, which means
executing them. The exact route refuses the original.

## The two enumerated differences against `constraint_occurrence_demand/overrides`

### 1. D-5 binding form — proved by the strip check

Applied by `scripts/make_d5_variant.py --formals reading`, one formal:

| Declaring block | formal | binding after |
|---|---|---|
| `constraint def AtLeastFive` | `reading` → `reading_in` | `in reading_in = reading;` |

**The formals came from the exact route's own refusal message**, not from the batch manifest,
because this fixture has no batch record. The refusal, recorded verbatim:

```
Model is not ready for the exact route: SI_SELF_BINDING: OccurrenceOverride__Cell__threshold.reading
```

That is the only code in it, so the rename recipe covers the whole refusal and the refusal-layer
protocol's stop does not fire on this layer.

### 2. `model.sysml` → `occurrence_overrides.sysml` — a rename of the file, not of its bytes

After the D-5 rename the exact route refused a **second time**, at projection rather than
admission:

```
exact graph projection failed: SI_RENDERING_COLLISION: package-scoped
'OccurrenceOverride__keep_pipeline' in a model.sysml has no root occurrence to take a
parameter-group identity from
```

This is the ratified rule from the Slice 3B orchestrator ruling of 2026-08-11 (option C): parameter
group identity derives from the **filename stem**, and `model.sysml` falls back to the declaring
package of the **owning root occurrence**. `calc keep_pipeline : PassThrough` is package-scoped, so
it has no owning root occurrence, and the file's own name supplies nothing. The refusal is correct
behaviour, and no mechanism was invented to get past it — the file is simply named, which is what
the ratified rule asks a model to do.

**The difference is one filename and zero bytes.** `occurrence_overrides.sysml` in this fixture,
after the `_in` suffix is stripped, is byte-identical to `model.sysml` in the original. Pinned by
`tests/conformance/test_d5_variants.py::test_the_occurrence_overrides_variant_differs_by_the_rename_and_the_filename`.

## What the exact route produces

```
OccurrenceOverride__plant__low__reading     4.0
OccurrenceOverride__plant__high__reading    6.0
OccurrenceOverride__keep_pipeline__x        1.0
```

The two sibling values arrive distinct, which is the OD-A11 subject. A collapsed or duplicated
supplied value would make them agree here.

## Hand-derived verdicts

`reading_in >= 5.0`. `low` carries `4.0` → violated, margin `-1.0`. `high` carries `6.0` →
satisfied, margin `1.0`. One violated sibling makes the run's headline `violation`, with
`assessed_entry_count` 2 (one authored usage over two occurrences, so the
coverage account reads `assessed_gate_count` 1 beside it).
