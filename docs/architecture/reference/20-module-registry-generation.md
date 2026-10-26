# 20 -- Module Registry Generation: Import Paths and Type Derivation

## What the Registry Does

The generated `__init__.py` registers all pipeline modules with TEAx so the
runtime can discover and instantiate them. It contains:

1. **Import statements** for every module class
2. **`create_registry()`** call with all module classes
3. **`module_type_override`** mapping class names to namespaced types
4. **`CUSTOM_SCHEMA_TYPES`** for entry point and exit point type registration

**Source**: `generation/registry.py` (`generate_registry()`), template `registry_function.py.jinja2`.

---

## Design Constraints

Two key constraints shaped the registry design:

**Import path consistency**: Aggregation module import paths must use
design-scoped EQNs (`module_eqn`), not library-scoped QNs (`owning_part_qn`).
Library-based paths (e.g., `solarbatterylibrary.solar_array.capital_cost`)
do not match the actual filesystem, where files live under the design namespace
(e.g., `solarbatterydesign.solar_battery_plant.solar_array.capital_cost`).
The registry derives all paths from `module.name` (the design-scoped EQN)
to guarantee consistency with the generated module files.

**Class name collisions**: When multiple assemblies share identically-named
aggregation attributes (e.g., `capital_cost` on 4 different assemblies),
the resulting class names collide (`Capital_CostModule` appears 4 times).
Since `module_type_override` is a dict keyed by class name, unresolved
collisions cause silent overwrites. The registry uses aliased imports to
disambiguate (see `_resolve_class_name_collisions()` in `generation/registry.py`).

The alias keys on the **parent** segment only, so two different module types with the same class name and parent but different grandparents (e.g. `a.pump.Pump` and `b.pump.Pump`) alias identically. After aliasing, the registry re-checks uniqueness and **fails fast** on any residual collision (REQ-REG-08), before the output tree is touched. The committed fixture `tests/fixtures/refusal_cases/output-naming__registry_class_collision` (formulas `a::Site::t` and `b::Site::t`) is refused this way. Each import line is rendered from its own registry entry, so an alias always lands on the import of the file that defines that class (this closed `[SC11-IMPORT-REWRITE]`, where a substring search could alias the wrong line).

**Class identity: one class per module type.** A formula or rollup module's `module_type` comes from the definition feature that owns it, so every copy of that definition (`sub[0].capital_cost`, `sub[1].capital_cost`, or two named parts `a : Sub; b : Sub`) has the same module type. The registry registers each module type once, as it always did for calc defs; each copy keeps its own pipeline entry, inputs and output channel. TEAx requires this: it refuses a module type registered twice.

- **Same shape, one class.** Copies whose modules are equal apart from their occurrence fields (`resolution/models.py` `class_signature`) share one class, one file and one stencil.
- **Different shapes, one class per shape.** When copies differ (`a : Sub` sums three leaves, `b : Sub { part :>> leaf[2]; }` sums two), projection splits them (`elaboration/project.py` `_shape_split_module_types`): each distinct shape takes the module type of its first copy's occurrence path, by module name (`p.top.a.capital_costModule`, `p.top.b.capital_costModule`). Identical rows each holding such copies still share one class per shape.
- **Named and placed by the first copy.** A rollup class's file is its first copy's path (`modules/p/top/sub_0/capital_cost.py` for `Sub[2]`; no `sub_1` file is written). Renaming or removing that copy moves the class file and its stencil. These stencils are auto-implemented, so nothing handwritten is lost. A formula class's file is the definition's path, as before.
- **Remaining limit.** Two different shapes whose first copies have the same part name under different parents (`x.a` with three leaves, `y.a` with two) alias to one name and are refused with `REGISTRY_CLASS_NAME_COLLISION` (`tests/fixtures/repeated_rollup/divnamed`; backlog `[REPEATED-ROLLUP-SHAPE-ALIAS-LIMIT]`). Renaming one of the two parts builds it.

The module and stencil writers (`cli/emit.py`), the module template's own path (`generation/modules.py`), the duplicate-path preflight and the registry's import lines read a module's file path from one function, `generation/module_paths.py` `module_python_path`, and all four iterate the class owners (`generation/registry.py` `class_owners`), so every class file written is imported and every import names a written file. The stencil template's import path (`generation/stencils.py` `_get_module_sysml_qn`) is still worked out separately and gives the same path.

**Graph-derived schema authority**: The immutable `ComputationGraph` is the only account of root
outputs. `required_exit_point_wrapper_types()` walks that graph, validates every root token, and
returns the stable, de-duplicated wrapper set. `generate_registry()` and every exported alias take
the same four arguments; none accepts a caller-supplied type set. The baseline registry collector
could raise an untyped `RuntimeError` while consuming a fifth caller argument. The replacement raises
the typed `CodeGenerationError` code `EXIT_POINT_TYPE_UNSUPPORTED`, naming the token, module, output,
and source location before the public command changes the output tree.

---

## Requirements

| ID | Requirement | Rationale | Verified by |
|----|-------------|-----------|-------------|
| REQ-REG-01 | Aggregation module import paths SHALL use design-scoped EQN (`module_eqn`), not library QN (`owning_part_qn`) | Path consistency | Import paths match filesystem: `from {pkg}.modules.{design_path} import {Class}` |
| REQ-REG-02 | Import paths in registry SHALL match actual filesystem paths generated by CLI | Path consistency | `import {path}` succeeds for every module in registry |
| REQ-REG-03 | Class names in `module_type_override` dict SHALL be globally unique | Dict key uniqueness | `len(dict.keys()) == len(all_modules)` |
| REQ-REG-04 | When class names collide, registry SHALL use aliased imports (`import X as Assembly_X`) | Dict key uniqueness | No two modules share the same unaliased class name in registry |
| REQ-REG-05 | CalcUsage, computed attribute, and aggregation modules SHALL all derive paths from design-scoped qualified names | Path consistency | Same `SysMLQualifiedName` derivation for all three module types |
| REQ-REG-06 | `CUSTOM_SCHEMA_TYPES` SHALL include the stable, de-duplicated wrapper set derived inside the exported registry seam from every root output in the graph | TEAx integration | `tests/unit/test_registry_generation.py` covers no-root, one, repeated, and multiple root types and proves every alias has the same four-argument surface |
| REQ-REG-07 | Registry generation SHALL detect and report name collisions before rendering | Fail-fast diagnostics | Warning emitted when two modules produce same class name |
| REQ-REG-08 | After parent-segment aliasing, registry SHALL re-check class-name uniqueness and fail fast on any residual collision | Fail-fast diagnostics | `_residual_collisions()` reports two entries that alias identically (same class + parent, different grandparents), and the generation boundary refuses before writing; conformance: `test_sc11_recheck`, `test_public_authority_switch.py::test_a_registry_class_name_collision_refuses_before_the_writer_runs` |
| REQ-REG-09 | A root exit whose type token is outside `{float,int,str,bool}` SHALL refuse before output mutation as the graph-derived `CodeGenerationError` code `EXIT_POINT_TYPE_UNSUPPORTED`, naming the token, module identity, output identity, file:line, and public status 1 | Fail-before-mutate diagnostic | `tests/conformance/test_generation_exit_type_preflight.py` proves the complete sentinel tree stays byte-identical, direct generation refuses by the same typed error, and no exported alias accepts a caller type-set parameter |

`_preflight_exit_point_types` and every direct registry entry call the same graph operation,
`required_exit_point_wrapper_types`. The CLI call happens before the output directory is cleared;
the registry call happens before rendering. The operation owns both the supported token map and the
typed refusal, so there is no caller-owned set, second policy table, or late warn/omit branch.

---

## Module Type Derivation

Every module needs a `module_type` string (namespaced PascalCase) and a
corresponding Python import path. Both derive from a SysML qualified name
via three classes in `core/identifier_types.py`:

```python
@dataclass(frozen=True)
class SysMLQualifiedName:
    """Parse 'Lib::Part::element' into segments."""
    value: str  # e.g., "Lib::Part::element"

    @property
    def package_segments(self) -> list[str]:  # All but last
        return self.value.split("::")[:-1]

    @property
    def element_name(self) -> str:            # Last segment
        return self.value.split("::")[-1]

@dataclass(frozen=True)
class ModuleType:
    value: str

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "ModuleType":
        namespace = ".".join(sanitize_name(s).lower() for s in sqn.package_segments)
        class_name = f"{sanitize_name(sqn.element_name)}Module"
        return cls(f"{namespace}.{class_name}" if namespace else class_name)

@dataclass(frozen=True)
class PythonModulePath:
    directory: str
    filename: str

    @classmethod
    def from_sysml(cls, sqn: SysMLQualifiedName) -> "PythonModulePath":
        directory = "/".join(sanitize_name(s).lower() for s in sqn.package_segments)
        return cls(directory, sanitize_name(sqn.element_name).lower())
```

These classes are pure transformations -- correctness depends entirely on
feeding them the right QN (design-scoped EQN, not library-scoped QN). Each
segment passes through `sanitize_name()` before lowercasing (Item 5 /
REQ-NC-08), so a quoted SysML name emits a valid identifier instead of
leaking quotes into class names or file paths.

---

## Concrete Example: Design-Scoped vs Library-Scoped Paths

**Aggregation**: `solar_array` assembly's `capital_cost` attribute.

```
Design-scoped (correct -- uses module_eqn):
  Input QN: "SolarBatteryDesign::solar_battery_plant::solar_array::capital_cost"
  → SysMLQualifiedName: segments=["SolarBatteryDesign","solar_battery_plant","solar_array"], elem="capital_cost"
  → PythonModulePath: "solarbatterydesign/solar_battery_plant/solar_array/capital_cost.py"
  → Import: from pkg.modules.solarbatterydesign.solar_battery_plant.solar_array.capital_cost import Capital_CostModule

Library-scoped (incorrect -- uses owning_part_qn):
  Input QN: "SolarBatteryLibrary::Solar_Array::capital_cost"
  → SysMLQualifiedName: segments=["SolarBatteryLibrary","Solar_Array"], elem="capital_cost"
  → PythonModulePath: "solarbatterylibrary/solar_array/capital_cost.py"
  → Import: from pkg.modules.solarbatterylibrary.solar_array.capital_cost import Capital_CostModule
  → FAILS: file lives in solarbatterydesign/ not solarbatterylibrary/
```

The registry derives the aggregation QN from `module.name.replace("__", "::")`
(the design-scoped EQN), ensuring the import path matches the generated file location.

---

## Name Collision Example

5 aggregation attributes (`capital_cost`, `raw_material_cost`, `fabrication_cost`,
`installation_cost`, `idiot_index`) across 4 assemblies produce 20 modules
but only 5 unique class names:

```
solar_array::capital_cost      → Capital_CostModule
battery_system::capital_cost   → Capital_CostModule  (collision!)
site_infra::capital_cost       → Capital_CostModule  (collision!)
plant::capital_cost            → Capital_CostModule  (collision!)
```

Since `module_type_override` is a dict with class name as key,
collisions are resolved via aliased imports (REQ-REG-04):

```python
from pkg.modules...solar_array.capital_cost import Capital_CostModule as SolarArray_Capital_CostModule
from pkg.modules...battery_system.capital_cost import Capital_CostModule as BatterySystem_Capital_CostModule
```

---

## Template Rendering

**Template**: `registry_function.py.jinja2`

```python
def {{ function_name }}() -> PipelineModuleRegistry:
    return create_registry(
        [{% for module in all_modules %} {{ module.class_name }}, {% endfor %}],
        module_type_override={
            {% for module in all_modules %}
            {{ module.class_name }}: "{{ module.module_type }}",
            {% endfor %}
        },
    )
```

Per REQ-REG-03, when aliases are used, `module.class_name` must be the
alias (e.g., `SolarArray_Capital_CostModule`), not the original class name.

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `SysMLQualifiedName` | `core/identifier_types.py` | Parse `::` separated QN |
| `ModuleType` | `core/identifier_types.py` | Namespaced PascalCase type |
| `PythonModulePath` | `core/identifier_types.py` | File path for imports |
| `CalculationDefinitionData` | `extraction/data_models.py` | CalcDef with QN |
| `PipelineModule` | `resolution/models.py` | Exact projected calculation, formula, aggregation, constraint, or report module |
| `ModuleOutput` | `resolution/models.py` | Declared output channel and Python type |

---

## Related Documents

- **Upstream**: 07-graph-assembly (retired doc; git history) -- ComputationGraph feeds registry generation
- **Upstream**: 13-aggregation-scoping (retired doc; git history) -- produces ScopedAggregationData with module_eqn
- **Downstream**: [08-generation](08-generation.md) -- registry is one of 6 generated artifacts
- **Related**: [21-pipeline-yaml-generation](21-pipeline-yaml-generation.md) -- pipeline YAML must use matching module types
- **Naming**: [15-naming-conventions](15-naming-conventions.md) -- EQN derivation rules
- **Data models**: [09-data-models](09-data-models.md) -- ScopedAggregationData field definitions
