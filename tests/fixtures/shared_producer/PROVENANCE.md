# Provenance

Fixture for CONSTRAINT-LIFECYCLE-REMEDIATION Item 2 (spec SR-A02, SR-R23; design I9),
**closed by Item 4** (DD-R26, DD-R27, DD-R28, DD-A14). It was a recorded
known-incomplete fixture; it is now the acceptance surface for two-consumer
convergence.

## What it pins

One usage-owned design attribute, `SharedProducer::the_rig::gain` (literal 40.0),
read by two consumers — a calculation input (`calc scaler : Scaler { in gain = gain; }`)
and a constraint actual (`assert constraint floor_check : 'Gain Floor' { in gain = gain; }`).

Contract invariant 21 and SR-A02 require them to converge on one QN-keyed typed
entry point. **They now do.** The committed state is **one** entry point:

| Consumer | Entry point | How |
|---|---|---|
| constraint actual | `SharedProducer__the_rig__gain` | positive, occurrence-materialized design-attribute key form (row 16) |
| calculation input | `SharedProducer__the_rig__gain` | the same row 16, reached via the written-reference carry |

One modeled default (40.0), one group assignment.

## How Item 4 closed it

Item 2 recorded that the two consumers could not supply the same reference: the
constraint side had it (`FeatureReferenceFact.source_name` = `gain`) and the
calculation side was believed to have discarded the written name, making the
occurrence-materialized key form "structurally unreachable" from it.

**That premise was false, and Item 4's spec surfaced it.** The written name was
already on disk: `snapshot/serializer.py` writes `source_attribute_name` into every
serialized `BindingInfo`, and this fixture's snapshot has carried
`"source_attribute_name": "gain"` all along. The *loader* discarded it. The carry is
therefore loader plumbing plus call-site plumbing — no new extraction field, no
schema bump — and it works on unmodified v3 snapshots.

The calculation consumer now supplies `written_reference` and
`occurrence_owner_path` as row 16's two dedicated request inputs
(`resolution/producer_resolution.py`), so it reaches the same key the constraint
consumer reaches. No name is inferred from a formal.

**The written reference is the reference as written, including a chain qualifier.**
Carrying only the leaf name was measured to re-anchor a chained reference at the
wrong owner and select a same-named attribute elsewhere — `catf_mfe_model`'s
`in cryo_pump_count = cryo_pumps.n_pumps` selected the outer `n_pumps` (48.0) instead
of `cryo_pumps.n_pumps` (32.0). `BindingInfo.written_reference` composes
`{source_instance_name}.{source_attribute_name}` for chains.

## Corrections to this file

Two claims in the previous version were false and are recorded here rather than
silently dropped:

1. *"the occurrence-materialized key form is structurally unreachable from the
   calculation consumer."* False — the written name was in every committed snapshot;
   only the loader dropped it.
2. *"The two-entry-point state is the point; a test asserts it."* **No such test
   existed.** At the Item 4 predecessor this fixture appeared in `tests/` only as a
   registered session snapshot (`tests/conformance/conftest.py`). Item 4 therefore
   built the acceptance surface rather than flipping an existing one: it authored the
   test against the two-key state first, confirmed it green, then flipped it to the
   convergence assertion (design Gate 4).

The name-inference workaround Item 2 measured and rejected — recovering the written
reference from the structural equality `referent_qn == {usage_qn}::{param_name}` —
**stays rejected**. Item 4 did not use it; it used the reference the model actually
carries.

## The acceptance surface

`tests/conformance/test_shared_producer_convergence.py`, both public routes (live
extraction and the committed snapshot). It asserts one entry point,
`SharedProducer__the_rig__gain`, one modeled default of 40.0, and one group
assignment.
