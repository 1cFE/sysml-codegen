# 18 -- Literal Value Propagation for Aggregation Entry Points

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
| REQ-LVP-01 | `_find_literal_redefinition()` SHALL try type-aware resolution (Strategy 1) before name-based fallback (Strategy 2) | `graph_builder.py:870`: type-aware at 898-908, fallback at 910-912 |
| REQ-LVP-02 | SumTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution fails | `graph_builder.py:975` in `_build_aggregation_module()` |
| REQ-LVP-03 | SingletonTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution fails | `graph_builder.py:1087` in `_build_aggregation_module()` |
| REQ-LVP-04 | LocalTerms SHALL NOT use literal redefinition lookup (different resolution path) | No `_find_literal_redefinition` call in LocalTerm handling (lines 1133-1176) |
| REQ-LVP-05 | Entry point default backfill SHALL replace `None` defaults with literal values discovered by later terms | Backfill at lines 997-1006 (SumTerm) and 1109-1119 (SingletonTerm) |
| REQ-LVP-06 | `usage_type_map` SHALL be threaded from [`HierarchyExtractionResult`](09-data-models.md) through [`build_computation_graph()`](07-graph-assembly.md) to `_build_aggregation_module()` | Parameter passing: initialization.py:830 → graph_builder.py:80 → 929 |
| REQ-LVP-07 | Literal default found SHALL keep module `FULLY_COMPILABLE`; no default SHALL set `MANUAL_REQUIRED` | Compilability conditional in `_build_aggregation_module()` |

---

## The Solution: `_find_literal_redefinition()`

**File:** `src/sysml_codegen/resolution/graph_builder.py`, line 870.

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

**SumTerm fallback** (line 975) and **SingletonTerm fallback** (line 1087) in
`_build_aggregation_module()`. Both follow the same pattern: after channel
resolution fails, call `_find_literal_redefinition(part_usage, attr, ...)`.

For SumTerms, `part_usage` and `attr` come directly from the term fields.
For SingletonTerms, they're parsed from `source_path.rsplit(".", 1)`.

> **C16 conformance finding (2026-02-17)**: In solar_battery, the LITERAL
> redef fallback path is naturally exercised by **SingletonTerms** (permitting
> costs: raw_material_cost=0.0, fabrication_cost=0.0, installation_cost=0.0),
> not SumTerms. All SumTerms resolve via upstream channel successfully. The
> SumTerm fallback path is valid code but requires constructed test data to
> exercise. This is because Permitting_Interconnect is referenced as
> SingletonTerms in Site_Infrastructure aggregations, not as SumTerms.

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

## The usage_type_map

`HierarchyExtractionResult.usage_type_map: dict[tuple[str, str], str]`
(`extraction/data_models.py`). Maps `(owning_part_def_qn, usage_name)` to
`type_part_def_qn`. Built during hierarchy extraction from PartUsage types.

```python
{("Lib__Site_Infrastructure", "permitting"): "Lib__Permitting_Interconnect",
 ("Lib__Solar_Array", "pv_module"):          "Lib__PV_Module"}
```

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
