# Constraint Lowering & Catalog

Component: constraint execution (Items 5-9; Item 14 closes the extraction-side gap
that blocked the two grandfathered fixtures and retires the drop-manifest era).

## What this replaces

Section 8 of [modeling-assumptions.md](../modeling-assumptions.md) used to teach
"constraints are dropped, not executable." That was true through Item 4. Items 5-9
built a real execution path — the **executable profile** (in `agentic-mbse`)
classifies each constraint usage as `ADMIT`, `BLOCK`, `NON_NUMERICAL`, or `UNASSESSED`, and an
`ADMIT` usage **lowers**: every formal is strictly resolved to a real value and the constraint
becomes a pipeline module. This doc covers the sysml-codegen side of that path —
the profile itself, and the study layer that drives it in production, live in
`agentic-mbse` and `teax` respectively (see those repos' own docs).

## Lowering phase (`analysis/constraint_lowering.py`)

`lower_constraints(facts, prepared, registry, design_attrs)` is the [P1 RESOLVE]
step (Item 5), called from `pipeline_builder.py` right after the output registry and
the enriched graph-only design attributes are final.

`prepare_constraint_usages(facts, occ_index, calc_usages, source_location_mode,
source_roots)` runs first and owns the whole lifecycle boundary: it verifies the
usage/decision association (count plus exact identity and location per ordered pair,
so a nullable qualified name never stands in for identity), runs the existing
NON_NUMERICAL-warning-then-BLOCK preflight, projects every exclusion, and expands
every admitted owner through an explicit `part_def` / `calc_def` / `package` branch.
Owner query results are staged privately and frozen into the returned batch's
`occurrence_transcript` only after every item succeeds, so a later-owner failure
publishes nothing. Lowering then reads only that batch — it cannot evaluate the
profile, query an occurrence source, or re-derive a source referent.

For each prepared item:

1. **Profile preflight** (`evaluate_profile`): a BLOCK-eligibility usage halts
   generation immediately, loudly, naming every diagnostic — this is the one
   kept halt from the pre-Item-5 era, never retired.
   A `NON_NUMERICAL` usage warns with its identity, location, and actionable profile diagnostics,
   then becomes a validated exclusion. An `UNASSESSED` usage becomes a validated exclusion
   without predicate execution.
2. **Owner-kind dispatch** (D5): `part_def` owners expand to one concrete
   instance per `OccurrenceIndex.occurrences_of()` result; `calc_def` owners
   expand to one per matching concrete calc usage; `package` owners are already
   concrete (one instance, top-level scope). Any other owner kind (e.g.
   `requirement_def`) is defensively cataloged **unassessed** — one record,
   `eligible=False`, no expansion, no formal resolution, no node (D7).
3. **Per-instance formal resolution** (`resolve_actual`, the strict ladder):
   registry `scoped_lookup` → `alias_lookup` → `scoped_alias_lookup` (each tried
   occurrence-scoped then de-indexed) → occurrence-scoped design attribute
   (`{owner_instance_path}__{chain}`, the shape the supplied-value materializer
   synthesizes) → definition-scoped target QN → **definition-scoped base-literal
   default** (`{owner_def_qn}__{chain}`, Item 14's D2-twin rung — the
   constraint-actual analog of ADR-001's `LIBRARY_DEFAULT`: a modeled value
   recognized via a third key shape, not synthesized) → the shared
   terminal-disposition switch, called `strict=True` so it always raises rather
   than ever synthesizing a fallback (INV-2).

Supplied-value demand covers both routes. `enrich_graph_design_attributes()`
builds a `DemandOrigin` from every calc-usage binding **and** every admitted
constraint actual in the prepared batch, so a constraint actual with no calc-usage
binding of its own — a self-named `in gain = gain` referencing an instance-level
`:>>` redefinition nothing else reads — still reaches the value ladder. Without the
constraint route, the seam would never synthesize the design attribute the
occurrence-scoped rung above needs.

Origins that normalize to the same target QN merge into one `LogicalDemand`, so a
target reached by both routes is scanned once, counted once, warns at most once, and
synthesizes at most one attribute. Grouping provenance is chosen after resolution:
calc-route source first, then the exact captured design-attribute source, then the
real source behind the winning redefinition record, then the portable
constraint-usage source. Ambiguity or absence at the selected tier raises.

## Catalog (`generation/constraint_catalog.py`)

`assemble_constraint_catalog(concrete, facts)` builds the `ConstraintCatalog`
embedded on the graph (Item 7):

- **`source_records`** — one per `ConstraintDefinition` in `facts.definitions`,
  unconditionally (unused definitions stay visible as authoring inventory, never
  miscounted as unassessed — the "naming divergence" the concept's per-*usage*
  "source record" language and this per-*definition* field carry, recorded in
  the Item 14 design's Core Concept).
- **`concrete_entries`** — one per **eligible** concrete constraint, a thin
  catalog-shaped projection carrying `predicate_ir` so the same-IR guard
  (`assert_same_ir`) can compare byte-for-byte across every entry sharing one
  definition before the single per-definition compile.
- **`excluded_records`** — one per non-executed concrete record. Each carries a validated
  `ConstraintExclusion` payload with its exclusion kind, profile reasons, and rendered source
  location. It has no executable predicate, inputs, evaluation channel, or expected value.
- **`fingerprint`** — sha256 over canonical JSON of `source_records`, `concrete_entries`, and
  `excluded_records`, set once the
  catalog is embedded on the graph; every generation seam reads catalog data
  from `graph.constraint_catalog`, never from `ctx` directly.

A `BLOCK` decision never reaches catalog assembly. `NON_NUMERICAL` and `UNASSESSED` records do:
they are ineligible concrete records projected into `excluded_records`, never
`concrete_entries`. The migration mapping test (`test_constraint_migration_mapping.py`, D1/INV-A)
proves every swept usage lands in exactly one catalog outcome.

## Contracts

The constraint catalog this component assembles is embedded by value on the package's
semantic `ModelContract`, which — with the physical `PackageContract` seal and the
emitted verifier — is documented in its own reference doc:
[29-contracts-and-sealing](29-contracts-and-sealing.md). (`contracts/verify.py` carries
a `GENERATOR_MISMATCH` diagnostic reserved for a generator-version mismatch.)

## What lives elsewhere

- The executable profile (the four-outcome classification and its block list, including
  invocation, conditional, temporal, unit conversion, and numerical equality) is
  `agentic-mbse`'s `executable_profile.py` — documented there.
- The study layer that drives a lowered assertion over a design-space grid
  (Items 10-12) is `teax`'s evaluator/study-layer surface — documented there.
