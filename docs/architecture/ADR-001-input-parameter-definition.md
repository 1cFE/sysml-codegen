# ADR-001: Input Parameter Definition and Classification

## Status
**Accepted** - 2025-12-08

## Context

Multiple bugs and ongoing confusion in the codegen system stem from an unclear definition of what constitutes an "input parameter." The codebase evolved organically with overlapping code paths and a 4-type taxonomy that conflates orthogonal concerns.

This ADR establishes the definitive specification for input parameters to eliminate ambiguity and guide future development.

## Decision

### Core Principle

> **An input parameter is any literal value in a design file that the user may want to override for a scenario.**

Input parameters are:
- **Scenario-relative**: Determined by backtracing from target outputs
- **User-configurable**: Values the user provides to run a simulation
- **Design-scoped**: Only values in design files (not library algorithm constants)

### Input Parameter Sources (3 Types)

#### Type 1: LIBRARY DEFAULT
- **Location**: `calc def` input attribute in `library/`
- **Condition**: Calc usage does NOT bind this input
- **Value Source**: Default value in calc def declaration
- **Example**:
  ```sysml
  // library/power_balance.sysml
  calc def HeatingWallPlugPower {
      in heating_efficiency : Real = 0.5;  // ← DEFAULT, exposed if not bound
  }

  // design/physics.sysml
  calc wall_plug : HeatingWallPlugPower {
      in delivered_power = system.delivered_power;
      // heating_efficiency NOT bound → uses library default → IS input param
  }
  ```

#### Type 2: DESIGN ATTRIBUTE
- **Location**: `attribute` declaration in `design/` part
- **Condition**: Has literal value (not expression, not bound to calc output)
- **Value Source**: Literal in attribute declaration
- **Example**:
  ```sysml
  // design/physics.sysml
  part catf_physics {
      attribute p_fusion : Real = 2600.0;     // ← IS input param
      attribute eta_thermal : Real = 0.46;    // ← IS input param
      attribute p_net : Real = net_calc.p_net; // ← NOT input (bound to output)
  }
  ```

#### Type 3: USAGE LITERAL
- **Location**: Calc usage binding in `design/`
- **Condition**: Binding uses literal value (not attribute reference)
- **Value Source**: Literal in binding expression
- **Example**:
  ```sysml
  // design/magnets.sysml
  calc cryo_load : MagnetCryogenicLoad {
      in p_neutron = 2079.41;  // ← IS input param (literal binding)
      in b_field = tf_system.field_at_coil;  // ← NOT input (traces to attr)
  }
  ```

### What is NOT an Input Parameter

#### In Library (`library/`)
| Case | Example | Why NOT |
|------|---------|---------|
| Formula constants | `* 8760.0` (hours/year) | Algorithm constant, not configurable |
| Output attributes | `out revenue : Real` | Computed, not provided |
| Intermediate locals | `attribute temp = x * 0.5` | Internal calculation |
| Constraint bounds | `x > 0 and x < 100` | Validation logic |
| ANY hardcoded values | All literals in library | Library = algorithm, not configuration |

#### In Design (`design/`)
| Case | Example | Why NOT |
|------|---------|---------|
| Bound to calc output | `attr p_net = calc.output` | Computed value |
| Expression result (computed) | `attr total = a + b` | The expression result (`total`) is computed, not user-provided. However, its inputs (`a`, `b`) MAY be DESIGN_ATTRIBUTE entry points if they are literal-valued sibling attributes on the same part. See ADR-004 (Computed Attribute Pipeline Integration) and ADR-005 (Computed Attribute Classification) for details on how FORMULA computed attributes generate synthetic pipeline modules whose literal inputs become entry points. |
| Attribute without value | `attr future : Real;` | Must be bound elsewhere |
| Binding to calc output | `in x = other_calc.y` | Wiring, not a value |
| Binding to attribute | `in x = part.attr` | Wiring (traces to source attr) |

### Supported Value Types

Input parameters may be of the following types (extensible):

| Type | SysML | Python | Example |
|------|-------|--------|---------|
| Real | `Real` | `float` | `= 2600.0` |
| Integer | `Integer` | `int` | `= 12` |
| String | `String` | `str` | `= "HTS_CICC"` |
| Boolean | `Boolean` | `bool` | `= true` |

**Future expansion**: Enums, arrays, structured types as needed.

### Unit Handling

Units (e.g., `= 20 [K]`) are **metadata only** for now:
- The numeric value (20) is extracted as the parameter value
- The unit ([K]) is stored as metadata/documentation
- **Future work**: Automatic unit conversion system

### Namespace vs Grouping (Orthogonal Concepts)

**Critical Clarification**: Namespace and grouping are **separate concerns**:

| Concept | Purpose | Example |
|---------|---------|---------|
| **Namespace** | Globally unique identifier | `CATFMFEMagnets__catf_pf3__current` |
| **Grouping** | File organization for users | `magnets_params.json` |

A parameter's namespace ensures uniqueness; its grouping determines which JSON file it lives in. These do NOT need to match.

### Namespace Format

**Format**: Full SysML qualified path with `__` (double underscore) as hierarchy separator.

**Why double underscore**:
- Valid Python identifier
- Clearly shows hierarchy levels
- Can be parsed back (split on `__`)
- Avoids conflicts with names containing single `_`

#### Namespace by Parameter Type

**Type 1 - Library Default** (namespace by USAGE location, not definition):
```sysml
// library/power_balance.sysml
package FusionPhysics {
    calc def HeatingWallPlugPower {
        in heating_efficiency : Real = 0.5;
    }
}

// design/physics.sysml
package CATFMFEPhysics {
    part catf_physics {
        calc wall_plug : HeatingWallPlugPower {
            // heating_efficiency not bound → uses library default
        }
    }
}
```
**Namespace**: `CATFMFEPhysics__catf_physics__wall_plug__heating_efficiency`
**Rationale**: The parameter's identity is where it's USED, not where it's defined. The calc def is just the source of the default value.

**Type 2 - Design Attribute**:
```sysml
// design/magnets.sysml
package CATFMFEMagnets {
    part catf_tf_system {
        attribute fraction_insulation : Real = 0.0;
    }
    part catf_pf1 {
        attribute fraction_insulation : Real = 0.0;
    }
}
```
**Namespaces**:
- `CATFMFEMagnets__catf_tf_system__fraction_insulation`
- `CATFMFEMagnets__catf_pf1__fraction_insulation`

**Type 3 - Usage Literal**:
```sysml
// design/magnets.sysml
package CATFMFEMagnets {
    part catf_tf_system {
        calc cryo_load : MagnetCryogenicLoad {
            in p_neutron = 2079.41;
        }
    }
}
```
**Namespace**: `CATFMFEMagnets__catf_tf_system__cryo_load__p_neutron`

#### Arbitrary Nesting Depth

SysML v2 supports arbitrary part nesting. The namespace captures the **full hierarchy**:
```sysml
package CATFMFEMagnets {
    part catf_tf_system {
        part inner_coil {
            part winding_pack {
                attribute current : Real = 1.0e6;
            }
        }
    }
}
```
**Namespace**: `CATFMFEMagnets__catf_tf_system__inner_coil__winding_pack__current`

### Grouping Strategy

**Grouping** determines which JSON file a parameter lives in. Grouping is by **design file**:

| Design File | JSON File | Schema Class |
|-------------|-----------|--------------|
| `magnets.sysml` | `magnets_params.json` | `MagnetsParams` |
| `physics.sysml` | `physics_params.json` | `PhysicsParams` |

**All parameter types** from a design file go in that file's group:
- Design attributes from `magnets.sysml` → `magnets_params.json`
- Usage literals from `magnets.sysml` → `magnets_params.json`
- Library defaults used in `magnets.sysml` → `magnets_params.json`

### Combined Example

```json
// magnets_params.json
{
  "CATFMFEMagnets__catf_tf_system__fraction_insulation": 0.0,
  "CATFMFEMagnets__catf_tf_system__manufacturing_factor": 5.0,
  "CATFMFEMagnets__catf_pf1__fraction_insulation": 0.0,
  "CATFMFEMagnets__catf_pf1__manufacturing_factor": 2.0,
  "CATFMFEMagnets__catf_tf_system__cryo_load__p_neutron": 2079.41,
  "CATFMFEMagnets__catf_tf_system__cryo_load__carnot_efficiency": 0.3
}
```

```python
class MagnetsParams(BaseModel):
    CATFMFEMagnets__catf_tf_system__fraction_insulation: float = 0.0
    CATFMFEMagnets__catf_tf_system__manufacturing_factor: float = 5.0
    CATFMFEMagnets__catf_pf1__fraction_insulation: float = 0.0
    CATFMFEMagnets__catf_pf1__manufacturing_factor: float = 2.0
    CATFMFEMagnets__catf_tf_system__cryo_load__p_neutron: float = 2079.41
    CATFMFEMagnets__catf_tf_system__cryo_load__carnot_efficiency: float = 0.3
```

**Rationale**:
- Full namespaces ensure global uniqueness
- File-based grouping keeps related params together for user convenience
- Users configure "the magnets subsystem" in one file

### Validation Errors

The following are **model validation errors**, not input parameters:

| Error | Condition | Resolution |
|-------|-----------|------------|
| Unbound input without default | Library calc def input has no default AND usage doesn't bind it | Add default to calc def OR add binding in usage |
| Binding to undefined attribute | Usage binds to attribute that doesn't exist | Fix the binding path |
| Attribute without value, not bound | Design attribute declared but never assigned | Assign value OR bind to source |

### Scenario-Relative Determination

Input parameters are determined **per scenario** via backtracing:

1. Start with scenario target output(s)
2. Trace dependencies backward through calc usages
3. Collect all leaf values (not produced by any calc)
4. These are the input parameters for THIS scenario

Different scenarios may have different input parameter sets.

## Consequences

### Positive
1. **Clear definition** eliminates ambiguity in codegen
2. **Namespacing** preserves semantic distinctions between parts
3. **Scenario-relative** approach generates minimal parameter sets
4. **Validation errors** catch model issues early

### Negative
1. **More parameters** - Proper namespacing increases parameter count (e.g., 60+ for magnets)
2. **Longer names** - `catf_tf_system_manufacturing_factor` vs `manufacturing_factor`
3. **Migration** - Existing code using simple deduplication must be updated

### Implementation Requirements

#### Phase 1: Data Model Enhancement
1. **Add `qualified_name` to `CalcUsageData`** - Store full path from AST element
2. **Add `qualified_name` to `DesignAttributeData`** - Store full path from AST element
3. **Preserve AST element references in `BindingInfo`** - Stop discarding structured data

#### Phase 2: Namespace Implementation
4. **Update `_derive_from_design_attributes()`** - Use `qualified_name` for parameter namespace
5. **Update `_build_binding_index()`** - Use `qualified_name` for binding-traced params
6. **Update `_build_literal_index()`** - Use `qualified_name` for literal-bound params
7. **Update `_build_unbound_index()`** - Use calc usage `qualified_name` for library defaults

#### Phase 3: Transitive Binding Resolution and Cleanup

**Research Reference**: `project/research/20251219-192757_adr001-phase2-nulls-and-design-evaluation.md`

**Problem Statement**: Phase 2 revealed that bindings to calc outputs via design attributes (e.g., `in p_coils = catf_tf_system.cooling_power` where `cooling_power = cryo_load.cooling_power`) fail to resolve. These are incorrectly marked as entry points with `null` defaults, when they should be recognized as wiring to calc outputs.

**Requirements**:

8. **Implement transitive binding resolution in `DependencyBacktracker._resolve_binding_to_usage()`**
   - WHEN a binding resolves to a design attribute (not a calc output)
   - AND that design attribute is ITSELF bound to another source
   - THEN follow the chain transitively until reaching a calc output OR a true entry point (literal value)
   - Example: `p_coils → catf_tf_system.cooling_power → cryo_load.cooling_power → MagnetCryogenicLoad (CALC)`

9. **Reclassify binding-traced parameters**
   - Bindings to calc outputs SHALL NOT be entry points
   - They are dependency graph wiring, not user-provided inputs
   - Only leaf values (literals, unbound library defaults) are true entry points

10. **Remove null-valued calc-output bindings from generated JSON**
    - Parameters bound to calc outputs SHALL NOT appear in `*_params.json` files
    - These are computed values, not configurable inputs

11. **Remove transitional `collect_entry_point_attributes()` from `parameter_group_derivation.py`**
    - Lines 488-537 contain a Phase 2 transitional function that returns simple names for backward compatibility
    - This function is not used in the main pipeline and creates potential collision risk
    - Remove in favor of the canonical `entry_point.py` version or qualified-name-only lookups

12. **Update YAML generation** - Reference params by full namespace (carried from original Phase 3)

**Test Requirements**:

13. **Test: Cross-file binding to calc output resolves correctly**
    ```python
    def test_binding_through_design_attr_to_calc_output():
        """Binding via design attribute to calc output should NOT be entry point.

        Example: in p_coils = catf_tf_system.cooling_power
        Where: cooling_power = cryo_load.cooling_power (calc output)
        Expected: cryo_load added to required_usages, p_coils NOT in entry_points
        """
    ```

14. **Test: Transitive chain resolution**
    ```python
    def test_transitive_binding_chain():
        """Multi-hop binding chains should resolve completely.

        Chain: calc_input → design_attr_1 → design_attr_2 → calc_output
        Expected: Final calc added to dependencies, intermediate attrs not entry points
        """
    ```

15. **Test: True entry points still identified correctly**
    ```python
    def test_true_entry_points_identified():
        """Leaf literals and unbound library defaults should be entry points.

        - Literal in design attr: p_fusion = 2600.0 → IS entry point
        - Unbound library default: heating_efficiency → IS entry point
        - Binding to calc output: p_coils → cooling_power → NOT entry point
        """
    ```

16. **Test: No null values for calc-output bindings in JSON**
    ```python
    def test_no_null_calc_output_bindings_in_json():
        """Generated JSON should not contain null values for calc-output bindings.

        Parameters like p_coils, p_heating, p_pumps that are bound to calc outputs
        should not appear in the JSON at all (they are wiring, not inputs).
        """
    ```

#### Phase 4: Validation
17. **Add duplicate namespace detection** - Fail if same namespace appears twice
18. **Add validation for unresolved bindings** - Fail if binding target doesn't exist

## References

- `project/research/20251219-192757_adr001-phase2-nulls-and-design-evaluation.md` - Phase 3 requirements research
- `project/research/20251208-172130_json-default-value-extraction-bug.md`
- `project/research/20251208-172236_schema-generation-regression.md`
- `project/research/20251208-152235_input-parameter-tracing-methodology.md`
- `project/architecture/codegen_architecture.md`
- `project/backlog/epic_codegen_v2.md`

## Changelog

| Date | Change |
|------|--------|
| 2026-02-09 | **Clarification**: Computed attribute expression inputs may be entry points. The expression result is NOT an entry point, but its literal-valued sibling inputs MAY be DESIGN_ATTRIBUTE entry points. See ADR-004 and ADR-005 for FORMULA computed attribute handling. |
| 2025-12-19 | **Phase 3 Requirements Added** - Transitive binding resolution, test requirements, cleanup of transitional code (based on research into null value root causes) |
| 2025-12-19 | **Phase 2 Complete** - All indices now use qualified names; backtracker produces qualified names at source; collision problem solved (e.g., 9 `fraction_insulation` params now uniquely identified) |
| 2025-12-08 | Initial version - established definitive input parameter definition |
