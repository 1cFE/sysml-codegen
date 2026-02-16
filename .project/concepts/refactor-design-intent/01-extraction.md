# Step 1: Extraction

Extraction reads SysML v2 model files (via the SysIDE adapter from agentic-mbse),
walks the parsed AST, and produces structured Python dataclasses. No analysis,
resolution, or generation happens here -- it is a pure data-harvesting step.
Source: `src/sysml_codegen/extraction/`

## The 4 Things Extracted

### 1. Calculation Definitions (CalculationDefinitionData)

A calc def is a reusable formula. SysML input:
```sysml
calc def battery_cost_calc {
    in capacity : Real;  in unit_cost : Real;
    return total_cost : Real = capacity * unit_cost;
}
```
Key fields on the extracted `CalculationDefinitionData`:

| Field                    | Example Value                                |
|--------------------------|----------------------------------------------|
| `name`                   | `"battery_cost_calc"`                        |
| `qualified_name`         | `"SolarLib::battery_cost_calc"`              |
| `input_attributes`       | `[AttributeInfo(name="capacity", ...)]`      |
| `output_attributes`      | `[AttributeInfo(name="total_cost", ...)]`    |
| `calc_expressions`       | `["total_cost = (capacity * unit_cost)"]`    |
| `output_expression_asts` | `{"total_cost": <raw syside AST node>}`      |
| `all_member_names`       | `{"capacity", "unit_cost", "total_cost"}`    |
| `member_expressions`     | `{}` (ASTs for non-input/non-output members) |

Each `AttributeInfo` carries `name`, `sysml_type` (`"Real"`), `python_type`
(`"float"`), `default_value`, `binding_type`, `is_input`, `is_output`, `unit`.
The `output_expression_asts` dict holds raw AST nodes that the expression
compiler later converts to Python code.

### 2. Calculation Usages (CalcUsageData)

A calc usage instantiates a calc def with specific bindings. SysML input:
```sysml
part def SolarBattery {
    attribute capacity : Real = 100.0;
    calc battery_cost : battery_cost_calc {
        in capacity = SolarBattery::capacity;  in unit_cost = 4.5;
    }
}
```
Key fields on the extracted `CalcUsageData`:

| Field                     | Example Value                                       |
|---------------------------|-----------------------------------------------------|
| `instance_name`           | `"battery_cost"`                                    |
| `calc_def_name`           | `"battery_cost_calc"`                               |
| `module_type`             | `"SolarLibBatteryCostCalcModule"`                   |
| `bindings`                | `[BindingInfo(param_name="capacity", ...), ...]`    |
| `unbound_params`          | `["efficiency"]` (params with no binding)           |
| `qualified_name`          | `"solar_battery_plant__solar_battery__battery_cost"`|
| `is_template` / `owning_part_def_qn` | `True` / `"Lib__SolarBattery"` if owned by a PartDef |

Template calc usages (owned by a PartDefinition) get expanded: for each
PartUsage that instantiates the owning PartDef, the extractor creates a virtual
CalcUsageData with a design-relative qualified name.

### 3. Part Definitions (PartDefinitionData)

Part definitions model the structural hierarchy. SysML input:
```sysml
part def SolarBattery {
    doc /* Battery storage subsystem */
    attribute capacity : Real;  attribute voltage : Real = 48.0;
}
```
Key fields: `name` (`"SolarBattery"`), `qualified_name`, `doc_comment`
(`"Battery storage subsystem"`), `attributes` (list of `AttributeInfo`),
`constraints`, `source_file`. Literal attribute values like `voltage = 48.0`
become design attributes -- user-configurable inputs in the generated pipeline.

### 4. Hierarchy Data (HierarchyExtractionResult)

The hierarchy resolver (`hierarchy_resolver.py`) extracts structural patterns
beyond simple attributes. `extract_hierarchy_data()` returns: `redefinitions`,
`design_overrides`, `multiplicities`, `aggregation_expressions`,
`part_usage_names`, `usage_type_map`, `warnings`.

---

## Binding Types

Each parameter binding on a CalcUsageData is a `BindingInfo` classified by
`BindingType`. All five types:

**CHAIN** -- dotted path to another element's attribute:
```sysml
in capacity = solar_array.rated_capacity;
```
`BindingInfo(param_name="capacity", source_path="solar_array.rated_capacity", binding_type=CHAIN)`

**REFERENCE** -- direct reference to a sibling/ancestor attribute:
```sysml
in capacity = rated_capacity;
```
`BindingInfo(param_name="capacity", source_path="SolarLib::SolarBattery::rated_capacity", binding_type=REFERENCE)`

**LITERAL** -- hardcoded constant:
```sysml
in unit_cost = 4.5;
```
`BindingInfo(param_name="unit_cost", source_path="4.5", binding_type=LITERAL, literal_value=4.5)`

**EXPRESSION** -- computed value (OperatorExpression in the AST):
```sysml
in adjusted_cost = base_cost * inflation_factor;
```
`BindingInfo(param_name="adjusted_cost", source_path=None, binding_type=EXPRESSION, expression_ast=<node>)`

**UNBOUND** -- no binding expression at all. These appear in
`CalcUsageData.unbound_params` as bare parameter names, and also as
`BindingInfo` objects with `binding_type=UNBOUND` in the `bindings` list.
They become entry point candidates -- user-provided inputs in the generated
pipeline.

---

## Redefinitions (RedefinitionData)

A `:>>` redefinition overrides an inherited attribute on a PartDef. Three types:

**LITERAL**: `:>> wattage = 400.0;`
```python
RedefinitionData(owning_part_qn="Lib__PV_Module", attribute_name="wattage",
                 redefinition_type=RedefinitionType.LITERAL, literal_value=400.0)
```

**CHAIN**: `:>> total_capex = capital_cost;`
```python
RedefinitionData(owning_part_qn="Lib__Solar_Array", attribute_name="total_capex",
                 redefinition_type=RedefinitionType.CHAIN, source_path="capital_cost")
```

**EXPRESSION**: `:>> capital_cost = sum(pv_module.capital_cost) + bos_cost;`
```python
RedefinitionData(owning_part_qn="Lib__Solar_Array", attribute_name="capital_cost",
                 redefinition_type=RedefinitionType.EXPRESSION,
                 expression_text="sum(pv_module.capital_cost) + bos_cost")
```

Deep-path overrides on design PartUsages (e.g., `:>> pv_module.wattage = 400.0`)
are captured separately in `design_overrides` with `is_deep_path=True` and
`target_path=["pv_module", "wattage"]`.

---

## Aggregation Data (SumTerm, SingletonTerm, LocalTerm)

When an EXPRESSION redefinition contains `sum()`, the hierarchy resolver
decomposes it into typed terms. Given this SysML:
```sysml
part def Solar_Array {
    attribute module_count : Integer = 20;
    part pv_module : PV_Module [module_count];
    part inverter : Inverter;
    attribute misc_hardware_cost : Real;
    :>> capital_cost = sum(pv_module.capital_cost) + inverter.install_cost
                       + misc_hardware_cost;
}
```

The resolver produces an `AggregationExpressionData` with:
- `transformed_expression`: `"((module_count * pv_module.capital_cost) + inverter.install_cost) + misc_hardware_cost"`
- `sum_terms`: `[SumTerm(part_usage_name="pv_module", attribute_name="capital_cost", multiplicity_attr="module_count", multiplicity_count=20)]`
- `singleton_terms`: `[SingletonTerm(source_path="inverter.install_cost")]`
- `local_terms`: `[LocalTerm(attribute_name="misc_hardware_cost")]`
- `input_channels`: `["pv_module.capital_cost", "inverter.install_cost"]`
- `entry_points`: `["module_count"]`

The three term types:
- **SumTerm**: `sum(child.attr)` over a multiplicity child, transformed to `count_attr * child.attr`.
- **SingletonTerm**: `child.attr` to a singleton child PartUsage. Direct channel wire.
- **LocalTerm**: Attribute on the PartDef itself. Entry point or sibling wire.

Multiplicity is extracted separately as `MultiplicityData`:
```python
MultiplicityData(part_usage_name="pv_module", owning_part_def_qn="Lib__Solar_Array",
                 count=20, count_attribute_name="module_count", default_value=20)
```

---

## Expression Compiler

The expression compiler (`expression_compiler.py`) converts raw SysIDE AST
nodes from calc def outputs into Python strings. Three phases:

1. `build_expression_ast()` converts syside AST to a clean `ExpressionAST` IR
   (binary tree of operators, literals, input/intermediate references).
2. `compile_expression()` recurses the IR to emit Python: `(inputs.capacity * inputs.unit_cost)`.
3. Each output gets a `Compilability` verdict: `FULLY_COMPILABLE`,
   `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, or `UNKNOWN`.

The orchestrator `compile_calc_def()` handles topological sorting of outputs
(when one output depends on another) and discovers undeclared intermediates
(members that are neither inputs nor outputs but appear in expressions).
