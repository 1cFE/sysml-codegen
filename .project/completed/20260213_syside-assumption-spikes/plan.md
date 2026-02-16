# Plan: SysIDE AST Assumption Spikes

**Status:** Complete
**Spec:** `.project/active/syside-assumption-spikes/spec.md`
**Created:** 2026-02-13T17:26:40+00:00

---

## Implementation Strategy

Four independent spike scripts, each answering one question. They share a common
helper module for model loading and output formatting. Each script is self-contained
and runnable independently. Results feed into a summary research note.

### Execution Order

Spikes 1 and 4 are fully independent. Spike 2 builds on Spike 1's model loading.
Spike 3 builds on Spike 2's output key analysis. But since they're all diagnostic,
the practical order is: **write all four, run all four, write findings doc.**

```
Spike 1 (template binding format)    ─┐
Spike 4 (bare-name collisions)        │── independent, run in any order
Spike 2 (instance_name vs keys)       │
Spike 3 (EXPOSE_PURE trace)          ─┘
                                       │
                                       v
                            Summary findings doc
```

---

## Items

### Item 1: Shared helper module

**File:** `scripts/spikes/_helpers.py`

Extracted helpers used by all spikes. Follows the pattern from `spike_hierarchy_ast.py`:

```python
"""Shared utilities for SysIDE assumption spikes."""

# Model suite definitions
DEFAULT_SUITES = [
    ("solar_battery", [Path("tests/fixtures/solar_battery_model")]),
    ("chain_spike", [Path("tests/fixtures/chain_spike_model")]),
    ("e2e_attr_expr", [Path("~/1cfe/fusion-tea/models/tests/e2e_attr_expr")]),
]

EXTENDED_SUITES = DEFAULT_SUITES + [
    ("catf_mfe", [Path("tests/fixtures/catf_mfe_model")]),
]

def load_model(paths: list[Path]) -> SysMLDataExtractor:
    """Load a model, fail loudly if it doesn't work."""

def safe_attr(obj, attr, default="<missing>"):
    """Safely access attribute."""

def type_name(obj) -> str:
    """Return type(obj).__name__."""

def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print an aligned table to stdout."""

def print_section(title: str) -> None:
    """Print a section header."""
```

**Estimated effort:** Small. Mostly copy from existing spike helpers.

**Verification:** Import in each spike script without errors.

---

### Item 2: Spike 1 -- Template Binding source_path Format

**File:** `scripts/spikes/spike_template_binding_format.py`
**Answers:** Design comment Issue 7 (blocks everything)
**Models:** solar_battery, e2e_attr_expr, chain_spike

**Algorithm:**

```
1. For each model suite:
   a. Load model via SysMLDataExtractor
   b. Extract CalcDefs
   c. Call extract_calculation_usages(expand_templates=False)
      -> raw CalcUsages including templates
   d. Call extract_calculation_usages(expand_templates=True)
      -> expanded CalcUsages with virtual copies

2. For the unexpanded list (templates visible):
   For each CalcUsage where is_template == True:
     Print: instance_name, calc_def_name, owning_part_def_qn
     For each binding:
       Print: param_name, binding_type, source_path (EXACT string)

3. For the expanded list (virtual copies):
   For each CalcUsage where qualified_name contains "__" (virtual indicator):
     Print: instance_name, qualified_name
     For each binding:
       Print: param_name, binding_type, source_path (EXACT string)
       Compare: does source_path match {bare_name} or {dotted} or {sysml_qn}?

4. Summary table:
   Model | CalcUsage | Binding | source_path | Format Classification
   Where Format is one of: BARE, DOTTED, SYSML_QN, LITERAL, NONE
```

**Key API calls:**
- `SysMLDataExtractor(paths)` + `.load_models()`
- `extractor.extract_calculation_definitions()`
- `extract_calculation_usages(model, calc_defs=defs, expand_templates=False)`
- `extract_calculation_usages(model, calc_defs=defs, expand_templates=True)`

**Key data accessed:**
- `CalcUsageData.instance_name`, `.qualified_name`, `.is_template`, `.owning_part_def_qn`
- `BindingInfo.param_name`, `.binding_type`, `.source_path`, `.literal_value`

**Output format:**

```
========== SPIKE 1: Template Binding source_path Format ==========

--- Model: solar_battery ---

TEMPLATE CALCSAGES (expand_templates=False):

  Template: cost_model (owning: SolarBatteryLibrary::Solar_Array)
    Binding: wattage | REFERENCE | source_path="wattage"
    Binding: efficiency | REFERENCE | source_path="efficiency"
    ...

VIRTUAL CALCSAGES (expand_templates=True):

  Virtual: SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model
    Binding: wattage | REFERENCE | source_path="wattage"
    ...

SUMMARY:
  Model            | Templates | Virtuals | Bare | Dotted | SysML_QN | Other
  solar_battery    | 3         | 9        | 12   | 0      | 0        | 0
  e2e_attr_expr    | 0         | 0        | 0    | 4      | 2        | 0
```

**Verification:** Run on all three models. No crashes. Every binding has a format classification.

---

### Item 3: Spike 2 -- Virtual CalcUsage Instance Names and Output Keys

**File:** `scripts/spikes/spike_virtual_instance_keys.py`
**Answers:** Design comment Issue 1 (OutputRegistry virtual instance_name gap)
**Models:** solar_battery, e2e_attr_expr

**Algorithm:**

```
1. For each model:
   a. Load model, extract CalcDefs
   b. extract_calculation_usages(expand_templates=True)
   c. Build a CalcDef lookup by name

2. For each CalcUsage:
   a. Look up its CalcDef to get output_attributes
   b. Build the two candidate output keys:
      short_key = f"{short_instance_name}.{output_name}"
        where short_instance_name = instance_name.rsplit("__", 1)[-1]
        (or instance_name itself if no __ present)
      full_key = f"{instance_name}.{output_name}"
   c. Print both keys

3. For each CONSUMER CalcUsage (any CalcUsage with CHAIN bindings):
   For each CHAIN binding:
     a. Get source_path (e.g., "alpha_split.p_alpha" or "component_cost.total_cost")
     b. Identify the PRODUCER CalcUsage by extracting the instance segment
        (before the ".") and matching against all CalcUsage instance_names
     c. Report: does source_path match the producer's short_key or full_key?

4. Mismatch report:
   For each CHAIN binding where source_path matches NEITHER key format:
     Print: consumer, binding, source_path, producer short_key, producer full_key
```

**Output format:**

```
========== SPIKE 2: Virtual Instance Names and Output Keys ==========

--- Model: solar_battery ---

PRODUCER OUTPUT KEYS:

  CalcUsage: SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model
    short_instance: cost_model
    full_instance: SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model
    Output: total_cost
      short_key: cost_model.total_cost
      full_key:  SolarBatteryDesign__...cost_model.total_cost

CONSUMER BINDING -> PRODUCER KEY MATCHING:

  Consumer: annualized_financial
    Binding: total_capex <- source_path="capital_cost"
    Producer match: ??? (attempting short_key, full_key, bare_name)

MISMATCHES (source_path matches neither key format):
  [list or "None found"]
```

**Verification:** All CHAIN bindings are classified as matching short, full, or neither.

---

### Item 4: Spike 3 -- EXPOSE_PURE Transitive Resolution Chain

**File:** `scripts/spikes/spike_expose_pure_chain.py`
**Answers:** Design comment Issues 1 + 3 (Bug 2 root cause)
**Models:** e2e_attr_expr (primary), solar_battery (secondary)

**Algorithm:**

```
1. Load e2e_attr_expr model
2. Run the full extraction pipeline (but NOT the backtracker):
   a. extract_calculation_definitions()
   b. extract_calculation_usages(expand_templates=True)
   c. extract_design_attributes()
   d. _extract_and_filter_computed_attributes()

3. Find the specific entities:
   a. CalcUsage "financial" (or its qualified form)
   b. Its binding for param "total_capex"
   c. ComputedAttributeData for "total_capex" (expected: EXPOSE_PURE)
   d. CalcUsage "component_cost" (or its qualified form)
   e. DesignAttributeData for "total_capex"

4. Trace the resolution chain step by step:

   Step A: financial's binding
     Print: param_name, binding_type, source_path
     Classify source_path format

   Step B: Is source_path in computed_attr_index?
     For each computed attr, check if it matches
     Print: match found? classification? expression_text?

   Step C: If EXPOSE_PURE, what's the canonical target?
     Print: expression_text (e.g., "component_cost.total_cost")

   Step D: Is source_path in design_attr_binding_index?
     Build the index manually (parent_part.attr_name -> target)
     Print: match found? target value?

   Step E: Resolve the target to a CalcUsage output
     Print: component_cost's instance_name (short or qualified?)
     Build output catalog keys for component_cost
     Print: does target match any key?

   Step F: Build a prototype OutputRegistry
     Register all CalcUsage outputs with both short and full keys
     Register EXPOSE_PURE as alias
     Test: registry.resolve("total_capex") -> ???
     Test: registry.resolve("component_cost.total_cost") -> ???
     Print: resolution result at each step

5. Repeat for solar_battery: trace annualized_financial.total_capex chain
   (this goes through aggregation, not EXPOSE_PURE -- different path)
```

**Key imports beyond standard:**
- `_extract_and_filter_computed_attributes` from `generation/initialization.py`
- `extract_design_attributes` from `analysis/parameter_groups.py`
- `ComputedAttributeClassification` from `extraction/data_models.py`

**Output format:**

```
========== SPIKE 3: EXPOSE_PURE Transitive Resolution Chain ==========

--- Model: e2e_attr_expr ---

CHAIN TRACE: financial.total_capex

  Step A: Binding
    param_name: total_capex
    binding_type: REFERENCE
    source_path: "E2EAttrExprDesign::e2e_plant::total_capex"  (or whatever it actually is)

  Step B: Computed Attribute Index Lookup
    source_path in computed_attr_index? YES
    classification: EXPOSE_PURE
    expression_text: "component_cost.total_cost"

  Step C: EXPOSE_PURE Target
    canonical_target: "component_cost.total_cost"

  Step D: Design Attribute Binding Index
    key: "e2e_plant.total_capex"
    target: "component_cost.total_cost"

  Step E: CalcUsage Output Resolution
    component_cost instance_name: "component_cost"  (or qualified?)
    output catalog keys:
      "component_cost.total_cost" -> channel_X
    Does "component_cost.total_cost" match? YES/NO

  Step F: Prototype OutputRegistry
    registry.resolve("total_capex") = ???
    registry.resolve("e2e_plant.total_capex") = ???
    registry.resolve("component_cost.total_cost") = ???

DIAGNOSIS:
  Chain breaks at Step ___: [explanation of key format mismatch]
  Proposed fix: register additional key "___" -> channel_X
```

**Verification:** The chain trace either succeeds end-to-end or identifies the exact break point.

---

### Item 5: Spike 4 -- Bare-Name Ambiguity in Real Models

**File:** `scripts/spikes/spike_bare_name_collisions.py`
**Answers:** Design comment Issue 2 (bare-name collision policy)
**Models:** solar_battery, catf_mfe

**Algorithm:**

```
1. For each model:
   a. Load model, extract CalcDefs
   b. extract_calculation_usages(expand_templates=True)
   c. Build CalcDef lookup

2. Collect all (instance_name, output_name) pairs:
   For each CalcUsage:
     CalcDef = lookup[usage.calc_def_name]
     For each output_attr in CalcDef.output_attributes:
       Record: (usage.instance_name, output_attr.name)

3. Count bare-name ambiguity:
   output_name_to_usages: dict[str, list[str]] = defaultdict(list)
   For each (instance_name, output_name):
     output_name_to_usages[output_name].append(instance_name)

   N = total (instance_name, output_name) pairs
   M = len(output_name_to_usages)  # unique output names
   K = sum(1 for v in output_name_to_usages.values() if len(v) > 1)

4. For each ambiguous bare name (K > 0):
   Print: output_name, list of CalcUsages that produce it

5. Check downstream usage:
   For each ambiguous bare name:
     Scan all bindings across all CalcUsages
     Does any binding.source_path == bare_name (no dots, no ::)?
     Print: "bare name X is referenced by Y bindings"
```

**Output format:**

```
========== SPIKE 4: Bare-Name Ambiguity ==========

--- Model: solar_battery ---

STATISTICS:
  Total CalcUsage outputs (N): 27
  Unique output names (M): 8
  Ambiguous bare names (K): 3

AMBIGUOUS NAMES:
  "total_cost" produced by:
    - SolarBatteryDesign__...pv_module__cost_model
    - SolarBatteryDesign__...inverter__cost_model
    - SolarBatteryDesign__...frame__cost_model
  "capital_cost" produced by:
    - solar_array__capital_cost [AGG]
    - battery_system__capital_cost [AGG]
    - site_infra__capital_cost [AGG]
    - solar_battery_plant__capital_cost [AGG]

DOWNSTREAM BARE-NAME REFERENCES:
  "total_cost" referenced by bare name: 0 bindings (always dotted)
  "capital_cost" referenced by bare name: 1 binding (annualized_financial.total_capex via alias)

RECOMMENDATION:
  K=3 ambiguous names. Bare-name registration needs collision handling.
```

**Verification:** N, M, K are concrete numbers. Every ambiguous name is listed with producers.

---

### Item 6: Summary Findings Document

**File:** `.project/research/{timestamp}_spike_results_syside_assumptions.md`

Written after running all four spikes. Structure:

```markdown
# Research: SysIDE AST Assumption Spike Results

## Spike 1 Findings: Template Binding source_path Format
[Exact format observed, per model, per binding type]
[Design implication for Step 3.5E and OutputRegistry]

## Spike 2 Findings: Virtual Instance Names and Output Keys
[Short vs. qualified instance_name usage]
[Design implication for OutputRegistry registration]

## Spike 3 Findings: EXPOSE_PURE Resolution Chain
[Exact break point identified]
[Proposed registration keys]

## Spike 4 Findings: Bare-Name Collisions
[N, M, K per model]
[Policy recommendation]

## Design Comment Resolutions
| Comment Issue | Finding | Resolution |
|---|---|---|
| Issue 1 (virtual instance_name) | [spike 2 result] | [update to design] |
| Issue 2 (bare-name ambiguity) | [spike 4 result] | [policy choice] |
| Issue 3 (design attr two-hop) | [spike 3 result] | [approach decision] |
| Issue 7 (probe first) | [spike 1 result] | [design confidence] |
```

**Verification:** Every design comment issue has a corresponding finding and resolution.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| e2e_attr_expr model not loadable (lives in fusion-tea, not sysml-codegen) | Medium | Blocks Spike 3 | Fall back to constructing the scenario from solar_battery, or copy the fixture |
| catf_mfe fixture not complete (may be a subset) | Low | Reduces Spike 4 coverage | Use solar_battery as primary, catf_mfe as secondary |
| SysIDE produces a format we haven't predicted | Medium | Changes OutputRegistry design | That's exactly why we're running spikes -- discovery is the point |
| Template expansion crashes on e2e_attr_expr (no PartDef templates) | Low | Spike 1 less interesting for this model | Still valuable to confirm CalcUsages are concrete, not virtual |

---

## Implementation Notes

### Item 1 Completion
**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/_helpers.py` with shared utilities
- Functions: `load_model()`, `safe_attr()`, `type_name()`, `print_section()`, `print_subsection()`, `print_table()`
- Constants: `DEFAULT_SUITES` (solar_battery, chain_spike, e2e_attr_expr), `EXTENDED_SUITES` (+catf_mfe)
- Also re-exports `CalcUsageData` and `extract_calculation_usages` from the extraction layer

**Verification:**
- All imports succeed
- Formatting helpers produce correctly aligned output
- `load_model` signature matches existing spike pattern (returns model, adapter, extractor tuple)
- Uses python-dotenv to load SYSIDE_LICENSE_KEY from `~/1cfe/agentic-mbse/.env`

### Item 2 Completion (Spike 1)
**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_template_binding_format.py`
- Runs on solar_battery, chain_spike, e2e_attr_expr models
- Classifies every binding source_path as BARE, DOTTED, SYSML_QN, LITERAL, EXPRESSION, or NONE

**Key Findings:**
- **ZERO bare-name source_paths** across all 3 models
- **REFERENCE bindings always produce SYSML_QN** format (e.g., `SolarBatteryLibrary::'PV Module'::cost_model::wattage`)
- **CHAIN bindings always produce DOTTED** format (e.g., `annualized_financial.annualized_capital_cost`)
- Template bindings (expand_templates=False) use the SAME SYSML_QN format as concrete bindings
- Virtual CalcUsages (expand_templates=True) INHERIT the original source_path format unchanged

**Format Distribution:**
- chain_spike: 6 DOTTED, 6 SYSML_QN (0 BARE)
- e2e_attr_expr: 4 DOTTED, 16 SYSML_QN (0 BARE)
- solar_battery: 8 DOTTED, 50 SYSML_QN, 4 LITERAL (0 BARE)

**Design Implication:** The virtual binding rewrite in Step 3.5E that handles bare-name source_paths
may be dead code. SysIDE always produces SYSML_QN for REFERENCE and DOTTED for CHAIN. The
OutputRegistry needs to handle these two formats, not bare names.

### Item 3 Completion (Spike 2)
**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_virtual_instance_keys.py`
- Runs on solar_battery, e2e_attr_expr models

**Key Findings:**
- All CHAIN bindings use DOTTED format with the **short** instance name
  (e.g., `annualized_financial.annualized_capital_cost`, NOT the qualified form)
- For solar_battery: 4 CHAIN bindings, all use short_key format, all match FULL_KEY
  (because concrete CalcUsage instance_name IS the short name)
- For e2e_attr_expr: 2 CHAIN bindings, both use short_key format, both match FULL_KEY
  (all CalcUsages are concrete in this model -- no templates)
- **No CHAIN bindings target virtual CalcUsage outputs** in either model.
  Virtual CalcUsages (cost_model instances) are leaf nodes -- they produce outputs
  consumed by aggregation expressions (`:>>` aliases), NOT by CHAIN bindings.
- Short keys for virtual CalcUsages COLLIDE: 8 virtual CalcUsages all produce
  `cost_model.total_cost` as their short_key. Only full_key is unique.

**Design Implication:** CHAIN bindings always use short instance names. Virtual CalcUsage
outputs are consumed via aggregation/`:>>` aliases, not direct CHAIN references. The
OutputRegistry must register both short_key AND full_key for virtual CalcUsages, but
CHAIN resolution will use short_key (which is ambiguous for virtual CalcUsages --
confirming Issue 2's bare-name collision concern at the dotted-key level).

### Item 4 Completion (Spike 3)
**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_expose_pure_chain.py`
- Runs on e2e_attr_expr (Bug 2 model) and solar_battery
- Builds computed_attr_index, design_attr_binding_index, and output_catalog
- Traces resolution chains step by step

**Key Findings (e2e_attr_expr -- Bug 2 model):**

1. **EXPOSE_PURE expression_text is NOT a dotted path.** The design assumed
   `expression_text = "component_cost.total_cost"` but SysIDE actually produces
   `expression_text = ".(component_cost)"` -- the raw FeatureChainExpression AST text.
   The useful information is in the `references` field:
   - `name='total_cost' qualified='E2EAttrExprLibrary::ComponentCostCalc::total_cost'`
   - `name='component_cost' qualified='E2EAttrExprDesign::e2e_plant::component_cost'`

2. **Design attr binding index works correctly:**
   `e2e_plant.total_capex -> component_cost.total_cost`
   This IS a valid dotted path and IS in the output catalog.

3. **The resolution chain for `financial.total_capex`:**
   - source_path = `E2EAttrExprDesign::e2e_plant::financial::total_capex` (SYSML_QN)
   - computed_attr_index finds it via bare name `total_capex` -> EXPOSE_PURE
   - But expression_text `.(component_cost)` is NOT parseable as a dotted key
   - design_attr_binding_index key `e2e_plant.total_capex` is NOT matched
     because the source_path is `financial.total_capex` (wrong parent!)
   - Chain BREAKS at Step C: expression_text format mismatch

4. **The correct resolution path is through `references`:**
   - EXPOSE_PURE references[0] = `total_cost` on `ComponentCostCalc`
   - EXPOSE_PURE references[1] = `component_cost` CalcUsage
   - Combined: `component_cost.total_cost` which IS in the output catalog
   - OutputRegistry must use `references` to build the canonical target, NOT expression_text

5. **Direct CHAIN bindings work fine:**
   - `lcoe.annualized_capital` source_path = `financial.annualized_cost`
   - Resolves directly in output catalog -> `financial__annualized_cost`

**Key Findings (solar_battery):**
- EXPOSE_PURE for `misc_hardware_cost`: same pattern, expression_text = `.(allocation_model)`
- Design attr binding index has broken key: `'.misc_hardware_cost'` (parent part is empty)
- `annualized_financial.total_capex` source_path = SYSML_QN `SolarBatteryLibrary::'Solar Battery Plant'::capital_cost`
  -- resolves through aggregation path, NOT through EXPOSE_PURE or design attr

**Design Implications:**
- OutputRegistry MUST NOT use `expression_text` for EXPOSE_PURE targets
- Must use `references` field to reconstruct `{instance_name}.{output_name}`
- The design_attr_binding_index two-hop approach works when keys match,
  but the key format requires `parent_part.attr_name` which may not match
  the binding's SYSML_QN source_path

### Item 5 Completion (Spike 4)
**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_bare_name_collisions.py`
- Runs on solar_battery and catf_mfe models

**Key Findings:**

solar_battery: N=56, M=16, **K=5** ambiguous bare names
- `total_cost`, `material_cost`, `fab_cost`, `install_cost`, `idiot_index`
  -- each produced by 9 virtual CalcUsages (all `cost_model` instances)
- **Zero bare-name references** in any binding source_path

catf_mfe: N=46, M=19, **K=5** ambiguous bare names
- `volume` (13 producers), `a` (13 producers), `area` (2), `p_net` (2), `pump_power` (2)
- **Zero bare-name references** in any binding source_path

**Cross-model totals:**
- 10 ambiguous bare names across both models
- **0 bare-name references** in any binding across both models

**Policy Recommendation:** Bare-name registration is OPTIONAL and can be skipped entirely.
No binding source_path in any tested model uses a bare output name. All references use
dotted (`instance.output`) or SysML QN (`Namespace::part::attr`) format. This eliminates
Issue 2 -- no collision handling needed because the feature isn't needed.

---

### Item 6 Completion (Summary Findings)
**Completed:** 2026-02-13
**Changes Made:**
- Created `.project/research/20260213_spike_results_syside_assumptions.md`
- Synthesizes findings from all 4 spikes into design comment resolutions
- Provides concrete recommendations for `08_algorithm_revised.md` update

---

## Definition of Done

- [x] All 4 spike scripts run without errors on their target models
- [x] Each spike produces structured output matching the format specified above
- [x] Summary findings doc is written with concrete data (no hand-waving)
- [x] Each design_revision_comments.md issue has a data-backed resolution
- [ ] Ready to update `08_algorithm_revised.md` in the next iteration
