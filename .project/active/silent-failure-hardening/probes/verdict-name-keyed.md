# Verdict: Name-Keyed Lookup Maps + Aggregation Operator Map — Item 5

Findings D3-7, D3-10, D3-11, D3-15 (name-keyed family) and D3-8 (blind-dispatch, but grouped
here by the probe agent). Completed by the orchestrator via code trace after the assigned
probe agent was cut off by a rate limit; its probe scripts and authored fixtures are
committed under `probes/` (`d37_partname_merge.py`, `d38_caret_operator.py`,
`d310_leaf_redef.py`, `d311_usage_by_name.py` + `fixtures/`).

**Execution note.** Python execution blocked in this sandbox; these are deterministic
lookup/dispatch bugs, so the code trace is airtight. Several need two same-named siblings to
trip — the authored fixtures under `probes/fixtures/` supply that shape and become permanent
fixtures in design/impl.

## D3-7 — attribute-resolution map keyed by bare `owning_part_name`
- **Intended:** `07-graph-assembly.md` / `15-naming-conventions.md` — two distinct PartDefs
  must not share a resolution namespace.
- **Trace:** `graph_builder.py:984` writes `result[ca.owning_part_name]`; `:1102` reads
  `resolution_map.get(ca.owning_part_name, {})`. Two `Widget` PartDefs in different packages
  merge into one bucket; a same-named attr overwrites first-wins — a silent cross-wire that
  passes Step-8 validation.
- **Verdict: CONFIRMED-latent.** Needs the authored `d37_partname_merge` two-package fixture.

## D3-8 — aggregation `^` silently compiles to Python XOR
- **Intended:** `13-aggregation-scoping.md` / `14-expression-compiler.md` — `^` is power → `**`;
  untranslatable nodes set `has_unsupported`.
- **Trace:** `hierarchy_resolver.py:370,382` use `OPERATOR_MAP`, where `"^": " ^ "`
  (`expression_utils.py:27` = Python bitwise XOR) and the fallback `f" {operator} "` passes
  unknown ops through verbatim — and never set `has_unsupported`.
- **Verdict: CONFIRMED-latent.** No corpus aggregation uses `^`; the `d38_caret` fixture trips
  it. Belongs to the **blind-dispatch family** (wrong-map onto valid-looking output), not the
  name-keyed family.

## D3-10 — redefinition matched by leaf name, first-wins
- **Intended:** `07-graph-assembly.md` — a redefinition binds to its own part's attribute.
- **Trace:** `graph_builder.py:1246-1251` matches on `redef.attribute_name == attr` plus a
  leaf-name compare, then `break` (first-wins) across all redefinitions.
- **Verdict: CONFIRMED-latent.** Needs two partdefs sharing a leaf name (`d310_leaf_redef`).

## D3-11 — `_usage_by_name` first-wins; `.output` half never validated
- **Intended:** `11-analysis-backtracker.md` — target resolution unambiguous, named output
  validated.
- **Trace:** `dependency_backtracker.py:244-248` — `target.split(".")[0]` discards the
  `.output` suffix unchecked; `self._usage_by_name.get(instance_name)` collapses same-named
  usages. `sibling_channel_ambiguity` already carries two `power_calc` usages.
- **Verdict: CONFIRMED.**

## D3-15 — `design_prefix` first-wins across two designs
- **Intended:** `13-aggregation-scoping.md` — aggregation keys scoped to their own design.
- **Trace:** `pipeline_builder.py:597` — `design_prefix = segments[0]` taken from the first
  virtual usage, first-wins; two designs in one model mis-key aggregations.
- **Verdict: CONFIRMED-latent.** Needs a two-design model (`d315_two_designs`, to author).

## Family choke point (name-keyed: D3-7, D3-10, D3-11, D3-15)
Key resolution maps so two distinct SysML entities cannot merge: key by qualified name (QN),
or — where a leaf-name match is structurally required — enforce uniqueness and warn on
collision at lookup. Validate the `.output` half of a backtracker target against the resolved
usage's real outputs. Design may split the QN re-key to a follow-on if churn is large
(epic-pre-authorized); a require-unique-or-warn interim is the loud, low-churn stopgap.
