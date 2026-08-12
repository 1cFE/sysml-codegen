# Modeling Assumptions and Prerequisites

This document captures the SysML modeling conventions and structural requirements that the sysml-codegen pipeline depends on. Models that follow these conventions will be correctly transformed into executable TEAx pipelines. Models that violate them will produce extraction errors or incorrect pipeline behavior.

This is a **prerequisites** document -- it describes what the SysML models MUST look like, not how the pipeline processes them. For pipeline internals, see the [reference documentation](reference/).

---

## 1. Library/Design Separation

The pipeline enforces a strict separation between **algorithm definitions** and **configuration values**:

| Location | Contains | Role |
|----------|----------|------|
| `models/library/` | `calc def` declarations | Reusable algorithms (behaviors) |
| `models/designs/` | Part definitions, attribute values, calc usages | Configuration (values and wiring) |

**Rules:**

- All `calc def` declarations SHALL be in `models/library/`. Calc defs in `designs/` are a validation error.
- Calc usages in `designs/` instantiate library calc defs and bind inputs to design values.
- Design attributes contain values and wiring, not computations (with specific exceptions below).

**Relaxation -- CalcDefs in Library PartDefs:** CalcDefs embedded within PartDefs in library packages are permitted. These are template CalcUsages instantiated per design PartUsage via virtual CalcUsage generation (see [Section 5](#5-template-instantiation-convention)).

**Rationale:** Calc defs are reusable algorithms that require testing, documentation, and implementation. Placing them in `library/` ensures they are properly managed as shared components. The codegen generates module stubs, implementation stencils, and auto-implemented code for library calc defs.

---

## 2. Input Parameter Classification

### Core Principle

> **An input parameter is any literal value in a design file that the user may want to override for a scenario.**

Input parameters are:
- **Scenario-relative**: Determined by backtracing from target outputs
- **User-configurable**: Values the user provides to run a simulation
- **Design-scoped**: Only values in design files (not library algorithm constants)

### Three Input Parameter Types

#### LIBRARY_DEFAULT
A calc def input attribute with a default value, where the calc usage does NOT bind that input. The default value from the library becomes the user-overridable parameter.

```sysml
// library/power_balance.sysml
calc def HeatingWallPlugPower {
    in heating_efficiency : Real = 0.5;  // default exposed if not bound
}

// designs/physics.sysml
calc wall_plug : HeatingWallPlugPower {
    in delivered_power = system.delivered_power;
    // heating_efficiency NOT bound -> uses library default -> IS input param
}
```

#### DESIGN_ATTRIBUTE
A literal-valued attribute in a design part. This includes both pure literals and statically-evaluated expressions (expressions that resolve entirely to constants).

```sysml
// designs/physics.sysml
part catf_physics {
    attribute p_fusion : Real = 2600.0;     // IS input param (literal)
    attribute eta_thermal : Real = 0.46;    // IS input param (literal)
    attribute p_net : Real = net_calc.p_net; // NOT input (bound to output)
}
```

#### USAGE_LITERAL
A literal value used directly in a calc usage binding expression.

```sysml
// designs/magnets.sysml
calc cryo_load : MagnetCryogenicLoad {
    in p_neutron = 2079.41;              // IS input param (literal binding)
    in b_field = tf_system.field_at_coil; // NOT input (traces to attr)
}
```

### What Is NOT an Input Parameter

**In library files:** All values are algorithm constants -- formula constants (e.g., `* 8760.0` for hours/year), output attributes, intermediate locals, constraint bounds, and any hardcoded values. Library = algorithm, not configuration.

**In design files:** Attributes bound to calc outputs (computed values), expression results that depend on calc outputs, attributes without values (must be bound elsewhere), and bindings that wire to other calc outputs or attributes (these are wiring, not values).

**Exception -- FORMULA inputs:** When a design attribute contains a FORMULA expression (e.g., `area = length * width`), the expression result (`area`) is NOT an entry point, but its literal-valued sibling inputs (`length`, `width`) MAY be DESIGN_ATTRIBUTE entry points. See [Section 3](#3-design-attribute-expression-rules).

### Supported Value Types

| Type | SysML | Python | Example |
|------|-------|--------|---------|
| Real | `Real` | `float` | `= 2600.0` |
| Integer | `Integer` | `int` | `= 12` |
| String | `String` | `str` | `= "HTS_CICC"` |
| Boolean | `Boolean` | `bool` | `= true` |

### Unit Handling

Units (e.g., `= 20 [K]`) are **metadata only**:
- The numeric value (20) is extracted as the parameter value
- The unit ([K]) is stored as metadata for documentation
- Automatic unit conversion is not supported

### Parameter Grouping

Parameters are grouped by the file that **declares** them, into JSON input files:

| Declaring File | JSON File |
|-------------|-----------|
| `magnets.sysml` | `magnets_params.json` |
| `physics.sysml` | `physics_params.json` |

**Declaration site, not use site.** A parameter declared in a library file and consumed from a design lands in the *library's* group, named after the library file. The one exception is a `model.sysml`, which carries no identity of its own: its group takes the name of the package that declares the owning root occurrence. See [17-parameter-group-deriver](reference/17-parameter-group-deriver.md).

**A design attribute's key names the attribute, not the consumer.** Two calculations reading the same modelled attribute share one JSON key and one entry. A library default and a usage literal still key by the consuming calc usage and its formal, because there is no supplying attribute to name. See [06-entry-point-classifier](reference/06-entry-point-classifier.md).

Grouping is orthogonal to namespacing -- a parameter's namespace ensures uniqueness while its grouping determines which JSON file it lives in.

---

## 3. Design Attribute Expression Rules

Design attributes may contain several kinds of expressions, each with different pipeline treatment.

### Expression Type Taxonomy

| Expression | Feature Refs | Classification | Result |
|------------|-------------|----------------|--------|
| `= 3.0` | 0 | Literal | PASS |
| `= 3.0 [m]` | 0 (SI units filtered) | True Static | PASS |
| `= 3.14159 * 2.0` | 0 | True Static | PASS |
| `= length * width` (sibling attrs only) | >=1 (siblings) | FORMULA | PASS (generates pipeline module) |
| `= my_calc.output` | 1 (EXPOSE) | EXPOSE Pattern | PASS (channel alias) |
| `= tf_coil.volume_calc.volume` (multi-hop chain) | 1 (EXPOSE, confirmed transitively) | EXPOSE Pattern | PASS (channel alias to the transitive channel) |
| `= my_calc.output * 0.95` | 1+ (calc output + arithmetic) | Derived expression | FAIL (requires CalcDef) |
| `= calc1.output + calc2.output` | >=1 (calc output refs) | Derived expression | FAIL (requires CalcDef) |

### Literal Values

Pure constants that become entry points. This includes numeric literals, string literals, and boolean literals.

### True Static Expressions

Expressions where **all operands resolve transitively to literal values**. These are evaluated at extraction time to produce a constant. An expression is "true static" if it contains only literal values, standard library references (SI::, ISQ::, ScalarValues::), and arithmetic operators.

### FORMULA Expressions

Arithmetic expressions referencing **only sibling attributes on the same part**. These generate synthetic pipeline modules with auto-implemented code.

**Conditions** (ALL must hold):
- All feature references resolve to sibling attributes (same owning part)
- No `FeatureChainExpression` nodes (no dotted paths to calc outputs or other parts)
- Supported operators: `+`, `-`, `*`, `/`

```sysml
part plant {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;
    attribute area : Real = length * width;           // FORMULA: siblings only
    attribute cost : Real = area * rate;              // FORMULA: chain is fine
    attribute p_net_kw : Real = p_net_mw * 1000.0;   // FORMULA: unit conversion
}
```

Chains (computed attributes referencing other computed attributes) work naturally -- each becomes its own pipeline module, and the graph builder handles topological ordering.

### EXPOSE Pattern

Design attributes may reference a single calc output as a pure alias (no arithmetic). This surfaces an internal calc output at the part boundary for wiring convenience.

```sysml
part subsystem {
    calc instance_name : CalcDefFromLibrary {
        in some_input = ...;
    }

    // EXPOSE: pure value propagation, no computation
    attribute exposed_name : Real = instance_name.calc_output;
}
```

This is permitted because it introduces no new computation -- it is pure value forwarding. Consumers bind to `subsystem.exposed_name` without knowing the internal calc structure.

**Multi-hop chains (Item 10 / REQ-CA-10).** The exposed reference may reach through
nested parts: `attribute magnet_volume_total : Real = tf_coil.volume_calc.volume`.
Extraction alone cannot tell whether such a chain lands on a calc output, so it is
classified tentatively (`EXPOSE_CHAIN_TENTATIVE`) and confirmed during registry build
(the Phase 3b confirm walk): a chain that resolves transitively to a canonical channel
becomes an EXPOSE alias of that channel; one that does not reverts to FORMULA
treatment. The confirm walk is reconstructed when generating from a snapshot, so
offline and live runs wire the same channel.

**Part-def EXPOSE (shape A).** The EXPOSE attribute may also live on a `part def`
(REQ-CA-03). It then expands per design instance: each instance's consumers resolve to
that instance's own channel, so two siblings of the same type never share (or collide
on) an exposed name. The part-usage form shown above is shape B.

**What "exposed_name" means concretely (Item 5 / Item 11).** The name a consumer
binds to is the derived, *sanitized* `python_name`, not the raw SysML name. Item 5
derives every identifier once at extraction (`_sanitize_name`, REQ-NC-06) and looks it
up thereafter; for a spaced name `'total cost'` the bound form is `total_cost`. As of
Item 11 (SC-7 / REQ-DM-09 / REQ-PY-08) that sanitized name **surfaces into generated
output**: it lands on `ComputationGraph.output_aliases` and, in the pipeline YAML,
becomes the output filename on the exposed channel's exit line
(`{instance_path}__{exposed_name}.json`). Both EXPOSE_PURE shapes surface — a part-def
EXPOSE (shape A, e.g. `total_cost` on a `part def`) via the `_scoped_alias` registry,
and a part-usage EXPOSE (shape B) via its `expose_pure` `ChannelAlias`. See
[16-computed-attributes](reference/16-computed-attributes.md) and
[21-pipeline-yaml-generation](reference/21-pipeline-yaml-generation.md).

**EXPOSE_COMPUTED (deferred):** Combining a calc output reference with arithmetic (e.g., `= calc.output * 1.15`) is NOT supported. Create a CalcDef for the adjustment instead -- the pipeline auto-implements simple arithmetic CalcDefs, so no handwritten `_impl.py` is needed.

### Dynamic Expressions (Error)

Expressions that reference calc outputs in arithmetic context cannot be statically evaluated and are a validation error:

```sysml
// ERROR: Depends on calc output -- must be a calc def
part system {
    attribute p_net : Real = gross_power_calc.p_gross - parasitic_power;
}
```

**Resolution:** Extract to a calc def in `library/` and wire via calc usage.

### Supported Operators

Static evaluation and FORMULA compilation support:

| Operator | Behavior | Example |
|----------|----------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction (binary) | `a - b` |
| `-` | Negation (unary) | `-a` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `[` | Unit annotation | `3.0 [m]` |

**NOT supported** (require a calc def):
- Exponentiation (`**`, `^`)
- Functions (`sin`, `cos`, `sqrt`)
- Conditionals (`if`, `?:`)

---

## 4. Aggregation via Redefinition

PartDef attributes may use `:>>` redefinition with aggregation expressions combining `sum()` of child costs and direct child attribute references.

**Conditions** (ALL must hold):
- Expression uses only `sum()` calls on child PartUsage attributes and direct child attribute references
- Expression is on a PartDef in `library/` (not `designs/`)
- **No two terms in one expression may read a same-named attribute off different children** — see the rule below

### One named intermediate per child role

> **An assembly cannot write `sum(a.capital_cost) + sum(b.capital_cost)`. Give each child's
> contribution its own named attribute and add the names.**

```sysml
// REFUSED: two terms, both reading `capital_cost`
:>> capital_cost = sum(deck_panel.capital_cost) + sum(caster.capital_cost);

// WORKS: one named intermediate per child role, added by the rollup
attribute panel_capital  : Real = sum(deck_panel.capital_cost);
attribute caster_capital : Real = sum(caster.capital_cost);
:>> capital_cost = panel_capital + caster_capital;
```

**Why.** An expression parameter is named after the **last member** of the reference, with the
qualifier dropped (`fact.resolved_member_names[-1]`, `elaboration/elaborate.py:1937`). Two terms
reading a same-named attribute off different children therefore both render `capital_cost`, and
the projection refuses the model with `SI_RENDERING_COLLISION` rather than letting two distinct
sources collapse onto one parameter (`elaboration/project.py:598-604`).

**The refusal is correct, and is the point.** A silent collapse here is exactly the failure this
architecture exists to prevent: two different children's costs quietly becoming one number. The
refusal names the parameter and the owner, so the fix is mechanical.

**This bites every costed assembly by construction.** A part hierarchy where children specialize
a shared interface — the Costed Item pattern, where every child exposes `capital_cost`,
`raw_material_cost`, `fabrication_cost` — has same-named attributes on every child by design.
Any rollup over two or more such children needs the named-intermediate form.

**Worked example:** `tests/fixtures/costed_cart_d5/library.sysml`. Its `Deck Assembly` names
`panel_capital`, `caster_capital`, `panel_material`, `caster_material`, `panel_fabrication`,
and `caster_fabrication`, then adds them in the four `:>>` rollups. Its `Frame Assembly` does
the same for two singleton children (`rail_capital`, `brace_capital`). Refusal pinned by
`tests/integration/test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_is_refused`.

**Cross-reference — the same class from the other side.** This is the filed Item 10 cross-part
`child.attr` collapse class, where the resolver does not follow per-child `:>>` redefinitions.
The deleted legacy route collapsed those terms through a qualifier-dropping name match; the exact
route refuses instead. Recorded on recovery ledger row L-199 and carried to the Phase 5 owner
packet.

---

## 5. Template Instantiation Convention

CalcUsages embedded within PartDefs are **templates**. They define the calculation shape for a component type, but must be instantiated once per design PartUsage that uses that PartDef.

### How It Works

1. A CalcUsage inside a PartDef is detected as a template (its `owning_type` is a `PartDefinition`)
2. For each PartUsage in the design that instantiates that PartDef, a **virtual CalcUsage** is generated
3. The virtual CalcUsage's qualified name reflects the full design hierarchy path
4. Parameter bindings are resolved through the design instance's `:>>` redefinitions

**Example:**
```sysml
// library/solar_battery.sysml
part def 'PV Module' :> 'Costed Component' {
    calc cost_model : PVModuleCostCalc { ... }  // Template CalcUsage
}

// designs/solar_battery/design.sysml
part solar_array {
    part pv_module : 'PV Module' [module_count] {
        :>> wattage = 400.0;  // Override template parameter
    }
}
```

This generates a virtual CalcUsage: `solar_array__pv_module__cost_model` with `wattage=400.0` resolved from the `:>>` redefinition.

### Redefinition Types

| Type | Pattern | Treatment |
|------|---------|-----------|
| LITERAL | `:>> wattage = 400.0` | Becomes a DESIGN_ATTRIBUTE entry point |
| CHAIN | `:>> capital_cost = cost_model.total_cost` | Wired as MODULE_OUTPUT in the pipeline |
| Deep-path | `:>> pv_module.wattage = 400.0` | Traversed through hierarchy to leaf attribute |
| Type (retyping) | `:>> driver : 'HIF Driver'` (where `'HIF Driver' :> 'IFE Driver'`) | Pulls in the subtype's template calcs; supertype templates continue to flow (see below) |

### Type Redefinition (Retyping)

A usage may **retype** to a subtype: `part :>> driver : 'HIF Driver'` where
`part def 'HIF Driver' :> 'IFE Driver'`. The retyped usage instantiates **both** its
subtype's template calcs **and** the supertype-owned templates it already carried — it is
indexed under every user-model PartDefinition it carries (its owned FeatureTyping target plus
the user supertypes present in its flattened type list). A usage's declared type is read from
its **owned FeatureTyping relationship**, never from a position in the type list (that list is
order-unstable and, for a retyped usage, lists the supertype first and the declared subtype
last).

Two rules govern a subtype template that meets a supertype template on the same instantiation:

- **Same name (redefinition).** A calc that *replaces* an inherited one reuses its name — the
  two resolve to the same virtual QN. The most-specific owner (the subtype) wins; a **V9**
  warning names both owners and the winner. This is how the modeler signals "override".
- **Different names.** Both instantiate — retyping *adds* the subtype's calcs while the
  supertype's continue to flow. No warning (there is no signal that a differently-named calc
  was meant as a replacement).

**Not covered:** a *plain* `part x : 'HIF Driver'` (no `:>>`) does **not** pull supertype
templates — its type list carries only the declared type, so the supertype-owned template
finds no instantiation path to it. Supertype-chain template inheritance for plain usages needs
a deliberate specialization walk (deferred; MFE-epic note).

**Values through the specialization chain.** A retyped part's specialized-def `:>>`
values participate in binding resolution with a fixed precedence: **usage override >
specialized-def `:>>` > base def** (REQ-VBR-10). This holds whether the retype sits on
the def or on a part usage (the two-level shape, REQ-VBR-11) — it is how a consumer calc
declared on a base def reaches a value or channel supplied by the subtype (e.g. the
`gamma → lcoe` wiring).

**Value-carrying redefinitions use the bare member form.** Every `:>>` shown above is
the bare form (`:>> attr = value`), which parses as a ReferenceUsage member and is
captured — on template-instantiating usages (all RHS kinds) and on plain typed usages
(literal RHS only; Item 9 / REQ-HR-08). The `attribute :>> attr = <expression>` form
(an AttributeUsage redefinition) is **not captured** — it is currently dropped at
extraction without a diagnostic. Use the bare form.

### Cross-Part Supplied Values (Item 2, REQ-SVM-01..04)

A plant calc may read a subsystem value it does not own, cross-part or in-part. The
supplied-value materializer carries the model literal into the consumer's entry point,
so the reference resolves to a filled `DESIGN_ATTRIBUTE` parameter instead of a valueless
one. Four value-provision shapes are supported (see
[25-hierarchy-resolver §Supplied-Value Materializer](reference/25-hierarchy-resolver.md#supplied-value-materializer-req-svm-01-04)):

- **(a)** a subtype-def literal reached through a usage-level retype (`:>> driver : 'Hif Driver'` with `Hif_Driver.efficiency = 0.35`);
- **(b)** a bare no-retype override block (`part :>> target_factory { :>> cost_per_target = 10.0; }`);
- **(c)** a plain one-hop cross-part attribute with a usage-level dotted override (`:>> chamber.cost_per_unit = 7.0`);
- **(d)** in-part consumption of an inherited attribute the same def redefines below the binding (`in flow_rate = throughput` with `:>> throughput = 8.0`).

Precedence is **usage override > specialized-def `:>>` > base def**. Entry points key by
the **source attribute's QN**, so two differently-named consumers of one source collapse
onto one parameter. Only LITERAL values apply; a non-literal supplied value falls through
to the uncovered-parameter diagnostic (V11) with a WARN, never silently.

**Limitation — nested-occurrence overrides are not captured correctly
(`[NESTED-OCCURRENCE-OVERRIDE]`, BACKLOG P2).** A `:>>` override on a usage nested inside an
*instantiated* part def is captured **definition-relative** while demand resolves
**occurrence-relative**, so the materializer never matches and the model literal is lost — the
calc binding falls to a manual-required entry point (value dropped, with a WARN naming both the
captured and the demanded scope — a tripwire added 2026-07-24, not a fix), and a constraint
actual halts generation under strict INV-2. Shape (b) above is safe only in its flat,
non-nested form; do not read this section as promising nested-occurrence override capture. Probe
fixture: `tests/fixtures/nested_occurrence_override_probe/` (expected to halt; its flat sibling
`constraint_def_owned_redefining/` resolves through the same machinery, isolating nesting as the
sole trigger).

---

## 6. Arrayed Children Are Enumerated, Not Multiplied

When a part contains arrayed children with multiplicity (e.g., `pv_module : 'PV Module' [20]`), the elaborator **enumerates the occurrences**. Each one is a separate occurrence node with its own attribute nodes, and an aggregation over them expands into one term per occurrence.

### The Consequences for a Modeller

- **Each occurrence is its own parameter.** A modelled attribute on an arrayed child mints one entry point per occurrence, and the key carries the index: `…__battery_pack[0]__capacity_kwh`, `…__battery_pack[1]__capacity_kwh`. Three modelled members do not collapse into one shared parameter (`test_exact_projection_aggregation.py::test_every_member_occurrence_is_its_own_entry_point`).
- **Non-uniform arrays are expressible.** Different values per instance are a normal shape now, not an unsupported one, because each occurrence carries its own value site.
- **The multiplicity must be modelled.** `part cell [count]` where `count` is a modelled attribute with a value produces that many occurrences; the count is read from the model rather than left as a user-supplied array size.
- **The output grows with the array.** Enumeration means one node per member rather than one multiply. That is a real size change: `solar_battery`'s pipeline YAML grows from 526 to 1343 lines under enumeration.

### Schema Field Names vs JSON Keys

An occurrence-indexed key (`…__battery_pack[0]__capacity_kwh`) is not a legal Python identifier, so it cannot be a schema field name. `core/qualified_names.params_field_name` sanitizes the field, and the generated schema keeps the exact key as the field's **alias**. The JSON key is the graph's entry-point name verbatim; the Python attribute is the sanitized form. See [22-output-schema-rules](reference/22-output-schema-rules.md).

### Parametric Multiply (retired)

The deleted legacy route rewrote `sum(child.attribute)` to `count * child.attribute` at compile time and required every instance in an array to share the same parameter bindings. That transformation is gone with that route. If you are reading a model or a baseline that assumed it, the uniform-array requirement no longer applies and the per-instance keys are the expected shape.

---

## 7. Compute Once, Look Up Thereafter

> **Identifiers are computed ONCE at extraction time and LOOKED UP thereafter. Downstream code never re-derives or reconstructs identifiers.**

This principle applies throughout the pipeline:
- Element qualified names (EQN) are computed by AST traversal during extraction
- All downstream phases (backtracking, graph building, generation) look up identifiers rather than reconstructing them
- Binding resolutions are stored in a single authoritative mapping, not re-derived

The naming convention uses `__` (double underscore) as the hierarchy separator throughout:
- Element names: `Package__Part__Element`
- Parameter names: `Package__Part__Element__param`
- Module names: Element name, lowercased

For the full identifier taxonomy and naming rules, see [15-naming-conventions.md](reference/15-naming-conventions.md).

---

## 8. Constraints Execute Under a Profile — Block List and Fallback

> **A constraint predicate the executable profile ADMITs lowers into a real pipeline module and
> executes; one it BLOCKs halts generation loudly, naming why; everything else catalogs unassessed.**

SysML lets a modeler attach `constraint` usages to calc defs, part defs, and part usages — for
example a physical-consistency check like `outer_radius == inner_radius + thickness`, or a
plausibility bound like `eta * gain >= threshold`. Through Item 4, sysml-codegen had no execution path
for any of them and dropped every one, loudly. Items 5-9 built the real path (see
[28-constraint-lowering-and-catalog.md](reference/28-constraint-lowering-and-catalog.md) for the
mechanism); this section teaches what a modeler should now expect.

**The three outcomes.** `agentic-mbse`'s executable profile (`evaluate_profile`) classifies every
swept `ConstraintUsage` (subtypes included) exactly one way:

- **ADMIT** — the predicate lowers: every formal strictly resolves to a real producer channel, a
  design attribute, or a modeled default, and the constraint becomes a pipeline module whose
  evaluation is a real output channel.
- **BLOCK** — generation halts before any lowering, naming every offending usage and its reason. This
  is the one loud, hard-stop diagnostic (never a silent drop, never retried with a fallback).
- **unassessed** — a requirement-side usage (`RequirementUsage`/`SatisfyRequirementUsage`, excluded
  from execution by design) or an out-of-profile owner (e.g. a `requirement_def` owner) is cataloged
  defensively — one record, no expansion, no formal resolution, no node — never silently absent.

**The block list.** A predicate BLOCKs for an unsupported construct or operand shape, most commonly:
an invocation expression (`block_invocation`), a feature-chain reference the profile cannot resolve
(`block_feature_chain`), `xor`/`implies` operators (`block_xor`/`block_implies`), an assert-by-reference
form (`block_assert_by_reference`), a real-valued or quantity-typed `==`/`!=` comparison with no
tolerance band (`block_real_equality_requires_tolerance`), or a comparison across incompatible/unknown
units (`block_unit_conversion_required`, `block_incompatible_dimensions`, `block_unknown_exact_unit`).
**The real-equality idiom:** model a tolerance band explicitly as two inequalities
(`x - tol <= y` and `y <= x + tol`) rather than `x == y` — the profile admits an inequality
comparison on real/quantity operands, never a bare equality one.

**Every manifest entry has a carrier — the migration invariant.** `collect_constraint_manifest()`
still sweeps the model exactly as before (REQ-EXT-09) — it is the license-free proof surface a kept
conformance test (`test_constraint_migration_mapping.py`) reads directly, not a generation-time
report anymore. That test proves, for every constraint-bearing fixture, that each swept usage has a
catalog carrier: an eligible concrete entry, an explicit unassessed record, or a named,
justified requirement/satisfy exclusion — nothing silently absent.

**What a modeler needing an enforced gate should do.** Author an `assert constraint` (or bare
`constraint`/`require constraint`) against a defined `constraint def`, bind every formal to a real
value in scope, and keep any equality check as an explicit two-inequality tolerance band. If the
profile BLOCKs it, the generation error names the exact construct to fix.

---

## Validation Rules

The pipeline enforces these rules to catch modeling violations early. V1–V10 fire at
extraction time; V11 fires at the generation boundary (see the V11 note below):

| Rule | Condition | Error |
|------|-----------|-------|
| V1 | Calc def in `designs/` | "Calculation definitions must be in `library/`, not `designs/`" |
| V2 | Static evaluation failure | "Expression cannot be statically evaluated. Operand is not a literal. Consider extracting to a calc def in `library/`." |
| V3 | Circular reference | "Circular dependency detected" |
| V4 | Unknown operator | "Unsupported operator in static expression. Use calc def for complex calculations." |
| V5 | Unbound input without default | Add default to calc def OR add binding in usage |
| V6 | Binding to undefined attribute | Fix the binding path |
| V7 | Calc def extracts with zero output attributes | "Calc def '{name}' extracted with zero output attributes. A pipeline module needs at least one output channel. Likely cause: the calc def declares no result — add one, e.g. `out attribute y : Real = <expr>` or `return y : Real = <expr>`. (An anonymous `return` is reported separately.)" |
| V8 | Calc def has an anonymous `return` (a result with no name) | "Calc def '{name}' has an anonymous `return` (a result with no name), so no output channel can be built. Give the result a name, e.g. `return result : Real = <expr>`." |
| V9 | Two template calcs from different owners (a retyped usage's super- and subtype) resolve to the same virtual QN | "Template collision on '{virtual_qn}': owners '{owner_a}' and '{owner_b}' both define calc '{calc_name}'; kept most-specific owner '{winner}'." |
| V10 | A usage has multiple incomparable owned types (neither specializes the other) | "Usage '{owning_qn}.{name}' has multiple incomparable owned types {sorted_qns}; resolved defaults against '{winner}' (first in stable order)." |
| V11 | A module input references a params key no parameter group provides — its entry point fell through resolution (Step-4), carries no value, and is still wired (Item 7 / SC-8) | "V11: {n} module input(s) reference a params key that no parameter group provides — the JSON never mints the key, so the pipeline will KeyError at load. Cause: an unresolved cross-part reference not yet wired (Items 9-11) or a resolution bug. Offenders: module '{name}' input '{param}' -> params key '{group}.{qn}'" |

**V11 note (SC-8).** Unlike V1–V10 (extraction-time), V11 fires at the
**generation boundary** (`run_codegen`), where the computation graph and derived
parameter groups both exist. It is the wired half of the fell-through-valueless
partition (M1): the **unwired** half is a WARNING reconciliation summary
(`Unresolved after assembly: …`), not a hard error. A null-default entry point
that did *not* fall through is the legitimate user-fill signature and never trips
V11. Behavioral note: Item 7 also fixed two resolution matcher bugs (the FORMULA
`::`-QN per-segment sanitize and def-owned dotted leaf-unique match), which
reclassify some entry points `USAGE_LITERAL` → `DESIGN_ATTRIBUTE` and switch their
default-value source; see the Item 7 release notes.

**No V12/V13 (Item 10 note).** The Item-10 design tentatively proposed V12 (multi-hop
EXPOSE coverage) and V13 (specialization-chain channel coverage) as new diagnostic codes.
They were not added: Item 10's mechanisms are **positive resolution** (they wire cross-part
channels that previously fell through), not new abort diagnostics, so a V12/V13 code would
emit nothing. The coverage is instead tracked as requirements — REQ-CA-10 (multi-hop
EXPOSE), REQ-LVP-09 + REQ-VBR-11 (specialization chain), REQ-BT-11 (scoped-alias sibling
disambiguation) — in the [verification matrix](verification-matrix.md). A model that still
fails to wire a cross-part input surfaces through the existing **V11** boundary.

---

## Related Documents

- [Architecture Overview](overview.md) -- Top-level pipeline summary and reading guide
- [Reference Documentation](reference/) -- Detailed design documentation for each pipeline component
- [Verification Matrix](verification-matrix.md) -- REQ-to-test traceability
