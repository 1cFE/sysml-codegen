# 20 -- Module Registry Generation: Import Paths and Type Derivation

## What the Registry Does

The generated `__init__.py` registers all pipeline modules with TEAx so the
runtime can discover and instantiate them. It contains:

1. **Import statements** for every module class
2. **`create_registry()`** call with all module classes
3. **`module_type_override`** mapping class names to namespaced types
4. **`CUSTOM_SCHEMA_TYPES`** for entry point and exit point type registration

**Source**: `generation/registry.py:65-156`, template `registry_function.py.jinja2`.
**CLI entry**: `cli/__init__.py:737-770` (`_generate_registry()`).

---

## Module Type Derivation

Every module needs a `module_type` string (namespaced PascalCase) and a
corresponding Python import path. Both derive from a SysML qualified name.

### For CalcUsage Modules

Input: `CalculationDefinitionData.qualified_name` (e.g., `"SolarBatteryLibrary::BatteryPackCostCalc"`)

```
SysMLQualifiedName("SolarBatteryLibrary::BatteryPackCostCalc")
  package_segments = ["SolarBatteryLibrary"]
  element_name = "BatteryPackCostCalc"

ModuleType:
  namespace = "solarbatterylibrary"
  class_name = "BatteryPackCostCalcModule"
  module_type = "solarbatterylibrary.BatteryPackCostCalcModule"

PythonModulePath:
  directory = "solarbatterylibrary"
  filename = "batterypackcostcalc"
  full_path = "solarbatterylibrary/batterypackcostcalc.py"

Import: from {package}.modules.solarbatterylibrary.batterypackcostcalc
         import BatteryPackCostCalcModule
```

### For Aggregation Modules (No CalcDef)

Aggregation modules have no `CalculationDefinitionData`. A synthetic SysML QN
is constructed from the owning PartDef and attribute name:

```python
# registry.py:126
sysml_qn = f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}"
```

Input: `owning_part_qn="SolarBatteryLibrary::Solar_Array"`, `attribute_name="capital_cost"`

```
Synthetic QN: "SolarBatteryLibrary::Solar_Array::capital_cost"
  package_segments = ["SolarBatteryLibrary", "Solar_Array"]
  element_name = "capital_cost"

ModuleType:
  namespace = "solarbatterylibrary.solar_array"
  class_name = "Capital_CostModule"
  module_type = "solarbatterylibrary.solar_array.Capital_CostModule"

PythonModulePath:
  directory = "solarbatterylibrary/solar_array"
  filename = "capital_cost"
  full_path = "solarbatterylibrary/solar_array/capital_cost.py"

Import: from {package}.modules.solarbatterylibrary.solar_array.capital_cost
         import Capital_CostModule
```

### For Computed Attribute Modules

Same as aggregation: synthetic QN from `owning_part_qn::attribute_name`.
Handled at `registry.py:104-121`.

---

## The Derivation Functions

**File**: `core/identifier_types.py`

```python
class SysMLQualifiedName:
    """Parse 'Lib::Part::element' into segments."""
    package_segments: list[str]   # All but last
    element_name: str             # Last segment

class ModuleType:
    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "ModuleType":
        namespace = ".".join(s.lower() for s in sqn.package_segments)
        class_name = f"{sqn.element_name}Module"
        return cls(f"{namespace}.{class_name}" if namespace else class_name)

class PythonModulePath:
    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "PythonModulePath":
        directory = "/".join(s.lower() for s in sqn.package_segments)
        return cls(directory, sqn.element_name.lower())

    @property
    def import_path(self) -> str:
        """Convert to Python import path (dots not slashes)."""
        return self.full_path.replace("/", ".").removesuffix(".py")
```

---

## Import Statement Construction

**File**: `registry.py:197-238` (`_generate_import_statements()`)

For each module (CalcUsage, computed attribute, aggregation):

```python
sqn = SysMLQualifiedName(qualified_name)
python_path = PythonModulePath.from_sysml(sqn)
class_name = f"{calc_def.name}Module"  # or derive_module_type().split(".")[-1]
import_module = f"{package_name}.modules.{python_path.import_path}"
# Result: "from {package}.modules.{path} import {ClassName}"
```

---

## Name Collision Risk

Module **names** (EQN-based, e.g., `design__plant__solar_array__capital_cost`)
are globally unique. But **class names** can collide:

```
Solar_Array   → capital_cost → Capital_CostModule
Battery_Pack  → capital_cost → Capital_CostModule  (same class name!)
PV_Module     → capital_cost → Capital_CostModule  (same class name!)
```

**Current mitigation**: Each module lives in its own file under a namespaced
directory. Python imports disambiguate via module path:

```python
from pkg.modules.solarbatterylibrary.solar_array.capital_cost import Capital_CostModule
from pkg.modules.solarbatterylibrary.battery_pack.capital_cost import Capital_CostModule
```

**Limitation**: The `module_type_override` dict in the registry uses class names
as keys. If two modules share a class name, the last one wins. The current
codebase avoids this because aggregation attributes typically have different
names within the same scope, but no collision detection exists.

---

## Template Rendering

**Template**: `registry_function.py.jinja2`

```python
def {{ function_name }}():
    return create_registry(
        [
            {%- for module in all_modules %}
            {{ module.class_name }},
            {%- endfor %}
        ],
        module_type_override={
            {%- for module in all_modules %}
            {{ module.class_name }}: "{{ module.module_type }}",
            {%- endfor %}
        },
    )
```

Exit point types (e.g., `Float`) are added to `CUSTOM_SCHEMA_TYPES` if any
single-output modules exist. See `_collect_exit_point_primitive_types()` at
`registry.py:175-195`.

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `SysMLQualifiedName` | `core/identifier_types.py` | Parse `::` separated QN |
| `ModuleType` | `core/identifier_types.py` | Namespaced PascalCase type |
| `PythonModulePath` | `core/identifier_types.py` | File path for imports |
| `CalculationDefinitionData` | `extraction/data_models.py` | CalcDef with QN |
| `ScopedAggregationData` | `extraction/data_models.py` | Aggregation with owning_part_qn |
| `ComputedAttributeData` | `extraction/data_models.py` | Computed attr with owning_part_name |
