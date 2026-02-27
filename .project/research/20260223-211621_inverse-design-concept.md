---
date: 2026-02-23T21:16:21-05:00
researcher: Claude
topic: "Inverse Design Concept: Full-Dimensional TEA and Design Space Exploration"
tags: [research, inverse-design, bayesian-optimization, design-space-exploration, sysmlv2, architecture]
status: complete
last_updated: 2026-02-23
---

# Research: Inverse Design Concept

**Date**: 2026-02-23T21:16:21-05:00
**Researcher**: Claude
**Research Type**: Architecture / Domain / Feasibility

## Research Question

Synthesize the motivating thesis behind the sysml-codegen toolchain (exposing ALL independent design parameters), then investigate:
(a) How to replicate "inverse design" models in SysML v2 or as Python utilities on the generated codebase
(b) How to quantify and address the curse of dimensionality imposed by the full-parameter approach

## Thesis: Full-Dimensional TEA vs. Traditional Reduced-Input Design

### The Traditional Approach

Engineering design and techno-economic analysis (TEA) typically follows a three-stage process:

1. **System Understanding**: Build mental models of constraints and causal relationships
2. **Dimensionality Reduction**: Select a small set of independent "knob" variables based on the analyst's question (e.g., 5-15 key parameters)
3. **Inverse Design Modeling**: Build heuristics or models that "fill in" the full design parameter space given the reduced inputs, implicitly baking in:
   - Model simplifications (linearizations, fixed ratios)
   - Design optimization heuristics ("use the cheapest material that meets stress requirements")
   - Default values ("assume standard operating temperature")

This is fundamentally an **inverse design** step: moving from a lower-dimensional representation to a higher-dimensional one, with assumptions doing the heavy lifting.

### The sysml-codegen Approach

The sysml-codegen pipeline inverts this paradigm. Instead of reducing dimensionality upfront, it:

- **Exposes ALL independently variable parameters** as entry points in the generated pipeline
- **Makes constraints explicit** in SysML v2 rather than implicitly encoding them in step-3 heuristics
- **Preserves the full causal graph** from SysML calculation definitions through to TEAx pipeline execution

### The Trade-off

**Gains:**
- Broader design space exploration, potentially avoiding invalid or incomplete assumptions
- Generalized input model -- different users with different questions don't need custom TEA codebases
- Verifiable constraints (captured in SysML) vs. implicit assumptions (buried in code)

**Costs:**
- **Curse of dimensionality**: Much larger input space, much of which is infeasible
- **Usability**: Users with specific questions must work with ALL parameters, not just their relevant subset

### The Missing Layer

The toolchain currently has no equivalent to the traditional "step 3" -- the inverse design layer that maps from a user's reduced-dimensional question to the full parameter space. This research investigates how to fill that gap.

---

## Detailed Findings

### 1. Current Dimensionality: Quantified from Pipeline Baselines

The sysml-codegen test suite provides exact dimensionality data for four models:

| Model | Modules | Entry Points | EP Groups | EP/Module Ratio | EP-Sourced Inputs | MO-Sourced Inputs |
|-------|---------|-------------|-----------|----------------|-------------------|-------------------|
| chain_spike | 3 | 3 | 1 | 1.00 | 3 (50%) | 3 (50%) |
| attr_expr_probe | 16 | 16 | 1 | 1.00 | 31 (84%) | 6 (16%) |
| solar_battery | 36 | 62 | 3 | 1.72 | 71 (54%) | 61 (46%) |
| catf_mfe | 42 | 61 | 8 | 1.45 | 106 (78%) | 30 (22%) |

**Key observation**: The catf_mfe model (a partial fusion reactor) has 78% of module inputs sourced from entry points -- the graph is **wide and shallow**, with most wiring going to the boundary rather than between internal modules.

**Projected full-scale**: The catf_mfe model covers only the physics/thermal layer. The full PyFECONS model would add ~40 cost calculation modules, projecting to:
- ~140 pipeline modules
- **~200+ independent input parameters**
- ~15-20 JSON input files

Source references:
- `tests/fixtures/baseline_outputs/catf_mfe/computation_graph.json` (207,493 bytes)
- `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json` (158,251 bytes)
- `tests/conformance/test_backtracker.py:715` (solar: 15 usages, 61 resolutions)
- `tests/conformance/test_backtracker.py:727` (catf: 42 usages, 136 resolutions)
- `tests/conformance/test_extractor.py:205-206` (solar: 30 unbound params)

### 2. SysML v2 Native Constructs for Inverse Design

SysML v2 has several first-class constructs directly relevant to inverse design (SysML Spec Part 1):

#### 2a. Constraint Definitions (Spec Section 7.20)

Constraints are predicates that can be bound to design parameters and asserted:

```sysml
constraint def MassFeasibility {
    in mass : MassValue;
    mass >= 1000 [kg] and mass <= 3000 [kg]
}
```

**`assert constraint`** (Section 7.20.3) declares that a constraint must **always be true** -- when asserted constraints involve multiple unknowns, a solver is expected to find satisfying values.

#### 2b. Requirement Definitions as Parameter Bounds (Section 7.21)

Requirements are specialized constraints with subject/assume/require semantics:

```sysml
requirement def MinRange {
    subject vehicle : Vehicle;
    attribute requiredRange : DistanceValue;
    require constraint { vehicle.range >= requiredRange }
}
requirement vehicleRange : MinRange {
    attribute :>> requiredRange = 300 [mi];
}
```

This is directly applicable to bounding output requirements and "back-solving" for inputs.

#### 2c. Analysis Cases with Simultaneous Equations (Section 7.23.1)

The spec explicitly supports inverse design via asserted constraints in analysis cases:

> "An analysis case can also specify a set of simultaneous equations to be solved. This can be done defining one or more constraint usages that logically `and` each of the equations, and asserting that the constraint must be true. A solver would be expected to solve the equations such that it returns values that satisfy each equation."

#### 2d. Trade Studies (Section 7.23.3, Section 9.4.5)

The Analysis Domain Library provides `TradeStudy`, `MaximizeObjective`, and `MinimizeObjective`:

```sysml
analysis engineTradeStudy : TradeStudy {
    subject : Engine = (engine4cyl, engine6cyl);
    objective : MaximizeObjective;
    calc :>> evaluationFunction {
        in part anEngine : Engine :>> alternative;
        return :>> result : Real = score(anEngine);
    }
    return part :>> selectedAlternative : Engine;
}
```

#### 2e. Summary: SysML v2 Construct Mapping

| Inverse Design Concept | SysML v2 Construct | Spec Reference |
|---|---|---|
| Forward model (inputs -> outputs) | `calc def` | 7.19 |
| Design parameters | `attribute` on `part def` | 7.7, 7.11 |
| Output requirements / bounds | `requirement def` with `require constraint` | 7.21 |
| Feasibility constraints | `assert constraint` | 7.20.3 |
| Simultaneous equation solving | `analysis` with asserted constraints | 7.23.1 |
| Objective function | `MaximizeObjective` / `MinimizeObjective` | 9.4.5 |
| Design space exploration | `analysis : TradeStudy` | 7.23.3 |

### 3. Current Toolchain Gaps (agentic-mbse + sysml-codegen + TEAx)

**agentic-mbse** provides: model parsing, binding classification, expression evaluation, graph algorithms, constraint *counting* (Level 4 validation). It does NOT provide constraint solving, optimization, or inverse design.

**sysml-codegen** provides: extraction of calc defs, dependency backtracking, computation graph building, TEAx code generation. It does NOT extract constraint definitions, requirement definitions, analysis cases, or trade study constructs.

**TEAx** provides: forward pipeline execution (modules in topological order), type-safe channel routing, JSON input loading. It does NOT provide optimization loops, parameter sweeps, sensitivity analysis, or inverse solving.

The gap is clear: **none of the three packages currently support constraint extraction, parameter bounding, sensitivity analysis, or optimization.**

### 4. Design Concepts for Filling the Gap

#### Concept A: SysML-Native Inverse Design Layer

**Idea**: Express inverse design relationships in SysML v2 using the native constructs (constraints, requirements, analysis cases), then extend sysml-codegen to extract and generate solver-compatible code.

**What would need to change:**

1. **sysml-codegen extraction**: Add extractors for `ConstraintDefinition`, `ConstraintUsage`, `RequirementDefinition`, `RequirementUsage`, `AnalysisCaseDefinition`. These are currently ignored.

2. **sysml-codegen resolution**: Extend `ComputationGraph` with a `constraints` field listing extracted constraints and their parameter bindings.

3. **Code generation**: Generate Python constraint functions alongside TEAx modules:
   ```python
   # Generated from SysML constraint def
   def mass_feasibility(mass: float) -> bool:
       return 1000.0 <= mass <= 3000.0

   # Generated from SysML requirement def
   def min_range_check(range_value: float, required_range: float = 300.0) -> bool:
       return range_value >= required_range
   ```

4. **Solver integration**: Generate a `DesignProblem` class that bundles the forward model (TEAx pipeline), constraints, bounds, and objectives into a solver-ready interface.

**Pros**: Model-driven, verifiable, all design intent captured in SysML
**Cons**: Requires significant extraction work; SysML v2 constraint syntax is complex; analysis cases are the most advanced part of the spec

**Effort estimate**: Medium-high. Constraint/requirement extraction is non-trivial but well-defined.

#### Concept B: Python Utility Layer on Generated Code

**Idea**: Instead of extending the SysML extraction, build a Python utility layer that wraps the generated TEAx pipeline with inverse design capabilities. The generated pipeline already exposes all entry points as JSON schemas.

**Components:**

1. **DesignSpace definition** (from generated schemas):
   ```python
   # Auto-generated from ComputationGraph.entry_point_groups
   class DesignSpace:
       parameters: list[Parameter]  # name, type, bounds, default
       constraints: list[Constraint]  # callable returning bool
       objectives: list[Objective]  # callable returning float
   ```

2. **Parameter bounds** (from entry point metadata):
   - `EntryPoint.default_value` provides a nominal point
   - Bounds could be specified as multiplicative ranges around defaults (e.g., 0.5x to 2.0x)
   - Or loaded from a companion YAML/JSON "design space spec" file

3. **Sensitivity analysis wrapper**:
   ```python
   # Morris screening to find active parameters
   from salib.sample import morris
   design_space.screen(method="morris", N=15)
   # Returns: ranking of parameters by influence on objectives
   ```

4. **Optimization wrapper**:
   ```python
   # Constrained BO on reduced parameter set
   design_space.optimize(
       method="scbo",  # TuRBO + constraints
       budget=200,
       active_params=screening_result.top(50),
   )
   ```

5. **"Scenario" or "Lens" definitions** (the inverse design layer):
   ```python
   # A "lens" reduces the full design space to a user-relevant subset
   class UserFacingRequirementsLens(DesignLens):
       """Start from user requirements, solve for engineering parameters."""
       fixed = {"efficiency": 0.35, "operating_temp": 600}
       objectives = [minimize("lcoe")]
       constraints = [lambda p: p["range"] >= 300]
       free_params = ["battery_capacity", "vehicle_mass", ...]

   class EngineeringHardpointsLens(DesignLens):
       """Start from engineering constraints, back into user specs."""
       fixed = {"reactor_radius": 3.2, "blanket_thickness": 0.8}
       objectives = [maximize("net_electric_power")]
       free_params = ["p_fusion", "q_plasma", ...]
   ```

**Pros**: Can be built incrementally without changing SysML extraction; works with today's generated code; easy to prototype
**Cons**: Design intent not captured in the SysML model; constraints defined in Python rather than SysML; no formal verification path

**Effort estimate**: Low-medium. Can start with a thin wrapper around the generated JSON schemas.

#### Concept C: Hybrid Approach (Recommended)

**Phase 1** (near-term): Build Concept B -- Python utility layer on generated code. This is immediately useful and validates the approach.

**Phase 2** (mid-term): Extract constraint and requirement definitions from SysML (Concept A, items 1-2). Generate constraint functions alongside the existing pipeline code.

**Phase 3** (long-term): Full analysis case extraction and solver integration. This is the most ambitious but provides the complete model-driven inverse design loop.

### 5. Curse of Dimensionality: Quantified and Addressable

#### The Scale of the Problem

- Current models: 61-62 entry points (catf_mfe, solar_battery)
- Projected full-scale: ~200+ entry points
- Entry-point-sourced inputs: 54-84% of all module inputs (most of the graph is boundary)

#### Recent BO Research (2024-2025): Better Than Expected

A landmark finding from ICML 2024 (Hvarfner et al.) showed that **standard GP-based BO with proper configuration works well up to hundreds of dimensions** -- the previous ~20D limit was due to poor hyperparameter initialization, not fundamental limitations:

| Dimensions | Standard BO (Matern + DSP) | Specialized Methods? |
|---|---|---|
| 1-20 | Excellent | Not needed |
| 20-50 | Very good | Generally not needed |
| 50-200 | Workable | Recommended for sample efficiency |
| 200-1000 | Feasible | Strongly recommended (TuRBO, SAASBO, BAxUS) |

#### Recommended Pipeline for ~200D TEA

**Stage 1: Morris Screening** (~2000-4000 evaluations)
- Cost: ~10*(D+1) model evaluations
- Expected outcome: Reduce 200 parameters to ~20-50 "active" parameters
- Tool: SALib

**Stage 2: Feasibility Mapping** (~500 evaluations)
- LHS sampling + feasibility classifier on the reduced space
- Identify approximately feasible regions before expensive optimization
- Tools: scipy.stats.qmc.LatinHypercube, scikit-learn

**Stage 3: Constrained Bayesian Optimization** (100-500 evaluations)
- SAASBO (via Ax) for < 100 eval budget, automatically discovers active subspace
- SCBO (TuRBO + constraint GPs, via BoTorch) for 100-500 eval budget
- BAxUS for > 200 effective dimensions
- Tools: Ax, BoTorch

**Stage 4: Validation** (10-50 evaluations)
- Evaluate BO-found optima with additional runs
- Multi-fidelity refinement if applicable

#### Key Insight: Effective Dimensionality is Likely Much Lower

Engineering TEA models almost always have **effective dimensionality far below nominal dimensionality**. Most outputs are dominated by a small subset of parameters (capital costs, feedstock prices, key conversion efficiencies). The 200-parameter space likely has effective dimensionality of 15-30, which is well within standard BO range.

#### Python Library Stack

| Library | Purpose | Status |
|---|---|---|
| **Ax** (Meta) | High-level BO with SAASBO, constraints | Production-ready |
| **BoTorch** (Meta) | Low-level BO: TuRBO, SCBO, BAxUS, multi-fidelity | Production-ready |
| **SALib** | Morris screening, Sobol indices | Production-ready |
| **SMT** | Surrogate modeling (Kriging, KPLS) | Production-ready |
| **Optuna** | Rapid prototyping, TPE, CMA-ES | Production-ready |

#### TEA-Specific Literature

Recent work confirms BO/surrogate approaches work for TEA:
- BO for TEA of pressure swing adsorption (Elsevier 2024)
- BO for PET chemical recycling TEA optimization (Computers & Chem Eng 2023)
- BO for integrated energy systems TEA at INL (Energy 2025)
- BioProcessNexus: surrogate TEA model training platform (Comp & Chem Eng 2025)

---

## Code References

- Entry point model: `src/sysml_codegen/resolution/models.py:23-68` (EntryPointType, EntryPoint)
- Parameter groups: `src/sysml_codegen/resolution/models.py:70-98` (ParameterGroup)
- Computation graph: `src/sysml_codegen/resolution/models.py:192-207` (ComputationGraph)
- Pipeline module: `src/sysml_codegen/resolution/models.py:160-190` (PipelineModule)
- Parameter group deriver: `src/sysml_codegen/analysis/parameter_groups.py:290-738` (ParameterGroupDeriver)
- Graph builder: `src/sysml_codegen/resolution/graph_builder.py` (build_computation_graph)
- Backtracker baselines: `tests/conformance/test_backtracker.py:714-738`
- Pipeline E2E: `tests/conformance/test_pipeline_e2e.py:185`
- Generated inputs: `/home/reid/1cfe/fusion-tea/generated/solar_battery_v5/inputs/` (3 JSON files, 62 parameters)
- agentic-mbse constraint validation: `agentic_mbse/validation/level4_constraints.py` (metrics only, no solving)
- TEAx module interface: `teax-simkit/simkit/core/base.py:19-29` (ModuleBase)
- TEAx pipeline executor: `teax-simkit/simkit/core/pipeline_executor.py:107-228`

## Architecture Insights

### The "Lens" Pattern is the Key Abstraction

The core insight is that the traditional "step 3" (inverse design heuristics) can be formalized as a **lens** -- a projection from the full design space to a task-relevant subspace. Different users with different questions define different lenses:

- **"What's the LCOE of a 500MW fusion plant?"** -- fixes most engineering parameters, frees cost drivers
- **"Can we reduce blanket thickness by 20%?"** -- fixes most parameters, frees radial build dimensions and their downstream effects
- **"What design minimizes tritium inventory?"** -- fixes user-facing specs, frees engineering parameters, optimizes for tritium

Each lens is: a set of fixed parameters, a set of free parameters, constraints, and objectives. The full-dimensional pipeline is the invariant substrate; lenses are the variable views.

### The Pipeline is Already Lens-Ready

The generated TEAx pipeline already has the right structure:
- Entry points are typed with `EntryPointType` (LIBRARY_DEFAULT, DESIGN_ATTRIBUTE, USAGE_LITERAL)
- Entry points are grouped by source file into parameter groups
- Each parameter has a default value
- The pipeline is a pure function: given all entry point values, it deterministically produces outputs

What's missing is the **lens definition format** and the **optimization/sensitivity machinery** to operate through a lens.

### Constraint Extraction is the High-Value Long-Term Investment

While the Python utility layer (Concept B) is immediately practical, the real leverage comes from extracting constraints from SysML (Concept A). This enables:
- Automatic feasibility checking before optimization
- Constraint propagation to prune infeasible regions
- Formal verification that a design point satisfies all model constraints
- Bidirectional traceability from constraints to the SysML model

## Feasibility Assessment

### Concept B (Python utility layer): HIGH feasibility
- Can be built on today's generated code without pipeline changes
- SALib + Ax/BoTorch are mature, well-documented libraries
- The "lens" pattern is a pure Python abstraction over existing JSON schemas
- **Could prototype in 1-2 sessions**

### Concept A (SysML constraint extraction): MEDIUM feasibility
- Constraint and requirement extraction follows the same patterns as calc def extraction
- syside already supports `ConstraintUsage`, `ConstraintDefinition`, `RequirementUsage`, `RequirementDefinition`
- The hard part is binding resolution for constraint parameters (same complexity as calc input resolution)
- **Could be built incrementally alongside Phase 6-7 of the current refactor**

### Dimensionality concern: ADDRESSABLE
- Morris screening alone should reduce 200 parameters to ~20-50 active ones
- SAASBO/TuRBO are well-validated at these scales
- TEA models specifically have been shown to work with BO in recent literature
- The main risk is evaluation cost -- if the TEAx pipeline is slow, multi-fidelity methods may be needed

## Recommendations

### Near-Term (Next 1-2 sprints)

1. **Capture the "lens" concept** in a design document (this research provides the basis)
2. **Prototype a `DesignSpace` class** that wraps the generated JSON schemas with bounds and defaults
3. **Run Morris screening** on solar_battery (62 parameters) as a proof-of-concept to measure effective dimensionality

### Mid-Term (Next quarter)

4. **Build the optimization wrapper** (Ax/BoTorch integration) for constrained BO through a lens
5. **Begin constraint extraction** from SysML -- add `ConstraintDefinitionData` and `RequirementDefinitionData` to the extraction layer
6. **Generate constraint functions** alongside TEAx module code

### Long-Term (Future)

7. **Full analysis case extraction** and solver integration
8. **Multi-fidelity support** -- generate both full-fidelity and reduced-fidelity pipeline variants
9. **Interactive design exploration UI** -- let users define lenses visually and explore the design space

## Open Questions

1. **Evaluation cost**: How fast is a full TEAx pipeline evaluation? If < 1 second, brute-force sampling becomes viable. If > 1 minute, multi-fidelity is essential.

2. **Constraint formalism**: Should constraints be expressed in SysML (verifiable, model-driven) or Python (flexible, quick to iterate)? The hybrid approach (Concept C) defers this decision.

3. **Multi-objective**: Should the toolchain support Pareto front exploration (e.g., LCOE vs. capital cost vs. environmental impact)? BoTorch has mature multi-objective BO support.

4. **Lens authoring UX**: How should users define lenses? YAML? Python? A GUI? This is a product design question, not a technical one.

5. **Interaction with the current refactor**: The Phase 6-7 refactor is still in progress. Constraint extraction should wait until the extraction layer stabilizes.

6. **Feasibility classifier**: For the large-infeasible-region problem, should we train a fast classifier (RF/GP) on feasibility before running expensive BO? Or rely on SCBO's built-in constraint handling?
