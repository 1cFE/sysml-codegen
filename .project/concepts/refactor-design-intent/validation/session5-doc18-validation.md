# Session 5: Doc 18 (Literal Value Propagation) Validation

Validated against source code on the `cost-pattern` branch.

---

## 1. `_find_literal_redefinition()` Function Signature

**Doc claim (line 51-57):**
```python
def _find_literal_redefinition(
    part_usage: str,
    attr: str,
    redefinitions: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str] | None,
    owning_part_qn: str | None,
) -> float | None
```

**Actual** (`graph_builder.py`, lines 870-876):
```python
def _find_literal_redefinition(
    part_usage: str,
    attr: str,
    redefinitions: list[RedefinitionData],
    usage_type_map: dict[tuple[str, str], str] | None = None,
    owning_part_qn: str | None = None,
) -> float | None
```

**Verdict: MINOR DISCREPANCY.** The doc omits the default values (`= None`) on the last two parameters. The types, parameter names, and return type are correct. This is cosmetic -- the doc signature is invocation-compatible.

---

## 2. Two Matching Strategies

**Doc claims (lines 70-101):**
- Strategy 1: Type-aware via `usage_type_map` -- resolve `(owning_part_qn, part_usage)` to target PartDef QN, then match `redef.owning_part_qn` exactly.
- Strategy 2: Name-based fallback -- extract last segment of `redef.owning_part_qn`, compare case-insensitive with `sanitize_name()`.

**Actual** (`graph_builder.py`, lines 898-918):
```python
target_partdef_qn: str | None = None
if usage_type_map and owning_part_qn:
    target_partdef_qn = usage_type_map.get((owning_part_qn, part_usage))

for redef in redefinitions:
    if redef.redefinition_type == RedefinitionType.LITERAL and redef.attribute_name == attr:
        matched = False
        if target_partdef_qn is not None:
            matched = redef.owning_part_qn == target_partdef_qn
        else:
            redef_part_name = redef.owning_part_qn.split("__")[-1]
            matched = sanitize_name(redef_part_name).lower() == part_usage.lower()
```

**Verdict: ACCURATE.** Both strategies match exactly. Strategy 1 does exact QN match when `target_partdef_qn` is resolved. Strategy 2 falls back to name-based with `sanitize_name().lower()` comparison on the last segment. Note: the strategies are exclusive (if/else), not sequential -- the doc correctly describes this ("If no `usage_type_map` or no match" on line 89 is slightly ambiguous but functionally correct since Strategy 2 only runs when `target_partdef_qn is None`, i.e., when Strategy 1 couldn't even resolve a target).

---

## 3. Call Sites: Line Numbers

**Doc claims (lines 107-108):**
- SumTerm fallback at line 974
- SingletonTerm fallback at line 1081

**Actual:**
- SumTerm fallback: `_find_literal_redefinition` called at line 975-978
- SingletonTerm fallback: `_find_literal_redefinition` called at lines 1087-1089

**Verdict: MINOR DISCREPANCY.** Line numbers are approximate but close. SumTerm is off by ~1-4 lines, SingletonTerm by ~6-8 lines. The doc says "line 974" and "line 1081" which are in the right neighborhood. This is expected drift from edits after the doc was written.

---

## 4. SumTerm and SingletonTerm Fallback Pattern

**Doc claims (lines 108-116):**
- Both follow same pattern: after channel resolution fails, call `_find_literal_redefinition(part_usage, attr, ...)`
- For SumTerms, `part_usage` and `attr` come from term fields
- For SingletonTerms, parsed from `source_path.rsplit(".", 1)`
- Literal default found -> FULLY_COMPILABLE; not found -> MANUAL_REQUIRED

**Actual:**
- SumTerm (line 975): `_find_literal_redefinition(term.part_usage_name, term.attribute_name, ...)` -- CORRECT
- SingletonTerm (line 1086): `s_part_usage, s_attr = s_term.source_path.rsplit(".", 1)` then `_find_literal_redefinition(s_part_usage, s_attr, ...)` -- CORRECT
- SumTerm: `literal_default is None` -> `compilability = Compilability.MANUAL_REQUIRED` (line 985) -- CORRECT
- SingletonTerm: `literal_default is None` -> `compilability = Compilability.MANUAL_REQUIRED` (line 1097) -- CORRECT

**Verdict: ACCURATE.** The doc correctly describes the fallback pattern for both term types, including the compilability implications.

---

## 5. Entry Point Default Backfill

**Doc claim (lines 125-129):** If `entry_points[ep_qn].default_value is None` and a `literal_default` is found, a new `EntryPoint` replaces the old one.

**Actual:**
- SumTerm backfill (lines 997-1006):
  ```python
  elif literal_default is not None and entry_points[ep_qn].default_value is None:
      ep = entry_points[ep_qn]
      entry_points[ep_qn] = EntryPoint(
          qualified_name=ep.qualified_name,
          ...
          default_value=literal_default,
          ...
      )
  ```
- SingletonTerm backfill (lines 1109-1119): identical pattern.

**Verdict: ACCURATE.** Both SumTerm and SingletonTerm implement the backfill. The doc's description matches.

---

## 6. `expose_aliases` and `usage_type_map` on `_build_aggregation_module()`

**Doc claims (lines 145, 187):** These parameters are on `_build_aggregation_module()`.

**Actual** (`graph_builder.py`, lines 922-929):
```python
def _build_aggregation_module(
    agg: ScopedAggregationData,
    redefinitions: list[RedefinitionData],
    output_registry: OutputRegistry,
    entry_points: dict[str, EntryPoint],
    group_deriver: ParameterGroupDeriver | None,
    expose_aliases: dict[tuple[str, str], str] | None = None,
    usage_type_map: dict[tuple[str, str], str] | None = None,
) -> PipelineModule:
```

**Verdict: ACCURATE.** Both parameters are present on the function signature.

---

## 7. LocalTerms Do NOT Call `_find_literal_redefinition`

**Doc claim (lines 118-119):** "LocalTerms -- not applicable. They reference same-PartDef attributes, not child part usages, so LITERAL :>> redefinition lookup doesn't apply."

**Actual** (`graph_builder.py`, lines 1133-1189): The LocalTerm processing block tries:
1. Sibling aggregation output (lines 1140-1146)
2. EXPOSE_PURE alias resolution (lines 1148-1163)
3. Falls through to entry point creation (lines 1166-1182)

There is **no call** to `_find_literal_redefinition` in the LocalTerm block.

**Verdict: ACCURATE.** The doc's claim is correct. LocalTerms never invoke `_find_literal_redefinition`.

---

## 8. `usage_type_map` on `HierarchyExtractionResult`

**Doc claim (line 135):** `HierarchyExtractionResult.usage_type_map: dict[tuple[str, str], str]`

**Actual** (`data_models.py`, lines 341-344):
```python
usage_type_map: dict[tuple[str, str], str] = field(default_factory=dict)
```

**Verdict: ACCURATE.** Type and field name match. The doc doesn't mention the `field(default_factory=dict)` default, which is fine -- it's describing the type, not the full dataclass field declaration.

---

## 9. `_find_literal_redefinition` Line Number

**Doc claim (line 43):** "File: `src/sysml_codegen/resolution/graph_builder.py`, line 870."

**Actual:** Function definition starts at line 870.

**Verdict: ACCURATE.** Exact match.

---

## 10. Data Models Table

**Doc claims (lines 178-189):**

| Model | File | Verdict |
|-------|------|---------|
| `RedefinitionData` in `extraction/data_models.py` | Line 234 | ACCURATE |
| `HierarchyExtractionResult` in `extraction/data_models.py` | Line 332 | ACCURATE |
| `EntryPoint` in `resolution/models.py` | Line 37 | ACCURATE |
| `SumTerm` in `extraction/data_models.py` | Line 274 | ACCURATE |
| `SingletonTerm` in `extraction/data_models.py` | Line 284 | ACCURATE |
| `_find_literal_redefinition()` in `resolution/graph_builder.py` | Line 870 | ACCURATE |
| `_build_aggregation_module()` in `resolution/graph_builder.py` | Line 922 | ACCURATE |
| `hierarchy_resolver.py` populates `usage_type_map` | Lines 508-531 | ACCURATE |
| `generation/initialization.py` threads `usage_type_map` | Line 830 | ACCURATE |

**Verdict: ALL ACCURATE.** Every file location and model name is correct.

---

## 11. Threading Path: `usage_type_map`

**Doc claim (lines 144-145):** `HierarchyExtractionResult` -> `build_pipeline_context()` -> `build_computation_graph()` -> `_build_aggregation_module()`.

**Actual:**
1. `extract_hierarchy_data()` populates `HierarchyExtractionResult.usage_type_map` (`hierarchy_resolver.py:572`)
2. `build_pipeline_context()` passes `hierarchy_data.usage_type_map` to `build_computation_graph()` (`initialization.py:830`)
3. `build_computation_graph()` passes `usage_type_map or {}` to `_build_aggregation_module()` (`graph_builder.py:195`)
4. `_build_aggregation_module()` passes it to `_find_literal_redefinition()` (`graph_builder.py:977, 1089`)

**Verdict: ACCURATE.** The threading chain is correctly described.

---

## Summary

| Check | Verdict |
|-------|---------|
| Function signature | MINOR: defaults omitted |
| Two matching strategies | ACCURATE |
| SumTerm fallback call site | MINOR: ~4 lines off |
| SingletonTerm fallback call site | MINOR: ~8 lines off |
| Fallback pattern description | ACCURATE |
| Entry point backfill | ACCURATE |
| `expose_aliases` / `usage_type_map` params | ACCURATE |
| LocalTerms skip literal lookup | ACCURATE |
| `usage_type_map` on HierarchyExtractionResult | ACCURATE |
| `_find_literal_redefinition` line number | ACCURATE |
| Data models table | ACCURATE |
| Threading path | ACCURATE |

**Overall assessment:** The doc is highly accurate. Three minor discrepancies (default parameter values omitted, call-site line numbers drifted by a few lines). No factual errors found. All architectural claims about control flow, data threading, and behavioral semantics are correct.
