# Provenance

New fixture for CONSTRAINT-LIFECYCLE Item 13 (composed proof), Appendix C **case 5**
("Shared definition × mixed polarity"), authored per the evidence-coordinate register's
"author if absent" instruction (Stage 2 execution, 2026-07-20).

## What it proves

One shared `constraint def 'Within Bound'` (`m >= 0.0`), compiled once to a single neutral
predicate body, is typed by two named usages with **opposite polarity**:

- `assert constraint pos_bound : 'Within Bound'` — positive.
- `assert not constraint neg_bound : 'Within Bound'` — negated.

Both take their actual from `margin_calc.m` (a producer channel). The coordinate: each usage
retains its **own** polarity and **margin sign independent of catalog sort order**
(invariant 29) — the margin sign must not be taken from whichever catalog entry sorts first.

## Validation at authoring (pin `7526665`, licensed)

`sysml-codegen generate --models tests/fixtures/constraint_shared_polarity` exits 0 and emits
both `thedesignhposboundconstraintmodule.py` and `thedesignhnegboundconstraintmodule.py` plus
the shared `constraints/predicates.py`. This confirms the fixture is a valid public-seam input.

## Classification note

Case 5 is **compose**-classified in the manifest. This session (Stage 2) authored the fixture
only; the sealed-thread evaluation (both usages, complementary verdict/margin) is the
compose-group deliverable.
