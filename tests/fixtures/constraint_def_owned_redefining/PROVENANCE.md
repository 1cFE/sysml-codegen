# Provenance

Fixture for CONSTRAINT-LIFECYCLE Item 13 (composed proof), Appendix C **case 18**
("Definition-owned assert through redefining usage"), authored per the evidence-coordinate
register's "author if absent" instruction (Stage 2 execution, 2026-07-20).

## What it proves (coordinate)

The `part def Panel` **owns** the assertion (`assert constraint within : 'Within Limit'`,
typed by a shared constraint def). The nested design attribute `source.reading` is declared
without a value binding and is **redefined at the usage** via `:>> source.reading = 80.0`.
The coordinate: the definition-owned assert SOURCE (`Panel::within`, typed by `'Within Limit'`)
and the redefining occurrence's actual identity
(`constraint_def_owned_redefining__panel__source__reading`) remain **distinct** (invariant 27),
and the sealed thread yields the expected verdict (`reading = 80.0` satisfies `v <= 100.0`).

The redefining usage is at package level (`part panel : Panel { :>> ... }`) — the canonical
plant-idiom shape (cf. `plant_value_shapes`'s top-level `part shapes_design`), where the
`:>>` override is captured at the same scope the resolver resolves at. The redefined attribute
then resolves under **exact identity** like any design attribute: the supplied-value
materializer synthesizes it, and the shared strict resolver's row 16
(`occurrence_materialized_qn`) returns it — no leniency, no constraint-specific shim.

## Validation (pin `7526665`, licensed)

`sysml-codegen generate --models tests/fixtures/constraint_def_owned_redefining` **succeeds**:
Step 3.5 captures the redefinition ("1 design overrides"); the supplied-value materializer
applies the literal ("1 literal applied"); the constraint actual resolves to a real
`design_attribute` entry point `constraint_def_owned_redefining__panel__source__reading` with
`default_value: 80.0`. `80.0 <= 100.0` → satisfied verdict.

## History (fixture-shape correction, 2026-07-20)

The first authored form (Stage 2) wrapped the redefining usage in an extra
`part def Design { part panel : Panel { :>> ... } } part the_design : Design` layer. That
layer over-built the contract row (which requires only a definition-owned assert and a
redefining usage) and tripped a **general** supplied-value gap: an override on a usage nested
inside an *instantiated* part def is captured **definition-relative** (`Design__panel`) while
demand resolves **occurrence-relative** (`the_design__panel`), so `_match_override` never finds
the literal — 0 applied on **both** the calc and constraint paths. The gap is not
constraint-specific and not mandated by row 18. Per owner ruling (2026-07-20, Option A) the
fixture was flattened to the canonical package-level shape; the nested shape is preserved as a
known-incomplete probe at `tests/fixtures/nested_occurrence_override_probe/`, and the general
gap is filed to the Item-10 occurrence-materialization family in `.project/backlog/BACKLOG.md`.

## Classification note

Case 18 is **compose**-classified in the manifest. Item 2's machinery was correct throughout;
the finding resolved to fixture shape plus a filed general gap, not a product defect.
