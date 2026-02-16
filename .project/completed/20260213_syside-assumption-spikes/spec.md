# Spec: SysIDE AST Assumption Spikes

**Status:** Implementation Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13T17:26:40+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

The revised algorithm design (`08_algorithm_revised.md`) introduces an OutputRegistry
to replace 5 ad-hoc indexes in the backtracker. Review comments
(`design_revision_comments.md`) identified 4 empirical uncertainties that block confident
design finalization. Without resolving these, we risk repeating the implement-discover-patch
cycle that produced the current bug stream.

### Success Criteria

- [ ] Each spike question has a definitive, evidence-backed answer
- [ ] Answers are documented with exact values from real models (not inferences)
- [ ] The design revision comments' Issues 1, 2, 7, and 8 can be closed or updated
  with concrete data
- [ ] `08_algorithm_revised.md` can be updated with empirically grounded decisions

### Priority

Blocks all implementation of the OutputRegistry. This is step 2 in the iterative
process: comments (done) -> **spikes** -> update design -> repeat.

---

## Problem Statement

### Current State

The revised algorithm design makes assumptions about SysIDE parser behavior and
data format prevalence that have never been empirically verified:

1. We don't know what `source_path` format SysIDE produces for template CalcUsage
   bindings (bare name? dotted? full SysML QN?). The virtual binding rewrite in
   Step 3.5E only handles bare names -- if SysIDE produces another format, it's
   dead code.

2. We know virtual CalcUsages use qualified `instance_name` (code confirms this at
   `usage_extractor.py:255`), but we haven't traced whether downstream binding
   `source_path` values use the short or qualified form.

3. Bug 2 (EXPOSE_PURE two-hop failure) has been analyzed theoretically but the
   resolution chain has not been traced with actual data from the e2e_attr_expr model.

4. The OutputRegistry bare-name registration policy depends on knowing how many
   output names collide across CalcUsages in real models -- we've never counted.

### Desired Outcome

Four diagnostic scripts that extract exact values from real SysML models, answering
each question definitively. Results documented in a structured research note that
directly informs design updates.

---

## Scope

### In Scope

- 4 standalone diagnostic scripts in `scripts/spikes/`
- Each script loads real SysML models, extracts specific data, prints structured output
- A summary findings document at `.project/research/`
- Scripts are READ-ONLY -- no pipeline code modifications

### Out of Scope

- OutputRegistry implementation
- Any changes to the codegen pipeline
- Updating `08_algorithm_revised.md` (that happens after spike results are in)
- Testing against models outside the established fixtures + fusion-tea e2e_attr_expr

### Models to Test Against

| Model | Path | Why |
|-------|------|-----|
| solar_battery | `tests/fixtures/solar_battery_model/` | Real-world hierarchy, templates, aggregation, `:>>` aliases |
| e2e_attr_expr | `~/1cfe/fusion-tea/models/tests/e2e_attr_expr/` | Bug 2 model -- EXPOSE_PURE + CalcUsage wiring failure |
| chain_spike | `tests/fixtures/chain_spike_model/` | Simple baseline -- no hierarchy, no templates |
| catf_mfe | `tests/fixtures/catf_mfe_model/` | Large model -- stress test for bare-name collision counting |

---

## Requirements

### Functional Requirements

#### FR-1: Spike 1 -- Template Binding source_path Format

**Question:** What `source_path` format does SysIDE produce for CalcUsage bindings
inside PartDefinitions (templates)?

**Design comment addressed:** Issue 7 (probe MUST be step 1)

The script MUST:
- Load solar_battery model (has template CalcUsages on PartDefs like `Solar_Array`)
- Load e2e_attr_expr model (has CalcUsages inside untyped PartUsage)
- For each CalcUsage, report:
  - `instance_name`
  - `is_template` flag
  - `owning_part_def_qn` (if template)
  - `source_file`
- For each binding on each CalcUsage, report:
  - `param_name`
  - `binding_type` (CHAIN, REFERENCE, LITERAL, UNBOUND, EXPRESSION)
  - `source_path` (the exact string -- this is the key question)
  - `literal_value` (if LITERAL)
- Separately table template CalcUsages vs. concrete CalcUsages
- Call `extract_calculation_usages()` with `expand_templates=False` first (to see
  raw template bindings), then with `expand_templates=True` (to see virtual copies)

**Pass criteria:**
- Document the exact `source_path` format for each binding type
- Determine: are template binding source_paths bare names, dotted, or full SysML QN?
- If the format varies by binding type or model, document each case

#### FR-2: Spike 2 -- Virtual CalcUsage Instance Names and Output Keys

**Question:** For virtual (template-expanded) CalcUsages, what lookup keys would
downstream bindings use to reference their outputs?

**Design comment addressed:** Issue 1 (OutputRegistry doesn't solve virtual instance_name problem)

The script MUST:
- Load solar_battery model with `expand_templates=True`
- For each CalcUsage (concrete and virtual), report:
  - `instance_name` (the key question -- short or qualified?)
  - `qualified_name`
  - `is_template`
  - For each output attribute from the CalcDef: the dotted key
    (`{instance_name}.{output_name}`) that would be registered
- For each binding on CONSUMER CalcUsages (non-template CalcUsages that reference
  other CalcUsage outputs via CHAIN bindings), report:
  - The binding's `source_path`
  - Whether it matches the PRODUCER's dotted key or qualified key
- Explicitly compare: does the consumer's `source_path` match
  `{short_instance_name}.{output}` or `{qualified_instance_name}.{output}`?

**Pass criteria:**
- For every CHAIN binding that references a virtual CalcUsage output, confirm which
  key format matches
- Identify any bindings where NEITHER format matches (these are the gap cases)

#### FR-3: Spike 3 -- EXPOSE_PURE Transitive Resolution Chain

**Question:** Can we trace the full Bug 2 resolution chain with actual data?

**Design comment addressed:** Issues 1 + 3 (virtual instance_name + design attr two-hop)

The script MUST:
- Load e2e_attr_expr model
- Extract CalcUsages, design attributes, and computed attributes
- Trace the specific chain for `financial.total_capex`:
  1. What is the binding's `source_path`? (Expected: some form of `total_capex`)
  2. Is `total_capex` in the computed attribute index? What classification?
  3. What is the EXPOSE_PURE's `expression_text`? (Expected: `component_cost.total_cost`)
  4. What is `component_cost`'s `instance_name`? (Short or qualified?)
  5. What output catalog keys does `component_cost` produce?
  6. Does `"component_cost.total_cost"` match any of those keys?
- Also trace `lcoe.annual_om` -> FORMULA computed attr `annual_om` -> resolution chain
- Build a prototype OutputRegistry from the extracted data and test resolution

**Pass criteria:**
- Document exactly where the Bug 2 chain breaks (which key format mismatch)
- Propose the specific registration keys that would make it work
- Confirm whether `component_cost` is concrete or virtual in this model

#### FR-4: Spike 4 -- Bare-Name Ambiguity in Real Models

**Question:** How many CalcUsage output names collide across multiple CalcUsages?

**Design comment addressed:** Issue 2 (bare-name collision policy)

The script MUST:
- Load solar_battery + catf_mfe models
- After template expansion, collect all `(instance_name, output_name)` pairs
- Count:
  - Total output pairs (N)
  - Unique output names (M)
  - Output names that appear in >1 CalcUsage (K -- the ambiguous ones)
  - List each ambiguous name with all CalcUsages that produce it
- Also check: for each ambiguous bare name, do any downstream bindings actually
  reference it by bare name (vs. dotted format)?

**Pass criteria:**
- Quantify N, M, K per model
- Determine whether bare-name registration is viable (K == 0), needs collision
  handling (K small), or should be skipped entirely (K large)

### Non-Functional Requirements

- **NFR-1:** Scripts MUST follow existing spike conventions (`spike_hierarchy_ast.py`
  pattern): shebang, docstring with usage, `safe_attr()` helper, structured stdout
- **NFR-2:** Scripts MUST be independently runnable via `uv run python scripts/spikes/<name>.py`
- **NFR-3:** Output MUST be machine-parseable (consistent formatting, no interleaved prose)
- **NFR-4:** Scripts MUST NOT modify any pipeline code or data models
- **NFR-5:** Each spike SHOULD complete in <30 seconds per model

---

## Acceptance Criteria

### Core Functionality

- [ ] **AC-1:** Spike 1 produces a table of every binding's source_path format for
  template vs. concrete CalcUsages across solar_battery and e2e_attr_expr
- [ ] **AC-2:** Spike 2 produces a comparison of consumer binding source_paths vs.
  producer output catalog keys, identifying all format mismatches
- [ ] **AC-3:** Spike 3 traces the Bug 2 resolution chain with actual data values
  and identifies the exact key format mismatch point
- [ ] **AC-4:** Spike 4 quantifies bare-name collisions (N, M, K) for solar_battery
  and catf_mfe models
- [ ] **AC-5:** A summary research note documents findings with direct design implications

### Quality & Integration

- [ ] All scripts run without errors on the specified models
- [ ] Existing tests continue to pass (scripts don't touch pipeline code)
- [ ] Each finding directly maps to a design_revision_comments.md issue

---

## Related Artifacts

- **Design comments:** `.project/reports/design_revision_comments.md`
- **Revised design:** `.project/reports/08_algorithm_revised.md`
- **Bug research:** `.project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md`
- **Algorithm overview:** `.project/reports/06_algorithm_overview.md`
- **Open issues:** `.project/reports/07_open_issues.md`
- **Plan:** `.project/active/syside-assumption-spikes/plan.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_plan` (plan already requested alongside spec)
