# Orchestrator dispositions of the spike findings

**Date:** 2026-08-15. All rulings below are `[AGENT]` grade — the owner reserved no gates for this
run, so these are the orchestrator's calls, recorded so they can be challenged by re-deriving
against this reasoning. None of it is owner intent.

Source: `.project/active/self-binding-replacement/spike/findings.md`.

## F-1 — the `[HARD]` `SI_OCCURRENCE_AMBIGUOUS` row is falsified as written → **spec amended**

Not a premise surprise. The spec itself stamped this row *measurement pending re-establishment* and
forbade design from building on it; the spike is the protocol working as designed. The row now
states the measured rule (position, not occurrence count), and the three-shapes section states D-6's
real behavior and its sideways reach.

**What this does not do:** it does not reopen the migration form. D-6 turning out safer than the
spec assumed is not a reason to prefer it. D-5 stays the ratified shape for all 15 fusion-tea sites
(`[NEED]`, 2026-08-05 ratification), the codegen fixture already uses it, and the owner's situational
rule assigns D-5 to exactly this situation — an attribute on the part owning the calculation.

## F-2 — agentic-mbse validator false-positives on D-6 → **FIX, in agentic-mbse only**

The spec's disposition rule for a newly found defect is `[INFERRED]`, agent-grade: file it, unless
the repair is small and contained. This one is small and contained, and it is also **load-bearing
for this item's own deliverable**. We are about to publish guidance that teaches owner qualification
with its limits. An author or agent following that guidance gets a spurious blocking ERROR from the
validator. Publishing teaching that our own validator contradicts is the exact failure mode this
item exists to end — a document that forbids by example what the product allows, inverted.

It also sharpens the success criterion. "The agentic-mbse validation path is confirmed to refuse the
self-named form" is only honestly discharged once we can say *what* it refuses on. Today it refuses
on name equality, which catches the right shape for the wrong reason and catches a valid shape too.

**Bound:** agentic-mbse only, no codegen change — mirror codegen's identity comparison
(`extraction/source_evidence.py:130-138`) inside `check_self_named_bindings`
(`level2_structure.py:350`), plus a test in each direction. If it turns out not to be contained,
stop and file it rather than growing the item.

## F-3 — unhandled traceback on the D-5 rename collision → **FIX the traceback; file the rest**

This sits directly on the road we are telling every author to walk. The migration *is* D-5 renames,
and a rename that collides with the calc def's own `out` parameter exits with a raw
`GraphValidationError` naming no file, no line, and no binding. Nothing ships wrong — it is loud —
but an author hitting it during migration has nothing to act on, and 15 fusion-tea sites plus a
99-site stellarator model are about to be renamed by someone.

**In scope:** turn that throw into a named readiness diagnostic carrying the offending binding and
its location, consistent with how the route reports every other refusal. **Out of scope and filed
with a name, owner, and vehicle:** the `SI_OCCURRENCE_MISSING` bare-`FeatureSlotId` detail (F-3
second half) and F-5's garbage chain source paths — both are reporting quality with no author on the
migration path today.

**If design finds the diagnostic repair is not contained** — if it needs graph-layer restructuring
rather than a catch-and-report at the boundary — then file it too, with the same name/owner/vehicle
discipline, and say so plainly. Do not grow a docs-and-models item into graph work.

## F-4 — the sideways reach → **one sentence in the guidance**

Characterised, not a defect: it is what the measured rule specifies, it is the only occurrence, and
a second one converts it into a loud refusal. It earns a guidance sentence because it violates the
intuition the spelling creates — owner qualification does not mean "mine."

## F-5 — chain source paths → **filed, not fixed**

No in-tree consumer; the one caller filters `CHAIN` out first. Recorded so it is not rediscovered.
