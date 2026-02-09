# ADR-005: Computed Attribute Classification

## Status
**Accepted** - 2026-02-09

## Context

Phase 1 (EXPR-CODEGEN) built an expression compiler that auto-implements CalcDef outputs as Python code. Phase 2 (ATTR-EXPR) extends codegen to capture attribute-level expressions on PartDefs/PartUsages -- expressions like `attribute area = length * width` that previously required a full CalcDef+CalcUsage ceremony.

SysIDE populates `feature_value_expression` on all PartDef/PartUsage attributes. An ATTR-EXPR spike (Item 1) inventoried attribute expression patterns across 540+ attributes in probe, solar_battery, and CATF models. The findings revealed that attribute expressions fall into distinct categories requiring fundamentally different pipeline treatment. A classification scheme is needed to route each attribute expression to the correct handler.

### Prior Art

The original ATTR-EXPR concept document proposed a 5-way classification: FORMULA, EXPOSE, MIXED, LITERAL, UNRESOLVABLE. Spike findings refined this -- MIXED was never observed in any model, and the EXPOSE category conflated two distinct concerns (pure alias vs. alias-with-arithmetic). This ADR formalizes the refined classification.

## Decision

### Decision 1: Five-Way Classification Scheme

Replace the original classification with a more precise 5-way scheme that splits EXPOSE and drops MIXED.

#### FORMULA -- Arithmetic on sibling attributes

**Definition**: An attribute expression where ALL feature references resolve to sibling attributes on the same PartDef/PartUsage. No `FeatureChainExpression` nodes (no dotted paths to calc outputs or other parts). Supported operators: `+`, `-`, `*`, `/`.

**Pipeline treatment**: Generate a synthetic `PipelineModule` with auto-implemented code. The Phase 1 expression compiler processes the attribute's AST identically to a CalcDef output expression.

**SysML examples (probe fixture)**:

```sysml
part probe_design {
    attribute length : Real = 10.0;      // LITERAL input
    attribute width : Real = 5.0;        // LITERAL input
    attribute height : Real = 3.0;       // LITERAL input
    attribute rate : Real = 12.0;        // LITERAL input

    // FORMULA: simple binary
    attribute area : Real = length * width;

    // FORMULA: 3-term product
    attribute volume : Real = length * width * height;

    // FORMULA: chain -- references another computed attr
    attribute cost : Real = area * rate;

    // FORMULA: multi-hop chain
    attribute marked_up_cost : Real = cost * 1.15;

    // FORMULA: fan-in from two computed attrs
    attribute cost_density : Real = cost / volume;

    // FORMULA: deeply nested, 7 refs
    attribute p_blanket_thermal : Real =
        m_neutron * p_fusion + p_input
        + eta_thermal * (f_pump * eta_pump + f_subsystem)
          * (m_neutron * p_fusion);
}
```

**Compiled output** (verified correct in spike):
```python
area         = (inputs.length * inputs.width)
volume       = ((inputs.length * inputs.width) * inputs.height)
cost         = (inputs.area * inputs.rate)
cost_density = (inputs.cost / inputs.volume)
```

**Real model example** (solar_battery `design.sysml:60`):
```sysml
part solar_battery_plant {
    attribute p_net_mw : Real = 0.008;
    attribute p_net_kw : Real = p_net_mw * 1000.0;   // FORMULA
}
```

**Key finding**: The compiler treats computed attribute references identically to literal attribute references. `cost = area * rate` compiles to `(inputs.area * inputs.rate)` whether `area` is a literal or itself a computed attribute. Chain resolution is entirely a graph-builder concern (topological ordering), not a compiler concern.

#### EXPOSE_PURE -- Single reference to a calc output, no operators

**Definition**: An attribute expression that is a single `FeatureChainExpression` with no surrounding operators. The attribute's value IS the calc output -- pure value forwarding.

**Pipeline treatment**: Channel alias. No synthetic module generated. When something references this attribute, the graph builder resolves through the alias to the upstream calc output channel.

**SysML examples (probe fixture)**:

```sysml
part probe_design {
    calc scale_calc : ScaleCalc { in value = area; }
    calc split : SplitCalc { in value = volume; }

    // EXPOSE_PURE: surface a single calc output as a part-level attribute
    attribute scale_result : Real = scale_calc.result;
    attribute half_vol : Real = split.half;
    attribute quarter_vol : Real = split.quarter;
}
```

**Real model examples** (CATF `physics.sysml:114-122`):
```sysml
part def FusionPlasmaPhysics {
    calc alpha_neutron_split : AlphaNeutronSplitCalc {
        in p_fusion = p_fusion;
    }

    // EXPOSE_PURE: surface calc outputs for downstream wiring
    attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;
    attribute p_neutron_out : Real = alpha_neutron_split.p_neutron;
}
```

**Modeling practice impact**: No change. This IS the existing EXPOSE pattern modelers already use for wiring convenience so that other parts can reference `physics.p_alpha_out` instead of the deeper path `physics.alpha_neutron_split.p_alpha`.

**Why classification matters even though no module is generated**: FORMULA modules may reference EXPOSE attributes as inputs. If `useful_power = p_fusion * thermal_efficiency` and `thermal_efficiency` is an EXPOSE alias for `efficiency_calc.eta_thermal`, the graph builder must resolve `thermal_efficiency` through the alias to the upstream calc output channel. So the classifier must identify EXPOSE attributes to provide wiring context.

#### EXPOSE_COMPUTED -- Calc output reference wrapped in arithmetic

**Definition**: An attribute expression containing BOTH a `FeatureChainExpression` (calc output reference) AND arithmetic operators. This is "EXPOSE + math."

**Pipeline treatment**: **DEFERRED.** Classify and record, but do not generate a module. Log as "not yet supported" if encountered in a real model.

**SysML example (probe fixture)**:

```sysml
part probe_design {
    calc scale_calc : ScaleCalc { in value = area; }

    // EXPOSE_COMPUTED: takes a calc output AND does math on it
    attribute scaled_area : Real = scale_calc.result * 2.0;
}
```

The spike found this produces `unsupported operator: .` because the `FeatureChainExpression` (`scale_calc.result`) hits the compiler's unsupported-node path.

**Status**: No current model uses this pattern. When modelers need post-calc arithmetic today, they create another CalcDef (which Phase 1 auto-implements). The decomposition strategy (resolve FeatureChainExpression to upstream channel, compile remaining expression as FORMULA) is technically tractable but defers implementation complexity until a concrete modeling need arises.

**Workaround**: Create a CalcDef for the adjustment. Phase 1 auto-implements it, so no handwritten `_impl.py` is needed. The overhead is the CalcDef ceremony (~20 lines), not manual implementation.

#### LITERAL -- No expression or pure constants

**Definition**: An attribute with either no expression (just a type declaration) or a pure constant expression (`LiteralRational`, `LiteralInteger`, etc.) with no feature references.

**Pipeline treatment**: Not a computed attribute. Handled by existing extraction as `DesignAttributeData` with `default_value`. May become an entry point via the existing `ParameterGroupDeriver`.

**Examples**:
```sysml
part probe_design {
    attribute length : Real = 10.0;      // LITERAL (constant)
    attribute width : Real = 5.0;        // LITERAL (constant)
    attribute name : String;             // LITERAL (no expression)
}
```

#### UNRESOLVABLE -- References that can't be resolved

**Definition**: An attribute expression with feature references that don't match any sibling attribute or known calc usage on the same part.

**Pipeline treatment**: Log a warning, skip. Do not generate a module.

**Example** (hypothetical):
```sysml
part probe_design {
    // UNRESOLVABLE: 'mystery_value' is not a sibling attribute or calc usage
    attribute broken : Real = length * mystery_value;
}
```

### Classification Summary

| Classification | Generates Module? | Exists in Current Models? | Modeling Practice Change? |
|---------------|-------------------|--------------------------|--------------------------|
| FORMULA | Yes (synthetic, auto-implemented) | Rare (1 instance in solar_battery) | **New option**: write formulas without CalcDefs |
| EXPOSE_PURE | No (channel alias) | Common (19+ in CATF) | **No change**: existing EXPOSE pattern continues |
| EXPOSE_COMPUTED | Deferred | None | **Deferred**: new option for post-calc arithmetic |
| LITERAL | No (existing handling) | Very common | **No change** |
| UNRESOLVABLE | No (warning) | None | **No change** |

### Why MIXED Was Dropped

The original classification had MIXED defined as "references both sibling attributes and calc outputs." The spike found:

1. **Zero MIXED patterns in any real model** across 540 attributes.
2. **The D2 pattern** (`scale_calc.result * 2.0`) was predicted to be MIXED but classified as EXPOSE because the `2.0` is a literal (no feature ref), not a sibling attribute reference.
3. **The MIXED concept conflated two distinct concerns**: "what do the references point to?" and "what operations wrap them?" The EXPOSE_PURE / EXPOSE_COMPUTED split captures the meaningful distinction more precisely.

If a true MIXED pattern appears in a future model (`attr = sibling_a + calc.output`), it would be classified as EXPOSE_COMPUTED (because it contains a FeatureChainExpression + operators) and handled by the same decomposition strategy.

### Decision 2: EXPOSE Handling Strategy

- **EXPOSE_PURE**: Classify and record, but do not generate a module. Provide alias resolution context to the graph builder so that FORMULA modules referencing EXPOSE attributes wire correctly.
- **EXPOSE_COMPUTED**: Classify and record, but defer implementation. Log as "not yet supported" if encountered in a real model.

**Rationale for EXPOSE_PURE not needing a module**: An EXPOSE_PURE attribute like `attribute p_alpha_out = alpha_neutron_split.p_alpha` carries no computation. It's a name alias. Generating a passthrough module would create pipeline overhead (module wrapper, YAML entry, schema) for zero computational value.

Instead, the graph builder maintains an alias map:
```
p_alpha_out -> alpha_neutron_split::p_alpha (module output channel)
```

When building a FORMULA module that references `p_alpha_out` as an input, the graph builder resolves the alias to the upstream calc output channel and wires directly.

### EXPOSE-within-FORMULA Interaction

A FORMULA attribute may reference an EXPOSE attribute as one of its inputs:

```sysml
part def PowerPlant {
    calc efficiency_calc : EfficiencyCalc { ... }

    // EXPOSE_PURE: surface calc output
    attribute thermal_efficiency : Real = efficiency_calc.eta_thermal;

    // FORMULA: references an EXPOSE attribute
    attribute useful_power : Real = p_fusion * thermal_efficiency;
}
```

The graph builder maintains a per-part attribute resolution map built from classification results:

| Input Name | Resolution Kind | Wiring Action |
|-----------|----------------|---------------|
| Literal sibling | `literal` | Wire to entry point |
| Another FORMULA | `formula` | Wire to synthetic module output |
| EXPOSE_PURE alias | `expose_alias` | Wire to upstream calc output channel |
| Not found | default | Wire to entry point (conservative) |

This is the primary reason EXPOSE classification is needed even though EXPOSE itself generates no module.

### Decision 3: Qualified Name Resolution in Classification

The computed attribute classifier MUST use `ref.qualified_name` to determine reference targets. Simple `ref.name` matching is insufficient and produces incorrect classifications.

**The Problem**: The ATTR-EXPR v1 spike found 19 CATF attributes misclassified as MIXED because CalcDef output names collided with sibling attribute names:

```sysml
part def FusionPlasmaPhysics {
    attribute p_alpha : Real = 2600.0 * 3.52 / 17.58;  // sibling attr named "p_alpha"

    calc alpha_neutron_split : AlphaNeutronSplitCalc {
        out p_alpha : Real = ...;                        // calc output also named "p_alpha"
    }

    attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;  // EXPOSE
}
```

When classifying `p_alpha_out`, `extract_feature_refs()` returns refs including one with `ref.name = "p_alpha"` and `ref.qualified_name = "CATFLibrary::AlphaNeutronSplitCalc::p_alpha"`.

Using simple name matching, `p_alpha` matches the sibling attribute AND is part of a calc output reference. The classifier incorrectly produces MIXED.

Using qualified name matching, `CATFLibrary::AlphaNeutronSplitCalc::p_alpha` is clearly a CalcDef output (different namespace), not a sibling attribute. The classifier correctly produces EXPOSE_PURE.

**Resolution rules** for each ref returned by `extract_feature_refs()`:
1. Check if `ref.qualified_name` shares the same parent namespace as the owning part's qualified name -> **sibling attribute reference**
2. Check if `ref.qualified_name` matches a CalcDef output namespace -> **calc output reference** (EXPOSE indicator)
3. Check if `ref.name` matches a CalcUsage name on the owning part -> **calc usage instance** (part of a FeatureChainExpression, EXPOSE indicator)
4. Otherwise -> **unresolvable**

## Consequences

### Positive

1. **Precise routing**: Each classification maps to exactly one pipeline treatment, with no ambiguity.
2. **FORMULA enables new modeling capability**: Modelers can write `attribute volume = l * w * h` instead of creating CalcDef + CalcUsage. This eliminates the biggest remaining source of SysML modeling overhead.
3. **EXPOSE_PURE requires zero modeling changes**: The existing EXPOSE pattern continues to work; codegen now classifies it internally for wiring context.
4. **EXPOSE_COMPUTED deferral is safe**: No current model uses this pattern. The workaround (CalcDef with Phase 1 auto-implementation) is viable.
5. **Qualified name resolution eliminates misclassification**: The 19-CATF-misclassification bug is structurally prevented.
6. **Chain handling is a non-issue**: The compiler's chain-blindness is a feature -- each computed attribute compiles independently, and the graph builder handles ordering.

### Negative

1. **Known UX gap**: From a modeler's perspective, `attribute area = length * width` (FORMULA, works) and `attribute adj = calc.output * 1.15` (EXPOSE_COMPUTED, deferred) look similar. The distinction is an implementation detail of how SysIDE represents dotted paths. Modelers may find this surprising.
2. **Classification depends on SysIDE qualified names**: If SysIDE changes its qualified name format, the classifier needs updating.
3. **EXPOSE_PURE adds implementation complexity**: Even though it generates no module, the alias resolution logic in the graph builder is new code that must be maintained.

## Examples

### Example 1: Probe Fixture Chain (area -> cost -> cost_density)

```sysml
part probe_design {
    attribute length : Real = 10.0;   // LITERAL
    attribute width : Real = 5.0;     // LITERAL
    attribute rate : Real = 12.0;     // LITERAL
    attribute height : Real = 3.0;    // LITERAL

    attribute area : Real = length * width;             // FORMULA
    attribute cost : Real = area * rate;                // FORMULA (chain)
    attribute volume : Real = length * width * height;  // FORMULA
    attribute cost_density : Real = cost / volume;      // FORMULA (fan-in)
}
```

Classification results:
- `area`: FORMULA (refs: `length`, `width` -- both siblings)
- `cost`: FORMULA (refs: `area`, `rate` -- both siblings, even though `area` is computed)
- `volume`: FORMULA (refs: `length`, `width`, `height` -- all siblings)
- `cost_density`: FORMULA (refs: `cost`, `volume` -- both siblings)

Pipeline modules generated: `probe_design__area`, `probe_design__cost`, `probe_design__volume`, `probe_design__cost_density`. Execution order determined by topological sort in graph builder.

### Example 2: Solar Battery p_net_kw

```sysml
part solar_battery_plant {
    attribute p_net_mw : Real = 0.008;
    attribute p_net_kw : Real = p_net_mw * 1000.0;   // FORMULA

    calc annualized_om : AnnualizedOMCalc {
        in p_net_kw = p_net_kw;   // binds to FORMULA computed attribute
    }
}
```

Classification: `p_net_kw` is FORMULA (ref `p_net_mw` is a sibling attribute). Generates synthetic module `solar_battery_plant__p_net_kw`. The backtracker resolves `annualized_om`'s binding to `p_net_kw` as MODULE_OUTPUT from the synthetic module (not as an entry point).

### Example 3: CATF EXPOSE Pattern with Qualified Name Resolution

```sysml
part def FusionPlasmaPhysics {
    attribute p_alpha : Real = 2600.0 * 3.52 / 17.58;   // sibling attr

    calc alpha_neutron_split : AlphaNeutronSplitCalc {
        out p_alpha : Real = ...;                         // calc output, same name!
    }

    attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;  // EXPOSE_PURE
}
```

Without qualified name resolution: `p_alpha` matches sibling attribute -> misclassified as MIXED.
With qualified name resolution: `CATFLibrary::AlphaNeutronSplitCalc::p_alpha` is a CalcDef output namespace -> correctly classified as EXPOSE_PURE.

## References

- **Concept document**: `.project/concepts/attr-expr-architectural-decisions.md` -- Sections 3-4, 6-7 (source material for this ADR)
- **Spike report v1**: `.project/active/attr-expr-spike/report.md` -- 540-attribute inventory, misclassification discovery
- **Spike report v2**: `.project/active/attr-expr-spike/findings_v2.md` -- Probe fixture validation of all 5 classifications
- **ADR-004**: `docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` -- Pipeline treatment for each classification
- **ADR-002**: `docs/architecture/ADR-002-calculation-architecture.md` -- Rule 3 amendment permits FORMULA patterns

## Changelog

| Date | Change |
|------|--------|
| 2026-02-09 | Initial version -- formalized 5-way classification scheme, EXPOSE handling strategy, and qualified name resolution requirement from ATTR-EXPR spike findings and concept document |
