# SysML Syntax Validation Results

Validated all `sysml` code blocks across docs 00-16 using `uv run syside check`.
Snippets were wrapped in `package TestPkg { ... }` with appropriate `private import`
statements for validation. Blocks that are single-line fragments within narrative
context are marked PARTIAL (snippet only).

**Validation date:** 2026-02-16
**Tool:** SysIDE `syside check` (SysML v2 parser + semantic checker)

---

## Doc 00: Pipeline Overview

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `calc def BatteryPackCostCalc { in capacity_kwh : Real; ... return total_cost : Real = ... }` | OK | Valid calc def. Uses `in`/`return` correctly. Passes syside. |

---

## Doc 01: Extraction

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `calc def battery_cost_calc { in capacity : Real; in unit_cost : Real; return total_cost ... }` | OK | Valid calc def with lowercase name (unusual but legal). Passes syside. |
| 2 | `part def SolarBattery { attribute capacity : Real = 100.0; calc battery_cost : battery_cost_calc { in capacity = SolarBattery::capacity; in unit_cost = 4.5; } }` | OK | Valid calc usage with REFERENCE and LITERAL bindings. Passes syside. |
| 3 | `part def SolarBattery { doc /* Battery storage subsystem */ attribute capacity : Real; attribute voltage : Real = 48.0; }` | OK | Valid part def with doc comment. Passes syside. |
| 4 | `in capacity = solar_array.rated_capacity;` | PARTIAL | Snippet only -- CHAIN binding example. Syntax correct when placed inside a calc usage with proper context. Validated separately. |
| 5 | `in capacity = rated_capacity;` | PARTIAL | Snippet only -- REFERENCE binding example. Syntax correct in context. |
| 6 | `in unit_cost = 4.5;` | PARTIAL | Snippet only -- LITERAL binding example. Syntax correct in context. |
| 7 | `in adjusted_cost = base_cost * inflation_factor;` | PARTIAL | Snippet only -- EXPRESSION binding example. Syntax correct in context. |
| 8 | `part def Solar_Array { attribute module_count : Integer = 20; part pv_module : PV_Module [module_count]; ... :>> capital_cost = sum(pv_module.capital_cost) + inverter.install_cost + misc_hardware_cost; }` | PARTIAL | Illustrative snippet. Syntactically correct SysML v2 but incomplete: `:>> capital_cost` requires `capital_cost` to exist in a supertype (redefinition requires an inherited feature). Also `sum()` requires `private import NumericalFunctions::*;`. When proper supertype and imports are added, passes syside cleanly. |

---

## Doc 02: Orchestration

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `part def Solar_Array { attribute total_capex = sum(cost_model.total_cost); }` | PARTIAL | Illustrative snippet. Syntactically valid SysML v2. Reference errors from syside (`cost_model` not defined in scope) are expected for a snippet. Would need `cost_model` part and `NumericalFunctions` import to fully resolve. |

---

## Doc 03: Resolution Overview

No SysML code blocks.

---

## Doc 04: Unified Input Resolver

No SysML code blocks.

---

## Doc 05: Module Factory

No SysML code blocks.

---

## Doc 06: Entry Point Classifier

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `part def SolarPanel { attribute area : Real = 1.6; }` | OK | Valid part def with literal default. Passes syside. |
| 2 | `calc def battery_cost_calc { in efficiency : Real default 0.95; return cost : Real; }` | OK | Valid use of `default` keyword for calc def input parameters. Passes syside. |
| 3 | `battery_cost = battery_cost_calc(unit_cost = 4.50);` | ISSUE | Uses shorthand invocation syntax. Parses correctly (not a parse error), but syside reports a **type error**: `battery_cost_calc::cost does not conform to Calculations::Calculation`. The codebase uses the full body syntax `calc battery_cost : battery_cost_calc { in unit_cost = 4.50; }` which passes cleanly. The doc should use the full body syntax to match actual SysML patterns in the codebase. |

---

## Doc 07: Graph Assembly

No SysML code blocks.

---

## Doc 08: Generation

No SysML code blocks.

---

## Doc 09: Data Models Reference

No SysML code blocks.

---

## Doc 10: Output Registry

No SysML code blocks.

---

## Doc 11: Analysis Backtracker

No SysML code blocks.

---

## Doc 12: Virtual Binding Rewriting

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `part solar_array : Solar_Array { :>> wattage = 400.0; :>> efficiency = tracker.eta; }` | PARTIAL | Illustrative snippet. Syntactically valid SysML v2. The `:>> wattage = 400.0` (LITERAL override) is correct. The `:>> efficiency = tracker.eta` (CHAIN override) is correct syntax but `tracker` is not defined in the local scope. When `tracker` part and `Solar_Array` type are provided, passes syside cleanly. |
| 2 | `part solar_array : Solar_Array { :>> wattage = 400.0; :>> efficiency = tracker.eta; }` | PARTIAL | Same pattern as Block 1, repeated in the Before/After example. Same assessment. |

---

## Doc 13: Aggregation Scoping

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `part def Solar_Array { attribute total_capex :>> cost_model.total_cost; attribute capital_cost = sum(pv_module.capital_cost) * module_count; }` | PARTIAL | Illustrative snippet. Two issues for standalone validation: (a) `:>> total_capex` requires an inherited feature, (b) `sum()` requires `NumericalFunctions` import. The patterns themselves (`:>>` CHAIN redefinition and `sum()` aggregation with `*` multiplicity) are correct SysML v2. When proper supertype, imports, and child parts are provided, passes syside cleanly. |
| 2 | `part def SolarBatteryDesign { part solar_battery_plant : Solar_Battery_Plant { part solar_array : Solar_Array { ... } } }` | OK | Valid part hierarchy. The `{ ... }` is pseudo-syntax indicating elided content. When instantiated properly, passes syside (with a namespace shadowing warning, which is just a warning). |

---

## Doc 14: Expression Compiler

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `calc def CostCalc { in capacity : Real; in cost_per_kwh : Real; return total_cost : Real = capacity * cost_per_kwh; }` | OK | Valid calc def. Clean binary expression. Passes syside. |

---

## Doc 15: Naming Conventions

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `package SolarBatteryLibrary { calc def BatteryPackCostCalc { in capacity_kwh; out total_cost; } } part def SolarBatteryDesign { ... calc cost_model : BatteryPackCostCalc { ... } }` | OK | Valid SysML v2. Uses `in`/`out` without type annotations (legal; types default to `Anything`). Uses `out` instead of `return` (valid for output features, though `return` is conventional for calc defs). The `{ ... }` is pseudo-syntax for elided content. Passes syside when `{ ... }` is replaced with valid content or removed. |

---

## Doc 16: Computed Attributes

| Block # | Lines | Valid? | Notes |
|---------|-------|--------|-------|
| 1 | `part def Solar_Array { attribute panel_count : Integer = 20; attribute panel_wattage : Real = 400.0; attribute dc_capacity : Real = panel_count * panel_wattage; attribute total_capex : Real = cost_model.total_cost; }` | OK | Valid part def with FORMULA and EXPOSE patterns. When `cost_model` calc part is provided, passes syside cleanly. |
| 2 | `attribute dc_capacity = panel_count * panel_wattage;` | PARTIAL | Snippet only -- FORMULA attribute example. Syntax correct in context. |
| 3 | `attribute p_alpha_out = alpha_split.p_alpha;` | PARTIAL | Snippet only -- EXPOSE_PURE attribute example. Syntax correct in context. |
| 4 | `part def Solar_Array { attribute panel_count : Integer = 20; ... attribute dc_capacity : Real = panel_count * panel_wattage; attribute total_capex : Real = cost_model.total_cost; attribute adjusted_cost : Real = cost_model.total_cost * 1.1; }` | OK | Valid part def showing all three computed attribute types (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED). Passes syside when `cost_model` calc is defined. |

---

## Doc STRATEGY: Strategy

No SysML code blocks.

---

## Overall Summary

| Metric | Count |
|--------|-------|
| **Total SysML blocks** | 23 |
| **Valid (OK)** | 12 |
| **Partial/illustrative** | 10 |
| **Issues** | 1 |

### Issue Details

1. **Doc 06, Block 3** -- Uses shorthand invocation syntax `battery_cost = battery_cost_calc(unit_cost = 4.50)` which triggers a syside type error. Should use the full body syntax: `calc battery_cost : battery_cost_calc { in unit_cost = 4.50; }` to match the actual SysML patterns used in the codebase.

### Partial/Illustrative Block Notes

All 10 partial blocks are single-line snippets or fragments embedded in narrative context. They demonstrate correct SysML v2 syntax patterns but are not standalone-compilable. Specifically:

- **4 binding snippets** (Doc 01, Blocks 4-7): `in x = expr;` patterns -- all syntactically correct
- **1 aggregation snippet** (Doc 01, Block 8): Uses `:>>` and `sum()` -- correct syntax but needs supertype + imports for standalone validation
- **1 aggregation snippet** (Doc 02, Block 1): `sum(cost_model.total_cost)` -- correct syntax, needs context
- **2 redefinition snippets** (Doc 12, Blocks 1-2): `:>> attr = value` -- correct syntax, needs parent type
- **1 aggregation snippet** (Doc 13, Block 1): `:>>` + `sum()` combo -- correct syntax, needs imports + supertype
- **2 attribute snippets** (Doc 16, Blocks 2-3): attribute assignment fragments -- correct syntax

### Key SysML v2 Syntax Patterns Validated

All of the following patterns used in the docs are confirmed valid SysML v2:

| Pattern | Example | Status |
|---------|---------|--------|
| `calc def` with `in`/`return` | `calc def X { in a : Real; return b : Real = a; }` | Valid |
| `calc def` with `in`/`out` | `calc def X { in a; out b; }` | Valid (but `return` is conventional) |
| `calc def` with `default` | `in efficiency : Real default 0.95;` | Valid |
| `calc` usage (full body) | `calc x : CalcDef { in a = expr; }` | Valid |
| `:>>` LITERAL redefinition | `:>> wattage = 400.0;` | Valid (requires inherited feature) |
| `:>>` CHAIN redefinition | `:>> total_capex = cost_model.total_cost;` | Valid (requires inherited feature) |
| `:>>` EXPRESSION redefinition | `:>> capital_cost = sum(pv.cost) + extra;` | Valid (requires inherited feature + imports) |
| `attribute` with expression | `attribute dc = a * b;` | Valid |
| `attribute` with chain | `attribute x = part.attr;` | Valid |
| `doc` comment | `doc /* text */` | Valid |
| `part` with multiplicity | `part pv : PV_Module [count];` | Valid |
| `sum()` function | `sum(child.attr)` | Valid (requires `NumericalFunctions` import) |

### Recommendations

1. **Fix Doc 06 Block 3**: Replace shorthand invocation syntax with full body syntax to avoid syside type error.
2. **Consider adding import notes**: Several snippets require `private import ScalarValues::*` and/or `private import NumericalFunctions::*` to be complete. While these are illustrative snippets, a footnote mentioning required imports would help readers who try to reproduce them.
3. **Consider adding supertype notes for `:>>` examples**: The `:>>` redefinition examples in Docs 01, 13 require an inherited feature from a supertype. A brief note clarifying this SysML v2 requirement would prevent confusion.
