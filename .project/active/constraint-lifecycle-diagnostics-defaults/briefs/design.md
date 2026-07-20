# Design Brief — Lifecycle Item 4: Diagnostic Severity and Modeled-Default Fidelity

**Stage:** design (independent design_review follows in a fresh session)
**Spec:** `.project/active/constraint-lifecycle-diagnostics-defaults/spec.md` (just authored).
Same authority chain and firewall as `briefs/spec.md`.

## Open with DD-B1, as the spec directs

Severity as a fact-schema field vs a reader-side classification table. The spec recommends the
schema field (reader-side tables reproduce exactly the version-skew the contract closes); the
recommendation is [INFERRED]/challengeable. Settle it with code evidence and commit to the
consequences: if schema field, the licensed 34-snapshot re-capture with captured_at churn is a
named phase using the documented byte-identity procedure (timestamp-only diff check + revert —
see project memory `byte-identity-captured_at-churn`); if reader-side wins instead, DD-R12/R13
and three acceptance cells fall away and the spec gets amended, not worked around.

## The written-reference carry — design it as the blast-radius decision it is

The mechanism is cheap (loader plumbing + one call site; `source_attribute_name` already in
every snapshot). The CONSEQUENCE is not: Item 2 measured ~22 entry points across 6 fixtures
identity-renaming to source-QN keys, with V11 fallback membership shrinking accordingly.
Requirements:
1. Every renamed entry point enumerated and pinned (fixture, old key, new key, default carried)
   in a forced-difference table; generated baselines regenerate ONCE under that table.
2. Item 3's vacuity dividing line must be re-verified after the shrink (fallback keys stay
   calc-EQN-shaped; no design-attr QN enters the fallback set) — cite the decision record.
3. shared_producer flips from known-incomplete to the convergence proof (SR-A02/PC-4 close);
   build the RED surface first — the spec found PROVENANCE.md's claimed test does not exist.
4. Precedence: a positive written-name resolution must never override a differently-sourced
   existing behavior silently — if any of the 22 changes a value (not just a key), that's a
   stop, not a rename.

## Also owned

- Tier-2 malformed-literal silence (supplied_values.py:278-287, :540-543): the malformed
  candidate gets a diagnostic consistent with the new severity contract — design where it
  fires and its code/sink; no invented value.
- R-8 family: total out-of-root warning rendering, order preserved before BLOCK, preparation
  can never displace the BLOCK diagnostic. Item 1 froze current bytes precisely for this item
  to change them deliberately — any byte change is a forced difference with its own pin.
- Signed/unit default fidelity through typed entry points and generated JSON.
- PC-2 one-line SR-R16 amendment in Item 2's spec (record as cross-item correction).
- Consolidation: one typed diagnostic representation; delete duplicated parsing paths.

## Constraints

Extend, never rework, Items 1–3 certified seams. Fold the phased plan in (no plan.md);
agentic-mbse-first phasing ONLY if DD-B1 lands on a facts-side change — if everything lands
codegen-side, say so and drop the cross-repo ceremony. State load-bearing assumptions for the
reviewer. Qualitative simplicity; named deletions.
