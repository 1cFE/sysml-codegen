# Provenance

New fixture for CONSTRAINT-LIFECYCLE-REMEDIATION Item 2 (spec SR-A02, SR-R23;
design I9). It is a **recorded known-incomplete fixture**: it pins a state Item 2
does not fix, so that the state is visible rather than assumed.

## What it pins

One usage-owned design attribute, `SharedProducer::the_rig::gain` (literal 40.0),
read by two consumers — a calculation input (`calc scaler : Scaler { in gain = gain; }`)
and a constraint actual (`assert constraint floor_check : 'Gain Floor' { in gain = gain; }`).

Contract invariant 21 and SR-A02 require them to converge on one QN-keyed typed
entry point. They do not. The committed state is **two** entry points:

| Consumer | Entry point | How |
|---|---|---|
| constraint actual | `SharedProducer__the_rig__gain` | positive, occurrence-materialized design-attribute key form |
| calculation input | `SharedProducer__the_rig__scaler__gain` | per-consumer lenient terminal-miss mint |

## Why Item 2 does not fix it

The two consumers cannot supply the same reference. The shared resolution request
carries the reference *as written*; the constraint side has it
(`FeatureReferenceFact.source_name` = `gain`), the calculation side does not.
Calculation binding extraction resolves the reference to its referent's qualified
name and discards the written name, and for a self-named binding the referent is the
calc usage's *own formal* — `SharedProducer::the_rig::scaler::gain`. `raw_expression`
does not carry it either: live it holds the debug rendering
`'FeatureReferenceExpression -> SharedProducer::the_rig::scaler::gain'`, and it is
empty in all 247 bound bindings across every committed snapshot.

So the occurrence-materialized key form is structurally unreachable from the
calculation consumer, and every other design-attribute key form keys on the target QN
or a leaf name. **Design invariant I9 — that convergence is a free property of tier-2
resolution — is falsified for the self-named shape.** SR-A02 is not deliverable by
Item 2's means.

A name-inference workaround was measured and rejected (orchestrator ruling, agent-grade,
2026-07-19). Recovering the written reference from the structural equality
`referent_qn == {usage_qn}::{param_name}` is exact, but it newly resolves 22 self-named
bindings across six existing fixtures (`fusion_tea`, `solar_battery_model`,
`catf_mfe_model`, `chain_spike_model`, `return_styles`, `expression_binding_probe`).
Those 22 are all **single-consumer**, so the convergence property SR-A02 names never
arises in them — the change would be an identity rename across six fixtures' generated
surfaces that fixes no wrong value (each per-consumer entry point already carries the
correct modeled default), and it would shrink `fallback_entry_points` membership ahead
of Item 3's vacuity proof, whose experiments build on today's V11 shapes.

## What completes it

The written-reference carry: extraction preserves the reference as written and the
snapshot format carries it. That is a coordinated `agentic-mbse` + codegen change,
folded into **Item 4**, which already owns a versioned schema change with two-direction
skew handling — the machinery this needs. SR-A02 then completes on real data with no
name inference.

## Do not

Do not "fix" this fixture by adding a passthrough, by renaming the calc entry point, or
by inferring the written reference from the formal name. The two-entry-point state is
the point; a test asserts it.
