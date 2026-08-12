# 18 -- Literal Value Propagation for Aggregation Entry Points

> **Status: the mechanism below was deleted; the shipped equivalent is described first.**
> `_find_literal_redefinition` in `resolution/graph_builder.py` went with the Item 7
> retirement (2026-08-12, `19072ad` / `82c7951` / `882fc8d` / `3071fba`). The problem it
> solved is real and the shipped route still solves it, by a different shape — that is the
> next section. Everything from "The Problem" onward is retained as the record of the deleted
> design; read it as history, and REQ-LVP-01..07 as that code's requirements.

## What the shipped route does instead

**The short version: there is no propagation.** A literal is not searched for after the fact,
because by the time anything asks for it the value already sits on the attribute node that
owns it. Elaboration decides once, per occurrence, who writes a value; projection reads it.

The mental model is a **slot with exactly one writer**. Elaboration walks occurrences, and for
each attribute slot in a scope it collects every declaration that could supply a value —
the base declaration, a specialized definition's `:>>`, an occurrence's own override — and
resolves them to one (`elaboration/elaborate.py`, `_resolve_value_writer` /
`_require_one_writer`). Two writers it cannot order raise
`SI_REDEFINITION_INVALID`. That is the whole precedence mechanism: not a strategy ladder that
tries and falls back, but a single-writer requirement that fails loudly when the model is
ambiguous.

Having picked the writer, `_create_value_node` records **where the value came from** as a
`ValueSite` on the node (`elaboration/graph.py:59`):

| `ValueSite` | The writer is |
|---|---|
| `OCCURRENCE_OVERRIDE` | a `:>>` on the part usage, inside this occurrence's scope |
| `SPECIALIZED_DEF` | a different declaration from the base — a specializing def redefined it |
| `DEFINITION_DEFAULT` | the base declaration's own value |
| `NONE` | there is no value expression at all |

`value_site` is a **record, not a switch**. Nothing branches on it to decide how to find a
value; it says where the one value already found was written. Projection reads it only to
classify the entry point, and all four sites classify the same way — `DESIGN_ATTRIBUTE`
(`elaboration/project.py:456-460`), because in every case a modelled attribute is what
supplies the number. The default that lands in the JSON template is `attr.value`, read
straight off the node.

Deep-path redefinitions (`:>> a.b.c = 0.0`, which parse as anonymous features with no
qualified name of their own) are applied in a separate sweep,
`_apply_deep_literal_redefinitions`, before the graph is handed on. That is the one place the
elaborator looks a value up rather than being handed it, and it is scoped to features the
occurrence walk cannot reach by name.

**What this buys over the deleted design.** The old mechanism ran after wiring failed: an
aggregation term that could not reach an upstream channel triggered a two-strategy search for
a matching redefinition, type-aware first, name-based second. Both strategies could miss, and
a name-based hit could be the wrong attribute. The shipped route never reaches that position —
the value is attached to the occurrence's node at elaboration, so an entry point either has
its modelled default or the model never wrote one.

**Evidence.** `tests/unit/test_zero_default_exact_route.py` (a `0.0` default projects as zero,
not null, and the check is identity not truthiness),
`tests/conformance/test_elaboration_shadowing.py` (the innermost definition wins per
occurrence; equal-valued independent literals stay distinct), and
`tests/conformance/test_elaboration_specialization_retypes.py` (a specialized definition's
`:>>` reaches the occurrence that retyped to it).

## The Problem

When an aggregation input (SumTerm or SingletonTerm) can't be wired to an
upstream module's output channel, it becomes an entry point -- a value the user
provides via a JSON input file. Before this feature, those entry points always
had `default_value = None`, producing `null` in the JSON template:

```json
{
  "permitting_raw_material_cost": null,
  "permitting_fabrication_cost": null,
  "permitting_installation_cost": null
}
```

But SysML PartDefs often declare these values explicitly:

```sysml
part def 'Permitting & Interconnect' :> 'Costed Component' {
    :>> raw_material_cost = 0.0;
    :>> fabrication_cost = 0.0;
    :>> installation_cost = 0.0;
}
```

Permitting is a soft cost -- it has no material, fabrication, or installation
split. The PartDef says so. The JSON template should reflect that:

```json
{
  "permitting_raw_material_cost": 0.0,
  "permitting_fabrication_cost": 0.0,
  "permitting_installation_cost": 0.0
}
```

---

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-LVP-01 | `_find_literal_redefinition()` SHALL try type-aware resolution (Strategy 1) before name-based fallback (Strategy 2) | `_find_literal_redefinition()` in `graph_builder.py`: type-aware match via `target_partdef_qn`, fallback via last-segment name comparison |
| REQ-LVP-02 | SumTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution fails | SumTerm `else` branch in `_build_aggregation_module()` |
| REQ-LVP-03 | SingletonTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution fails | SingletonTerm `if s_source is None` branch in `_build_aggregation_module()` |
| REQ-LVP-04 | LocalTerms SHALL NOT use literal redefinition lookup (different resolution path) | No `_find_literal_redefinition` call in LocalTerm handling within `_build_aggregation_module()` |
| REQ-LVP-05 | Entry point default backfill SHALL replace `None` defaults with literal values discovered by later terms | `elif literal_default is not None` backfill blocks in both SumTerm and SingletonTerm handling |
| REQ-LVP-06 | `usage_type_map` SHALL be threaded from [`HierarchyExtractionResult`](09-data-models.md) through [`build_computation_graph()`](07-graph-assembly.md) to `_build_aggregation_module()` | `pipeline_builder.py` passes `hierarchy_data.usage_type_map` to `build_computation_graph()`, which forwards it to `_build_aggregation_module()` |
| REQ-LVP-07 | Literal default found SHALL keep module `FULLY_COMPILABLE`; no default SHALL set `MANUAL_REQUIRED` | Compilability conditional in `_build_aggregation_module()` |
| REQ-LVP-08 | `usage_type_map` SHALL resolve each `(owning_qn, usage_name)` to the most-specific owned FeatureTyping target (not `next(iter(member.types))`); incomparable multi-typings resolve sorted-first with a V10 warning | `most_specific()` selection in `extract_hierarchy_data()` (`extraction/hierarchy_resolver.py`) |
| REQ-LVP-09 | `_index_usage_level_retypes` SHALL index usage-level retypes of inherited part usages (`part hif_plant : Base { part :>> driver : Subtype }`) into `usage_type_map`, keyed by the CONTAINER usage's instance QN, limited to GENUINE retypes (a `:>>` whose most-specific owned type differs from the base def's declared type for that member) so value-only `:>>` overrides are excluded | `_index_usage_level_retypes()` in `extraction/hierarchy_resolver.py` |

---

## The Solution: `_find_literal_redefinition()`

**File:** `src/sysml_codegen/resolution/graph_builder.py`.

When a SumTerm or SingletonTerm in `_build_aggregation_module()` fails to
resolve to an upstream channel, the builder now checks for a LITERAL `:>>`
redefinition before creating the entry point. If found, the literal value
becomes the entry point's `default_value`.

```python
def _find_literal_redefinition(
    part_usage: str,                                    # "permitting"
    attr: str,                                          # "raw_material_cost"
    redefinitions: list[RedefinitionData],               # all :>> redefinitions
    usage_type_map: dict[tuple[str, str], str] | None,  # type-aware lookup
    owning_part_qn: str | None,                         # aggregation owner
) -> float | None
```

Returns a `float` if a matching LITERAL redefinition exists, `None` otherwise.

---

## Two Matching Strategies

The function needs to match a `(part_usage, attr)` pair against the
`redefinitions` list. The challenge: usage names may not match PartDef names.
A PartDef `Permitting_Interconnect` might be instantiated as usage `permitting`.

### Strategy 1: Type-Aware (via usage_type_map)

If `usage_type_map` is available, resolve `(owning_part_qn, part_usage)` to the
child's type PartDef QN, then match `redef.owning_part_qn` exactly.

```
usage_type_map = {
    ("SolarBatteryLibrary__Site_Infrastructure", "permitting"):
        "SolarBatteryLibrary__Permitting_Interconnect"
}

# Looking for ("permitting", "raw_material_cost"):
# 1. Resolve: ("Site_Infrastructure", "permitting") → "Permitting_Interconnect"
# 2. Match: redef.owning_part_qn == "SolarBatteryLibrary__Permitting_Interconnect"
# 3. Found: redef.literal_value = 0.0
```

### Strategy 2: Name-Based Fallback

If no `usage_type_map` or no match, extract the last segment of
`redef.owning_part_qn` and compare (case-insensitive, sanitized) to `part_usage`.

```
redef.owning_part_qn = "Lib__Permitting_Interconnect"
last_segment = "Permitting_Interconnect"
sanitize_name("Permitting_Interconnect").lower() == "permitting".lower()
→ False (names don't match, no fallback hit)
```

This is why Strategy 1 exists: name-based matching fails when usage names are
abbreviated or aliased. The `usage_type_map` provides the authoritative
type resolution.

---

## Where It's Called

**SumTerm fallback** and **SingletonTerm fallback** in
`_build_aggregation_module()`. Both follow the same pattern: after channel
resolution fails, call `_find_literal_redefinition(part_usage, attr, ...)`.

For SumTerms, `part_usage` and `attr` come directly from the term fields.
For SingletonTerms, they're parsed from `source_path.rsplit(".", 1)`.

> **Design note:** In practice, the LITERAL redef fallback path is naturally
> exercised by **SingletonTerms** (e.g., permitting costs:
> raw_material_cost=0.0, fabrication_cost=0.0, installation_cost=0.0),
> not SumTerms. SumTerms typically resolve via upstream channel successfully.
> The SumTerm fallback path is valid but defensive -- it fires when a
> component is referenced as a SingletonTerm in parent aggregations rather
> than as a SumTerm (e.g., Permitting_Interconnect in Site_Infrastructure).

When a literal default is found, the module stays `FULLY_COMPILABLE` (the value
is known, just user-overridable via JSON). When no literal is found, the entry
point gets `default_value=None` and compilability drops to `MANUAL_REQUIRED`.

**LocalTerms** -- not applicable. They reference same-PartDef attributes, not
child part usages, so LITERAL `:>>` redefinition lookup doesn't apply.

---

## Entry Point Default Backfill

An entry point may be created by one term before a later term discovers a
literal default for the same QN. The backfill handles this: if
`entry_points[ep_qn].default_value is None` and a `literal_default` is found,
a new `EntryPoint` is created with the literal default and replaces the old one
in the shared `entry_points` dict. The orchestrator sees the default when grouping.

---

## Related Path: Design-Override Literals on Calc-Usage Bindings

Aggregation terms are not the only place modeled literals reach entry-point
defaults. Design-level `:>>` LITERAL overrides -- including those declared on a
plain typed usage's members, kept only when the RHS is a literal (REQ-HR-08) --
are captured by `extract_design_overrides()` (`extraction/hierarchy_resolver.py`)
and applied by `_rewrite_virtual_bindings()` (`orchestration/pipeline_builder.py`),
which rewrites the matching CalcUsage binding to a LITERAL binding carrying the
value. Those literals then surface as entry-point defaults through normal
binding classification. That path is separate from the
`_find_literal_redefinition()` lookup this document describes.

---

## The usage_type_map

`HierarchyExtractionResult.usage_type_map: dict[tuple[str, str], str]`
(`extraction/data_models.py`). Maps `(owning_part_def_qn, usage_name)` to
`type_part_def_qn`. Built during hierarchy extraction from PartUsage types.

```python
{("Lib__Site_Infrastructure", "permitting"): "Lib__Permitting_Interconnect",
 ("Lib__Solar_Array", "pv_module"):          "Lib__PV_Module"}
```

Two later refinements changed how the map is built (both in
`extraction/hierarchy_resolver.py`):

- The type recorded for each usage is the **most-specific owned FeatureTyping
  target**, not an arbitrary first entry from `member.types`; incomparable
  multi-typings pick sorted-first and warn (V10). (REQ-LVP-08)
- **Usage-level retypes** of inherited part usages
  (`part hif_plant : Base { part :>> driver : Subtype }`) are also indexed,
  keyed by the container usage's instance QN instead of a PartDef QN --
  `_index_usage_level_retypes()`, genuine retypes only, so value-only `:>>`
  overrides stay out of the map. (REQ-LVP-09)

Threaded: `HierarchyExtractionResult` -> `build_pipeline_context()` ->
`build_computation_graph()` -> `_build_aggregation_module()`.

---

## Concrete Example: Permitting Soft Costs

```sysml
part def 'Permitting & Interconnect' :> 'Costed Component' {
    calc cost_model : PermittingCostCalc { in system_capacity_kw = system_capacity_kw; }
    :>> capital_cost = cost_model.total_cost;   // CHAIN → wires to calc output
    :>> raw_material_cost = 0.0;                // LITERAL → entry point default
    :>> fabrication_cost = 0.0;                 // LITERAL → entry point default
    :>> installation_cost = 0.0;                // LITERAL → entry point default
}
```

Site Infrastructure aggregates: `:>> raw_material_cost = sum(permitting.raw_material_cost) + ...`

**Resolution trace** for `permitting.raw_material_cost`:
1. Channel resolution fails (no upstream module produces it)
2. `_find_literal_redefinition("permitting", "raw_material_cost", ...)` called
3. `usage_type_map` resolves `("Site_Infrastructure", "permitting")` to
   `"Permitting_Interconnect"`
4. Matches `RedefinitionData(owning_part_qn="..Permitting_Interconnect",
   attribute_name="raw_material_cost", literal_value=0.0)`
5. Entry point created with `default_value=0.0`, module stays `FULLY_COMPILABLE`

**Result:** JSON template: `"permitting_raw_material_cost": 0.0` (not `null`).

---

## Data Models and Source Files

| Model | File | Role |
|-------|------|------|
| `RedefinitionData` | `extraction/data_models.py` | `:>>` redefinition with type + literal_value |
| `HierarchyExtractionResult` | `extraction/data_models.py` | Carries `usage_type_map` |
| `EntryPoint` | `resolution/models.py` | Receives `default_value` from literal lookup |
| `SumTerm` / `SingletonTerm` | `extraction/data_models.py` | Term types checked for literal fallback |

## Related Documents

- **Pipeline**: [00-pipeline-overview](00-pipeline-overview.md) — Step 5 module building invokes aggregation construction
- **Aggregation scoping**: [13-aggregation-scoping](13-aggregation-scoping.md) — discovers SumTerm/SingletonTerm that need literal fallback
- **Virtual bindings**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — `:>>` CHAIN redefinitions that carry literal values
- **Module factory**: [05-module-factory](05-module-factory.md) — term resolution strategies (SumTerm, SingletonTerm, LocalTerm)
- **Entry points**: [06-entry-point-classifier](06-entry-point-classifier.md) — factory-created EPs receive literal defaults
- **Parameter groups**: [17-parameter-group-deriver](17-parameter-group-deriver.md) — groups EPs with backfilled defaults into JSON files
- **Naming**: [15-naming-conventions](15-naming-conventions.md) — EQN format used by `usage_type_map` keys
- **Data models**: [09-data-models](09-data-models.md) — `RedefinitionData`, `EntryPoint`, `HierarchyExtractionResult` definitions
