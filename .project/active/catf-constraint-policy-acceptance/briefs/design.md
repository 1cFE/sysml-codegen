# Orchestration brief — design stage — CONSTRAINT-SEMANTICS Item 5

Design for **Item 5: CATF Derivative and End-to-End Acceptance**. Item home:
`.project/active/catf-constraint-policy-acceptance/`. Write `design.md` there.

## Authorities (read in this order)

1. `spec.md` in the item home — SC-1 met, SC-3 **amended** (accounting identity), the rest as
   written.
2. `owner-disposition.md` in the item home — **RULED 2026-08-13**. This is the sole source of
   intent classes, tolerance values, deletion authority, and basis choices. Do not re-litigate
   any row. The identity in force: **65 = 56 carriers + 9 named deletions** (7 derive-instead
   A1/A4/A5/A6/A7/A8/C37 + 2 O2 placeholder deletions C21/C28). Survivors: 3 asserted gates
   (A2 one-sided; A3 band, edges 0.10/0.90 [OWNER]; A9 band, 1% relative [OWNER]), 5
   `@inapplicable:` part-def guards, 48 plain awaits-capability calc-def guards.
3. The spec's Required-reading pointers as needed (Items 2–3 close records for catalog/report
   contracts as landed; modeling-assumptions §8/§9; Item 4 surfaced limits).

## What design must decide (the spec and ruling leave exactly these open)

- **Derivative fixture name** (working name `catf_mfe_gated`) and its **integrity check** —
  byte-reversal does not transfer; the umbrella flagged a provenance-diff manifest. The check
  should machine-verify the accounting identity (56 carriers + 9 named deletions ↔ table rows).
- **The rewrite mechanics for the three asserted gates** (bindings-only shape per Q4; formals
  renamed off their attributes — never a bare self-named binding; if renaming cannot avoid one,
  surface and stop). A9's `ProductWithinBand` becomes relative-form per the ruling — if the
  def-shape changes materially from the table's sketch, note it in the design, don't silently
  adapt.
- **The unit approach per gate (O4)**: generic dimensionless band under human review vs
  per-dimension in-predicate spelling (§8). The two do not compose (spec item5-F3); pick per
  gate and record the unit reasoning in a committed artifact (table row cites + PROVENANCE), not
  just review conversation.
- **The derivation edit shape (O6)**: A5/A6 basis is ruled (axis root radius + 14 thicknesses
  free, radii derived) — design decides the concrete SysML edit (`:>>` computed attributes,
  calc usages, or bindings), sized honestly (~27 attribute declarations). Every one of the 7
  derivations carries the ruled doc comment: the undirected relation + "direction is a chosen
  basis, not physics". A7: neutron fraction free, gamma derived.
- **The constraint-def library home and names (O7)** — `PositiveQuantity`, `FractionWithinBand`,
  `ProductWithinBand` provisional; fixture-local homes only (guidance graduation is Item 7's).
- **PROVENANCE structure**: per-change records; 9 named deletion records citing table rows (the
  7 with relation + basis statements); the two O3 model-debt entries (partial shield closure;
  B4 thickness-set mismatch); the d5 stale-acceptance-paragraph correction (SC-2/scope 6).
- **Expected-outputs capture (SC-6)**: file layout and commit-order evidence, following Item 3's
  `expected-coverage.md` precedent — expected catalog, report, and study outcomes derived from
  the ruled table BEFORE confirmation tests run.
- **SC-5 mutation mechanics**: which physics input, mutated where, how the rejection is
  reproducible. A2 is the anchor. **Probe all three candidates (A2/A3/A9) for ADMIT before
  committing the design** — owner-endorsed; only A2 has a measured ADMIT. Use throwaway probes
  (scratchpad), not committed fixtures.
- **R3 baseline shape (SC-8)**: which fixture carries the calc-def-only byte baseline and how it
  enters `tests/fixtures/baseline_outputs/` without churning others.

## Constraints that bound the design

- Atomic landing: one BLOCK on any asserted gate halts the whole model. Design the authoring so
  the derivative is introduced in a generating state (probes first).
- Both frozen twins byte-untouched except d5's PROVENANCE paragraph.
- TEAx stays on `constraint-semantics-item3` @ `5b70ae9` (orchestrator verified this session);
  execution lane imports simkit from that working tree.
- Test invocation: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`; licensed env via
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero license-skip lines is the only
  licensed-run proof.
- Three routes gated: licensed live, in-place snapshot, relocated snapshot.
- Grade every design decision's provenance; the ruled table's grades are already assigned — do
  not promote or dilute them.

## Probes you should run in this stage

The ADMIT probes for A3/A9 rewritten shapes (A2's is already measured), and anything you need to
de-risk the derivation edit shape (e.g. one radial-build layer derived end-to-end). Throwaway
code in the scratchpad; findings recorded in the design. If a probe contradicts a premise (e.g. a
band shape BLOCKs), surface it in the design and stop that thread rather than working around it
silently.

End your final message with `ARTIFACT: <path>`.
